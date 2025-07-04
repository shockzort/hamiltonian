from __future__ import annotations
import sys
import random
import time
import signal
import os
import plotly.graph_objects as go

# Try to import tomllib (Python 3.11+), fallback to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: TOML support not available. Please install tomli: pip install tomli")
        sys.exit(1)

class discrete_point:
    x: int
    y: int
    idx: int

    def __init__(self, x: int, y: int, idx: int):
        self.x = x
        self.y = y
        self.idx = idx

    def is_neighbour(self, other: discrete_point) -> bool:
        return (abs(self.x - other.x) == 1 and abs(self.y - other.y) == 0) or (
            abs(self.x - other.x) == 0 and abs(self.y - other.y) == 1
        )



class node:
    p: discrete_point
    neighbours: list[discrete_point]

    def __init__(self, p: discrete_point):
        self.p = p
        self.neighbours = []
        self.visited = False

    def connected(self) -> bool:
        return len(self.neighbours) == 2

    def connect(self, other: node) -> bool:
        if self.p.idx == other.p.idx:
            return False

        if self.connected() or other.connected():
            return False

        if not self.p.is_neighbour(other.p):
            return False

        self.neighbours.append(other.p)
        other.neighbours.append(self.p)

        return True

class hamiltonian_grid:

    w: int = 0
    h: int = 0
    nodes: dict = {}
    path: list = []
    generation_stats: dict = {}
    progress_frequency: int = 50000

    def __init__(self, w: int, h: int, progress_frequency: int = 50000):
        if w <= 0 or h <= 0:
            print("cannot init hamiltonian grid: dims incorrect w={}, h={}".format(w, h))
            return

        self.w = w
        self.h = h
        self.path = []
        self.progress_frequency = progress_frequency
        self.generation_stats = {
            'total_attempts': 0,
            'successful_attempts': 0,
            'total_time': 0,
            'backtrack_steps': 0,
            'max_depth_reached': 0
        }

        idx = 0
        for x in range(w):
            for y in range(h):
                self.nodes[idx] = node(discrete_point(x + 0.5, y + 0.5, idx))
                idx += 1

        self._init_grid()

    def _init_grid(self):
        for n_out in self.nodes.values():
            for n_in in self.nodes.values():
                if n_out.p.idx == n_in.p.idx:
                    continue

                if n_out.p.is_neighbour(n_in.p):
                    if n_in.p not in n_out.neighbours:
                        n_out.neighbours.append(n_in.p)

                    if n_out.p not in n_in.neighbours:
                        n_in.neighbours.append(n_out.p)



    def as_adjacency_matrix(self):
        res = [[0 for i in range(self.w)]
                 for j in range(self.h)]

        for node_idx, node in self.nodes.items():
            row = res[int(node_idx % self.w)]

            row[int(node.p.idx % self.w)] = 1

            for n in node.neighbours:
                row[int(n.idx % self.w)] = 1

        return res


    def has_hamiltonian_path(self) -> bool:

        adj_matrix = self.as_adjacency_matrix()
        print("adj_matrix: {}".format(adj_matrix))

        num_rows = len(adj_matrix)

        dp = [[False for i in range(1 << num_rows)]
                    for j in range(num_rows)]

        # Set all dp[i][(1 << i)] to
        # true
        for i in range(num_rows):
            dp[i][1 << i] = True

        # Iterate over each subset
        # of nodes
        for i in range(1 << num_rows):
            for j in range(num_rows):

                # If the jth nodes are not included
                # in the current subset
                if ((i & (1 << j)) == 0):
                    continue

                # Find K, neighbour of j
                # also present in the
                # current subset
                for k in range(num_rows):
                    if ((i & (1 << k)) != 0 and
                            adj_matrix[k][j] == 1 and
                                    j != k and
                        dp[k][i ^ (1 << j)]):

                        # Update dp[j][i]
                        dp[j][i] = True

                        break

        # Traverse the vertices
        for i in range(num_rows):
            # Hamiltonian Path exists
            if (dp[i][(1 << num_rows) - 1]):
                return True

        return False

    def reset_grid(self):
        """Reset all nodes to unvisited state and clear connections"""
        for node in self.nodes.values():
            node.visited = False
            node.neighbours = []
        self.path = []

    def get_unvisited_neighbors(self, node_idx: int) -> list[int]:
        """Get list of unvisited neighbor node indices"""
        current_node = self.nodes[node_idx]
        neighbors = []
        
        for other_idx, other_node in self.nodes.items():
            if (other_idx != node_idx and 
                not other_node.visited and 
                current_node.p.is_neighbour(other_node.p)):
                neighbors.append(other_idx)
        
        return neighbors

    def generate_random_hamiltonian_path(self, max_attempts: int = 100, verbose: bool = True) -> bool:
        """Generate a random Hamiltonian path using backtracking with retry logic"""
        start_time = time.time()
        
        if verbose:
            print(f"Starting Hamiltonian path generation for {self.w}x{self.h} grid...")
            print(f"Total nodes to visit: {len(self.nodes)}")
            print(f"Maximum attempts: {max_attempts}")
            print("-" * 50)
        
        for attempt in range(max_attempts):
            attempt_start_time = time.time()
            
            if verbose:
                print(f"Attempt {attempt + 1}/{max_attempts}:", end=" ")
            
            if self._try_generate_path(verbose=verbose):
                attempt_time = time.time() - attempt_start_time
                total_time = time.time() - start_time
                
                self.generation_stats['total_attempts'] = attempt + 1
                self.generation_stats['successful_attempts'] = 1
                self.generation_stats['total_time'] = total_time
                
                if verbose:
                    print(f"SUCCESS! (took {attempt_time:.3f}s)")
                    print(f"Total generation time: {total_time:.3f}s")
                    self._print_stats()
                
                return True
            else:
                attempt_time = time.time() - attempt_start_time
                if verbose:
                    print(f"Failed (took {attempt_time:.3f}s)")
        
        total_time = time.time() - start_time
        self.generation_stats['total_attempts'] = max_attempts
        self.generation_stats['successful_attempts'] = 0
        self.generation_stats['total_time'] = total_time
        
        if verbose:
            print("-" * 50)
            print(f"Failed to generate path after {max_attempts} attempts")
            print(f"Total time spent: {total_time:.3f}s")
            self._print_stats()
        
        return False
    
    def _try_generate_path(self, verbose: bool = False) -> bool:
        """Single attempt to generate a Hamiltonian path"""
        self.reset_grid()
        
        # Start from a random node
        start_idx = random.randint(0, len(self.nodes) - 1)
        
        # Reset per-attempt stats
        backtrack_count = 0
        max_depth = 0
        
        def backtrack(current_idx: int, path: list[int]) -> bool:
            nonlocal backtrack_count, max_depth
            
            self.nodes[current_idx].visited = True
            path.append(current_idx)
            backtrack_count += 1
            
            # Track maximum depth reached
            if len(path) > max_depth:
                max_depth = len(path)
            
            # Progress indicator for deep searches
            if verbose and backtrack_count % self.progress_frequency == 0:
                print(f"\n    Backtrack steps: {backtrack_count:,}, Max depth: {max_depth}/{len(self.nodes)}", end=" ")
            
            # If we've visited all nodes, we found a Hamiltonian path
            if len(path) == len(self.nodes):
                return True
            
            # Get unvisited neighbors and randomize the order
            neighbors = self.get_unvisited_neighbors(current_idx)
            random.shuffle(neighbors)
            
            # Try each neighbor
            for neighbor_idx in neighbors:
                if backtrack(neighbor_idx, path):
                    return True
            
            # Backtrack
            self.nodes[current_idx].visited = False
            path.pop()
            return False
        
        path = []
        success = backtrack(start_idx, path)
        
        # Update stats
        self.generation_stats['backtrack_steps'] += backtrack_count
        if max_depth > self.generation_stats['max_depth_reached']:
            self.generation_stats['max_depth_reached'] = max_depth
        
        if success:
            self.path = path
            self._build_path_connections()
            return True
        
        return False
    
    def validate_path(self) -> bool:
        """Validate that the current path is a valid Hamiltonian path"""
        if len(self.path) != len(self.nodes):
            return False
        
        # Check that all nodes are visited exactly once
        if len(set(self.path)) != len(self.path):
            return False
        
        # Check that consecutive nodes in path are neighbors
        for i in range(len(self.path) - 1):
            current_node = self.nodes[self.path[i]]
            next_node = self.nodes[self.path[i + 1]]
            
            if not current_node.p.is_neighbour(next_node.p):
                return False
        
        return True

    def _print_stats(self):
        """Print detailed statistics about the generation process"""
        stats = self.generation_stats
        print("\n" + "="*50)
        print("GENERATION STATISTICS")
        print("="*50)
        print(f"Total attempts: {stats['total_attempts']}")
        print(f"Successful attempts: {stats['successful_attempts']}")
        print(f"Success rate: {(stats['successful_attempts']/stats['total_attempts']*100):.1f}%" if stats['total_attempts'] > 0 else "Success rate: 0%")
        print(f"Total time: {stats['total_time']:.3f}s")
        print(f"Average time per attempt: {(stats['total_time']/stats['total_attempts']):.3f}s" if stats['total_attempts'] > 0 else "Average time per attempt: 0s")
        print(f"Total backtrack steps: {stats['backtrack_steps']:,}")
        print(f"Max depth reached: {stats['max_depth_reached']}/{len(self.nodes)} nodes")
        print(f"Completion rate: {(stats['max_depth_reached']/len(self.nodes)*100):.1f}%")
        print("="*50)

    def _build_path_connections(self):
        """Build connections between consecutive nodes in the path"""
        for i in range(len(self.path) - 1):
            current_idx = self.path[i]
            next_idx = self.path[i + 1]
            
            current_node = self.nodes[current_idx]
            next_node = self.nodes[next_idx]
            
            # Add bidirectional connection
            current_node.neighbours.append(next_node.p)
            next_node.neighbours.append(current_node.p)


def draw_node(fig: go.Figure, n: node):
    fig.add_shape(
            type="rect",
            x0=(n.p.x - 0.5),
            y0=(n.p.y - 0.5),
            x1=(n.p.x + 0.5),
            y1=(n.p.y + 0.5),
            line=dict(color="RoyalBlue", width=2),
        )

    for nb in n.neighbours:
        fig.add_shape(
            type="line",
            x0=(n.p.x),
            y0=(n.p.y),
            x1=(nb.x),
            y1=(nb.y),
            line=dict(color="Red", width=3),
        )

def draw_path_with_numbers(fig: go.Figure, grid: hamiltonian_grid):
    """Draw the path with numbered nodes showing the order"""
    x_coords = []
    y_coords = []
    text_labels = []
    
    for i, node_idx in enumerate(grid.path):
        node = grid.nodes[node_idx]
        x_coords.append(node.p.x)
        y_coords.append(node.p.y)
        text_labels.append(str(i + 1))
    
    # Add numbered markers for the path
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        marker=dict(
            size=20,
            color='yellow',
            line=dict(color='black', width=2)
        ),
        text=text_labels,
        textposition="middle center",
        textfont=dict(size=10, color='black'),
        name='Path Order',
        showlegend=False
    ))

class Config:
    """Configuration class for Hamiltonian path generator"""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = config_path
        self.grid_width = 6
        self.grid_height = 6
        self.max_attempts = 20
        self.timeout_seconds = 30
        self.verbose = True
        self.progress_frequency = 50000
        self.show_visualization = True
        self.window_width = 800
        self.window_height = 800
        
        self.load_config()
        self.validate_config()
    
    def load_config(self):
        """Load configuration from TOML file"""
        if not os.path.exists(self.config_path):
            print(f"Warning: Config file '{self.config_path}' not found. Using default values.")
            return
        
        try:
            with open(self.config_path, 'rb') as f:
                config_data = tomllib.load(f)
            
            # Load grid settings
            if 'grid' in config_data:
                grid_config = config_data['grid']
                self.grid_width = grid_config.get('width', self.grid_width)
                self.grid_height = grid_config.get('height', self.grid_height)
            
            # Load algorithm settings
            if 'algorithm' in config_data:
                algo_config = config_data['algorithm']
                self.max_attempts = algo_config.get('max_attempts', self.max_attempts)
                self.timeout_seconds = algo_config.get('timeout_seconds', self.timeout_seconds)
                self.verbose = algo_config.get('verbose', self.verbose)
                self.progress_frequency = algo_config.get('progress_update_frequency', self.progress_frequency)
            
            # Load visualization settings
            if 'visualization' in config_data:
                vis_config = config_data['visualization']
                self.show_visualization = vis_config.get('show_visualization', self.show_visualization)
                self.window_width = vis_config.get('window_width', self.window_width)
                self.window_height = vis_config.get('window_height', self.window_height)
            
            print(f"✓ Configuration loaded from '{self.config_path}'")
            
        except Exception as e:
            print(f"Error loading config file '{self.config_path}': {e}")
            print("Using default values.")
    
    def validate_config(self):
        """Validate configuration parameters"""
        errors = []
        
        # Validate grid dimensions
        if self.grid_width <= 0 or self.grid_width > 20:
            errors.append(f"Grid width must be between 1 and 20, got {self.grid_width}")
        if self.grid_height <= 0 or self.grid_height > 20:
            errors.append(f"Grid height must be between 1 and 20, got {self.grid_height}")
        
        # Validate algorithm parameters
        if self.max_attempts <= 0 or self.max_attempts > 1000:
            errors.append(f"Max attempts must be between 1 and 1000, got {self.max_attempts}")
        if self.timeout_seconds < 0 or self.timeout_seconds > 3600:
            errors.append(f"Timeout must be between 0 and 3600 seconds, got {self.timeout_seconds}")
        if self.progress_frequency <= 0:
            errors.append(f"Progress frequency must be positive, got {self.progress_frequency}")
        
        # Validate visualization parameters
        if self.window_width <= 0 or self.window_width > 2000:
            errors.append(f"Window width must be between 1 and 2000, got {self.window_width}")
        if self.window_height <= 0 or self.window_height > 2000:
            errors.append(f"Window height must be between 1 and 2000, got {self.window_height}")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        
        print("✓ Configuration validation passed")
    
    def print_config(self):
        """Print current configuration"""
        print(f"Grid size: {self.grid_width}x{self.grid_height}")
        print(f"Max attempts: {self.max_attempts}")
        print(f"Timeout: {self.timeout_seconds}s")
        print(f"Verbose: {self.verbose}")
        print(f"Progress frequency: {self.progress_frequency:,}")
        print(f"Show visualization: {self.show_visualization}")
        print(f"Window size: {self.window_width}x{self.window_height}")

def main() -> int:

    # Load configuration
    try:
        config = Config()
    except SystemExit:
        return 1
    except Exception as e:
        print(f"Error initializing configuration: {e}")
        return 1

    print("="*60)
    print("HAMILTONIAN PATH GENERATOR")
    print("="*60)
    config.print_config()
    print(f"Total nodes: {config.grid_width * config.grid_height}")
    print(f"Search space complexity: O({config.grid_width * config.grid_height}!)")
    print("="*60)

    # Initialize grid with config parameters
    grid = hamiltonian_grid(config.grid_width, config.grid_height, config.progress_frequency)

    # Set up timeout if specified
    def timeout_handler(signum, frame):
        raise TimeoutError("Generation timeout reached")
    
    if config.timeout_seconds > 0:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(config.timeout_seconds)

    try:
        # Generate a random Hamiltonian path with config parameters
        if grid.generate_random_hamiltonian_path(max_attempts=config.max_attempts, verbose=config.verbose):
            if config.timeout_seconds > 0:
                signal.alarm(0)  # Cancel timeout
            
            print(f"\n✓ Generated Hamiltonian path with {len(grid.path)} nodes")
            
            # Validate the generated path
            print("\nValidating generated path...")
            if grid.validate_path():
                print("✓ Path validation: PASSED")
            else:
                print("✗ Path validation: FAILED")
                return 1
            
            # Show visualization if enabled
            if config.show_visualization:
                print("\nGenerating visualization...")
                fig = go.Figure()

                for n in grid.nodes.values():
                    draw_node(fig, n)
                
                # Add numbered path visualization
                draw_path_with_numbers(fig, grid)

                fig.update_yaxes(scaleanchor="x", scaleratio=1, range=[0, config.grid_height])
                fig.update_xaxes(scaleratio=1, range=[0, config.grid_width])

                fig.update_layout(
                    autosize=False,
                    width=config.window_width,
                    height=config.window_height,
                    showlegend=False,
                    margin=go.layout.Margin(l=25, r=25, b=25, t=25, pad=10),
                    xaxis=dict(visible=False, fixedrange=True),
                    yaxis=dict(visible=False, fixedrange=True),
                    title=f"Random Hamiltonian Path in {config.grid_width}x{config.grid_height} Grid"
                )
                
                print("Opening visualization in browser...")
                fig.show()
                print("✓ Visualization complete!")
            else:
                print("Visualization disabled in configuration.")
                
        else:
            if config.timeout_seconds > 0:
                signal.alarm(0)  # Cancel timeout
            print("\n✗ Failed to generate a Hamiltonian path!")
            return 1

    except TimeoutError:
        print(f"\n✗ Generation timeout reached ({config.timeout_seconds}s)")
        return 1
    except KeyboardInterrupt:
        print("\n✗ Generation interrupted by user")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())  # next section explains the use of sys.exit
