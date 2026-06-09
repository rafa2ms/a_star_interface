"""Interactive A* pathfinding visualizer.

Grid values:
0 - empty cell
1 - start point
2 - target point
3 - wall
"""

from dataclasses import dataclass
from heapq import heappop, heappush
import tkinter as tk
from tkinter import messagebox


EMPTY = 0
START = 1
TARGET = 2
WALL = 3

MIN_GRID_SIZE = 2
MAX_GRID_SIZE = 50
CANVAS_SIZE = 720

w = 0
h = 0
grid = []


@dataclass
class AStarResult:
    path: list[tuple[int, int]]
    g_score: dict[tuple[int, int], int]
    h_score: dict[tuple[int, int], int]
    f_score: dict[tuple[int, int], int]
    closed_set: set[tuple[int, int]]


def create_grid(width, height):
    return [[EMPTY for _ in range(width)] for _ in range(height)]


def heuristic(a, b):
    """Manhattan distance for four-direction grid movement."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(node):
    neighbors = []
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for row_delta, col_delta in directions:
        neighbor = (node[0] + row_delta, node[1] + col_delta)
        row, col = neighbor

        if 0 <= row < h and 0 <= col < w and grid[row][col] != WALL:
            neighbors.append(neighbor)

    return neighbors


def reconstruct_path(came_from, current):
    total_path = [current]

    while current in came_from:
        current = came_from[current]
        total_path.append(current)

    return total_path[::-1]


def a_star(start, target):
    """Run A* and return path plus G/H/F values for discovered cells."""
    open_heap = []
    open_lookup = {start}
    closed_set = set()
    came_from = {}
    tie_breaker = 0

    g_score = {start: 0}
    h_score = {start: heuristic(start, target)}
    f_score = {start: h_score[start]}

    heappush(open_heap, (f_score[start], h_score[start], tie_breaker, start))

    while open_heap:
        _, _, _, current = heappop(open_heap)

        if current not in open_lookup:
            continue

        open_lookup.remove(current)

        if current == target:
            return AStarResult(
                reconstruct_path(came_from, current),
                g_score,
                h_score,
                f_score,
                closed_set,
            )

        closed_set.add(current)

        for neighbor in get_neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g_score = g_score[current] + 1

            if tentative_g_score >= g_score.get(neighbor, float("inf")):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            h_score[neighbor] = heuristic(neighbor, target)
            f_score[neighbor] = g_score[neighbor] + h_score[neighbor]

            tie_breaker += 1
            heappush(
                open_heap,
                (f_score[neighbor], h_score[neighbor], tie_breaker, neighbor),
            )
            open_lookup.add(neighbor)

    return AStarResult([], g_score, h_score, f_score, closed_set)


def update_grid(start, target, barriers):
    for row in range(h):
        for col in range(w):
            grid[row][col] = EMPTY

    if start is not None:
        grid[start[0]][start[1]] = START

    if target is not None:
        grid[target[0]][target[1]] = TARGET

    for barrier in barriers:
        if barrier != start and barrier != target:
            grid[barrier[0]][barrier[1]] = WALL


def udpate_grid(start, target, barrier):
    """Compatibility wrapper for the original misspelled function name."""
    update_grid(start, target, barrier)


class AStarGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Pathfinding Visualizer")

        self.start = None
        self.target = None
        self.barriers = set()
        self.result = None
        self.path_cells = set()
        self.path_parent = {}

        self.cell_size = min(CANVAS_SIZE / w, CANVAS_SIZE / h)
        self.grid_origin_x = 0
        self.grid_origin_y = 0
        self.grid_width = self.cell_size * w
        self.grid_height = self.cell_size * h

        instruction_frame = tk.Frame(root, bg="#e0f2fe", padx=12, pady=10)
        instruction_frame.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=12,
            pady=(12, 6),
        )
        tk.Label(
            instruction_frame,
            text="A* Pathfinding Visualizer",
            bg="#e0f2fe",
            fg="#0f172a",
            anchor="w",
            font=("Arial", 14, "bold"),
        ).grid(row=0, column=0, sticky="ew")
        instruction_steps = [
            "1. Click a start cell.",
            "2. Click a target cell.",
            "3. Add walls.",
            "4. Press Run A*.",
        ]

        for index, step in enumerate(instruction_steps, start=1):
            tk.Label(
                instruction_frame,
                text=step,
                bg="#e0f2fe",
                fg="#334155",
                anchor="w",
                font=("Arial", 11),
            ).grid(row=index, column=0, sticky="ew", pady=(3 if index == 1 else 1, 0))
        instruction_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            root,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="#f8fafc",
            highlightthickness=0,
        )
        self.canvas.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=12,
            pady=(12, 8),
        )

        self.status = tk.StringVar(value="Click an empty cell for start.")
        tk.Label(root, textvariable=self.status, anchor="w").grid(
            row=2, column=0, columnspan=4, sticky="ew", padx=12
        )

        tk.Button(root, text="Run A*", command=self.run_pathfinding).grid(
            row=3, column=0, sticky="ew", padx=(12, 4), pady=12
        )
        tk.Button(root, text="Clear Path", command=self.clear_path_view).grid(
            row=3, column=1, sticky="ew", padx=4, pady=12
        )
        tk.Button(root, text="Reset Grid", command=self.reset_grid).grid(
            row=3, column=2, sticky="ew", padx=4, pady=12
        )
        tk.Button(root, text="Quit", command=root.destroy).grid(
            row=3, column=3, sticky="ew", padx=(4, 12), pady=12
        )

        for column in range(4):
            root.columnconfigure(column, weight=1)
        root.rowconfigure(1, weight=1)
        root.minsize(420, 520)

        self.canvas.bind("<Button-1>", self.handle_left_click)
        self.canvas.bind("<Button-3>", self.handle_right_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<Configure>", self.handle_canvas_resize)

        self.draw_grid()

    def handle_left_click(self, event):
        cell = self.event_to_cell(event)
        if cell is None:
            return

        self.clear_path()

        if self.start is None:
            self.start = cell
            self.barriers.discard(cell)
            self.status.set("Click another empty cell for target.")
        elif self.target is None and cell != self.start:
            self.target = cell
            self.barriers.discard(cell)
            self.status.set("Add walls or run A*.")
        elif cell != self.start and cell != self.target:
            self.toggle_wall(cell)

        update_grid(self.start, self.target, self.barriers)
        self.draw_grid()

    def handle_right_click(self, event):
        cell = self.event_to_cell(event)
        if cell is None:
            return

        self.clear_path()
        self.clear_cell(cell)
        update_grid(self.start, self.target, self.barriers)
        self.draw_grid()

    def handle_drag(self, event):
        cell = self.event_to_cell(event)
        if cell is None or cell == self.start or cell == self.target:
            return

        if self.start is not None and self.target is not None:
            self.clear_path()
            self.barriers.add(cell)
            update_grid(self.start, self.target, self.barriers)
            self.draw_grid()

    def handle_canvas_resize(self, event):
        self.draw_grid()

    def event_to_cell(self, event):
        x = event.x - self.grid_origin_x
        y = event.y - self.grid_origin_y

        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return None

        row = int(y // self.cell_size)
        col = int(x // self.cell_size)

        if 0 <= row < h and 0 <= col < w:
            return (row, col)

        return None

    def toggle_wall(self, cell):
        if cell in self.barriers:
            self.barriers.remove(cell)
            self.status.set("Wall removed.")
        else:
            self.barriers.add(cell)
            self.status.set("Wall added.")

    def clear_cell(self, cell):
        if cell == self.start:
            self.start = None
            self.status.set("Start cleared.")
        elif cell == self.target:
            self.target = None
            self.status.set("Target cleared.")
        elif cell in self.barriers:
            self.barriers.remove(cell)
            self.status.set("Wall cleared.")

    def clear_path(self):
        self.result = None
        self.path_cells = set()
        self.path_parent = {}

    def clear_path_view(self):
        self.clear_path()
        self.status.set("Path cleared.")
        self.draw_grid()

    def reset_grid(self):
        self.start = None
        self.target = None
        self.barriers.clear()
        self.clear_path()
        update_grid(self.start, self.target, self.barriers)
        self.status.set("Click an empty cell for start.")
        self.draw_grid()

    def run_pathfinding(self):
        if self.start is None or self.target is None:
            messagebox.showinfo("A*", "Choose both start and target cells first.")
            return

        update_grid(self.start, self.target, self.barriers)
        self.result = a_star(self.start, self.target)
        self.path_cells = set(self.result.path)
        self.path_parent = {
            cell: self.result.path[index - 1]
            for index, cell in enumerate(self.result.path)
            if index > 0
        }

        if self.result.path:
            self.status.set(f"Path found with {len(self.result.path) - 1} steps.")
            print("Path found:", self.result.path)
        else:
            self.status.set("No path found.")
            print("No path found.")

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self.update_canvas_metrics()

        for row in range(h):
            for col in range(w):
                self.draw_cell(row, col)

    def update_canvas_metrics(self):
        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())

        if canvas_width <= 1:
            canvas_width = CANVAS_SIZE
        if canvas_height <= 1:
            canvas_height = CANVAS_SIZE

        self.cell_size = max(1, min(canvas_width / w, canvas_height / h))
        self.grid_width = self.cell_size * w
        self.grid_height = self.cell_size * h
        self.grid_origin_x = (canvas_width - self.grid_width) / 2
        self.grid_origin_y = (canvas_height - self.grid_height) / 2

    def draw_cell(self, row, col):
        x1 = self.grid_origin_x + col * self.cell_size
        y1 = self.grid_origin_y + row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        cell = (row, col)
        cell_value = grid[row][col]
        fill = self.cell_fill(cell, cell_value)

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=fill,
            outline="#94a3b8",
            width=1,
        )

        self.draw_parent_arrow(cell, x1, y1, x2, y2)

        if cell_value == START:
            self.draw_marker(x1, y1, x2, y2, "S", "#166534")
        elif cell_value == TARGET:
            self.draw_marker(x1, y1, x2, y2, "T", "#991b1b")
        elif cell_value == WALL:
            self.draw_marker(x1, y1, x2, y2, "#", "#f8fafc")

        self.draw_scores(cell, x1, y1, x2, y2)

    def cell_fill(self, cell, cell_value):
        if cell_value == WALL:
            return "#334155"
        if cell_value == START:
            return "#bbf7d0"
        if cell_value == TARGET:
            return "#fecaca"
        if cell in self.path_cells:
            return "#fde68a"
        if self.result and cell in self.result.closed_set:
            return "#dbeafe"
        if self.result and cell in self.result.g_score:
            return "#e0f2fe"
        return "#f8fafc"

    def draw_marker(self, x1, y1, x2, y2, text, color):
        marker_size = max(10, min(24, int(self.cell_size // 3)))
        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill=color,
            font=("Arial", marker_size, "bold"),
        )

    def draw_parent_arrow(self, cell, x1, y1, x2, y2):
        parent = self.path_parent.get(cell)

        if parent is None:
            return

        row_delta = parent[0] - cell[0]
        col_delta = parent[1] - cell[1]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        arrow_length = self.cell_size * 0.28
        end_x = center_x + col_delta * arrow_length
        end_y = center_y + row_delta * arrow_length
        line_width = max(1, int(self.cell_size // 26))
        head = max(7, int(self.cell_size // 7))

        self.canvas.create_line(
            center_x,
            center_y,
            end_x,
            end_y,
            fill="#854d0e",
            width=line_width,
            arrow=tk.LAST,
            arrowshape=(head, head + 2, max(3, head // 2)),
        )

    def draw_scores(self, cell, x1, y1, x2, y2):
        if self.result is None or cell not in self.result.g_score:
            return

        if grid[cell[0]][cell[1]] == WALL:
            return

        g = self.result.g_score[cell]
        h_cost = self.result.h_score[cell]
        f = self.result.f_score[cell]
        score_size = max(7, min(12, int(self.cell_size // 6)))
        padding = max(3, self.cell_size // 16)

        labels = [
            (f"F:{f}", x1 + padding, y1 + padding, "nw"),
            (f"G:{g}", x1 + padding, y2 - padding, "sw"),
            (f"H:{h_cost}", x2 - padding, y2 - padding, "se"),
        ]

        for text, x, y, anchor in labels:
            self.canvas.create_text(
                x,
                y,
                text=text,
                fill="#0f172a",
                anchor=anchor,
                font=("Arial", score_size),
            )


def ask_grid_dimensions():
    root = tk.Tk()
    root.title("Grid dimensions")
    root.resizable(False, False)

    dimensions = {}
    width_var = tk.IntVar(value=5)
    height_var = tk.IntVar(value=3)

    frame = tk.Frame(root, padx=16, pady=16)
    frame.grid(row=0, column=0, sticky="nsew")

    tk.Label(frame, text="Width").grid(row=0, column=0, sticky="w", pady=(0, 8))
    width_spinbox = tk.Spinbox(
        frame,
        from_=MIN_GRID_SIZE,
        to=MAX_GRID_SIZE,
        textvariable=width_var,
        width=8,
    )
    width_spinbox.grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

    tk.Label(frame, text="Height").grid(row=1, column=0, sticky="w", pady=(0, 12))
    height_spinbox = tk.Spinbox(
        frame,
        from_=MIN_GRID_SIZE,
        to=MAX_GRID_SIZE,
        textvariable=height_var,
        width=8,
    )
    height_spinbox.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 12))

    button_frame = tk.Frame(frame)
    button_frame.grid(row=2, column=0, columnspan=2, sticky="e")

    def submit(event=None):
        try:
            width = int(width_spinbox.get())
            height = int(height_spinbox.get())
        except ValueError:
            messagebox.showerror(
                "Grid dimensions",
                "Width and height must be whole numbers.",
                parent=root,
            )
            return

        if not (
            MIN_GRID_SIZE <= width <= MAX_GRID_SIZE
            and MIN_GRID_SIZE <= height <= MAX_GRID_SIZE
        ):
            messagebox.showerror(
                "Grid dimensions",
                f"Choose values from {MIN_GRID_SIZE} to {MAX_GRID_SIZE}.",
                parent=root,
            )
            return

        dimensions["value"] = (width, height)
        root.destroy()

    def cancel(event=None):
        root.destroy()

    tk.Button(button_frame, text="Cancel", command=cancel).grid(
        row=0, column=0, padx=(0, 8)
    )
    tk.Button(button_frame, text="Create Grid", command=submit).grid(row=0, column=1)

    frame.columnconfigure(1, weight=1)
    root.bind("<Return>", submit)
    root.bind("<Escape>", cancel)
    root.protocol("WM_DELETE_WINDOW", cancel)

    width_spinbox.focus_set()
    root.mainloop()

    return dimensions.get("value")


def run_interface():
    global w, h, grid

    dimensions = ask_grid_dimensions()

    if dimensions is None:
        return

    w, h = dimensions
    grid = create_grid(w, h)

    root = tk.Tk()
    AStarGridApp(root)
    root.mainloop()


def main():
    run_interface()


if __name__ == "__main__":
    main()
