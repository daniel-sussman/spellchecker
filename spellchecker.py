from pynput import keyboard
from collections import deque
import os, string, json

class TextHandler:
    def __init__(self):
        self.word_checker = WordChecker()
        self.view = View(self)
        self.last_word = ""
        self.text = []
        self.next_word = []
        self.autocomplete = []
        self.autocomplete_index = 0
        self.display()

    def add_char(self, char):
        self.last_word += char
        self.display()

    def handle_space(self, space):
        word = self.last_word
        if self.autocomplete_index > 0:
            word = self.autocomplete[self.autocomplete_index]
        elif self.word_checker.check_word(word.lower()):
            pass
        else:
            suggested_word = self.word_checker.fetch_suggestions(word)
            word = suggested_word or word
        self.text.append(word + space)
        self.last_word = ''
        self.autocomplete = []
        self.autocomplete_index = 0
        self.display()

    def handle_backspace(self):
        if self.last_word:
            self.last_word = self.last_word[:-1]
        elif self.text:
            self.last_word = self.text.pop()[:-1]
        self.display()

    def move_autocomplete_selector(self, direction):
        if not self.autocomplete:
            return
        
        if direction == 'down':
            self.autocomplete_index += 1
        else:
            self.autocomplete_index -= 1
        self.autocomplete_index = self.autocomplete_index % len(self.autocomplete)
        self.display()

    def display(self):
        if len(self.last_word) > 2:
            self.autocomplete = self.word_checker.auto_complete(self.last_word.lower())

        self.view.show(''.join(self.text) + self.last_word, self.autocomplete, self.autocomplete_index)

class View():
    def __init__(self, text_handler):
        self.text_handler = text_handler
        
    def show(self, text, autocomplete, autocomplete_index):
        os.system('clear')
        print(text + '_\n')
        for (index, suggestion) in enumerate(autocomplete):
            indent = " -> " if index == autocomplete_index else "    "
            print(indent + suggestion)

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
        return [w for w in words if w[:len(proto_word)] == proto_word][:5]

    # How can I run this in a separate thread to prevent thread timeout?
    def fetch_suggestions(self, word):
        search_queue = deque()
        already_tried = set()

        search_queue += self.fetch_permutations(word)
        
        while search_queue:
            try_word = search_queue.popleft()
            if try_word in already_tried:
                continue
            already_tried.add(try_word)
            if self.check_word(try_word):
                return try_word
            else:
                search_queue += self.fetch_permutations(try_word, already_tried)
        
        return None

    def fetch_permutations(self, word, already_tried = set()):
        permutations = []
        for i in range(len(word)):
            for new_char in string.ascii_lowercase:
                next_permutation = word[:i] + new_char + word[i + 1:]
                if next_permutation == word or next_permutation in already_tried:
                    continue
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
        elif key == keyboard.Key.down:
            handler.move_autocomplete_selector('down')
        elif key == keyboard.Key.up:
            handler.move_autocomplete_selector('up')

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

