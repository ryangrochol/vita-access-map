from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the page
st.set_page_config(
    page_title="VITA Access Map",
    page_icon="📊",
    layout="wide"
)


# Load the final processed dataset
project_root = Path(__file__).parent

data_path = (
    project_root
    / "data"
    / "processed"
    / "final_need_ranking.csv"
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


# Sidebar: adjustable weights
st.sidebar.header("Adjust the Need Score")

st.sidebar.write(
    """
    Adjust how much each community indicator contributes. The app
    automatically converts your choices into weights totaling 100%.
    """
)

poverty_input = st.sidebar.slider(
    "Poverty",
    min_value=0,
    max_value=100,
    value=35,
    step=5
)

disability_input = st.sidebar.slider(
    "Disability",
    min_value=0,
    max_value=100,
    value=20,
    step=5
)

language_input = st.sidebar.slider(
    "Limited English",
    min_value=0,
    max_value=100,
    value=25,
    step=5
)

internet_input = st.sidebar.slider(
    "No internet access",
    min_value=0,
    max_value=100,
    value=20,
    step=5
)

weight_total = (
    poverty_input
    + disability_input
    + language_input
    + internet_input
)

if weight_total == 0:
    st.sidebar.error("At least one weight must be greater than zero.")
    st.stop()

poverty_weight = poverty_input / weight_total
disability_weight = disability_input / weight_total
language_weight = language_input / weight_total
internet_weight = internet_input / weight_total

st.sidebar.subheader("Normalized weights")

st.sidebar.write(
    f"""
    - Poverty: **{poverty_weight:.0%}**
    - Disability: **{disability_weight:.0%}**
    - Limited English: **{language_weight:.0%}**
    - No internet: **{internet_weight:.0%}**
    """
)


# Recalculate the score
data["adjusted_need_score"] = (
    poverty_weight * data["poverty_z"]
    + disability_weight * data["disability_z"]
    + language_weight * data["limited_english_z"]
    + internet_weight * data["no_internet_z"]
)


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
    The score is a community-level exploratory measure. It does not determine
    individual VITA eligibility or provide tax advice.
    """
)

st.link_button(
    "Find Current VITA/TCE Sites",
    "https://freetaxassistance.for.irs.gov/s/sitelocator"
)


# Summary metrics
metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric(
        "ZIP codes analyzed",
        len(data)
    )

with metric2:
    st.metric(
        "Highest poverty rate",
        f"{data['poverty_rate'].max():.1f}%"
    )

with metric3:
    st.metric(
        "Highest limited-English rate",
        f"{data['limited_english_rate'].max():.1f}%"
    )

with metric4:
    st.metric(
        "Highest no-internet rate",
        f"{data['no_internet_rate'].max():.1f}%"
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
    color="adjusted_need_score",
    size="poverty_rate",
    hover_name="location",
    hover_data={
        "poverty_rate": ":.1f",
        "disability_rate": ":.1f",
        "limited_english_rate": ":.1f",
        "no_internet_rate": ":.1f",
        "eitc_rate": ":.1f",
        "adjusted_need_score": ":.2f",
        "latitude": False,
        "longitude": False,
        "zip_code": False,
        "city": False,
        "location": False
    },
    labels={
        "poverty_rate": "Poverty rate (%)",
        "disability_rate": "Disability rate (%)",
        "limited_english_rate": "Limited-English rate (%)",
        "no_internet_rate": "No-internet rate (%)",
        "eitc_rate": "EITC claim rate (%)",
        "adjusted_need_score": "Need score"
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
    Marker color represents the adjustable need score. Marker size represents
    poverty rate. Marker locations are Census ZCTA representative coordinates.
    """
)


# Community ranking
st.header("Community-Need Ranking")

ranked_data = data.sort_values(
    "adjusted_need_score",
    ascending=False
).reset_index(drop=True)

top_10 = ranked_data.head(10)

st.dataframe(
    top_10[
        [
            "location",
            "poverty_rate",
            "disability_rate",
            "limited_english_rate",
            "no_internet_rate",
            "eitc_rate",
            "adjusted_need_score"
        ]
    ],
    hide_index=True,
    use_container_width=True,
    column_config={
        "location": "Community",
        "poverty_rate": st.column_config.NumberColumn(
            "Poverty (%)",
            format="%.1f"
        ),
        "disability_rate": st.column_config.NumberColumn(
            "Disability (%)",
            format="%.1f"
        ),
        "limited_english_rate": st.column_config.NumberColumn(
            "Limited English (%)",
            format="%.1f"
        ),
        "no_internet_rate": st.column_config.NumberColumn(
            "No Internet (%)",
            format="%.1f"
        ),
        "eitc_rate": st.column_config.NumberColumn(
            "EITC Claims (%)",
            format="%.1f"
        ),
        "adjusted_need_score": st.column_config.NumberColumn(
            "Need Score",
            format="%.2f"
        )
    }
)

chart_data = top_10[
    ["location", "adjusted_need_score"]
].set_index("location")

st.bar_chart(chart_data)


# Individual ZIP explorer
st.header("Explore a Community")

selected_location = st.selectbox(
    "Choose a city and ZIP code",
    sorted(data["location"].unique())
)

selected_data = data[
    data["location"] == selected_location
].iloc[0]

row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.metric(
        "Poverty rate",
        f"{selected_data['poverty_rate']:.1f}%"
    )

with row1_col2:
    st.metric(
        "Disability rate",
        f"{selected_data['disability_rate']:.1f}%"
    )

with row1_col3:
    st.metric(
        "Limited-English rate",
        f"{selected_data['limited_english_rate']:.1f}%"
    )

row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.metric(
        "No-internet rate",
        f"{selected_data['no_internet_rate']:.1f}%"
    )

with row2_col2:
    st.metric(
        "EITC claim rate",
        f"{selected_data['eitc_rate']:.1f}%"
    )

with row2_col3:
    st.metric(
        "Adjusted need score",
        f"{selected_data['adjusted_need_score']:.2f}"
    )


# Methodology
st.header("Methodology")

st.write(
    f"""
    Each indicator is standardized using a z-score so variables measured on
    different scales can be compared.

    The current adjusted score uses:

    - **{poverty_weight:.0%} poverty**
    - **{disability_weight:.0%} disability**
    - **{language_weight:.0%} limited English**
    - **{internet_weight:.0%} no internet access**

    Moving the sidebar controls recalculates the score, ranking, and map.
    This sensitivity analysis demonstrates how modeling choices affect which
    communities are prioritized.
    """
)

st.warning(
    """
    This analysis does not estimate individual eligibility or prove that a
    community is underserved. ACS values are survey estimates, and ZIP Code
    Tabulation Areas do not perfectly match postal ZIP codes or county
    boundaries. The IRS site locator is seasonal and is updated primarily
    during filing season.
    """
)

st.caption(
    """
    Sources: IRS Statistics of Income 2022 ZIP Code Data, U.S. Census Bureau
    2022 American Community Survey 5-Year Estimates, and 2022 Census
    Gazetteer Files.
    """
)