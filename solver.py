from game_interface import Answer, GameMessage, TotemAnswer


# objet magique de debug qui compte le nombre de fois que chaque fonction est call
from time import perf_counter
from collections import defaultdict


class FuncMarker:

  def __init__(self):
    self.call_count = 0
    self.cum = 0

  def __add__(self, time):
    self.cum += perf_counter() - time
    self.call_count += 1
    return self

  def __str__(self):
    return f"{self.cum:,.5f}s [{self.call_count:,}]"


class TimeIt:
  stats = defaultdict(FuncMarker)

  def __call__(self, func):
    def wrapped(*args, **kwargs):
      start = perf_counter()
      r = func(*args, **kwargs)
      self.stats[func.__name__] += start
      return r

    return wrapped

  def report(self):
    for k, v in self.stats.items():
      print(k, v)

  def __del__(self):
    self.report()


timeit = TimeIt()
########################################################################################################################

class Solver:
  def __init__(self):
    self.Board = None
    pass
  @timeit
  def get_answer(self, game_message: GameMessage) -> Answer:
    # on récupère la question
    question = game_message.payload
    print("Received Question", ":", question, "\n\t length = (", len(question.totems), ")")

    start = perf_counter()
    answer = Answer(Board(question.totems).set_totems())
    end = perf_counter()
    # on crée un noveau board
    print("Sending Answer", ":", answer, "\n\t length = (", len(answer.totems), ")")

    print("took: ", (end - start), " \n\n\n")
    return answer


class Board:
  def __init__(self, payload):
    self.board = {}

    self.shapes = {}
    self.length = len(payload)
    self.count_shape(payload)


    # la hauteur et la largeur d'un nouveau board est de 0
    self.width = self.height = 0

    # génération des différentes positions des pièces
    self.totems = {
      "I": [
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 0), (1, 0), (2, 0), (3, 0)]
      ],
      "J": [
        [(0, 1), (0, 0), (2, 0), (1, 0)],
        [(0, 2), (1, 2), (0, 1), (0, 0)],
        [(0, 1), (1, 1), (2, 1), (2, 0)],
        [(0, 0), (1, 0), (1, 1), (1, 2)]
      ],
      "L": [
        [(0, 2), (0, 1), (0, 0), (1, 0)],
        [(0, 1), (1, 1), (2, 1), (0, 0)],
        [(0, 2), (1, 2), (1, 1), (1, 0)],
        [(0, 0), (1, 0), (2, 0), (2, 1)]
      ],
      "O": [
        [(0, 0), (0, 1), (1, 0), (1, 1)]
      ],
      "S": [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(1, 0), (1, 1), (0, 1), (0, 2)]
      ],
      "T": [
        [(0, 0), (1, 0), (1, 1), (2, 0)],
        [(0, 0), (0, 1), (0, 2), (1, 1)],
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (2, 1)]
      ],
      "Z": [
        [(0, 1), (1, 1), (1, 0), (2, 0)],
        [(0, 0), (0, 1), (1, 1), (1, 2)]
      ]
    }

  @timeit
  def totem_answer(self, name, coordinates):
    return TotemAnswer(shape=name, coordinates=coordinates)

  @timeit
  def get_new_size(self, coords):
    w = self.width
    h = self.height
    for x, y in coords:
      if x > w:
        w = x
      if y > h:
        h = y
    return w, h

  @timeit
  def count_shape(self, payload):
    """
    compte le nombres de fois que la pièce apparait dans le payload
    """
    self.shapes = {k: 0 for k in "IJLOSTZ"}
    while payload:
      self.shapes[payload.pop().shape] += 1

  @timeit
  def context_totem_coords(self, totem_coords, x, y):
    return [(_x + x, _y + y) for _x, _y in totem_coords]

  @timeit
  def get_shape(self, totem):
    return self.totems[totem]

  @timeit
  def position_is_valid(self, coords):
    for coord in coords:
      if coord in self.board:
        return False
    return True

  @timeit
  def add_shape_to_board(self, coords):
    for x, y in coords:
      self.board[(x, y)] = True
      if x > self.width:
        self.width = x
      if y > self.height:
        self.height = y

  # TODO: la FONCTION DE MERDE que l'on doit retaper, elle est 5 fois trop lente !
  # TODO: remplacer calcul ratio par un calcul du pointage, car le calcul raito cause trop d'erreur
  @timeit
  def set_totems(self):
    answer = []

    for i in range(0, self.length):
      choice = self.calculate_best_totem()
      if choice is not None:
        name, coord = choice
        self.shapes[name] -= 1
        self.add_shape_to_board(coord)
        answer.append(self.totem_answer(name, coord))

    return answer

  @timeit
  def calculate_best_totem(self):
    choice = None
    best_ratio = 0

    for totem, count in self.shapes.items():
      x = y = 0
      if count > 0:
        if self.width + self.height == 0:
          return totem, self.get_shape(totem)[0]

        current_best, current_best_ratio = self.get_best_rotation(totem)

        if current_best_ratio > best_ratio:
          choice = current_best
          best_ratio = current_best_ratio

    return choice

  @timeit
  def get_best_rotation(self, totem):
    x = y = 0

    current_best = None
    current_best_ratio = 0

    is_fucking_done = False
    while not is_fucking_done:
      has_found = False

      while not has_found:
        for rotation in self.get_shape(totem):
          t = self.context_totem_coords(rotation, x, y)
          if self.position_is_valid(t):
            has_found = True
            nx, ny = self.get_new_size(t)
            ratio = min(nx, ny) / max(nx, ny)
            if ratio > current_best_ratio:
              current_best_ratio = ratio
              current_best = (totem, t)
            if x == 0:
              is_fucking_done = True
        x += 1
      x = 0
      y += 1

    return current_best, current_best_ratio





