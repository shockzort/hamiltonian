from __future__ import annotations
import sys
import plotly.graph_objects as go


class discrete_point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def is_neighbour(self, other: discrete_point) -> bool:
        return (abs(self.x - other.x) == 1 and abs(self.y - other.y) == 0) or (
            abs(self.x - other.x) == 0 and abs(self.y - other.y) == 1
        )


class node:
    p: discrete_point
    neighbours: list[discrete_point]
    free_neighbours: list[discrete_point]

    def __init__(self, p: discrete_point):
        self.p = p
        self.neighbours = []
        self.free_neighbours = []

    def connected(self) -> bool:
        return len(self.neighbours) == 2

    def end(self) -> bool:
        return len(self.neighbours) == 1 and len(self.free_neighbours) == 0

    def connect(self, other: node) -> bool:
        if self.connected() or other.connected():
            return False

        if not self.p.is_neighbour(other.p):
            return False

        self.neighbours.append(other.p)
        if other.p in self.free_neighbours:
            self.free_neighbours.remove(other.p)

        other.neighbours.append(self.p)
        if self.p in other.free_neighbours:
            other.free_neighbours.remove(self.p)

        return True


def main() -> int:
    nodes = []

    w = 8
    h = 8

    for x in range(w):
        for y in range(h):
            nodes.append(node(discrete_point(x + 0.5, y + 0.5)))

    def pick_node(nodes: list[node]):
        for n in nodes:
            if not n.connected():
                return n

        return None

    for n in nodes:
        sel = pick_node(nodes)
        if sel is not None:
            n.connect(sel)
        else:
            print("all connected")
            break

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
    return 0


if __name__ == "__main__":
    sys.exit(main())  # next section explains the use of sys.exit
