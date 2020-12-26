import pathlib
import re
from typing import Iterable
from typing import TextIO
from typing import Union

import numpy as np
from tap import Tap

FLIP = slice(None, None, -1)  # For convenience, not in SLICES

TOP = slice(None, 1)
TOP_FLIP = (TOP, FLIP)
RIGHT = (slice(None), slice(-1, None))
RIGHT_FLIP = (FLIP, RIGHT[1])
BOTTOM = slice(-1, None)
BOTTOM_FLIP = (BOTTOM, FLIP)
LEFT = (slice(None), slice(None, 1))
LEFT_FLIP = (FLIP, LEFT[1])
SLICES = [TOP, TOP_FLIP, RIGHT, RIGHT_FLIP, BOTTOM, BOTTOM_FLIP, LEFT, LEFT_FLIP]
TILE_EDGE = tuple[np.ndarray, np.ndarray, slice]


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of tiles

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        unmatched = [x for x in readTiles(file)]
    unmatched = match(unmatched)
    print(unmatched)


def edge(array: np.ndarray, slice: slice) -> str:
    return ''.join(array[slice].squeeze())


def match(unmatched: Iterable[tuple[np.ndarray, np.ndarray]]) -> Iterable[tuple[np.ndarray, np.ndarray]]:
    matched = []
    edges: dict[str, TILE_EDGE] = {}
    leftover = []
    for id, array in unmatched:
        if match := findMatch(edges, array):
            slice, match = match
            match_id, match_array, _ = match
            leftover.remove(match_id)
            for s in SLICES:
                del edges[edge(match_array, s)]
            matched.append(stitch((id, array, slice), match))
        else:
            leftover.append(id)
            for s in SLICES:
                e = edge(array, s)
                edges[e] = id, array, s
    if leftover:
        raise ValueError
    return matched


def findMatch(edges: dict[str, TILE_EDGE], array: np.ndarray) -> Union[tuple[slice, TILE_EDGE], None]:
    for slice in SLICES:
        e = edge(array, slice)
        if match := edges.get(e):
            return slice, match
    return None


def stitch(tile1: TILE_EDGE, tile2: TILE_EDGE) -> tuple[np.ndarray, np.ndarray]:
    # To simplify stitching, we'll manipulate the tiles first

    # Side note: if slice were hashable, this would be much cleaner as a dictionary of lambdas
    # Could work around by making hashable classes, but just doing the if-elif tree for now

    # Make matching edge the bottom of tile1
    tile_1_id, tile_1_array, tile_1_slice = tile1
    if tile_1_slice == BOTTOM_FLIP:
        tile_1_id = np.fliplr(tile_1_id)
        tile_1_array = np.fliplr(tile_1_array)
    elif tile_1_slice == TOP:
        tile_1_id = np.flipud(tile_1_id)
        tile_1_array = np.flipud(tile_1_array)
    elif tile_1_slice == TOP_FLIP:
        tile_1_id = np.flipud(np.fliplr(tile_1_id))
        tile_1_array = np.flipud(np.fliplr(tile_1_array))
    elif tile_1_slice == LEFT:
        tile_1_id = np.rot90(tile_1_id)
        tile_1_array = np.rot90(tile_1_array)
    elif tile_1_slice == LEFT_FLIP:
        tile_1_id = np.rot90(np.flipud(tile_1_id))
        tile_1_array = np.rot90(np.flipud(tile_1_array))
    elif tile_1_slice == RIGHT:
        tile_1_id = np.rot90(np.fliplr(tile_1_id))
        tile_1_array = np.rot90(np.fliplr(tile_1_array))
    elif tile_1_slice == RIGHT_FLIP:
        tile_1_id = np.rot90(tile_1_id, axes=(1, 0))
        tile_1_array = np.rot90(tile_1_array, axes=(1, 0))

    # Make matching edge the top of tile2
    tile_2_id, tile_2_array, tile_2_slice = tile2
    if tile_2_slice == TOP_FLIP:
        tile_2_id = np.fliplr(tile_2_id)
        tile_2_array = np.fliplr(tile_2_array)
    elif tile_2_slice == BOTTOM:
        tile_2_id = np.flipud(tile_2_id)
        tile_2_array = np.flipud(tile_2_array)
    elif tile_2_slice == BOTTOM_FLIP:
        tile_2_id = np.rot90(tile_2_id, 2)
        tile_2_array = np.rot90(tile_2_array, 2)
    elif tile_2_slice == LEFT:
        tile_2_id = np.rot90(np.fliplr(tile_2_id))
        tile_2_array = np.rot90(np.fliplr(tile_2_array))
    elif tile_2_slice == LEFT_FLIP:
        tile_2_id = np.rot90(tile_2_id, axes=(1, 0))
        tile_2_array = np.rot90(tile_2_array, axes=(1, 0))
    elif tile_2_slice == RIGHT:
        tile_2_id = np.rot90(tile_2_id)
        tile_2_array = np.rot90(tile_2_array)
    elif tile_2_slice == RIGHT_FLIP:
        tile_2_id = np.rot90(np.flipud(tile_2_id))
        tile_2_array = np.rot90(np.flipud(tile_2_array))

    # Now simply concatenate the tiles
    return np.concatenate((tile_1_id, tile_2_id)), np.concatenate((tile_1_array, tile_2_array))


def readTiles(file: TextIO) -> Iterable[tuple[np.ndarray, np.ndarray]]:
    tilePattern = re.compile(r'^Tile (?P<id>\d+):\s*$')

    while match := tilePattern.match(next(file, '')):
        buffer = []
        for line in file:
            line = line.rstrip()
            if not line:
                break
            buffer.append(list(line))
        yield np.array([[int(match.group('id'))]]), np.array(buffer)


if __name__ == '__main__':
    parser = MainArgs(description='Combine tiles into larger whole')
    main(parser.parse_args())
