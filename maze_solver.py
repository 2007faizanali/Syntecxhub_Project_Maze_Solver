
import tkinter as tk
import heapq

# 1. Maze design
maze = [
    "S...#",
    "#...#",
    "...#.",
    ".##..",
    "....G"
]

CELL_SIZE = 60
ROWS = len(maze)
COLS = len(maze[0])

# Animation speed in milliseconds
SEARCH_SPEED = 200
PATH_SPEED = 100


# 2. Find Start and Goal
def find_position(symbol):
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == symbol:
                return (r, c)
    return None


start = find_position("S")
goal = find_position("G")


# 3. Manhattan distance
def heuristic(cell):
    r, c = cell
    gr, gc = goal
    return abs(r - gr) + abs(c - gc)


# 4. Find valid neighbors
def get_neighbors(cell):
    r, c = cell

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbors = []

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc

        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if maze[nr][nc] != "#":
                neighbors.append((nr, nc))

    return neighbors


# 5. Create window
root = tk.Tk()
root.title("Maze Solver - A* Search")
root.resizable(False, False)

canvas = tk.Canvas(
    root,
    width=COLS * CELL_SIZE,
    height=ROWS * CELL_SIZE
)
canvas.pack(padx=10, pady=10)

status = tk.Label(
    root,
    text="Click Solve Maze to start!",
    font=("Arial", 11)
)
status.pack(pady=5)


# 6. Search data
frontier = set()
visited = set()
came_from = {}
g_score = {}
open_heap = []
final_path = []

path_progress = 0
counter = 0
run_id = 0
running = False


# 7. Draw the maze
def draw_maze():
    canvas.delete("all")

    path_cells = set(final_path[:path_progress])

    for r in range(ROWS):
        for c in range(COLS):
            cell = (r, c)
            symbol = maze[r][c]

            color = "white"

            if symbol == "#":
                color = "#333333"
            elif cell in visited:
                color = "#A9D6FF"
            elif cell in frontier:
                color = "#DCCBFF"

            if cell in path_cells:
                color = "#FFD966"

            if cell == start:
                color = "#55CC77"
            elif cell == goal:
                color = "#FF7777"

            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="#AAAAAA"
            )

            if symbol in ("S", "G"):
                canvas.create_text(
                    x1 + CELL_SIZE / 2,
                    y1 + CELL_SIZE / 2,
                    text=symbol,
                    font=("Arial", 18, "bold")
                )


# 8. Draw final path one cell at a time

def animate_path(token, index=0):
    global running, path_progress

    # Stop outdated animations
    if token != run_id:
        return

    # All path cells have been drawn
    if index >= len(final_path):
        running = False

        status.config(
            text=(
                f"Path found! Moves: {len(final_path) - 1} | "
                f"Explored: {len(visited)}"
            )
        )
        return

    # Reveal only the next cell
    path_progress = index + 1
    draw_maze()

    # Animate the next cell
    root.after(
        PATH_SPEED,
        lambda: animate_path(token, index + 1)
    )



# 9. Reconstruct the path
def build_path():
    path = []
    node = goal

    while node in came_from:
        path.append(node)
        node = came_from[node]

    path.append(start)
    path.reverse()

    return path


# 10. One step of A* search
def search_step(token):
    global counter, final_path, running

    if token != run_id:
        return

    # Remove outdated queue entries
    while open_heap:
        _, queued_g, _, current = heapq.heappop(open_heap)

        if (
            current not in visited
            and queued_g == g_score.get(current)
        ):
            break
    else:
        running = False
        status.config(text="No path exists!")
        draw_maze()
        return

    frontier.discard(current)
    visited.add(current)

    # Goal reached
    if current == goal:
        final_path = build_path()

        status.config(text="Goal found! Showing shortest path...")
        draw_maze()

        animate_path(token)
        return

    # Explore neighbors
    for neighbor in get_neighbors(current):
        if neighbor in visited:
            continue

        tentative_g = g_score[current] + 1

        if tentative_g < g_score.get(
            neighbor, float("inf")
        ):
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g

            f_score = tentative_g + heuristic(neighbor)

            counter += 1

            heapq.heappush(
                open_heap,
                (f_score, tentative_g, counter, neighbor)
            )

            frontier.add(neighbor)

    draw_maze()

    status.config(
        text=(
            f"Exploring: {current} | "
            f"Visited cells: {len(visited)}"
        )
    )

    # Schedule the next step
    root.after(
        SEARCH_SPEED,
        lambda: search_step(token)
    )


# 11. Start search
def solve_maze():
    global frontier, visited, came_from
    global g_score, open_heap, final_path
    global counter, run_id, running, path_progress

    if running:
        return

    if start is None or goal is None:
        status.config(text="Start or Goal is missing!")
        return

    run_id += 1
    token = run_id

    frontier = {start}
    visited = set()
    came_from = {}
    g_score = {start: 0}
    open_heap = []
    final_path = []
    path_progress = 0
    counter = 0
    running = True

    heapq.heappush(
        open_heap,
        (heuristic(start), 0, counter, start)
    )

    status.config(text="A* search started...")
    draw_maze()

    root.after(
        SEARCH_SPEED,
        lambda: search_step(token)
    )


# 12. Reset the maze
def reset_maze():
    global frontier, visited, came_from
    global g_score, open_heap, final_path
    global counter, run_id, running, path_progress

    # Invalidate previously scheduled animation callbacks
    run_id += 1
    running = False

    frontier = set()
    visited = set()
    came_from = {}
    g_score = {}
    open_heap = []
    final_path = []
    path_progress = 0
    counter = 0

    status.config(text="Maze reset. Ready to solve!")
    draw_maze()


# 13. Buttons
buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons,
    text="Solve Maze",
    command=solve_maze,
    width=14
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="Reset",
    command=reset_maze,
    width=14
).pack(side="left", padx=5)


# 14. Legend
legend = tk.Label(
    root,
    text="Green: Start | Red: Goal | Gray: Wall\n"
         "Purple: Frontier | Blue: Explored | Yellow: Path",
    font=("Arial", 9)
)
legend.pack(pady=5)

draw_maze()
root.mainloop()
