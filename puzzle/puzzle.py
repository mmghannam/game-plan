from gameplan.game import Game
from gameplan.state import *
from gameplan.solver import *
from random import shuffle, seed
from copy import deepcopy
from math import sqrt


class Puzzle(Game):
    def __init__(self, width, height):
        self.board = Board(width, height)

    def solve(self, frontier=AstarFrontier, heuristic='how_many_wrong'):
        return solve(self.board, frontier, heuristic)


class Board(GameState):
    def __init__(self, width=3, height=3, initial_conf=None):
        if not initial_conf:
            initial_conf = PuzzleConfiguration(width, height)
        super().__init__(initial_conf)

    def neighbours(self):
        moves = {
            'Up': self.slide_up,
            'Down': self.slide_down,
            'Left': self.slide_left,
            'Right': self.slide_right
        }

        neighbours = []

        for move in moves.keys():
            move_result = moves[move]()
            if move_result:
                neighbours.append(move_result)

        return neighbours

    def is_goal(self):
        for i in range(len(self.configuration.slots)):
            if i != self.configuration.slots[i].number:
                return False
        return True

    def slide_up(self):
        conf = deepcopy(self.configuration)
        empty_index, empty_slot = conf.empty_slot()
        x, y = conf.position_of(0)
        if conf.on_top(empty_slot):
            return None
        else:
            other_index, _ = conf.get_slot_at(x, y - 1)
            conf.swap(empty_index, other_index)
            return Board(initial_conf=conf)

    def slide_down(self):
        conf = deepcopy(self.configuration)
        empty_index, empty_slot = conf.empty_slot()
        x, y = conf.position_of(0)
        if conf.on_bottom(empty_slot):
            return None
        else:
            other_index, _ = conf.get_slot_at(x, y + 1)
            conf.swap(empty_index, other_index)
            return Board(initial_conf=conf)

    def slide_left(self):
        conf = deepcopy(self.configuration)
        empty_index, empty_slot = conf.empty_slot()
        x, y = conf.position_of(0)
        if conf.on_left_side(empty_slot):
            return None
        else:
            other_index, _ = conf.get_slot_at(x - 1, y)
            conf.swap(empty_index, other_index)
            return Board(initial_conf=conf)

    def slide_right(self):
        conf = deepcopy(self.configuration)
        empty_index, empty_slot = conf.empty_slot()
        x, y = conf.position_of(0)
        if conf.on_right_side(empty_slot):
            return None
        else:
            other_index, _ = conf.get_slot_at(x + 1, y)
            conf.swap(empty_index, other_index)
            return Board(initial_conf=conf)

    def __str__(self):
        return str(self.configuration)

    def __eq__(self, other):
        return self.configuration == other.configuration

    def __lt__(self, other):
        return True


class PuzzleConfiguration(Configuration):
    def __init__(self, width, height):
        self.slots = [Slot(i) for i in range(width * height)]
        seed(4)
        shuffle(self.slots)
        self.width = width
        self.height = height

    def empty_slot(self):
        for i, slot in enumerate(self.slots):
            if slot.is_empty():
                return i, slot
        raise UndefinedConfigurationError

    def to_list(self):
        return self.slots

    def get_slot_at(self, x, y):
        index = self.width * y + x
        return index, self.slots[index]

    def swap(self, oldi, newi):
        self.slots[oldi], self.slots[newi] = self.slots[newi], self.slots[oldi]

    def __str__(self):
        result = "-" * (self.width * 6 - 1) + "\n"
        for x in range(self.width):
            for y in range(self.height):
                slot = self.slots[x * self.width + y]
                result += str(slot)
            result += "\n"
        result += "-" * (self.width * 6 - 1) + "\n"
        return result

    def position_of(self, number):
        for i, slot in enumerate(self.slots):
            if slot.number == number:
                return i % self.width, i // self.width  # (x,y)

    def index_of(self, number):
        for i, slot in enumerate(self.slots):
            if slot.number == number:
                return i

    def on_top(self, slot):
        for i in range(self.width):
            if slot == self.slots[i]:
                return True
        return False

    def on_bottom(self, slot):
        for i in range(self.width):
            if slot == self.slots[self.height * (self.width - 1) + i]:
                return True
        return False

    def on_left_side(self, slot):
        for i in range(self.height):
            if slot == self.slots[i * self.width]:
                return True
        return False

    def on_right_side(self, slot):
        for i in range(self.height):
            if slot == self.slots[i * self.width + self.width - 1]:
                return True
        return False

    def __eq__(self, other):
        for slot, other_slot in zip(self.slots, other.slots):
            if slot != other_slot:
                return False
        return True

    def manhattan_distance(self):
        distance = 0
        for i in range(len(self.slots)):
            current_position = (i % self.width, i // self.width)
            goal_position = self.position_of(i)
            distance += abs(current_position[0] - goal_position[0]) + abs(current_position[1] - goal_position[1])
        return distance

    def euclidean_distance(self):
        distance = 0
        for i in range(len(self.slots)):
            current_position = (i % self.width, i // self.width)
            goal_position = self.position_of(i)
            distance += sqrt(
                (current_position[0] - goal_position[0]) ** 2 + (current_position[1] - goal_position[1]) ** 2)
        return distance

    def how_many_wrong(self):
        result = 0
        for i, slot in enumerate(self.slots):
            if slot.number != i:
                result += 1
        return result

    def wrong_and_manhattan(self):
        return self.manhattan_distance() + self.how_many_wrong()

    def heuristic_value(self, func_name):
        if func_name == 'how_many_wrong':
            return self.how_many_wrong()
        elif func_name == 'manhattan_distance':
            return self.manhattan_distance()
        elif func_name == 'euclidean_distance':
            return self.euclidean_distance()
        elif func_name == 'wrong_and_manhattan':
            return self.wrong_and_manhattan()
        else:
            return 0


class Slot:
    def __init__(self, number):
        self.number = number

    def is_empty(self):
        return self.number == 0

    def __str__(self):
        return "| {} | ".format(self.number)

    def __eq__(self, other):
        return self.number == other.number


class UndefinedConfigurationError(Exception):
    pass
