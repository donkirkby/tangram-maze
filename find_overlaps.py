import re
from collections import Counter
from pathlib import Path


def main():
    path = Path('/etc/dictionaries-common/words')
    with path.open() as f:
        all_words = (word.strip() for word in f)
        clean_words = (word
                       for word in all_words
                       if re.match('^[a-z]+$', word))
        lower_words = [word
                       for word in clean_words
                       if word.islower()]
        start_counts: Counter[str] = Counter()
        mid_counts: Counter[str] = Counter()
        end_counts: Counter[str] = Counter()
        for word in lower_words:
            start = word[:3]
            start_counts[start] += 1
            for i in range(1, len(word)-3):
                mid = word[i:i+3]
                mid_counts[mid] += 1
            end = word[-3:]
            end_counts[end] += 1
        print(start_counts.most_common(100))
        print(mid_counts.most_common(100))
        print(end_counts.most_common(100))


main()
