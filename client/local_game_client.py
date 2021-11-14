import random

from game_interface import GameMessage, Question, TotemQuestion
from solver import Solver


class LocalGameClient:
  def __init__(self, solver: Solver):
    self.solver = solver

  async def run(self):
    print("[Running in local mode]")
    game_message: GameMessage = GameMessage(
      tick=1, payload=Question(
        totems=[TotemQuestion(shape=random.choice("IJLOSTZ")) for _ in range(128)])
      )
    self.solver.get_answer(game_message)
