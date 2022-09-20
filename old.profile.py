import models
import reader

with open("my_patterns/1.rle") as f:
    string = f.read()

b = models.Board(reader.rle(string))

while True:
    changed = b.next_generation()
    if b.repeated_previous_states:
        break
