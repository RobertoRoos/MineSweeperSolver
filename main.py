from minefield import MineField, BEGINNER_FIELD, INTERMEDIATE_FIELD, EXPERT_FIELD
from solvers import MineSweeperSolverRandom


def main():
    field = MineField(**BEGINNER_FIELD)

    field.sweep_cell(4, 4)

    solver = MineSweeperSolverRandom(**BEGINNER_FIELD)

    for i in range(100):

        step = solver.get_next_sweep()
        result = field.sweep_cell(**step)
        solver.update(**step, result=result)
        print(step, result)

        solver.print()


if __name__ == "__main__":
    main()
