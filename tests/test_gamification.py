from datetime import date, timedelta

import pytest

from backend.services import gamification


class Result:
    def __init__(self, data):
        self.data = data


class Query:
    def __init__(self, client, table):
        self.client = client
        self.table = table
        self.filters = []
        self.operation = 'select'
        self.payload = None
        self.conflict = None

    def select(self, *_fields):
        self.operation = 'select'
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def limit(self, _value):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def insert(self, payload):
        self.operation = 'insert'
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = 'update'
        self.payload = payload
        return self

    def upsert(self, payload, on_conflict=None):
        self.operation = 'upsert'
        self.payload = payload
        self.conflict = [item.strip() for item in (on_conflict or '').split(',') if item.strip()]
        return self

    def delete(self):
        self.operation = 'delete'
        return self

    def execute(self):
        rows = self.client.rows.setdefault(self.table, [])
        matches = [row for row in rows if all(row.get(field) == value for field, value in self.filters)]
        if self.operation == 'select':
            return Result([dict(row) for row in matches])
        if self.operation == 'insert':
            row = dict(self.payload)
            if 'id' not in row:
                row['id'] = self.client.next_id
                self.client.next_id += 1
            rows.append(row)
            return Result([dict(row)])
        if self.operation == 'update':
            for row in matches:
                row.update(self.payload)
            return Result([dict(row) for row in matches])
        if self.operation == 'delete':
            self.client.rows[self.table] = [row for row in rows if row not in matches]
            return Result([])
        if self.operation == 'upsert':
            existing = next((row for row in rows if self.conflict and all(row.get(key) == self.payload.get(key) for key in self.conflict)), None)
            if existing:
                existing.update(self.payload)
                return Result([dict(existing)])
            row = dict(self.payload)
            if 'id' not in row:
                row['id'] = self.client.next_id
                self.client.next_id += 1
            rows.append(row)
            return Result([dict(row)])
        raise AssertionError(f'Unsupported operation: {self.operation}')


class FakeClient:
    def __init__(self):
        self.next_id = 1
        self.rows = {
            'gamification_profiles': [],
            'xp_events': [],
            'learning_streaks': [],
            'badges': [],
            'user_badges': [],
            'submissions': [],
        }

    def table(self, table):
        return Query(self, table)


@pytest.fixture()
def fake_client(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(gamification.db, '_client', client)
    return client


def test_award_xp_is_idempotent(fake_client):
    first = gamification.award_xp(7, 'submission:10', 'accepted_submission', 80)
    retry = gamification.award_xp(7, 'submission:10', 'accepted_submission', 80)

    assert first['awarded'] is True
    assert retry == {'awarded': False, 'xp_amount': 0, 'reason': 'already_awarded'}
    assert fake_client.rows['xp_events'][0]['xp_amount'] == 80
    assert gamification._profile(7)['total_xp'] == 80


def test_streak_same_day_increment_and_gap_reset(fake_client):
    first_day = date(2026, 8, 24)
    first = gamification.record_activity(7, 'lesson', activity_day=first_day)
    same_day = gamification.record_activity(7, 'challenge', activity_day=first_day)
    next_day = gamification.record_activity(7, 'challenge', activity_day=first_day + timedelta(days=1))
    gap_day = gamification.record_activity(7, 'challenge', activity_day=first_day + timedelta(days=3))

    assert first['current_streak'] == 1
    assert same_day['current_streak'] == 1
    assert next_day['current_streak'] == 2
    assert gap_day['current_streak'] == 1
    assert gap_day['longest_streak'] == 2


def test_only_accepted_submission_gets_reward(fake_client):
    problem = {'id': 3, 'xp_reward': 100}
    rejected = gamification.award_submission_rewards(7, 11, problem, {'status': 'rejected'})
    assert rejected == {'awarded': False, 'reason': 'submission_not_accepted'}
    assert fake_client.rows['xp_events'] == []


def test_badge_awarded_once_and_bonus_is_added(fake_client):
    fake_client.rows['badges'] = [{
        'id': 4,
        'slug': 'first-win',
        'title': 'First win',
        'description': 'Pass one challenge',
        'condition_type': 'accepted_submissions',
        'condition_value': 1,
        'xp_reward': 25,
    }]
    fake_client.rows['submissions'] = [{'id': 20, 'user_id': 7, 'status': 'accepted', 'problems': {'content_type': 'exercise'}}]
    problem = {'id': 3, 'xp_reward': 100}

    first = gamification.award_submission_rewards(7, 20, problem, {'status': 'accepted'})
    retry = gamification.award_submission_rewards(7, 20, problem, {'status': 'accepted'})

    assert len(first['badges']) == 1
    assert retry['badges'] == []
    assert len(fake_client.rows['user_badges']) == 1
    assert gamification._profile(7)['total_xp'] == 125
