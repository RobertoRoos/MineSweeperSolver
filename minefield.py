from DecodeDemcon3.mineField import MineField as BaseMineField
from DecodeDemcon3.mineField import CellStatus, BEGINNER_FIELD, INTERMEDIATE_FIELD, EXPERT_FIELD


class MineField(BaseMineField):
    """Cooler minefield, based on the sample, with a few extra features.

    This class acts as the game. The mine info here should be hidden from the solver.
    """

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def number_of_mines(self) -> int:
        return self.__number_of_mines

    @property
    def field(self):
        return self.__field

    def print(self):
        """Print minefield as text."""

        for row in range(self.__width):

            line = ""
            for col in range(self.__height):
                line += "x " if self.__field[row][col] == CellStatus.MINE else "0 "
            print(line)
