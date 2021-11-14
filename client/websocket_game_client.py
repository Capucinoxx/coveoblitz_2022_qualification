import json
import os
import sys

import websockets

from game_interface import Answer, GameMessage
from solver import Solver


class WebSocketGameClient:
  uri = "ws://127.0.0.1:8765"

  def __init__(self, solver: Solver):
    self.solver = solver

  async def run(self):
    async with websockets.connect(self.uri) as websocket:
      await websocket.send(
        json.dumps({"type": "REGISTER", "token": os.environ["TOKEN"]})
      )
      while True:
        try:
          rawMessage = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
          # Connection is closed, the game is probably over
          break
        message = json.loads(rawMessage)
        if message["type"] == "ERROR":
          print(message, file=sys.stderr)
          return
        game_message: GameMessage = GameMessage.from_dict(message)

        answer: Answer = self.solver.get_answer(game_message)
        await websocket.send(
          json.dumps(
            {
              "type": "COMMAND",
              "tick": game_message.tick,
              "actions": answer.to_dict(),
            }
          )
        )
