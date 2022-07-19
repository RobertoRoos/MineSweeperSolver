from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Set, Optional
from random import randrange


Coord = Tuple[int, int]


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

        self._unknown_cells: Set[Coord] = set(
            (row, col) for col in range(self._width) for row in range(self._height)
        )  # List of all the cells we do not know yet

    @abstractmethod
    def get_next_sweep(self) -> Coord:
        """Implement this method to find the next sweep option.

        :return: (Row, Column)
        """
        pass

    def update(self, coord: Coord, result):
        """Insert a sweep result.

        :param coord:
        :param result: Number of adjacent bombs to a cell
        """

        self._set_cell(coord, result)

        self._sweeps += 1

    def _get_cell(self, coord: Coord) -> int:
        return self._field[coord[0]][coord[1]]

    def _set_cell(self, coord: Coord, value: int):

        if coord in self._unknown_cells:
            self._unknown_cells.remove(coord)

        self._field[coord[0]][coord[1]] = value

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

    def get_next_sweep(self) -> Coord:

        # Very first statement, just pick the corner
        if self._sweeps == 0:
            return 0, 0

        #
        # Loop over all cells - for each cell, check the adjacent cells and consider if all surrounding
        # bombs have been found. If so, pick the first adjacent cell that is not a bomb.
        #

        for row in range(self._height):
            for col in range(self._width):
                coord = (row, col)
                cell = self._get_cell(coord)

                if cell is None or cell == self.BOMB:
                    continue  # Skip a bomb or an unknown

                unknown_adjacents = self._get_adjacent_unknown(coord)
                if len(unknown_adjacents) == 0:
                    continue  # Nothing to click on at all

                known_adjacent_mines = self._get_adjacent_bombs(coord)
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
                coord = (row, col)
                cell = self._get_cell(coord)
                if cell is None:
                    first_unknown = coord
                elif cell > 0:
                    coords = self._get_adjacent_unknown(coord)
                    if coords:
                        return coords[0]

        # Okay, then just use the first unknown square we found
        if first_unknown:
            return first_unknown

        raise Exception("No unknown squares left!")

    def update(self, coord: Coord, result):

        super().update(coord, result)

        #
        # Update our estimation of where any mines are for certain
        #

        # TODO: Optimize

        for row_i in range(self._height):
            for col_i in range(self._width):

                coord_i = (row_i, col_i)
                cell = self._get_cell(coord_i)

                if cell is None or cell == self.BOMB:
                    continue  # Skip a bomb or an unknown

                unknown_adjacents = self._get_adjacent_unknown(coord_i)
                known_adjacent_mines = self._get_adjacent_bombs(coord_i)

                if len(unknown_adjacents) == cell - len(known_adjacent_mines):
                    # If there are as many unknown neighbours as remaining mines, they are all mines
                    # (there should never be less unknown neighbours than remaining bombs)
                    for coord_j in unknown_adjacents:
                        self._set_cell(coord_j, value=self.BOMB)
                elif len(unknown_adjacents) < cell - len(known_adjacent_mines):
                    raise Exception(
                        "Detected more mines than cell dictated, solver failed"
                    )

    def _get_adjacent_squares(self, coord: Coord) -> List[Coord]:
        """Get the coordinates of the adjacent squares.

        We keep rotating the preferred direction of adjacent cells to keep sweeps grouped together.
        """
        coords = []

        for i in range(len(self.OFFSETS)):

            i = (i + self._circle_offset) % len(self.OFFSETS)

            coord_i = (coord[0] + self.OFFSETS[i][0], coord[1] + self.OFFSETS[i][1])

            if coord_i[0] < 0 or coord_i[0] >= self._height or coord_i[1] < 0 or coord_i[1] >= self._width:
                continue

            coords.append(coord_i)

        self._circle_offset = (self._circle_offset + 1) % len(self.OFFSETS)

        return coords

    def _get_adjacent_where(self, coord: Coord, value) -> List[Coord]:
        """Get neighbouring cells with a specific value only"""

        coords = []
        for coord_i in self._get_adjacent_squares(coord):
            cell = self._get_cell(coord_i)
            if value is None and cell is None or cell == value:
                coords.append(coord_i)

        return coords

    def _get_adjacent_bombs(self, coord: Coord) -> List[Coord]:
        return self._get_adjacent_where(coord, self.BOMB)

    def _get_adjacent_unknown(self, coord: Coord) -> List[Coord]:
        return self._get_adjacent_where(coord, None)
