from backend.services.content_catalog import load_challenges, merge_published_challenges


def test_published_row_overrides_static_challenge_by_slug():
    static = [{"id": "py-greeting", "title": "Static", "course_id": "python"}]
    published = [{
        "id": 42,
        "slug": "py-greeting",
        "status": "published",
        "content_type": "exercise",
        "course_slug": "python",
        "lesson_slug": "py-start",
        "title": "DB version",
        "description": "Published description.",
        "starter_code": "print('db')",
        "language": "python",
        "difficulty": "easy",
        "xp_reward": 120,
    }]

    result = merge_published_challenges(static, published)

    assert len(result) == 1
    assert result[0]["title"] == "DB version"
    assert result[0]["xp"] == 120
    assert result[0]["problem_id"] == 42


def test_published_row_with_new_slug_is_appended():
    result = merge_published_challenges(
        [{"id": "static", "title": "Static"}],
        [{
            "id": 7,
            "slug": "new-db",
            "status": "published",
            "content_type": "bug_lab",
            "course_slug": "javascript",
            "lesson_slug": "js-dom-p5",
            "title": "New bug lab",
            "description": "Find the bug.",
            "starter_code": "const x = 1;",
            "language": "javascript",
            "difficulty": "hard",
            "xp_reward": 90,
        }],
    )

    assert [item["id"] for item in result] == ["static", "new-db"]
    assert result[-1]["difficulty"] == "advanced"


def test_load_challenges_falls_back_when_db_is_unavailable():
    class BrokenDB:
        def get_published_content(self):
            raise RuntimeError("database unavailable")

    static = [{"id": "fallback", "title": "Fallback"}]
    assert load_challenges(BrokenDB(), static) == static


def test_non_published_or_unlinked_rows_are_not_exposed():
    static = [{"id": "static", "title": "Static"}]
    rows = [
        {"id": 1, "slug": "draft", "status": "draft", "course_slug": "python", "content_type": "exercise"},
        {"id": 2, "slug": "unlinked", "status": "published", "course_slug": "", "content_type": "exercise"},
    ]
    assert merge_published_challenges(static, rows) == static
