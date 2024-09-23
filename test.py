import string

def fetch_permutations(word):
    new_words = []
    for i in range(len(word)):
        print(f"checking {word[i]}")
        for new_char in string.ascii_lowercase:
            if new_char != word[i]:
                new_words.append(word[:i] + new_char + word[i + 1:])
    return new_words[::-1]

result = fetch_permutations('hi')
print(result)