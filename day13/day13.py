import pathlib
from typing import List

from tap import Tap


class MainArgs(Tap):
    file: pathlib.Path  # A text file with a target and candidate integers

    def configure(self):
        self.add_argument('file', type=pathlib.Path)


def main(args: MainArgs):
    with args.file.open('r') as file:
        lines = [line for line in file]
        target = int(lines[0])
        candidates = [(idx, int(x)) for idx, x in enumerate(lines[1].split(',')) if x != 'x']
        id, score = findClosest(target, [x for idx, x in candidates])
        print(id * score)
        print(findCongruence(candidates))


def findClosest(target: int, candidates: List[int]) -> tuple[int, int]:
    scores = ((target + candidate - 1) // candidate * candidate - target for candidate in candidates)
    return min(((x, y) for x, y in zip(candidates, scores)), key=lambda x: x[1])


def findCongruence(candidates: List[tuple[int, int]]) -> int:
    # Convert indices to congruence classes (mod n):
    # x+idx=0 (mod n) => x=-idx (mod n)
    congruenceClasses = [(-idx % n, n) for idx, n in candidates]

    # https://en.wikipedia.org/wiki/Chinese_remainder_theorem
    # x = a_1, N = n_1, a = a_2, n = n_2 (for sequential application)
    x, N = congruenceClasses[0]
    for a, n in congruenceClasses[1:]:
        # Because N and n are coprime, we can find m1 * N + m2 * n = 1
        m1, m2 = extended_gcd(N, n)
        # Find x such that x=x (mod N) and x=a (mod n)
        x, N = x * m2 * n + a * m1 * N, N * n
        x %= N
    return x


def extended_gcd(a, b) -> tuple[int, int]:
    # https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_s, old_t


if __name__ == '__main__':
    parser = MainArgs(description='Find the integers whose multiple'
                                  ' is closest to the target')
    main(parser.parse_args())
