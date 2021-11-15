from game_interface import Answer, GameMessage, TotemAnswer

# objet magique de debug qui compte le nombre de fois que chaque fonction est call
from time import perf_counter

class Solver:
    def __init__(self):
        self.Board = None

    def get_answer(self, game_message: GameMessage) -> Answer:
        # on récupère la question
        question = game_message.payload
        print("Received Question", ":", question, "\n\t length = (", len(question.totems), ")")

        start = perf_counter()
        answer = Answer(Board(question.totems).set_totems())
        end = perf_counter()
        print("took: ", (end - start), " \n\n\n")
        # on crée un noveau board
        print("Sending Answer", ":", answer, "\n\t length = (", len(answer.totems), ")")

        return answer


class Board:
    def __init__(self, payload):
        self.board = {}
        self.test_position = {(0, 0): True}

        self.shapes = {}
        self.length = len(payload)
        self.count_shape(payload)
        self.nb_totem_placed = 0
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

    def totem_answer(self, name, coordinates):
        return TotemAnswer(shape=name, coordinates=coordinates)

    def get_new_size(self, coords):
        w = self.width
        h = self.height
        for x, y in coords:
            if x > w:
                w = x
            if y > h:
                h = y
        return w, h

    def count_shape(self, payload):
        """
    compte le nombres de fois que la pièce apparait dans le payload
    """
        self.shapes = {k: 0 for k in "IJLOSTZ"}
        while payload:
            self.shapes[payload.pop().shape] += 1

    def context_totem_coords(self, totem_coords, x, y):
        return [(_x + x, _y + y) for _x, _y in totem_coords]

    def get_shape(self, totem):
        return self.totems[totem]

    def position_is_valid(self, coords):
        for coord in coords:
            if coord in self.board:
                return False
        return True

    def add_shape_to_board(self, coords):
        for x, y in coords:
            self.board[(x, y)] = True
            if x > self.width:
                self.width = x
            if y > self.height:
                self.height = y

    def calculate_best_totem(self):
        choice = None
        best_score = 0

        for totem, count in self.shapes.items():
            if count > 0:
                current_best, current_best_score = self.get_totem_best_rotation(totem)

                if current_best_score > best_score:
                    choice = current_best
                    best_score = current_best_score
        return choice

    def get_totem_best_rotation(self, totem):
        current_best = None
        current_best_score = 0
        deleted_position = []

        # pour chaque cellule vide
        for x, y in self.test_position.keys():
            is_impossible = True
            # pour chaque rotation
            for rotation in self.get_shape(totem):
                t = self.context_totem_coords(rotation, x, y)  # on calcule les position de la pièce
                if self.position_is_valid(t):
                    is_impossible = False
                    nx, ny = self.get_new_size(t)
                    score = self.calculate_score(nx, ny)
                    if score > current_best_score:
                        current_best_score = score
                        current_best = (totem, t)
            if is_impossible:
                deleted_position.append((x, y))

        for pos in deleted_position:
            self.test_position.pop(pos)

        return current_best, current_best_score

    def set_totems(self):
        answer = []
        # pour chaque totem à placer
        for i in range(0, self.length):
            # on calcul le meilleur totem
            choice = self.calculate_best_totem()

            if choice is None:
                self.test_position.update({(self.width + 1, i): True for i in range(self.height + 2)})
                self.test_position.update({(i, self.height + 1): True for i in range(self.width + 2)})
                choice = self.calculate_best_totem()

            name, coords = choice
            old_width = self.width
            old_height = self.height
            self.shapes[name] -= 1
            self.add_shape_to_board(coords)
            answer.append(self.totem_answer(name, coords))
            self.nb_totem_placed += 1

            # - on retire les coordonnées déjà utilisées
            for coord in coords:
                self.test_position.pop(coord, None)

            if old_width != self.width:
                self.test_position.update({(self.width, i): True for i in range(self.height + 1)})

            if old_height != self.height:
                self.test_position.update({(i, self.height): True for i in range(self.width + 1)})

        x = self.width
        y = self.height
        print("score: ", (self.length * 10 - ((x + 1) * (y + 1))) * (min(x + 1, y + 1) / max(x + 1, y + 1)))

        # on actualise les
        return answer

    def calculate_score(self, x, y):
        return ((self.nb_totem_placed + 1) * 10 - ((x + 1) * (y + 1))) * (min(x + 1, y + 1) / max(x + 1, y + 1))
