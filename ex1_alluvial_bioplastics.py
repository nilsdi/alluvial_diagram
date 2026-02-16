# %%
import pandas as pd

from alluvial_diagram import AlluvialDiagram

data_path = "Mapping_final.xlsx"

data = pd.read_excel(
    data_path, sheet_name="Visualization", header=1, nrows=61, usecols="C:H"
)
print(data.head())

# %%
nodes = {
    "Main conversion pathway": {
        cat: {"facecolor": "lightgrey"}
        for cat in data["Main conversion pathway"].dropna().unique().tolist()
    },
    "Feedstock category": {
        "Agricultural Waste": {"facecolor": "green"},
        "Food Industry Peel Waste": {"facecolor": "salmon"},
        "Food Industry Seed Waste": {"facecolor": "blue"},
        "Food Industry Oil Waste": {"facecolor": "purple"},
        "Animal Industry Manufacturing Waste": {"facecolor": "yellow"},
        "Dairy Industry By-product": {"facecolor": "orange"},
        "Household Waste": {"facecolor": "lightsteelblue"},
        "Miscellaneous Waste": {"facecolor": "mediumpurple"},
        "Forestry Residues": {"facecolor": "silver"},
    },
    "Biopolymer family": {
        cat: {"facecolor": "darkgrey"}
        for cat in data["Biopolymer family"].dropna().unique().tolist()
    },
}
print(nodes)
line_data = {
    i: {
        "Feedstock category": data["Feedstock category"].iloc[i],
        "Biopolymer family": data["Biopolymer family"].iloc[i],
        "Main conversion pathway": data["Main conversion pathway"].iloc[i],
    }
    for i in range(len(data))
}
print(line_data)

AlluvialDiagram(
    line_data,
    nodes,
    sorted_category="Feedstock category",
    line_color_mode="sorted_category",
    dev_mode=False,
)

# %%
