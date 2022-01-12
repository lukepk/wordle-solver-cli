# wordle-solver-cli
CLI AI Player for Wordle. Solves any wordle in an average of 2.84 guesses and a maximum of 5 guesses.

# Installation
1. Extract all files to the same directory
2. Run

# Running
To interactively solve a game of wordle: ```python solver.py```

For help: ```python solver.py -h```

To measure the performance of the solver against all the possible answer words: ```python solver.py -s``` (WARNING: Will likely take multiple hours to complete)

To calculate the optimal first guess: ```python solver.py -f```

# Performance
Performance was measured by simulating the solver playing Wordle against every possible answer word. Note that calculation time will depend on your computer hardware. This is also for the non-hardmode version of the game only. The hardmode version (soon tm) will take more turns, but will run faster since it has to check less possible guesses.

The average number of turns taken to solve a wordle was 2.8419.

The maximum number of turns taken was 5.

The average time taken per game was 6.19s.

The maximum time taken for a wordle was less than 40 seconds.
