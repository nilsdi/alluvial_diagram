import matplotlib.pyplot as plt


class Node:

    def __init__(
        self,
        position: list[float] = [0, 0],
        extend: list[float] = [1, 1],
        label: str = "",
        edgecolor: str = "none",
        facecolor: str = "slategrey",
        opacity: float = 1,
    ) -> None:
        """
        Args:
            position (list[float]): The position (bottom left) of the node.
            extend (list[float]): The size (width and height) of the node.
            label (str): The label of the node.
            edgecolor (str): The color of the node's edge.
            facecolor (str): The color of the node's face.
            opacity (float): The opacity of the node (0 to 1).
        """
        self.position = position
        self.extend = extend
        self.label = label
        self.edgecolor = edgecolor
        self.facecolor = facecolor
        self.opacity = opacity

    def __repr__(self) -> str:
        return f"Node with label {self.label} at position {self.position} with extend {self.extend}"

    def plot(
        self,
        ax: plt.Axes,
    ) -> None:
        ax.add_patch(
            plt.Rectangle(
                self.position,
                self.extend[0],
                self.extend[1],
                edgecolor=self.edgecolor,
                facecolor=self.facecolor,
                alpha=self.opacity,
            )
        )
        return

    def print_label(
        self, ax: plt.Axes, label: list[str] = None, label_position: str = "bottom"
    ):
        if label is None:
            label = self.label
        if label_position == "bottom":
            y_loc = self.position[1] - 0.01
            va = "top"
        elif label_position == "center":
            y_loc = self.position[1] + self.extend[1] / 2
            va = "center"
        elif label_position == "top":
            y_loc = self.position[1] + self.extend[1] + 0.01
            va = "bottom"
        else:
            raise ValueError("label_position must be 'bottom', 'center', or 'top'")

        ax.text(
            self.position[0] + self.extend[0] / 2,
            y_loc,
            label,
            ha="center",
            va=va,
        )

        return
