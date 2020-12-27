import pathlib
from typing import Callable
from typing import Literal
from typing import NewType
from typing import TextIO

from tap import Tap

PLAYER = Literal[1, 2]
Card = NewType('Card', int)
Deck = NewType('Deck', list[Card])


class MainArgs(Tap):
    file: pathlib.Path  # A text file with the two decks

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        deck1, deck2 = readDecks(file)
    winner, deck = war(traditional, deck1[:], deck2[:])
    print(sum((i + 1) * c for i, c in enumerate(reversed(deck))))
    winner, deck = war(recursive, deck1, deck2)
    print(sum((i + 1) * c for i, c in enumerate(reversed(deck))))


def war(fight: Callable[[Card, Card, Deck, Deck], PLAYER], deck1: Deck, deck2: Deck) -> tuple[PLAYER, Deck]:
    rounds = set()
    winner: PLAYER
    deck: Deck
    while deck1 and deck2:
        td1, td2 = tuple(deck1), tuple(deck2)
        if (td1, td2) in rounds:
            winner = 1
            deck = deck1
            return winner, deck
        rounds.add((td1, td2))
        card1, card2 = deck1.pop(0), deck2.pop(0)
        if fight(card1, card2, deck1, deck2) == 1:
            deck1.extend([card1, card2])
        else:
            deck2.extend([card2, card1])
    if deck1:
        winner = 1
        deck = deck1
    else:
        winner = 2
        deck = deck2
    return winner, deck


def traditional(card1: Card, card2: Card, *_) -> PLAYER:
    winner: PLAYER
    if card1 > card2:
        winner = 1
    else:
        winner = 2
    return winner


def recursive(card1: Card, card2: Card, deck1: Deck, deck2: Deck) -> PLAYER:
    if len(deck1) < card1 or len(deck2) < card2:
        return traditional(card1, card2)
    winner, _ = war(traditional, deck1[:card1], deck2[:card2])
    return winner


def readDecks(file: TextIO) -> tuple[Deck, Deck]:
    next(file)  # Header
    deck1 = []
    for line in file:
        if str.isspace(line):
            break
        else:
            deck1.append(Card(int(line)))
    next(file)  # Header
    deck2 = []
    for line in file:
        if str.isspace(line):
            break
        else:
            deck2.append(Card(int(line)))
    return Deck(deck1), Deck(deck2)


if __name__ == '__main__':
    parser = MainArgs(description='War card game')
    main(parser.parse_args())
