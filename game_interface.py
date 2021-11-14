from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Tuple

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Question:
  totems: List[TotemQuestion]


@dataclass_json
@dataclass
class TotemQuestion:
  shape: Totem


Totem = Literal["I", "O", "J", "L", "S", "Z", "T"]


@dataclass_json
@dataclass
class Answer:
  totems: List[TotemAnswer]


@dataclass_json
@dataclass
class TotemAnswer:
  shape: Totem
  coordinates: List[CoordinatePair]


CoordinatePair = Tuple[int, int]


@dataclass_json
@dataclass
class GameMessage:
  tick: int
  payload: Question
