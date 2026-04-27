

#%%
import pandas as pd

from alluvial_diagram.alluvial_chart import AlluvialChart

#data_path = "data/lifetimes_lit_rev.xlsx"
data_path = "data/SI2_lifetimes_lit_rev.xlsx"

by_ref = pd.read_excel(data_path, sheet_name="by publication", header = 1, nrows = 48)
display(by_ref)

#%%
categories = ["World region", "Estimation approach", "Type of retrievable lifetime estimate", "Spatial coverage (as classified)" ]
categories_short_name = ["World region", "Estimation method", "Type of estimate", "Spatial coverage" ]
estimation_method_colors = {
    'Building tracking' : 'xkcd:blueberry',
    'Stock composition tracking': 'xkcd:faded blue',
    'Model calibration': 'xkcd:tealish',
    'Demolition accounting': "xkcd:tangerine",
    'Demolition sampling': "xkcd:salmon",
}
node_opacity = 0.8
nodes = {
    "World region": {
        "Asia": {"facecolor": "lightgrey"},
        "Europe": {"facecolor": "lightgrey"},
        "North America": {"facecolor": "lightgrey"},
        "Other": {"facecolor": "lightgrey"},
    },
    "Estimation method": {
        'Model calibration':  {
            "facecolor": estimation_method_colors['Model calibration'], 
            "opacity": node_opacity
        },
        'Stock composition tracking': {
            "facecolor": estimation_method_colors['Stock composition tracking'], 
            "opacity": node_opacity
        },
        'Building tracking' : {
            "facecolor": estimation_method_colors['Building tracking'],
            "opacity": node_opacity
        },
        'Demolition accounting': {
            "facecolor": estimation_method_colors['Demolition accounting'], 
            "opacity": node_opacity
        },
        'Demolition sampling': {
            "facecolor": estimation_method_colors['Demolition sampling'], 
            "opacity": node_opacity
        },

    },
    "Type of estimate": {
        cat: {"facecolor": "lightgrey"}
        for cat in by_ref["Type of retrievable lifetime estimate"].dropna().unique().tolist()
    },
    "Spatial coverage": {
        cat: {"facecolor": "lightgrey"}
        for cat in by_ref["Spatial coverage (as classified)"].dropna().unique().tolist()
    }
}
paper_labels = []
for year, authors in zip(by_ref["Publication year"],by_ref["Author(s)"]):
    # first_authors = authors.split("&")[0]
    # last_author = authors.split("&")[-1]
    author_last_names =  [authors.split(",")[i] for i in range(0, len(authors.split(",")), 2)]
    # clean out the "&" 
    # author_last_names = [name.replace("& ", "").strip() for name in author_last_names]
    if len(author_last_names) >= 3:
        label = f"{author_last_names[0]} et al. ({year})"
    # elif len(author_last_names) == 2:
    #     label = f"{author_last_names[0]} {author_last_names[1]} ({year})"
    else:        
        label = f"{''.join(author_last_names)} ({year})"
    paper_labels.append(label)
print(paper_labels)
by_ref["alluvial_id"] = paper_labels
#print(by_ref["alluvial_id"])
line_data = {
    by_ref["alluvial_id"].iloc[i]: {
        cat_name: {"node": by_ref[cat].iloc[i]}
        for cat_name, cat in zip(categories_short_name, categories)
    }
    for i in range(len(by_ref))
} 
# change entries in world region to "Other" if not Asia, Europe, or North America
for line in line_data.values():
    if line["World region"]["node"] not in ["Asia", "Europe", "North America"]:
        line["World region"]["node"] = "Other"
# sort by "Estimation method"
line_data = dict(sorted(line_data.items(), key=lambda item: item[1]["Estimation method"]["node"]))
print(line_data)

save_path = "data/alluvial_lit_review_v2.png"
AlluvialChart(
    line_data,
    nodes,
    sorted_category="Estimation method",
    line_color_mode="sorted_category",
    plot_id=True,
    dev_mode=False,
    save_path=save_path

)
# %%
