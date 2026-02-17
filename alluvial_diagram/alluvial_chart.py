# %%
from matplotlib import colormaps
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

from alluvial_diagram.alluvial_lines import StraightLine, CurvedLine, AgglutinatedLine
from alluvial_diagram.alluvial_nodes import Node, SubNode

# Set the resolution of the figures
plt.rcParams["figure.dpi"] = 600  # Change this value to adjust the resolution
plt.rcParams["savefig.dpi"] = 600  # Change this value to adjust the resolution


class AlluvialChart:
    """
    Class to create an alluvial chart.
    Note that througout the chart we determine positions and sizes based on a unit
    grid (0-1 in both x and y direction).
    """

    def __init__(
        self,
        line_data: list[dict],
        node_data: dict[str, dict[str, dict]],
        sorted_category: str = None,
        line_color_mode: str = "random",
        plot_id:bool = False,
        nodes_x_share: float = 0.3,
        node_min_y_extend: float = 0.01,
        node_label_position: str = "bottom",
        node_separation: float = 0.05,
        subnode_fontsize: float = 8,
        straight_line_outside_node: float = 0.05,
        extend_lines_into_outside_nodes: bool = False,
        figsize: tuple[float, float] = (10, 6),
        dev_mode: bool = False,
    ) -> None:
        """
        Args:
            line_data (list[dict]): List of dictionaries containing line segment data.
                each dict should have keys following the node categories, with values specifying the node (by label).
            nodes: dict[str, dict[str, dict]]: Dictionary containing node data keyed by category.
                Each category contains a dict keyed by node label, optionally keying in edgecolor, facecolor, opacity.
            sorted_category (str): The node category at which the lines are sorted (top to bottom) as in line_data.
                Defaults to None, in which case the lines are started with the first category and sorted to fit there.
            line_color_mode (str): Mode for coloring the lines ("random", "category", etc.).
            plot_id (bool): If True, plots the line IDs.
            nodes_x_share (float): The share of the x axis that is taken by the nodes. The rest is for the lines.
            node_min_y_extend (float): The minimum extend of a node in y independent of lines
            node_label_position (str): Position of the node labels ("bottom" or "top").
            straight_line_outside_node (float): The distance of straight lines outside the nodes in y direction
            extend_lines_into_outside_nodes (bool): If True, extends lines into the outside nodes.
            figsize (tuple[float, float]): Size of the figure (width, height).
            dev_mode (bool): If True, shows grid and axes for easier development.
        """
        self.line_data = line_data
        self.node_data = node_data
        self.sorted_category = sorted_category
        self.line_color_mode = line_color_mode
        self.plot_id = plot_id
        self.nodes_x_share = nodes_x_share
        self.node_min_y_extend = node_min_y_extend
        self.node_label_position = node_label_position
        self.node_separation = node_separation
        self.subnode_fontsize = subnode_fontsize
        self.straight_line_outside_node = straight_line_outside_node
        self.extend_lines_into_outside_nodes = extend_lines_into_outside_nodes
        self.figsize = figsize
        self.dev_mode = dev_mode
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

        self.make_nodes()
        self.make_lines()
        self.make_subnodes()
        self.set_line_color()
        self.plot()
        self.show_figure()

    def make_nodes(self) -> None:
        """
        Create Node objects based on the provided node data.
        Also takes care of determining the position and extend of the nodes based on the line data.
        """
        # x spacing between categories
        x_spacing = (1 - self.nodes_x_share) / (len(self.node_data) - 1)
        node_width = self.nodes_x_share / len(self.node_data)
        self.node_details = {}
        for i, (category, nodes) in enumerate(self.node_data.items()):
            self.node_details[category] = {
                node: {"x": i * (node_width + x_spacing), "width": node_width}
                for node in nodes
            }

        # y spacing - determine position and extend in y dimenstion for nodes in each category
        for category, nodes in self.node_data.items():
            # count how many lines go through each node in this category
            node_counts = {node: 0 for node in nodes}
            for line_id, line in self.line_data.items():
                node_counts[line[category]["node"]] += 1

            # determine the y position and extend of each node based on the counts
            total_count = sum(node_counts.values())
            y_position = 1
            # the position of the nodes is determinde top to bottom, and each node gets
            # a minium extend + some buffer
            y_space_taken_by_default = (
                len(nodes) * self.node_min_y_extend
                + (len(nodes) - 1) * self.node_separation
            )
            y_space_distributed = 1 - y_space_taken_by_default
            for node, count in node_counts.items():
                height = (
                    self.node_min_y_extend + count / total_count * y_space_distributed
                    if total_count > 0
                    else 0
                )
                self.node_details[category][node]["y"] = y_position - height
                self.node_details[category][node]["height"] = height
                y_position -= height + self.node_separation

        # finally just make the nodes
        self.nodes = {}
        for category, nodes in self.node_details.items():
            category_nodes = []
            for node, details in nodes.items():
                node_info = self.node_data[category][node]
                category_nodes.append(
                    Node(
                        position=[details["x"], details["y"]],
                        extend=[details["width"], details["height"]],
                        label=node,
                        edgecolor=node_info.get("edgecolor", "black"),
                        facecolor=node_info.get("facecolor", "slategrey"),
                        opacity=node_info.get("opacity", 1),
                    )
                )
            self.nodes[category] = category_nodes
        # print(self.node_details)
        # print(self.nodes)
        return

    def make_subnodes(self) -> None:
        for category, nodes_data, in self.node_data.items():
            nodes = self.nodes[category]
            for node,  node_data in zip(nodes, nodes_data.values()):
                if node.label and "subnodes" in node_data.keys():
                    self.place_subnodes(category, node_data, node)
        return
    
    def place_subnodes(self, category:str, node_data:dict, node:Node)-> None:
        subnode_rel_size = 0.9
        subnode_x = node.position[0] + node.extend[0] * (1 - subnode_rel_size) / 2
        subnode_width = node.extend[0] * subnode_rel_size
        subnodes = []
        self.subnodes_data = {subnode: self.node_data[category][node.label]["subnodes"][subnode] for subnode in node_data["subnodes"]}
        for subnode, subnode_data in self.subnodes_data.items():
            subnode_line_ys = []
            for line_id, line_data in self.line_data.items():
                if "subnode" in line_data[category].keys():
                    if line_data[category]["node"] == node.label and line_data[category]["subnode"] == subnode:
                        subnode_line_ys.append(self.line_y_positions[category][line_id])
            subnode_line_ys.sort()
            self.subnodes_data[subnode]["y"] = subnode_line_ys[0] - self.line_spacing[category] * (subnode_rel_size) / 2 if subnode_line_ys else None
            if len(subnode_line_ys) > 1:
                self.subnodes_data[subnode]["height"] = subnode_line_ys[-1] - subnode_line_ys[0] + self.line_spacing[category] * subnode_rel_size
            elif len(subnode_line_ys) == 1:
                self.subnodes_data[subnode]["height"] = self.line_spacing[category]*subnode_rel_size

            if self.subnodes_data[subnode].get("height"):
                subnodes.append(
                    SubNode(
                        position=[subnode_x, self.subnodes_data[subnode]["y"]],
                        extend=[subnode_width, self.subnodes_data[subnode]["height"]],
                        label=subnode,
                        label_fontsize=self.subnode_fontsize,
                        edgecolor=self.subnodes_data[subnode].get("edgecolor", "black"),
                        facecolor=self.subnodes_data[subnode].get("facecolor", "slategrey"),
                        opacity=self.subnodes_data[subnode].get("opacity", 1),
                    )
                )
        #node_object = next((n for n in self.nodes[category] if n.label == node_data["node"]), None)
        node.subnodes = subnodes
        
        return
    
    def make_lines(self) -> None:
        """
        Create line objects based on the provided line data and the created nodes.
        """
        self.line_segments = {l_id: [] for l_id in self.line_data.keys()}
        self.line_y_positions = {}
        self.line_spacing = {}

        # starting from the sorted category, go left (previous categories) and then right
        # (following categories) and create line segments between the nodes for each line in line_data

        # establish starting position of lines:
        start_category = (
            self.sorted_category
            if self.sorted_category
            else list(self.node_data.keys())[0]
        )
        left_node_x, right_node_x = self._get_line_x_position(start_category)
        start_node_y_positions = self._get_line_y_positions(
            {
                i: {start_category: line[start_category]["node"]}
                for i, line in self.line_data.items()
                if line[start_category]
            }
        )
        self.line_y_positions[start_category] = start_node_y_positions
        for line_id, line_y in start_node_y_positions.items():
            self.line_segments[line_id].append(
                StraightLine(
                    start=[left_node_x, deepcopy(line_y)],
                    finish=[right_node_x, deepcopy(line_y)],
                    name=start_category
                    + "_"
                    + self.line_data[line_id][start_category]["node"]
                    + "_"
                    + str(line_id),
                )
            )
        # going to the left of the sorted category:
        left_categories = list(self.node_data.keys())[
            : list(self.node_data.keys()).index(start_category)
        ]
        left_categories.reverse()  # we want to go from the sorted category to the leftmost category
        # print(f"left categories: {left_categories}")
        self.extend_line_segments(
            starting_x=left_node_x,
            y_positions=start_node_y_positions,
            categories=left_categories,
            direction="left",
        )
        # now going to the right of the sorted category:
        right_categories = list(self.node_data.keys())[
            list(self.node_data.keys()).index(start_category) + 1 :
        ]
        # print(f"right categories: {right_categories}")
        self.extend_line_segments(
            starting_x=right_node_x,
            y_positions=start_node_y_positions,
            categories=right_categories,
            direction="right",
        )
        # for line_id, segments in self.line_segments.items():
        #     print(f"line {line_id} segments: {segments}")
        self.lines = {
            line_id: AgglutinatedLine(name=line_id, color="k", segments=segments)
            for line_id, segments in self.line_segments.items()
        }

        return

    def _get_line_y_positions(self, ordered_line_data: dict[dict]) -> dict:
        """
        Get the next y position of a line segment based on a limited set of ordered line data.
        The y position is determined by the position of the node the line goes to, and
        its inital order.
        Args:
            ordered_line_data (dict[dict]): A dict of line segment ids and their target node category and target node.
        Returns:
            dict: A dict of line segment ids and their y position.
        """
        category = list(list(ordered_line_data.values())[0].keys())[0]
        # first we determine the central line spacing:
        total_node_space = sum(
            [node["height"] for node in self.node_details[category].values()]
        )
        total_line_space = (
            total_node_space * 0.9
        )  # we use only 90% of the node space for lines, the rest is buffer
        line_spacing = total_line_space / len(ordered_line_data)
        self.line_spacing[category] = line_spacing
        line_y_positions = {}
        for node, node_details in self.node_details[category].items():
            node_y_top = node_details["y"] + node_details["height"]
            tot_lines = sum(
                [1 for line in ordered_line_data.values() if line[category] == node]
            )
            line_space = line_spacing * tot_lines
            offset_borders = (node_details["height"] - line_space) / 2
            line_y = (
                node_y_top - offset_borders - line_spacing / 2
            )  # offset from the top of the node to center the lines
            if "subnodes" not in self.node_data[category][node].keys():
                for line_id, line_target in ordered_line_data.items():
                    target_node = line_target[category]
                    if node == target_node:
                        line_y_positions[line_id] = line_y
                        line_y -= line_spacing
            else:
                for subnode in self.node_data[category][node]["subnodes"]:
                    for line_id, line_target in ordered_line_data.items():
                        target_node = line_target[category]
                        if "subnode" in self.line_data[line_id][category].keys():
                            target_subnode = self.line_data[line_id][category]["subnode"]
                            if node == target_node and subnode == target_subnode:
                                line_y_positions[line_id] = line_y
                                line_y -= line_spacing
        return line_y_positions

    def _get_line_x_position(self, category: str) -> list:
        """
        Get the x positions of the lines to the left and right of the given category.
        For the nodes at the ends, we limit so the lines stay within the figure, for the ones
        in the center, we detach them a little from the nodes to make it look nicer.
        The x position is determined by the position and width of the nodes in that category.
        Args:
            category (str): The category the line segment is currently at.
        Returns:
            list: The x positions of the left and right edges of the line segment.
        """
        left_node_x = self.node_details[category][
            list(self.node_details[category].keys())[0]
        ]["x"]
        right_node_x = (
            self.node_details[category][list(self.node_details[category].keys())[0]][
                "x"
            ]
            + self.node_details[category][list(self.node_details[category].keys())[0]][
                "width"
            ]
        )
        if (
            category == list(self.node_data.keys())[0]
        ):  # leftmost category - only go to the middle (unless id is plotted.)
            if self.plot_id:
                left_node_x -= self.straight_line_outside_node
            else:
                if self.extend_lines_into_outside_nodes:
                    left_node_x = (left_node_x + right_node_x) / 2
                else:
                    left_node_x = right_node_x
        elif (
            category == list(self.node_data.keys())[-1]
        ):  # rightmost category - only go to the middle
            if self.extend_lines_into_outside_nodes:
                right_node_x = (left_node_x + right_node_x) / 2
            else:
                right_node_x = left_node_x
        else:  # for the middle categories, we detach a little from the nodes to make it look nicer
            left_node_x -= self.straight_line_outside_node / 2
            right_node_x += self.straight_line_outside_node / 2
        return [left_node_x, right_node_x]

    def extend_line_segments(
        self,
        starting_x: float,
        y_positions: dict,
        categories: list[str],
        direction: str,
    ) -> None:

        for category in categories:
            left_node_x_new, right_node_x_new = self._get_line_x_position(category)
            if direction == "left":
                connection_x = right_node_x_new
                new_starting_x = left_node_x_new
            elif direction == "right":
                connection_x = left_node_x_new
                new_starting_x = right_node_x_new
            # prepare the ordered line data dict:
            ordered_line_data = {
                line_id: {category: self.line_data[line_id][category]["node"]}
                for line_id in y_positions.keys()  # keeping the orer from the previous category
            }
            y_positions_new = self._get_line_y_positions(ordered_line_data)
            self.line_y_positions[category] = y_positions_new
            for line_id, line_y in y_positions_new.items():
                self.line_segments[line_id].append(
                    StraightLine(
                        start=[left_node_x_new, line_y],
                        finish=[right_node_x_new, line_y],
                        name=category
                        + "_"
                        + self.line_data[line_id][category]["node"]
                        + "_"
                        + str(line_id),
                    )
                )
                self.line_segments[line_id].append(
                    CurvedLine(
                        start=[
                            connection_x,
                            line_y,
                        ],  # right of the new node, y of the line id for the new category
                        finish=[
                            starting_x,
                            y_positions[line_id],
                        ],  # left of the past node, y of the line id for the past category
                        name=category
                        + "_"
                        + self.line_data[line_id][category]["node"]
                        + "_"
                        + str(line_id),
                    )
                )
            starting_x = new_starting_x
            y_positions = y_positions_new
        if category == list(self.node_data.keys())[0] and self.plot_id:
            self.plot_ids(y_positions, starting_x)
        return

    def plot_ids(self, y_positions_left:dict, left_node_x:float)-> None:
        # get the x_position for the line ids to the left of the leftmost category
        left_category = list(self.node_data.keys())[0]
        second_left_category = list(self.node_data.keys())[1]
        id_x_position = 0 - (
            self.node_details[second_left_category][
                list(self.node_details[second_left_category].keys())[0]
            ]["x"] - 
            self.node_details[left_category][list(self.node_details[left_category].keys())[0]][
                "x"
            ]
            - self.node_details[left_category][list(self.node_details[left_category].keys())[0]][
                "width"
            ]
            )/2
        # get the y_positions for each of the line_ids:
        line_id_space = 1 / len(self.line_data)
        y_position = 1 - line_id_space / 2
        for line_id, line_y in y_positions_left.items():
            id_y = y_position
            self.line_segments[line_id].append(
                    CurvedLine(
                        start=[
                            id_x_position,
                            id_y,
                        ],  # right of the new node, y of the line id for the new category
                        finish=[
                            left_node_x,
                            line_y,
                        ],  # left of the past node, y of the line id for the past category
                        name="id_"
                        + str(line_id),
                    )
                )
            self.ax.text(
                id_x_position - 0.01,
                id_y,
                str(line_id),
                ha="right",
                va="center",
                fontsize=6,
            )
            y_position -= line_id_space
        return

    def set_line_color(self, cmap_name: str = "tab20") -> None:
        """
        Set the color of the lines based on the specified mode.
        Args:
            cmap_name (str): The name of the colormap to use when mode is "cat_cmap". Defaults to "tab20".
        """
        if self.line_color_mode == "cat_cmap":
            cmap = colormaps[cmap_name]
            num_categories = len(self.nodes)
            category_colors = {
                category: cmap(i / num_categories)
                for i, category in enumerate(self.nodes)
            }
            for line in self.lines.values():
                category = line.name.split("_")[
                    0
                ]  # Assuming line names are formatted as "category_label"
                line.color = category_colors.get(
                    category, (0.5, 0.5, 0.5)
                )  # Default to grey if category not found
        elif self.line_color_mode == "random":
            for line in self.lines.values():
                line.color = np.random.rand(3)  # Random RGB color
        elif self.line_color_mode == "sorted_category":
            # lines get the color of the node they are sorted by in the sorted category
            for line_id, line in self.lines.items():
                category = self.sorted_category
                node_label = self.line_data[line_id][category]["node"]
                category_nodes = self.nodes[category]
                node = next((n for n in category_nodes if n.label == node_label), None)
                line_subnode = self.line_data[line_id][category]["subnode"] if "subnode" in self.line_data[line_id][category] else None
                node_color = node.get_color(subnode=line_subnode) 
                line.color = node_color
        else:
            raise ValueError(
                "Invalid mode for setting line colors. Choose 'cat_cmap', 'random', or 'sorted_category'."
            )
        return

    def plot(self) -> None:
        """Plot the alluvial diagram based on the line and node data."""
        # plot nodes
        for category, nodes in self.nodes.items():
            for node in nodes:
                node.plot(self.ax)
                node.print_label(ax=self.ax, label_position=self.node_label_position)
        # print category labels:
        for category, nodes in self.nodes.items():
            self.ax.text(
                nodes[0].position[0] + nodes[0].extend[0] / 2,
                1.01,
                category,
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
            )
        # plot lines
        for line in self.lines.values():
            #print(f"plotting line {line.name} with segments: {line.segments} and color {line.color}")
            line.plot(self.ax)

        return

    def show_figure(self) -> None:
        """Show the figure"""

        self.fig.tight_layout()
        if not self.dev_mode:
            plt.axis("off")
        else:
            # tight grid for development with lines every 0.1
            self.ax.set_xticks([i / 10 for i in range(0, 11)])
            self.ax.set_yticks([i / 10 for i in range(0, 11)])
            self.ax.grid(True)

        x_min = 0
        if self.plot_id:
            all_x = []
            for line in self.line_segments.values():
                for segment in line:
                    all_x.extend([segment.start[0], segment.finish[0]])
            if all_x:
                x_min = min(all_x)
            # small padding so labels/curves are not cut at the frame edge
            x_min -= 0.01

        self.ax.set_xlim(x_min, 1)
        self.ax.set_ylim(0, 1)
        plt.show()
        return


if __name__ == "__main__":
    # example data
    line_data = {
        1: {"A": {"node": "a1"}, "B": {"node": "b1", "subnode": "b1.1"}, "C": {"node": "c1"}},
        2: {"A": {"node": "a1"}, "B": {"node": "b2"}, "C": {"node": "c2"}},
        3: {"A": {"node": "a2"}, "B": {"node": "b1", "subnode": "b1.2"}, "C": {"node": "c2"}},
        4: {"A": {"node": "a2"}, "B": {"node": "b2"}, "C": {"node": "c1"}},
        5: {"A": {"node": "a2"}, "B": {"node": "b1", "subnode": "b1.1"}, "C": {"node": "c3"}},
        6: {"A": {"node": "a3"}, "B": {"node": "b2"}, "C": {"node": "c3"}},
    }
    nodes = {
        "A": {
            "a1": {"facecolor": "red"},
            "a2": {"facecolor": "blue"},
            "a3": {"facecolor": "grey"},
        },
        "B": {"b1": {"facecolor": "gainsboro", "subnodes":{
                "b1.1": {"facecolor": "forestgreen"},
                "b1.2": {"facecolor": "limegreen"},
        }}, "b2": {"facecolor": "orange"}},
        "C": {
            "c1": {"facecolor": "purple"},
            "c2": {"facecolor": "cyan"},
            "c3": {"facecolor": "magenta"},
        },
    }
    chart = AlluvialChart(
        line_data,
        nodes,
        sorted_category="B",
        plot_id=True,
        line_color_mode="sorted_category",
        dev_mode=False,
    )

# %%
