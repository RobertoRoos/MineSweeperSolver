# Mine Sweeper Solver

For the DEMCON minesweeper contest.

## How to use

Don't forget to update the Git submodule: `git submodule update --init`.

Then simply run `python main.py`. There are no external requirements.

### Tests

You can run the (very basic) tests with `python -m unittest discover`.

## Solver

The best solver here is `MineSweeperSolverSimple`, but it will fail often for difficult games.
It relies on using the information of only a single square to find the surrounding bombs.
It should succeed about 70% of the time with a random beginner field.
It fails with some regularity because it resorts to random choices, for example when the 
first square does not provide enough information yet.

## Author

 * Robert Roos
 