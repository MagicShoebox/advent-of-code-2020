import pathlib
import re
from typing import Iterable
from typing import List
from typing import TextIO
from typing import Union

import numpy as np
from tap import Tap

TILE = tuple[np.ndarray, np.ndarray]
TILE_EDGE = tuple[np.ndarray, np.ndarray, slice]

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


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a series of tiles

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        unmatched = [x for x in readTiles(file)]
    unmatched = match(unmatched)
    while len(unmatched) > 1:
        toBreak = None
        for i in range(len(unmatched)):
            if unmatched[i][0].size > 1:
                toBreak = unmatched.pop(i)
                break
        tiles = breakup(toBreak)
        unmatched.extend(tiles)
        unmatched = match(unmatched)

    ids, array = unmatched[0]
    # .item() needed to convert from int32->int and avoid overflow
    print(ids[0, 0].item() * ids[0, -1].item() * ids[-1, 0].item() * ids[-1, -1].item())


def edge(array: np.ndarray, slice: slice) -> str:
    return ''.join(array[slice].squeeze())


def match(unmatched: List[TILE]) -> List[TILE]:
    edges: dict[str, TILE_EDGE] = {}
    while unmatched:
        id, array = unmatched.pop(0)
        if match := findMatch(edges, array):
            slice, match = match
            _, match_array, _ = match
            for s in SLICES:
                e = edge(match_array, s)
                del edges[e]
            unmatched.append(stitch((id, array, slice), match))
        else:
            for s in SLICES:
                e = edge(array, s)
                edges[e] = id, array, s

    # Reassemble the remaining piece(s) from their TILE_EDGEs.
    # SLICES[0] is arbitrary, just needs to be consistent so we don't duplicate tiles
    return [(id, array) for id, array, slice in edges.values() if slice == SLICES[0]]


def findMatch(edges: dict[str, TILE_EDGE], array: np.ndarray) -> Union[tuple[slice, TILE_EDGE], None]:
    for slice in SLICES:
        e = edge(array, slice)
        if match := edges.get(e):
            return slice, match
    return None


def stitch(tile1: TILE_EDGE, tile2: TILE_EDGE) -> TILE:
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


def breakup(tile: TILE) -> Iterable[TILE]:
    ids, arrays = tile
    height, width = arrays.shape[0] // ids.shape[0], arrays.shape[1] // ids.shape[1]
    tiles = [(id, tile)
             for id, tile
             in zip(
            (y for x in np.split(ids, ids.shape[0], 0) for y in np.split(x, ids.shape[1], 1)),
            (y for x in np.split(arrays, ids.shape[0], 0) for y in np.split(x, ids.shape[1], 1)))]
    return tiles


def readTiles(file: TextIO) -> Iterable[TILE]:
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
    parser = MainArgs(description='Solve a jigsaw puzzle')
    main(parser.parse_args())
