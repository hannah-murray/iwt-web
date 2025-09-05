# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as colors
from streamlit_folium import st_folium
import folium

st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("false_positives_and_negatives.csv")
fp = df[df["label"] == "false_positive"].copy()

excluded_cols = [
    "Unnamed: 0", "Probabilities", "Predicted Class", "True Class",
    "Incidents", "Origin Count", "Transit Count", "Destination Count",
    "Seizure Count", "Incident Counts", "Binary Incident Observed",
    "Binary Origin Observed", "Binary Destination Observed",
    "Binary Transit Observed", "Source", "Type"
]

rename_dict = {
    "degree_full": "Degree Centrality (Full Flight Network)",
    "between_full": "Between Centrality (Full Flight Network)",
    "close_full": "Closeness Centrality (Full Flight Network)",
    "eigen_full": "Eigenvector Centrality (Full Flight Network)",
    "pr_full": "PageRank Centrality (Full Flight Network)",
    "degree_in_full": "Degree-In Centrality (Full Flight Network)",
    "degree_out_full": "Degree-Out Centrality (Full Flight Network)",
    "NON-RENEWABLE\nNON-RENEWABLE RESOURCE CRIMES": "Non-Renewable Resource Crimes"
}

fp = fp.drop(columns=excluded_cols, errors="ignore").rename(columns=rename_dict)
required_cols = ["latitude", "longitude", "IATA", "confidence", "name", "city", "country"]
missing_cols = [c for c in required_cols if c not in fp.columns]
if missing_cols:
    st.error(f"Missing columns: {missing_cols}")
    st.stop()

min_conf, max_conf = fp["confidence"].min(), fp["confidence"].max()

# Sidebar filter
st.sidebar.header("Filters")
confidence_range = st.sidebar.slider(
    "Model Confidence Range",
    min_value=float(min_conf),
    max_value=float(max_conf),
    value=(float(min_conf), float(max_conf)),
    step=0.01,
)

filtered_fp = fp[(fp["confidence"] >= confidence_range[0]) & (fp["confidence"] <= confidence_range[1])]

# Build Map
map_center = [filtered_fp["latitude"].median(), filtered_fp["longitude"].median()]
fmap = folium.Map(location=map_center, zoom_start=2, tiles="cartodbpositron")

norm_conf = colors.Normalize(vmin=min_conf, vmax=max_conf)
cmap = cm.Reds

for _, row in filtered_fp.iterrows():
    color = colors.rgb2hex(cmap(norm_conf(row["confidence"])))
    popup_html = (
        f"<b>{row['name']}</b><br>"
        f"City: {row['city']}<br>"
        f"Country: {row['country']}<br>"
        f"IATA: {row['IATA']}<br>"
        f"Model Confidence: <b>{row['confidence']:.2f}</b>"
    )
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.8,
        fill_color=color,
        popup=folium.Popup(popup_html, max_width=250),
    ).add_to(fmap)

# Display large map
st_folium(fmap, width=1200, height=800)

# Feature details section
st.header("Airport Feature Details")

# Airport selection dropdown
selected_iata = st.selectbox("Select an airport to view full features", filtered_fp["IATA"].unique())

if selected_iata:
    data = filtered_fp[filtered_fp["IATA"] == selected_iata].iloc[0]
    # Show features in an expander
    with st.expander(f"Features for {data['name']} ({selected_iata})"):
        # Display important fields and some computed features
        st.markdown(f"**City:** {data['city']}")
        st.markdown(f"**Country:** {data['country']}")
        st.markdown(f"**Model Confidence:** {data['confidence']:.2f}")
        
        # Show other additional columns (exclude main ones and renamed ones if desired)
        exclude_cols = ["latitude", "longitude", "IATA", "confidence", "name", "city", "country", "label"]
        for col in data.index:
            if col not in exclude_cols:
                st.markdown(f"**{col.replace('_',' ').title()}:** {data[col]}")


# import streamlit as st
# import pandas as pd
# import matplotlib.cm as cm
# import matplotlib.colors as colors
# from streamlit_folium import st_folium
# import folium
# import json

# st.set_page_config(layout="wide")

# # Load & preprocess data as before
# df = pd.read_csv("false_positives_and_negatives.csv")
# fp = df[df["label"] == "false_positive"].copy()

# excluded_cols = [
#     "Unnamed: 0", "Probabilities", "Predicted Class", "True Class",
#     "Incidents", "Origin Count", "Transit Count", "Destination Count",
#     "Seizure Count", "Incident Counts", "Binary Incident Observed",
#     "Binary Origin Observed", "Binary Destination Observed",
#     "Binary Transit Observed", "Source", "Type"
# ]
# rename_dict = {
#     "degree_full": "Degree Centrality (Full Flight Network)",
#     "between_full": "Between Centrality (Full Flight Network)",
#     "close_full": "Closeness Centrality (Full Flight Network)",
#     "eigen_full": "Eigenvector Centrality (Full Flight Network)",
#     "pr_full": "PageRank Centrality (Full Flight Network)",
#     "degree_in_full": "Degree-In Centrality (Full Flight Network)",
#     "degree_out_full": "Degree-Out Centrality (Full Flight Network)",
#     "NON-RENEWABLE\nNON-RENEWABLE RESOURCE CRIMES": "Non-Renewable Resource Crimes"
# }
# fp = fp.drop(columns=excluded_cols, errors="ignore").rename(columns=rename_dict)
# required_cols = ["latitude", "longitude", "IATA", "confidence", "name", "city", "country"]
# missing_cols = [c for c in required_cols if c not in fp.columns]
# if missing_cols:
#     st.error(f"Missing columns: {missing_cols}")
#     st.stop()

# min_conf, max_conf = fp["confidence"].min(), fp["confidence"].max()

# # Sidebar filter
# st.sidebar.header("Filters")
# confidence_range = st.sidebar.slider(
#     "Model Confidence Range",
#     min_value=float(min_conf),
#     max_value=float(max_conf),
#     value=(float(min_conf), float(max_conf)),
#     step=0.01,
# )

# filtered_fp = fp[(fp["confidence"] >= confidence_range[0]) & (fp["confidence"] <= confidence_range[1])]

# # Convert filtered data to GeoJSON format
# def df_to_geojson(df):
#     features = []
#     for _, row in df.iterrows():
#         prop = row.drop(["latitude", "longitude"]).to_dict()
#         features.append({
#             "type": "Feature",
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [row["longitude"], row["latitude"]]
#             },
#             "properties": prop
#         })
#     return {"type": "FeatureCollection", "features": features}

# geojson_data = df_to_geojson(filtered_fp)

# # Create map
# map_center = [filtered_fp["latitude"].median(), filtered_fp["longitude"].median()]
# fmap = folium.Map(location=map_center, zoom_start=2, tiles="cartodbpositron")

# # Prepare color scale
# norm = colors.Normalize(vmin=min_conf, vmax=max_conf)
# cmap = cm.Reds

# def style_function(feature):
#     conf = feature['properties']['confidence']
#     color = colors.rgb2hex(cmap(norm(conf)))
#     return {
#         'color': color,
#         'fillColor': color,
#         'fillOpacity': 0.8,
#         'radius': 7,
#         'weight': 1,
#     }

# # Add GeoJson layer with circle markers
# geojson_layer = folium.GeoJson(
#     geojson_data,
#     name='False Positives',
#     marker=folium.CircleMarker(),
#     style_function=style_function,
#     tooltip=folium.GeoJsonTooltip(fields=['name', 'city', 'country', 'confidence', 'IATA']),
#     popup=folium.GeoJsonPopup(fields=['name', 'city', 'country', 'confidence', 'IATA']),
# )

# geojson_layer.add_to(fmap)

# # Show Folium map with click support
# returned = st_folium(fmap, width=1200, height=800, returned_objects=['last_active_drawing', 'last_object_clicked', 'last_clicked'])

# # If marker clicked, get IATA and show details
# last_click = returned.get('last_clicked')

# if last_click and 'properties' in last_click:
#     props = last_click['properties']
#     selected_iata = props.get('IATA')

#     st.header(f"Details for Airport: {selected_iata}")
#     # Find row matching IATA
#     selected_row = filtered_fp[filtered_fp['IATA'] == selected_iata]
#     if not selected_row.empty:
#         data = selected_row.iloc[0]
#         # Show details excluding lat/lon
#         exclude_cols = ["latitude", "longitude"]
#         for col in data.index:
#             if col not in exclude_cols:
#                 st.markdown(f"**{col.replace('_', ' ').title()}:** {data[col]}")
#     else:
#         st.write("Selected airport data not found.")
