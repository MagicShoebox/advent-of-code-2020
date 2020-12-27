import pathlib
import re
from typing import Iterable
from typing import NewType
from typing import TextIO

from tap import Tap

Ingredient = NewType('Ingredient', str)
Allergen = NewType('Allergen', str)
Food = tuple[set[Ingredient], set[Allergen]]
Effects = dict[Ingredient, set[Allergen]]
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

    effects, causes = buildSources(allIngredients, allAllergens, foods)
    solve(effects, causes)
    print(sum(1 for ingredients, allergens in foods for ingredient in ingredients if len(effects[ingredient]) == 0))


def buildSources(allIngredients: set[Ingredient], allAllergens: set[Allergen], foods: Iterable[Food]) \
        -> tuple[Effects, Causes]:
    effects = {i: allAllergens.copy() for i in allIngredients}
    causes = {a: allIngredients.copy() for a in allAllergens}
    for ingredients, allergens in foods:
        for allergen in allergens:
            causes[allergen] &= ingredients
    return effects, causes


def solve(effects: Effects, causes: Causes) -> None:
    solved = [k for k, v in causes.items() if len(v) == 1]
    for effect in solved:
        [cause] = causes[effect]
        for ingredient, allergens in effects.items():
            if ingredient == cause:
                continue
            allergens.discard(effect)
        for allergen, ingredients in causes.items():
            if allergen == effect:
                continue
            ingredients.discard(cause)
            if len(ingredients) == 1 and allergen not in solved:
                solved.append(allergen)


def readFoods(file: TextIO) -> Iterable[Food]:
    linePattern = re.compile(r'^(?P<ingredients>[\w ]+) \(contains (?P<allergens>[\w ,]+)\)\s*$')

    for line in file:
        match = linePattern.match(line)
        yield set(match.group('ingredients').split()), set(match.group('allergens').split(', '))


if __name__ == '__main__':
    parser = MainArgs(description='Deduction game')
    main(parser.parse_args())
