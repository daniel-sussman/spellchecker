from pynput import keyboard
import os, json, Levenshtein

class TextHandler:
    def __init__(self):
        self.word_checker = WordChecker()
        self.view = View(self)
        self.last_word = ""
        self.text = []
        self.next_word = []
        self.suggestions = []
        self.selector_index = 0
        self.display()

    def add_char(self, char):
        self.last_word += char
        self.display()

    def handle_space(self, space):
        word = self.last_word
        if self.word_checker.check_word(word.lower()):
            pass
        elif self.suggestions:
            word = self.suggestions[self.selector_index]
        else:
            self.suggestions = self.word_checker.fetch_suggestions(word)
            self.display()
            return

        self.suggestions = []
        self.selector_index = 0
        self.text.append(word + space)
        self.last_word = ''
        self.display()

    def handle_backspace(self):
        if self.last_word:
            self.last_word = self.last_word[:-1]
        elif self.text:
            self.last_word = self.text.pop()[:-1]
        self.display()

    def move_selector(self, direction):
        if not self.suggestions:
            return
        
        if direction == 'down':
            self.selector_index += 1
        else:
            self.selector_index -= 1
        self.selector_index = self.selector_index % len(self.suggestions)
        self.display()

    def display(self):
        self.view.show(''.join(self.text) + self.last_word, self.suggestions, self.selector_index)

class View():
    def __init__(self, text_handler):
        self.text_handler = text_handler
        
    def show(self, text, suggestions, selector_index):
        os.system('clear')
        print(text + '_\n')
        for (index, suggestion) in enumerate(suggestions):
            indent = " -> " if index == selector_index else "    "
            print(indent + suggestion)

class WordChecker():
    def __init__(self):
        self.valid_words = self._fetch_valid_words()
        self.dictionary = self._fetch_dictionary(self.valid_words)

    def _fetch_valid_words(self):
        with open('words_dictionary.json') as word_file:
            valid_words = json.load(word_file)
        return valid_words

    def _fetch_dictionary(self, valid_words):
        word_length_dictionary = {}
        for word in valid_words:
            key = len(word)
            if word_length_dictionary.get(key):
                word_length_dictionary[key].append(word)
            else:
                word_length_dictionary[key] = [word]
        return word_length_dictionary
    
    def check_word(self, word):
        word = ''.join([char for char in word if char.isalpha()])
        return self.valid_words.get(word) if word else True
    
    def fetch_suggestions(self, word):
        words = []
        char_range = [n for n in range(len(word) - 1, len(word) + 2) if n > 0]
        for wordlist in [v for (k, v) in self.dictionary.items() if k in char_range]:
            words.extend(wordlist)
        words.sort(key=lambda candidate: Levenshtein.distance(word, candidate))
        return words[:5]

def on_press(key, handler):
    if key == keyboard.Key.esc:
        os.system('clear')
        return False
    
    try:
        handler.add_char(key.char) if key.char.isalpha() else handler.handle_space(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            handler.handle_space(' ')
        elif key == keyboard.Key.enter:
            handler.handle_space('\n')
        elif key == keyboard.Key.backspace:
            handler.handle_backspace()
        elif key == keyboard.Key.down:
            handler.move_selector('down')
        elif key == keyboard.Key.up:
            handler.move_selector('up')

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

