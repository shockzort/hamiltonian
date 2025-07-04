# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project generates Hamiltonian graphs or labyrinths in an 8x8 grid and visualizes them. The main goal is to create maze-like structures where a Hamiltonian path exists - a path that visits each node exactly once. The project uses dynamic programming to verify Hamiltonian path existence and Plotly for visualization.

## Architecture

- **Core Classes:**
  - `discrete_point`: Represents a point on a discrete grid with x, y coordinates and an index
  - `node`: Represents a graph node containing a discrete point and its neighbors (max 2 for path generation)
  - `hamiltonian_grid`: Main class that creates a grid graph and implements labyrinth generation with Hamiltonian path verification

- **Key Components:**
  - Grid initialization creates nodes for each position and establishes neighbor relationships
  - Node connection logic limits each node to maximum 2 neighbors (creating path-like structures)
  - Adjacency matrix representation for graph analysis
  - Dynamic programming algorithm for Hamiltonian path verification
  - Plotly visualization renders the labyrinth as connected grid cells

## Dependencies

The project uses:
- `plotly` for visualization (graph_objects module)
- Standard library modules: `sys`

## Running the Code

To run the main script:
```bash
python solve_hamiltonian.py
```

The script will:
1. Create an 8x8 grid labyrinth
2. Check for Hamiltonian path existence
3. Display the labyrinth visualization if path exists, otherwise print a message

## Key Algorithms

- **Labyrinth Generation**: Creates maze-like structures by limiting node connections to 2 neighbors maximum
- **Hamiltonian Path Verification**: Uses dynamic programming with bitmask approach to verify path existence
- **Grid Neighbor Detection**: Determines adjacency based on Manhattan distance of 1
- **Visualization**: Draws grid nodes as rectangles with connections as red lines forming the labyrinth paths