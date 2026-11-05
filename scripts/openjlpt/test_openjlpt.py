from openjlpt import find_word, get_grammar

word = find_word("食べる")

print("Word:", word.word)
print("Reading:", word.reading)
print("Romaji:", word.romaji)
print("Meaning:", word.meanings)
print("Level:", word.level)

grammar = get_grammar("N5")

print("\nN5 grammar count:", len(grammar))
print(grammar[0])