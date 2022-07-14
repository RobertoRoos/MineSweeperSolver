from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional
from random import randrange
from enum import Enum


class MineSweeperSolverBase(ABC):
    """Base class for any minesweeper solver.

    :ivar _field: None = unknown, -1 = mine (estimated), 0 - 8 = number of adjacent mines
    """

    def __init__(self, *, width: int, height: int, number_of_mines: int):

        self._width = width
        self._height = height
        self._number_of_mines = number_of_mines

        self._field: List[List[Optional[int]]] = [[None] * self._width for _ in range(self._height)]

    @abstractmethod
    def get_next_sweep(self) -> Dict[str, int]:
        """Implement this method to find the next sweep option.
        
        :return: {"row": Row, "column": Column}
        """
        pass

    def update(self, row, column, result):
        """Insert a sweep result.

        :param row:
        :param column:
        :param result: Number of adjacent bombs to a cell
        """

        self._field[row][column] = result

    def print(self):
        """Print the current field and the estimation."""

        for row in range(self._width):

            line = ""
            for col in range(self._height):
                cell = self._field[row][col]
                if cell is None:
                    line += "- "
                elif cell < 0:
                    line += "x "
                else:
                    line += str(cell) + " "
            print(line)


class MineSweeperSolverRandom(MineSweeperSolverBase):
    """Dummy class that just makes random swipes."""

    def get_next_sweep(self) -> Dict[str, int]:
        random_index = randrange(0, self._width * self._height)
        column = random_index % self._width
        row = random_index // self._width
        return {"row": row, "column": column}


class MineSweeperSolverSimple(MineSweeperSolverBase):
    """Sort of clever solver, without fancy stuff."""

    def get_next_sweep(self) -> Dict[str, int]:

        if all(cell is None for row in self._field for cell in row):
            # Very first statement, just pick the center thingy
            return {"row": self._height // 2, "column": self._width // 2}

        return {"row": 0, "column": 0}
