from __future__ import annotations
import sys
import plotly.graph_objects as go

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

    def __init__(self, w: int, h: int):
        if w <= 0 or h <= 0:
            print("cannot init hamiltonian grid: dims incorrect w={}, h={}".format(w, h))
            return

        self.w = w
        self.h = h

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


    def Hamiltonian_path(self) -> list:

        adj_matrix = self.as_adjacency_matrix()
        print("adj_matrix: {}".format(adj_matrix))

        num_rows = len(adj_matrix)

        result_path = []

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

                # If the jth nodes is included
                # in the current subset
                if ((i & (1 << j)) != 0):

                    # Find K, neighbour of j
                    # also present in the
                    # current subset
                    for k in range(num_rows):
                        if ((i & (1 << k)) != 0 and
                                adj_matrix[k][j] == 1 and
                                        j != k and
                            dp[k][i ^ (1 << j)]):

                            # Update dp[j][i]
                            # to true
                            dp[j][i] = True

                            result_path.append(k*self.w + j)

                            break

        # Traverse the vertices
        for i in range(num_rows):
            # Hamiltonian Path exists
            if (dp[i][(1 << num_rows) - 1]):
                return result_path

        # Otherwise, return false
        return []


def main() -> int:

    w = 8
    h = 8

    grid = hamiltonian_grid(w, h)

    p = grid.Hamiltonian_path()

    nodes = grid.nodes.values()

    if p != []:
        fig = go.Figure()

        for n in nodes:
            # Add shapes

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
                    line=dict(color="Red", width=2),
                )

        fig.update_yaxes(scaleanchor="x", scaleratio=1, range=[0, h])
        fig.update_xaxes(scaleratio=1, range=[0, w])

        fig.update_layout(
            autosize=False,
            width=800,
            height=800,
            showlegend=False,
            margin=go.layout.Margin(l=25, r=25, b=25, t=25, pad=10),
            xaxis=dict(visible=False, fixedrange=True),
            yaxis=dict(visible=False, fixedrange=True),
        )
        fig.show()
    else:
        print("hamiltonian path does not exist!")

    return 0


if __name__ == "__main__":
    sys.exit(main())  # next section explains the use of sys.exit
