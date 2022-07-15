import unittest
from solvers import MineSweeperSolverSimple
from minefield import MineField, BEGINNER_FIELD


class TestSimpleSolver(unittest.TestCase):
    """Testcase for the basic solver."""

    def setUp(self) -> None:

        self.field = MineField(**BEGINNER_FIELD)
        self.solver = MineSweeperSolverSimple(**self.field.info)

    def tearDown(self) -> None:
        self.field = None
        self.solver = None

    def test_zeros(self):
        """Test how a zero is surrounded."""

        # Insert 0 cell
        self.solver.update(3, 3, 0)

        steps = set()

        for i in range(8):
            step = self.solver.get_next_sweep()
            self.solver.update(**step, result=1)  # Put back mock result
            steps.add((step["row"], step["column"]))

        # self.solver.print()
        self.assertEqual(8, len(steps))

    def test_mines_found(self):
        """Test how un-mined squares are found."""

        # Insert 3, surrounded by mines
        self.solver.update(3, 3, 3)
        self.solver.update(4, 2, self.solver.BOMB)
        self.solver.update(4, 3, self.solver.BOMB)
        self.solver.update(4, 4, self.solver.BOMB)

        steps = set()

        for i in range(5):
            step = self.solver.get_next_sweep()
            self.solver.update(**step, result=1)  # Put back mock result
            steps.add((step["row"], step["column"]))

        self.solver.print()
        self.assertEqual(5, len(steps))


if __name__ == "__main__":
    unittest.main()
