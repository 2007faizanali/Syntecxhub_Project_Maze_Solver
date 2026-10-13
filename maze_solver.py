import tkinter as tk
import heapq

# Maze layout: S = Start, G = Goal, # = Wall, . = Open cell
maze = [
    "S.....#.....",
    "......#..#..",
    "...#.....#..",
    "...#..#..#..",
    "...#..###...",
    "..#...#..#..",
    "..##.....#..",
    "..##..#..#..",
    "...#..###...",
    "..#.........",
    "..#...#.....",
    "......#....G",
]

CELL_SIZE = 48
SEARCH_SPEED = 45       # milliseconds between A* steps
PATH_SPEED = 35         # milliseconds between path-animation steps

ROWS = len(maze)
COLS = len(maze[0])


def validate_maze(grid):
    """Check that the maze is rectangular and has exactly one S and one G."""
    if not grid or not grid[0]:
        raise ValueError("Maze cannot be empty.")
    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Every maze row must have the same number of columns.")
    if sum(row.count("S") for row in grid) != 1:
        raise ValueError("Maze must contain exactly one Start (S).")
    if sum(row.count("G") for row in grid) != 1:
        raise ValueError("Maze must contain exactly one Goal (G).")
    if any(ch not in "S G.#".replace(" ", "") for row in grid for ch in row):
        raise ValueError("Maze contains an unsupported character.")


validate_maze(maze)


def find_position(symbol):
    for r, row in enumerate(maze):
        for c, value in enumerate(row):
            if value == symbol:
                return (r, c)
    return None


start = find_position("S")
goal = find_position("G")


def heuristic(cell):
    """Manhattan distance: admissible when movement is up/down/left/right."""
    r, c = cell
    gr, gc = goal
    return abs(r - gr) + abs(c - gc)


def get_neighbors(cell):
    r, c = cell
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != "#":
            neighbors.append((nr, nc))
    return neighbors


# --- Window and interface ---
root = tk.Tk()
root.title("Maze Solver | A* Search Algorithm")
root.geometry("1366x768")
root.resizable(False, False)
root.configure(bg="#F3F5F8")

header = tk.Label(root, text="MAZE SOLVER", font=("Arial", 19, "bold"),
                  bg="#F3F5F8", fg="#202A44")
header.pack(pady=(4, 0))
subtitle = tk.Label(root, text="A* Search  •  Manhattan Distance  •  Shortest Path",
                    font=("Arial", 10), bg="#F3F5F8", fg="#586174")
subtitle.pack(pady=(0, 3))

main_frame = tk.Frame(root, bg="#F3F5F8")
main_frame.pack(fill="both", expand=True, padx=22, pady=1)
main_frame.grid_columnconfigure(0, weight=1, uniform="panels")
main_frame.grid_columnconfigure(1, weight=0)
main_frame.grid_columnconfigure(2, weight=1, uniform="panels")
main_frame.grid_rowconfigure(0, weight=1)

left_panel = tk.Frame(main_frame, bg="#F3F5F8", width=300)
left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
left_panel.grid_propagate(False)
tk.Label(left_panel, text="CELL LEGEND", font=("Arial", 13, "bold"),
         bg="#F3F5F8", fg="#202A44").pack(anchor="w", pady=(18, 8))

canvas = tk.Canvas(main_frame, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE,
                   bg="white", highlightthickness=1, highlightbackground="#B8C0CC")
canvas.grid(row=0, column=1, padx=4, pady=2, sticky="n")

right_panel = tk.Frame(main_frame, bg="#F3F5F8", width=300)
right_panel.grid(row=0, column=2, sticky="nsew", padx=(16, 0))
right_panel.grid_propagate(False)
tk.Label(right_panel, text="HOW IT WORKS", font=("Arial", 13, "bold"),
         bg="#F3F5F8", fg="#202A44").pack(anchor="w", pady=(18, 8))

# Status and statistics are displayed in the right panel, above the instructions.
status = tk.Label(right_panel, text="Ready to solve the maze.",
                  font=("Arial", 10, "bold"), bg="#F3F5F8", fg="#202A44",
                  width=36, wraplength=280, justify="left", anchor="w")
status.pack(fill="x", pady=(0, 3))
stats = tk.Label(right_panel, text=f"Grid: {ROWS} × {COLS}  |  Moves: —  |  Explored: 0",
                 font=("Arial", 9), bg="#F3F5F8", fg="#586174",
                 wraplength=280, justify="left", anchor="w")
stats.pack(fill="x", pady=(0, 7))

# A* state
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
search_finished = False


COLORS = {
    "open": "#FFFFFF",
    "wall": "#303746",
    "start": "#58C785",
    "goal": "#F27777",
    "frontier": "#D9C8FF",
    "visited": "#A9D6FF",
    "path": "#FFD966",
}


def draw_maze():
    canvas.delete("all")
    visible_path = set(final_path[:path_progress])

    for r in range(ROWS):
        for c in range(COLS):
            cell = (r, c)
            symbol = maze[r][c]
            color = COLORS["open"]

            if symbol == "#":
                color = COLORS["wall"]
            elif cell in visited:
                color = COLORS["visited"]
            elif cell in frontier:
                color = COLORS["frontier"]

            if cell in visible_path:
                color = COLORS["path"]
            if cell == start:
                color = COLORS["start"]
            elif cell == goal:
                color = COLORS["goal"]

            x1, y1 = c * CELL_SIZE, r * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="#D5DAE2",
                width=1,
            )

            if symbol in ("S", "G"):
                canvas.create_text(
                    x1 + CELL_SIZE / 2,
                    y1 + CELL_SIZE / 2,
                    text=symbol,
                    font=("Arial", 13, "bold"),
                    fill="#182033",
                )


def update_stats(moves="—"):
    stats.config(
        text=f"Grid: {ROWS} × {COLS}  |  Moves: {moves}  |  Explored: {len(visited)}"
    )


def build_path():
    path = [goal]
    node = goal
    while node != start:
        node = came_from[node]
        path.append(node)
    path.reverse()
    return path


def animate_path(token, index=0):
    global running, path_progress, search_finished

    if token != run_id:
        return

    if index >= len(final_path):
        running = False
        search_finished = True
        moves = len(final_path) - 1
        status.config(text=f"Path found! The shortest route uses {moves} moves.")
        update_stats(moves)
        return

    path_progress = index + 1
    draw_maze()
    update_stats(len(final_path) - 1)
    root.after(PATH_SPEED, lambda: animate_path(token, index + 1))


def search_step(token):
    global counter, final_path, running

    if token != run_id:
        return

    # Ignore outdated heap entries created when a better route was found.
    while open_heap:
        _, queued_g, _, current = heapq.heappop(open_heap)
        if current not in visited and queued_g == g_score.get(current):
            break
    else:
        running = False
        status.config(text="No path exists between Start and Goal.")
        update_stats("No path")
        draw_maze()
        return

    frontier.discard(current)
    visited.add(current)

    if current == goal:
        final_path = build_path()
        status.config(text="Goal reached! Highlighting the shortest path...")
        draw_maze()
        animate_path(token)
        return

    for neighbor in get_neighbors(current):
        if neighbor in visited:
            continue

        tentative_g = g_score[current] + 1
        if tentative_g < g_score.get(neighbor, float("inf")):
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            counter += 1
            f_score = tentative_g + heuristic(neighbor)
            heapq.heappush(
                open_heap,
                (f_score, tentative_g, counter, neighbor),
            )
            frontier.add(neighbor)

    draw_maze()
    status.config(text=f"Searching... Current cell: {current}")
    update_stats()
    root.after(SEARCH_SPEED, lambda: search_step(token))


def solve_maze():
    global frontier, visited, came_from, g_score, open_heap
    global final_path, path_progress, counter, run_id, running, search_finished

    if running:
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
    search_finished = False

    heapq.heappush(open_heap, (heuristic(start), 0, counter, start))
    status.config(text="A* search started...")
    update_stats()
    draw_maze()
    root.after(SEARCH_SPEED, lambda: search_step(token))


def reset_maze():
    global frontier, visited, came_from, g_score, open_heap
    global final_path, path_progress, counter, run_id, running, search_finished

    # Invalidate any search/path animation callback already scheduled.
    run_id += 1
    running = False
    search_finished = False
    frontier = set()
    visited = set()
    came_from = {}
    g_score = {}
    open_heap = []
    final_path = []
    path_progress = 0
    counter = 0

    status.config(text="Maze reset. Ready to solve!")
    update_stats()
    draw_maze()


for label, color, description in [
    ("Start", COLORS["start"], "Starting point"),
    ("Goal", COLORS["goal"], "Target destination"),
    ("Wall", COLORS["wall"], "Blocked cell"),
    ("Frontier", COLORS["frontier"], "Waiting to be explored"),
    ("Explored", COLORS["visited"], "Already checked by A*"),
    ("Shortest path", COLORS["path"], "Final route to the goal"),
]:
    row = tk.Frame(left_panel, bg="#F3F5F8")
    row.pack(fill="x", anchor="w", pady=7)
    swatch = tk.Canvas(row, width=24, height=24, bg=color,
                       highlightthickness=1, highlightbackground="#B8C0CC")
    swatch.pack(side="left", padx=(0, 10))
    text_frame = tk.Frame(row, bg="#F3F5F8")
    text_frame.pack(side="left", fill="x")
    tk.Label(text_frame, text=label, font=("Arial", 10, "bold"),
             bg="#F3F5F8", fg="#202A44").pack(anchor="w")
    tk.Label(text_frame, text=description, font=("Arial", 8),
             bg="#F3F5F8", fg="#586174").pack(anchor="w")

# Search controls live in the right panel, below the algorithm guide.
controls_card = tk.Frame(left_panel, bg="#F3F5F8")
controls_card.pack(fill="x", pady=(22, 4))

tk.Label(controls_card, text="CONTROLS", font=("Arial", 11, "bold"),
         bg="#F3F5F8", fg="#202A44").pack(anchor="w", pady=(0, 8))

tk.Button(
    controls_card, text="▶  Solve Maze", command=solve_maze,
    font=("Arial", 10, "bold"), bg="#2D6CDF", fg="white",
    activebackground="#2458B5", activeforeground="white",
    relief="flat", padx=12, pady=9, width=20
).pack(fill="x", pady=4)

tk.Button(
    controls_card, text="↻  Reset Maze", command=reset_maze,
    font=("Arial", 10, "bold"), bg="#E1E5EC", fg="#202A44",
    activebackground="#CBD2DE", relief="flat", padx=12, pady=9, width=20
).pack(fill="x", pady=4)


for heading, detail in [
    ("1. Start", "A* begins at the green S cell."),
    ("2. Explore", "Purple cells are queued; blue cells have been explored."),
    ("3. Heuristic", "Manhattan distance estimates distance to the goal."),
    ("4. Shortest route", "Yellow cells show the route found to red G."),
]:
    card = tk.Frame(right_panel, bg="#FFFFFF", padx=10, pady=7,
                    highlightthickness=1, highlightbackground="#DDE2EA")
    card.pack(fill="x", pady=4)
    tk.Label(card, text=heading, font=("Arial", 10, "bold"),
             bg="#FFFFFF", fg="#202A44").pack(anchor="w")
    tk.Label(card, text=detail, font=("Arial", 9), bg="#FFFFFF",
             fg="#586174", wraplength=260, justify="left").pack(anchor="w", pady=(4, 0))

draw_maze()
root.mainloop()
