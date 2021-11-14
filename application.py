#!/usr/bin/env python

import asyncio
import os

from client.local_game_client import LocalGameClient
from client.websocket_game_client import WebSocketGameClient
from solver import Solver


async def run():
  solver = Solver()
  if "TOKEN" in os.environ:
    await WebSocketGameClient(solver).run()
  else:
    await LocalGameClient(solver).run()


if __name__ == "__main__":
   asyncio.get_event_loop().run_until_complete(run())
