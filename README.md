# Maze Solver using A* Search Algorithm

## About the Project
This project uses the A* Search algorithm to find the shortest path from a Start cell to a Goal cell in a 12 × 12 grid-based maze.

The application is built with Python and Tkinter to visualize how the search algorithm explores the maze and finds a route to the goal.

## Features
- A* Search algorithm for pathfinding
- Manhattan distance heuristic
- Priority queue using Python's `heapq`
- Animated search visualization
- Color-coded frontier, explored cells, walls, start, goal, and final path
- Live statistics showing path moves and explored cells
- Reset functionality
- Handles cases where no valid path exists
- GUI with a maze legend and algorithm instructions

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

## Maze Legend
- Green: Start
- Red: Goal
- Gray: Wall
- Purple: Frontier cells waiting to be explored
- Blue: Explored cells
- Yellow: Shortest path

## Algorithm
A* evaluates cells using:

`f(n) = g(n) + h(n)`

- `g(n)`: Actual cost from the Start.
- `h(n)`: Estimated distance to the Goal using Manhattan distance.
- `f(n)`: Estimated total cost.

Each move costs 1, and movement is allowed in four directions: up, down, left, and right.

## Author
Created as a learning project during my learning journey with Syntecxhub.
