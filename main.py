from minefield import (
    MineField,
    ExplosionException,
    BEGINNER_FIELD,
    INTERMEDIATE_FIELD,
    EXPERT_FIELD,
)
from solvers import MineSweeperSolverRandom, MineSweeperSolverSimple


def main():
    field = MineField(**BEGINNER_FIELD)

    field.sweep_cell(4, 4)

    # solver = MineSweeperSolverRandom(**field.info)
    solver = MineSweeperSolverSimple(**field.info)

    for i in range(field.height * field.width - field.number_of_mines):

        step = solver.get_next_sweep()

        try:
            result = field.sweep_cell(**step)
            solver.update(**step, result=result)
        except ExplosionException:
            print("BOOM!")
            break
        finally:
            print(step)
            solver.print()


if __name__ == "__main__":
    main()
