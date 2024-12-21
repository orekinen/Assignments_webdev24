import json
import os
from difflib import get_close_matches
class DictionaryApp:
    def __init__(self):
        self.dictionary = {
            "koulu": "school",
            "oppilas": "student",
            "opettaja": "teacher"
        }
        self.load_dictionary()

    def load_dictionary(self):
        try:
            with open('dictionary.json', 'r') as f:
                self.dictionary = json.load(f)
        except:
            pass

    def save_dictionary(self):
        try:
            with open('dictionary.json', 'w') as f:
                json.dump(self.dictionary, f, indent=2)
        except:
            print("Error saving dictionary")

    def find_word(self, word):
        word = word.lower().strip()
        if word in self.dictionary:
            return self.dictionary[word]
        matches = get_close_matches(word, self.dictionary.keys(), n=1)
        if matches:
            print(f"Did you mean: {matches[0]}?")
        return None

    def add_word(self, word, definition):
        if word and definition:
            self.dictionary[word.lower().strip()] = definition.strip()
            return True
        return False

    def run(self):
        print("\nDictionary Application")
        print("Commands: search/s, add/a, quit/q")

        while True:
            command = input("\nEnter command: ").lower().strip()

            if command in ['quit', 'q']:
                break
            elif command in ['search', 's']:
                word = input("Enter word: ")
                if result := self.find_word(word):
                    print(f"{word} = {result}")
            elif command in ['add', 'a']:
                word = input("Enter word: ")
                defn = input("Enter definition: ")
                if self.add_word(word, defn):
                    print("Word added successfully")
            else:
                print("Invalid command")

        self.save_dictionary()
        print("Goodbye!")

if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
