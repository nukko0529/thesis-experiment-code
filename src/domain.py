from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    r: int
    c: int

class EyeSpaceKind(Enum):
    UNRELATED_LIBERTY = 1
    OUTSIDE_LIBERTY = 2
    SHARED_LIBERTY = 3
    EYE_LIBERTY = 4
    UNDEFINED = 100

class StoneKind(Enum):
    EMPTY = 0
    BLACK_SAFETY = 2
    WHITE_SAFETY = -2
    BLACK_ESSENTIAL = 3
    WHITE_ESSENTIAL = -3
    BLACK_NAKADE = 5
    WHITE_NAKADE = -5
    BLACK_ADDED = 1
    WHITE_ADDED = -1

class EvaluateResult(Enum):
    BLACK_WINNER = 1
    WHITE_WINNER = -1
    FIRST_WINNER = 0
    SEKI = 10
    BLACK_AD = 2
    WHITE_AD = -2