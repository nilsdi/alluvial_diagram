"""
Refactoring the old alluvial diagram code. The classes beneath should handle
the plotting of the lines.
Started 12.02.2026 by Nils Dittrich
"""

import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy


class LineSegment:

    def __init__(
        self, start: list[float], finish: list[float], name: str, color: list[float]
    ) -> None:
        """
        Args:
            start (list[float]): Starting point of the line [x, y].
            finish (list[float]): Ending point of the line [x, y].
            name (str): Name of the line segment.
            color (list[float]): Color of the line in RGB or RGBA format.
        """
        self.start = start
        self.finish = finish
        self.name = name
        self.color = color

    def __repr__(self) -> str:
        return f"linesegment of {self.name} from {self.start} to {self.finish}"

    def get_line_points(self, num: int = 10) -> list[list[float]]:
        """
        Returns all points as a vector of x and y coords so the line can be ddrawn with plt.plot.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class StraightLine(LineSegment):

    def __init__(
        self,
        start: list[float],
        finish: list[float],
        name: str,
        color: list[float] = None,
    ) -> None:
        """
        Args:
            start (list[float]): Starting point of the line [x, y].
            finish (list[float]): Ending point of the line [x, y].
            name (str): Name of the line segment.
            color (list[float]): Color of the line in RGB or RGBA format.
        """
        if finish[0] < start[0]:
            start = deepcopy(finish)
            finish = deepcopy(start)
        super().__init__(start, finish, name, color)

    def __repr__(self) -> str:
        return f"straightline of {self.name} from {self.start} to {self.finish}"

    def get_line_points(self, num: int = 10) -> list[list[float]]:
        """
        Returns all points as a vector of x and y coords so the line can be ddrawn with plt.plot.
        Args:
            num (int): Number of points to generate along the line.
        Returns:
            list[list[float]]: Two lists containing x and y coordinates.
        """
        actual_num = int(abs((self.finish[0] - self.start[0])) * num)

        x_coords = np.linspace(self.start[0], self.finish[0], num=actual_num)
        y_coords = np.linspace(self.start[1], self.finish[1], num=actual_num)
        return list(x_coords), list(y_coords)

    def plot(
        self, ax: plt.Axes, num: int = 10, alpha: float = 1, linewidth: float = 1
    ) -> None:
        """ "
        Plots the straight line on the given Axes.
        Args:
            ax (plt.Axes): The matplotlib Axes to plot on.
            num (int): Number of points to generate along the line.
            alpha (float): Transparency of the line.
            linewidth (float): Width of the line.
        Returns:
            None
        """
        x_coords, y_coords = self.get_line_points(num=num)
        ax.plot(x_coords, y_coords, color=self.color, alpha=alpha, linewidth=linewidth)
        return


class CurvedLine(LineSegment):
    """
    A cuved line in the style of a cubic Bezier curve, with two control points in the middle.
    The control points are determined by the start and finish points, so that the curve
    is smooth and goes through the start and finish points.
    """

    def __init__(
        self,
        start: list[float],
        finish: list[float],
        name: str,
        color: list[float] = None,
    ) -> None:
        """
        Args:
            start (list[float]): Starting point of the line [x, y].
            finish (list[float]): Ending point of the line [x, y].
            name (str): Name of the line segment.
            color (list[float], optional): Color of the line in RGB or RGBA format. Defaults to None.
        """
        super().__init__(start, finish, name, color)

    def __repr__(self) -> str:
        return f"curvedline of {self.name} from {self.start} to {self.finish}"

    def get_line_points(self, num: int = 100) -> list[list[float]]:
        """
        Returns all points as a vector of x and y coords so the line can be ddrawn with plt.plot.
        Args:
            num (int): Number of points to generate along the line.
        Returns:
            list[list[float]]: Two lists containing x and y coordinates.
        """
        if self.finish[0] < self.start[0]:
            start = deepcopy(self.finish)
            self.finish = deepcopy(self.start)
            self.start = deepcopy(start)
        actual_num = int((abs(self.finish[0] - self.start[0])) * num)
        t = np.linspace(0, 1, num=actual_num)  # Adjust num for curve smoothness
        control1 = [self.start[0] + (self.finish[0] - self.start[0]) / 2, self.start[1]]
        control2 = [
            self.start[0] + (self.finish[0] - self.start[0]) / 2,
            self.finish[1],
        ]
        coords_x = (
            (1 - t) ** 3 * self.start[0]
            + 3 * (1 - t) ** 2 * t * control1[0]
            + 3 * (1 - t) * t**2 * control2[0]
            + t**3 * self.finish[0]
        )
        coords_y = (
            (1 - t) ** 3 * self.start[1]
            + 3 * (1 - t) ** 2 * t * control1[1]
            + 3 * (1 - t) * t**2 * control2[1]
            + t**3 * self.finish[1]
        )
        return list(coords_x), list(coords_y)

    def plot(
        self, ax: plt.Axes, num: int = 100, alpha: float = 1, linewidth: float = 1
    ) -> None:
        """ "
        Plots the curved line on the given Axes.
        Args:
            ax (plt.Axes): The matplotlib Axes to plot on.
            num (int): Number of points to generate along the line.
            alpha (float): Transparency of the line.
            linewidth (float): Width of the line.
        Returns:
            None
        """
        coords_x, coords_y = self.get_line_points(num=num)
        ax.plot(coords_x, coords_y, color=self.color, alpha=alpha, linewidth=linewidth)
        return


class AgglutinatedLine(LineSegment):
    """
    This class is used to draw a line that is made up of multiple line segments.
    """

    def __init__(
        self,
        name: str,
        color: list[float] = None,
        num: int = 100,
        segments: list[LineSegment] = None,
    ) -> None:
        """
        No start and finish here - we will add all the waypoints from the other line segments.
        """
        self.name = name
        self.color = color
        self.num = num
        self.segments = segments if segments is not None else []
        return

    def __repr__(self) -> str:
        return f"AgglutinatedLine named {self.name} with segments: {self.segments}"

    def get_line_points(self, num: int = None) -> list[list[float]]:
        """
        Returns all points as a vector of x and y coords so the line can be ddrawn with plt.plot.
        Args:
            num (int): Number of points to generate along each line segment.
        Returns:
            list[list[float]]: Two lists containing x and y coordinates.
        """
        x_coords = []
        y_coords = []
        for line_segment in self.segments:
            segment_x, segment_y = line_segment.get_line_points(num=self.num)
            x_coords.extend(segment_x)
            y_coords.extend(segment_y)
        # sort them by x_coords

        x_coords, y_coords = zip(*sorted(set(zip(x_coords, y_coords))))
        return list(x_coords), list(y_coords)

    def plot(
        self, ax: plt.Axes, num: float = 100, alpha: float = 1, linewidth: float = 1
    ) -> None:
        """ "
        Plots the agglutinated line on the given Axes.
        Args:
            ax (plt.Axes): The matplotlib Axes to plot on.
            num (int): Number of points to generate along each line segment.
            alpha (float): Transparency of the line.
            linewidth (float): Width of the line.
        Returns:
            None
        """
        x_coords, y_coords = self.get_line_points(num=num)
        ax.plot(
            x_coords,
            y_coords,
            color=self.color,
            alpha=alpha,
            linewidth=linewidth,
        )
        return
