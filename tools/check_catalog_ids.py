from collections import Counter
from learning_experiences import PRACTICE_CHALLENGES

counts = Counter(item['id'] for item in PRACTICE_CHALLENGES)
for challenge_id, count in sorted(counts.items()):
    if count > 1:
        print(challenge_id, count)
