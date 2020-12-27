import pathlib
import re
from typing import Iterable
from typing import NewType
from typing import TextIO

from tap import Tap

Ingredient = NewType('Ingredient', str)
Allergen = NewType('Allergen', str)
Food = tuple[set[Ingredient], set[Allergen]]
Causes = dict[Allergen, set[Ingredient]]


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a list of suspects and clues

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        allIngredients = set()
        allAllergens = set()
        foods = []
        for ingredients, allergens in readFoods(file):
            allIngredients |= ingredients
            allAllergens |= allergens
            foods.append((ingredients, allergens))

    causes = buildSources(allIngredients, allAllergens, foods)
    safe, causes = solve(allIngredients, causes)
    print(sum(1 for ingredients, allergens in foods for ingredient in ingredients if ingredient in safe))
    print(','.join(ingredient for allergen in sorted(causes) for ingredient in causes[allergen]))


def buildSources(allIngredients: set[Ingredient], allAllergens: set[Allergen], foods: Iterable[Food]) -> Causes:
    causes = {a: allIngredients.copy() for a in allAllergens}
    for ingredients, allergens in foods:
        for allergen in allergens:
            causes[allergen] &= ingredients
    return causes


def solve(allIngredients: set[Ingredient], causes: Causes) -> tuple[set[Ingredient], Causes]:
    safe = allIngredients.copy()
    solved = [k for k, v in causes.items() if len(v) == 1]
    for effect in solved:
        [cause] = causes[effect]
        safe.discard(cause)
        for allergen, ingredients in causes.items():
            if allergen == effect:
                continue
            ingredients.discard(cause)
            if len(ingredients) == 1 and allergen not in solved:
                solved.append(allergen)
    return safe, causes


def readFoods(file: TextIO) -> Iterable[Food]:
    linePattern = re.compile(r'^(?P<ingredients>[\w ]+) \(contains (?P<allergens>[\w ,]+)\)\s*$')

    for line in file:
        match = linePattern.match(line)
        yield set(match.group('ingredients').split()), set(match.group('allergens').split(', '))


if __name__ == '__main__':
    parser = MainArgs(description='Deduction game')
    main(parser.parse_args())
