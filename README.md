# A* Grid Interface

This interface is an interactive grid tool for creating a simple pathfinding scenario. You choose the grid size, place a start cell, place a target cell, add walls, and then run the search to see which route is selected. The visualization shows the explored cells, the final path, the parent direction for each path cell, and the cost values used to compare possible moves.

A* is a pathfinding algorithm that searches for a low-cost route from a start point to a target point. It combines the cost already spent to reach a cell with an estimate of the remaining distance to the target, which helps it avoid exploring the whole grid when a promising route is available. In this interface, those values are shown as `G`, `H`, and `F`.

Run the visualizer with:

```bash
python3 a_star_interface.py
```

## Prerequisites

This script uses only Python standard library modules, so it does not need a `requirements.txt` file or any `pip` packages.

Tkinter must be available in your Python installation. It is included by default in many Python installs, but on some Linux systems you may need to install it separately:

```bash
sudo apt install python3-tk
```

## Using The Interface

1. Choose the grid width and height, then click `Create Grid`.
2. Click one grid cell to set the start point. It is marked with `S`.
3. Click another grid cell to set the target point. It is marked with `T`.
4. Click empty cells to toggle walls.
5. Drag across empty cells to draw multiple walls after the start and target are set.
6. Right-click a cell to clear it.
7. Click `Run A*` to find and display the path.
8. Click `Clear Path` to hide the current path result while keeping the grid setup.
9. Click `Reset Grid` to clear the start, target, walls, and path.

The grid resizes with the application window. If you maximize the window, the cells grow while staying square.

## Cell Values

- `0`: empty cell
- `1`: start point
- `2`: target point
- `3`: wall

## Visual Meaning

The yellow cells show the chosen path from the start to the target.

Each arrow points from a path cell back toward its parent cell. In other words, following the arrows backward leads from the target cell toward the start cell.

Cells explored by the search show three numbers:

- `F`: total estimated cost through that cell, `F = G + H`
- `G`: cost from the start cell to that cell
- `H`: estimated cost from that cell to the target cell

The numbers are placed as:

- `F`: top-left
- `G`: bottom-left
- `H`: bottom-right
