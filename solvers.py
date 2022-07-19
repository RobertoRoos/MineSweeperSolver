from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional
from random import randrange


class MineSweeperSolverBase(ABC):
    """Base class for any minesweeper solver.

    :ivar _field: None = unknown, -1 = mine (estimated), 0 - 8 = number of adjacent mines
    """

    BOMB = -1

    def __init__(self, *, width: int, height: int, number_of_mines: int):

        self._width = width
        self._height = height
        self._number_of_mines = number_of_mines

        self._field: List[List[Optional[int]]] = [
            [None] * self._width for _ in range(self._height)
        ]

        self._sweeps = 0

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

        self._sweeps += 1

    def print(self):
        """Print the current field and the estimation."""

        for row in range(self._height):

            line = ""
            for col in range(self._width):
                cell = self._field[row][col]
                if cell is None:
                    line += "- "
                elif cell < 0:
                    line += "x "
                else:
                    line += str(cell) + " "
            print(line)

    def is_done(self):
        """

        :return: True if there are no unknown squares left
        """
        return all(cell is not None for row in self._field for cell in row)


class MineSweeperSolverRandom(MineSweeperSolverBase):
    """Dummy class that just makes random swipes."""

    def get_next_sweep(self) -> Dict[str, int]:
        random_index = randrange(0, self._width * self._height)
        column = random_index % self._width
        row = random_index // self._width
        return {"row": row, "column": column}


class MineSweeperSolverSimple(MineSweeperSolverBase):
    """Sort of clever solver, without fancy stuff."""

    OFFSETS = [
        (-1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, -1),
    ]

    def __init__(self, *, width: int, height: int, number_of_mines: int):
        super().__init__(width=width, height=height, number_of_mines=number_of_mines)

        self._circle_offset = 0  # Switch the random direction each time

    def get_next_sweep(self) -> Dict[str, int]:

        # Very first statement, just pick the corner
        if self._sweeps == 0:
            return {"row": 0, "column": 0}

        #
        # Loop over all cells - for each cell, check the adjacent cells and consider if all surrounding
        # bombs have been found. If so, pick the first adjacent cell that is not a bomb.
        #

        for row in range(self._height):
            for col in range(self._width):

                cell = self._get_cell(row, col)

                if cell is None or cell == self.BOMB:
                    continue  # Skip a bomb or an unknown

                unknown_adjacents = self._get_adjacent_unknown(row, col)
                if len(unknown_adjacents) == 0:
                    continue  # Nothing to click on at all

                known_adjacent_mines = self._get_adjacent_bombs(row, col)
                if len(known_adjacent_mines) == cell:
                    # We identified all the mines around this square, so we could click any unknown square
                    # (there should never be more identified mines than the cell value)
                    return unknown_adjacents[0]  # Just return the first in the list
                if len(known_adjacent_mines) > cell:
                    raise Exception(
                        "Detected more mines than cell dictated, solver failed"
                    )

        # The above failed - looks like there is no certain sweep to be made. Just click one
        # next to a known cell then.

        first_unknown = None

        # Find the first neighbour of the first known cell:
        for row in range(self._height):
            for col in range(self._width):
                cell = self._get_cell(row, col)
                if cell is None:
                    first_unknown = {"row": row, "column": col}
                elif cell > 0:
                    coords = self._get_adjacent_unknown(row, col)
                    if coords:
                        return coords[0]

        # Okay, then just use the first unknown square we found
        if first_unknown:
            return first_unknown

        raise Exception("No unknown squares left")

    def update(self, row, column, result):

        super().update(row, column, result)

        #
        # Update our estimation of where any mines are for certain
        #

        # TODO: Optimize

        for row in range(self._height):
            for col in range(self._width):

                cell = self._get_cell(row, col)

                if cell is None or cell == self.BOMB:
                    continue  # Skip a bomb or an unknown

                unknown_adjacents = self._get_adjacent_unknown(row, col)
                known_adjacent_mines = self._get_adjacent_bombs(row, col)

                if len(unknown_adjacents) == cell - len(known_adjacent_mines):
                    # If there are as many unknown neighbours as remaining mines, they are all mines
                    # (there should never be less unknown neighbours than remaining bombs)
                    for coord in unknown_adjacents:
                        self._set_cell(**coord, value=self.BOMB)
                elif len(unknown_adjacents) < cell - len(known_adjacent_mines):
                    raise Exception(
                        "Detected more mines than cell dictated, solver failed"
                    )

    def _get_cell(self, row: int, column: int) -> int:
        return self._field[row][column]

    def _set_cell(self, row: int, column: int, value: int):
        self._field[row][column] = value

    def _get_adjacent_squares(self, row, column) -> List[Dict[str, int]]:
        """Get the coordinates of the adjacent squares.

        We keep rotating the preferred direction of adjacent cells to keep sweeps grouped together.
        """
        coords = []

        for i in range(len(self.OFFSETS)):

            i = (i + self._circle_offset) % len(self.OFFSETS)

            row_i = row + self.OFFSETS[i][0]
            col_i = column + self.OFFSETS[i][1]

            if row_i < 0 or row_i >= self._height or col_i < 0 or col_i >= self._width:
                continue

            coords.append({"row": row_i, "column": col_i})

        self._circle_offset = (self._circle_offset + 1) % len(self.OFFSETS)

        return coords

    def _get_adjacent_where(self, row, column, value) -> List[Dict[str, int]]:
        """Get neighbouring cells with a specific value only"""

        coords = []
        for coord in self._get_adjacent_squares(row, column):
            cell = self._get_cell(**coord)
            if value is None and cell is None or cell == value:
                coords.append(coord)

        return coords

    def _get_adjacent_bombs(self, row, column) -> List[Dict[str, int]]:
        return self._get_adjacent_where(row, column, self.BOMB)

    def _get_adjacent_unknown(self, row, column) -> List[Dict[str, int]]:
        return self._get_adjacent_where(row, column, None)
