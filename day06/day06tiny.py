import sys
from itertools import takewhile

stripped = map(str.rstrip, open(sys.argv[1], 'r'))
blocks = ([line, *takewhile(bool, stripped)] for line in stripped)
records = [[set(line) for line in block] for block in blocks]
print(sum(len(set.union(*record)) for record in records))
print(sum(len(set.intersection(*record)) for record in records))
