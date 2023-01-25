import random

detect = 0
all = 0
for x in range(0, 200):
    if random.getrandbits(2) == 1:
        detect += 1
    all += 1

print(detect/all)