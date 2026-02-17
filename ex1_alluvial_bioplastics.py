# %%
import pandas as pd

from alluvial_diagram.alluvial_chart import AlluvialChart

data_path = "data/Mapping_final.xlsx"

data = pd.read_excel(
    data_path, sheet_name="Visualization", header=1, nrows=61, usecols="C:H"
)
print(data.head())

# %% without subnodes
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
        "Feedstock category": {"node": data["Feedstock category"].iloc[i]},
        "Biopolymer family": {"node": data["Biopolymer family"].iloc[i]},
        "Main conversion pathway": {"node": data["Main conversion pathway"].iloc[i]},
    }
    for i in range(len(data))
}
print(line_data)

AlluvialChart(
    line_data,
    nodes,
    sorted_category="Feedstock category",
    node_separation=0.04,
    line_color_mode="sorted_category",
    dev_mode=False,
)

# %% with subnodes
#['Rice straw, rice husk', 'Corn stover', 'Corn waste', 'Wheat straw, wheat bran',
#  'Sugarcane bagasse', 'Sugar palm fibers', 'Cotton linters', 'Spent coffee grounds (SCG)', 
# 'Pineapple peel', 'Orange peel', 'Citrus peel', 'Banana peel', 'Green banana peel', 
# 'Cassava peel', 'Potato peel', 'Fruit peels (e.g. apple, dragon fruit etc.) ',
#  'Jackfruit seed', 'Avocado seed', 'Mango seed', 'Date seed', 'Pomegranate seed', 
# 'Used cooking oil (UCO)', 'Margarine manufacturing waste', 'Jatropha oil (Non edible)', 
# 'Seed Oil cake (e.g. sunflower, soybean, etc.)', 'Oil industry wastewater', 
# 'Crustacean shells,  insect exoskeletons etc.', 'Animal lung', 'Chicken backs or necks', 
# 'Chicken feathers, human hair, pig hairs, wool fibre, beaks, claws, nailshorns, hooles',
#  'Animal collagen (e.g. from fish skin, rabbit bone etc.) ', 'Egg albumin', 
# 'Milk whey', 'Wastewater', 'Municipal Solid Waste', 'Bread waste', 
# 'Sewage Sludge', 'Wood mill wastewater', 'Wood pulp', 'Wood chips, sawdust, bark']
nodes = {
    "Main conversion pathway": {
        cat: {"facecolor": "lightgrey"}
        for cat in data["Main conversion pathway"].dropna().unique().tolist()
    },
    "Feedstock category": {
        "Agricultural Waste": {"facecolor": "green", "subnodes": {
            "Rice straw, rice husk": {"facecolor": "chartreuse"},
            "Corn stover": {"facecolor": "palegreen"},
            "Corn waste": {"facecolor": "lightgreen"},
            "Wheat straw, wheat bran": {"facecolor": "yellowgreen"},
            "Sugarcane bagasse": {"facecolor": "forestgreen"},
            "Sugar palm fibers": {"facecolor": "lawngreen"},
            "Cotton linters": {"facecolor": "olive"},
            "Spent coffee grounds (SCG)": {"facecolor": "lime"},
        }},
        "Food Industry Peel Waste": {"facecolor": "salmon", "subnodes": {
            "Pineapple peel": {"facecolor": "lightsalmon"},
            "Orange peel": {"facecolor": "lightsalmon"},
            "Citrus peel": {"facecolor": "lightsalmon"},
            "Banana peel": {"facecolor": "lightsalmon"},
            "Green banana peel": {"facecolor": "lightsalmon"},
            "Cassava peel": {"facecolor": "lightsalmon"},
            "Potato peel": {"facecolor": "lightsalmon"},
            "Fruit peels (e.g. apple, dragon fruit etc.) ": {"facecolor": "lightsalmon"},
        }},
        "Food Industry Seed Waste": {"facecolor": "blue", "subnodes": {
            "Jackfruit seed": {"facecolor": "lightblue"}, 
            "Avocado seed": {"facecolor": "lightblue"},
            "Mango seed": {"facecolor": "lightblue"},
            "Date seed": {"facecolor": "lightblue"},
            "Pomegranate seed": {"facecolor": "lightblue"},
        }},
        "Food Industry Oil Waste": {"facecolor": "purple", "subnodes": {
            "Used cooking oil (UCO)": {"facecolor": "plum"},
            "Margarine manufacturing waste": {"facecolor": "plum"},
            "Jatropha oil (Non edible)": {"facecolor": "plum"},
            "Seed Oil cake (e.g. sunflower, soybean, etc.)": {"facecolor": "plum"},
            "Oil industry wastewater": {"facecolor": "plum"},
        }},
        "Animal Industry Manufacturing Waste": {"facecolor": "yellow", 
        "subnodes": {
            "Crustacean shells,  insect exoskeletons etc.": {"facecolor": "lightyellow"},
            "Animal lung": {"facecolor": "lightyellow"},
            "Chicken backs or necks": {"facecolor": "lightyellow"},
            "Chicken feathers, human hair, pig hairs, wool fibre, beaks, claws, nailshorns, hooles": {"facecolor": "lightyellow"},
            "Animal collagen (e.g. from fish skin, rabbit bone etc.) ": {"facecolor": "lightyellow"},
            "Egg albumin": {"facecolor": "lightyellow"},
        }},
        "Dairy Industry By-product": {"facecolor": "darkorange", "subnodes": {
            "Milk whey": {"facecolor": "orange"},
            "Wastewater": {"facecolor": "orange"},
        }},
        "Household Waste": {"facecolor": "lightsteelblue", "subnodes": {
            "Municipal Solid Waste": {"facecolor": "lightsteelblue"},
            "Bread waste": {"facecolor": "lightsteelblue"},
        }},
        "Miscellaneous Waste": {"facecolor": "mediumpurple", "subnodes": {
            "Sewage Sludge": {"facecolor": "mediumpurple"},
        }},
        "Forestry Residues": {"facecolor": "silver", "subnodes": {
            "Wood mill wastewater": {"facecolor": "lightgrey"},
            "Wood pulp": {"facecolor": "lightgrey"},
            "Wood chips, sawdust, bark": {"facecolor": "lightgrey"},
        }},
    },
    "Biopolymer family": {
        cat: {"facecolor": "darkgrey"}
        for cat in data["Biopolymer family"].dropna().unique().tolist()
    },
}
print(nodes)
line_data = {
    i: {
        "Feedstock category": {"node": data["Feedstock category"].iloc[i], "subnode": data["Feedstock Name"].iloc[i]},
        "Biopolymer family": {"node": data["Biopolymer family"].iloc[i]},
        "Main conversion pathway": {"node": data["Main conversion pathway"].iloc[i]},
    }
    for i in range(len(data))
}
print(line_data)

AlluvialChart(
    line_data,
    nodes,
    sorted_category="Feedstock category",
    node_separation=0.04,
    line_color_mode="sorted_category",
    subnode_fontsize=3,
    dev_mode=False,
)
#%% 
#print unique feedstock names:
print(data["Feedstock Name"].dropna().unique().tolist())