import models
import reader

with open("gol_patterns/windmill.rle") as f:
    string = f.read()

b = models.Board(reader.rle(string))

while True:
    changed = b.next_generation()
    if b.repeated_previous_states:
        break
