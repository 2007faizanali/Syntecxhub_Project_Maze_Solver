# Maze Solver using A* Search Algorithm

## About the Project
This project implements the A* Search algorithm to find the shortest path from a Start cell to a Goal cell in a grid-based maze.

The application is built using Python and Tkinter to provide a graphical visualization of the search process.

## Features
- A* Search algorithm for pathfinding
- Manhattan distance heuristic
- Priority queue using Python's `heapq`
- Animated search visualization
- Final shortest path highlighting
- Reset functionality
- Handles cases where no valid path exists

## Technologies Used
- Python
- Tkinter
- Heapq

## How to Run
1. Install Python 3.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Run:

   `python maze_solver.py`

Tkinter is included with many standard Python installations. If it is unavailable, check your Python installation.

## Maze Legend
- Green: Start
- Red: Goal
- Gray: Wall
- Purple: Frontier
- Blue: Explored cells
- Yellow: Final path

## Algorithm
A* evaluates cells using:

`f(n) = g(n) + h(n)`

- `g(n)`: Actual cost from the Start.
- `h(n)`: Estimated distance to the Goal using Manhattan distance.
- `f(n)`: Estimated total path cost.

Each move has a cost of 1, and movement is allowed in four directions.

## Author
Created as a learning project to understand pathfinding and A* Search.
