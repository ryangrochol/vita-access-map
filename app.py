from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the webpage
st.set_page_config(
    page_title="VITA Access Map",
    page_icon="📊",
    layout="wide"
)


# Locate the processed dataset
project_root = Path(__file__).parent

data_path = (
    project_root
    / "data"
    / "processed"
    / "preliminary_need_ranking.csv"
)


@st.cache_data
def load_data():
    data = pd.read_csv(
        data_path,
        dtype={"zip_code": str}
    )

    data["zip_code"] = data["zip_code"].str.zfill(5)

    return data


data = load_data()


# Introduction
st.title("VITA Access Map")

st.subheader(
    "Identifying communities with potential need "
    "for free tax-preparation assistance"
)

st.write(
    """
    This project combines aggregated IRS and U.S. Census data to examine
    community-level indicators related to access to free tax-preparation
    assistance in Alameda County, California.
    """
)

st.info(
    """
    This preliminary score currently uses poverty and disability rates.
    It does not determine individual eligibility for VITA services or
    provide tax advice.
    """
)

st.link_button(
    "Find an Official VITA/TCE Site",
    "https://freetaxassistance.for.irs.gov/s/sitelocator"
)

st.caption(
    """
    The IRS site locator is updated primarily during filing season,
    generally from February through April. Listings may be limited
    outside that period.
    """
)


# Summary metrics
column1, column2, column3 = st.columns(3)

with column1:
    st.metric(
        "ZIP codes analyzed",
        len(data)
    )

with column2:
    st.metric(
        "Highest poverty rate",
        f"{data['poverty_rate'].max():.1f}%"
    )

with column3:
    st.metric(
        "Highest disability rate",
        f"{data['disability_rate'].max():.1f}%"
    )


# Interactive map
st.header("Community-Need Map")

map_data = data.dropna(
    subset=["latitude", "longitude"]
).copy()

map_figure = px.scatter_map(
    map_data,
    lat="latitude",
    lon="longitude",
    color="preliminary_need_score",
    size="poverty_rate",
    hover_name="location",
    hover_data={
        "poverty_rate": ":.1f",
        "disability_rate": ":.1f",
        "eitc_rate": ":.1f",
        "preliminary_need_score": ":.2f",
        "latitude": False,
        "longitude": False,
        "zip_code": False,
        "city": False,
        "location": False
    },
    color_continuous_scale="YlOrRd",
    size_max=25,
    zoom=8.5,
    center={
        "lat": 37.68,
        "lon": -121.90
    },
    map_style="open-street-map",
    height=600
)

map_figure.update_layout(
    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0
    }
)

st.plotly_chart(
    map_figure,
    use_container_width=True
)

st.caption(
    """
    Marker color represents the preliminary need score. Marker size
    represents the poverty rate. Locations are approximate ZIP Code
    Tabulation Area representative coordinates.
    """
)


# Rankings
st.header("Preliminary Community-Need Ranking")

top_10 = data.sort_values(
    "preliminary_need_score",
    ascending=False
).head(10)

st.dataframe(
    top_10[
        [
            "zip_code",
            "city",
            "poverty_rate",
            "disability_rate",
            "eitc_rate",
            "preliminary_need_score"
        ]
    ],
    hide_index=True,
    use_container_width=True
)

chart_data = top_10[
    ["zip_code", "preliminary_need_score"]
].set_index("zip_code")

st.bar_chart(chart_data)


# Individual ZIP-code explorer
st.header("Explore a ZIP Code")

selected_location = st.selectbox(
    "Choose a city and ZIP code",
    sorted(data["location"].unique())
)

selected_data = data[
    data["location"] == selected_location
].iloc[0]

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric(
        "Poverty rate",
        f"{selected_data['poverty_rate']:.1f}%"
    )

with metric2:
    st.metric(
        "Disability rate",
        f"{selected_data['disability_rate']:.1f}%"
    )

with metric3:
    st.metric(
        "EITC claim rate",
        f"{selected_data['eitc_rate']:.1f}%"
    )

with metric4:
    st.metric(
        "Preliminary need score",
        f"{selected_data['preliminary_need_score']:.2f}"
    )


# Methodology
st.header("Current Methodology")

st.write(
    """
    Poverty and disability rates were standardized using z-scores and
    assigned equal weight.

    **Preliminary need score = (poverty z-score + disability z-score) / 2**

    Positive scores indicate above-average estimated need relative to the
    other ZIP codes included in the analysis.
    """
)

st.warning(
    """
    The score is an exploratory community-level measure. It should not be
    interpreted as an individual eligibility determination, proof of unmet
    demand, or tax advice.
    """
)

st.caption(
    """
    Sources: IRS Statistics of Income 2022 ZIP Code Data, 2022 American
    Community Survey 5-Year Estimates, and 2022 Census Gazetteer Files.
    """
)