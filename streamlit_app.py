import streamlit as st
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as colors
from streamlit_folium import st_folium
import folium

st.set_page_config(
    page_title="IWT Hotspots",
    page_icon="✈️",
    layout="wide"
)

# Add main title and subtitle with clickable link
st.title("Undetected Hotspots of Illegal Wildlife Trade Activity")
st.markdown(
    """
    <h4 style="margin-top:0;">
        This dashboard identifies the 306 airports detected by
        <a href="https://www.nature.com/articles/s43247-025-02371-5" target="_blank" style="text-decoration:underline;color:#3366cc;">
            our model
        </a>
        to likely be involved in the illicit wildlife trade despite not having an observed incidents in our dataset.
    </h4>
    """,
    unsafe_allow_html=True
)

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

# filtered_fp = fp[(fp["confidence"] >= confidence_range) & (fp["confidence"] <= confidence_range)]

filtered_fp = fp[
    (fp["confidence"] >= confidence_range[0]) &
    (fp["confidence"] <= confidence_range[1])
]


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

st_folium(fmap, width=1200, height=800)

st.header("Airport Feature Details")

airport_options = filtered_fp[["IATA", "name"]].copy()
airport_options["display"] = airport_options["name"] + " (" + airport_options["IATA"] + ")"
airport_options = airport_options.sort_values("display")

selected_display = st.selectbox(
    "Select an airport to view full features",
    airport_options["display"]
)

selected_iata = selected_display.split("(")[-1].strip(")")

# if selected_iata:
#     data = filtered_fp[filtered_fp["IATA"] == selected_iata].iloc
#     with st.expander(f"Features for {data['name']} ({selected_iata})"):
#         st.markdown(f"**City:** {data['city']}")
#         st.markdown(f"**Country:** {data['country']}")
#         st.markdown(f"**Model Confidence:** {data['confidence']:.2f}")

#         exclude_cols = ["latitude", "longitude", "IATA", "confidence", "name", "city", "country", "label"]
#         for col in data.index:
#             if col not in exclude_cols and pd.notnull(data[col]) and data[col] != '':
#                 st.markdown(f"**{col.replace('_', ' ').title()}:** {data[col]}")


selected_rows = filtered_fp[filtered_fp["IATA"] == selected_iata]
if not selected_rows.empty:
    data = selected_rows.iloc[0]
    with st.expander(f"Features for {data['name']} ({selected_iata})"):
        st.markdown(f"**City:** {data['city']}")
        st.markdown(f"**Country:** {data['country']}")
        st.markdown(f"**Model Confidence:** {data['confidence']:.2f}")

        exclude_cols = ["latitude", "longitude", "IATA", "confidence", "name", "city", "country", "label"]
        for col in data.index:
            if col not in exclude_cols and pd.notnull(data[col]) and data[col] != '':
                st.markdown(f"**{col.replace('_', ' ').title()}:** {data[col]}")
else:
    st.info(f"No data available for the selected airport: {selected_iata}")


# # Footer with citation and contact info
# st.markdown(
#     """
#     <hr style="margin-top:40px;margin-bottom:10px;">
#     <p style="font-size:0.95em;">
#     Citation:<br>
#     <a href="https://www.nature.com/articles/s43247-025-02371-5" target="_blank">
#         https://www.nature.com/articles/s43247-025-02371-5
#     </a>
#     <br>
#     <b>Contact:</b><br>
#     Hannah Murray (<a href="mailto:hannahmu@usc.edu">hannahmu@usc.edu</a>)<br>
#     Meredith Gore (<a href="mailto:gorem@umd.edu">gorem@umd.edu</a>)<br>
#     Bistra Dilkina (<a href="mailto:dilkina@usc.edu">dilkina@usc.edu</a>)
#     </p>
#     """,
#     unsafe_allow_html=True
# )

st.markdown(
    """
    <hr>
    <p style="font-size:0.9em;">
    Citation:<br>
    <a href="https://www.nature.com/articles/s43247-025-02371-5" target="_blank">
        https://www.nature.com/articles/s43247-025-02371-5
    </a><br><br>
    <b>Contact:</b><br>
    Hannah Murray (hannahmu@usc.edu)<br>
    Meredith Gore (gorem@umd.edu)<br>
    Bistra Dilkina (dilkina@usc.edu)
    </p>
    """,
    unsafe_allow_html=True
)

