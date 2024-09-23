from pynput import keyboard
from collections import deque
import os, string, json

class TextHandler:
    def __init__(self):
        self.word_checker = WordChecker()
        self.last_word = ""
        self.text = []
        self.next_word = []
        self.display()

    def add_char(self, char):
        self.last_word += char
        self.display()

    def handle_space(self, space):
        if self.word_checker.check_word(self.last_word.lower()):
            self.text.append(self.last_word + space)
            self.last_word = ''
            self.display()
        else:
            suggestions = self.word_checker.fetch_suggestions(self.last_word)
            if suggestions:
                self.text.append(suggestions[0] + space)
                self.last_word = ''
                self.display(suggestions)
            else:
                self.display(f"No suggestions for '{self.last_word}'.")

    def handle_backspace(self):
        if self.last_word:
            self.last_word = self.last_word[:-1]
        elif self.text:
            self.last_word = self.text.pop()[:-1]
        self.display()

    def display(self, message=None):
        os.system('clear')
        print(''.join(self.text) + self.last_word + '_')
        print(message)
        if len(self.last_word) > 2:
            self.next_word = self.word_checker.auto_complete(self.last_word.lower())
            print()
            print(self.next_word)

class WordChecker():
    def __init__(self):
        self.valid_words = self.fetch_valid_words()

    def fetch_valid_words(self):
        with open('words_dictionary.json') as word_file:
            valid_words = json.load(word_file)
        return valid_words
    
    def fetch_common_words(self):
        with open('common_words.json') as word_file:
            common_words = json.load(word_file)
        return common_words
    
    def auto_complete(self, proto_word):
        proto_word = ''.join([char for char in proto_word if char.isalpha()])
        words = self.valid_words.keys()
        return [w for w in words if w[:len(proto_word)] == proto_word][:6]

    # How can I run this in a separate thread to prevent thread timeout?
    def fetch_suggestions(self, word):
        search_queue = deque()
        search_queue += self.fetch_permutations(word)
        already_tried = {}
        results = []
        
        # Why is this giving me duplicate results?
        while len(results) < 4 and search_queue and len(search_queue) < 5000000:
            try_word = search_queue.popleft()
            already_tried[try_word] = True
            if self.check_word(try_word):
                results.append(try_word)
            else:
                search_queue += self.fetch_permutations(try_word, already_tried)
        
        return results

    def fetch_permutations(self, word, already_tried = {}):
        permutations = []
        for i in range(len(word)):
            for new_char in string.ascii_lowercase:
                if new_char == word[i]:
                    continue
                next_permutation = word[:i] + new_char + word[i + 1:]
                if not next_permutation in already_tried:
                    already_tried[next_permutation] = True
                    permutations.append(next_permutation)
        return permutations[::-1]
    
    def check_word(self, word):
        word = ''.join([char for char in word if char.isalpha()])
        return self.valid_words.get(word)

def on_press(key, handler):
    if key == keyboard.Key.esc:
        os.system('clear')
        return False
    
    try:
        handler.add_char(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            handler.handle_space(' ')
        elif key == keyboard.Key.enter:
            handler.handle_space('\n')
        elif key == keyboard.Key.backspace:
            handler.handle_backspace()

def on_release(key):
    if key == keyboard.Key.esc:
        os.system('clear')
        return False

handler = TextHandler()

with keyboard.Listener(
    on_press=lambda key: on_press(key, handler),
    on_release=on_release,
    suppress=True
) as listener:
    listener.join(timeout=500)

