import pandas as pd
import streamlit as st

DATA_PATH = "SKU WISE AD SPEND.xlsx"
USECOLS = "A,B,DV,DX,DZ,EE,EF,EI,EK,EM,EN,EO"
COLUMNS = [
    "CAT",
    "SKU PLAIN",
    "DEC-25 REVENUE",
    "DEC-25 ADVT SPEND",
    "% of Revenue (Spend)",
    "Signal(AMZ)",
    "Action(AMZ)",
    "REVENUE 2025",
    "ADVT SPEND 2025",
    "% of Revenue 2025",
    "Signal 2025",
    "Action 2025",
]
NUMERIC_COLUMNS = [
    "DEC-25 REVENUE",
    "DEC-25 ADVT SPEND",
    "% of Revenue (Spend)",
    "REVENUE 2025",
    "ADVT SPEND 2025",
    "% of Revenue 2025",
]


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_excel(
        path,
        engine="openpyxl",
        header=2,
        usecols=USECOLS,
    )
    data.columns = COLUMNS
    data = data.dropna(how="all", subset=["CAT", "SKU PLAIN"])
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    return data


def format_currency(value: float) -> str:
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "0%"
    return f"{value:.1%}"


st.set_page_config(page_title="SKU Wise Ad Spend Dashboard", layout="wide")

st.title("SKU Wise Ad Spend Dashboard")
st.markdown(
    "Dashboard built from the **SKU WISE AD SPEND** dataset using the same layout and logic as the "
    "Products Search Term 2025 dashboard."
)

with st.sidebar:
    st.header("Filters")
    data = load_data(DATA_PATH)

    cat_options = sorted(data["CAT"].dropna().unique())
    sku_options = sorted(data["SKU PLAIN"].dropna().unique())
    signal_amz_options = sorted(data["Signal(AMZ)"].dropna().unique())
    action_amz_options = sorted(data["Action(AMZ)"].dropna().unique())
    signal_2025_options = sorted(data["Signal 2025"].dropna().unique())
    action_2025_options = sorted(data["Action 2025"].dropna().unique())

    selected_cat = st.multiselect("Category (CAT)", cat_options, default=cat_options)
    selected_sku = st.multiselect("SKU Plain", sku_options, default=sku_options)
    selected_signal_amz = st.multiselect(
        "Signal (AMZ)", signal_amz_options, default=signal_amz_options
    )
    selected_action_amz = st.multiselect(
        "Action (AMZ)", action_amz_options, default=action_amz_options
    )
    selected_signal_2025 = st.multiselect(
        "Signal 2025", signal_2025_options, default=signal_2025_options
    )
    selected_action_2025 = st.multiselect(
        "Action 2025", action_2025_options, default=action_2025_options
    )

filtered = data[
    data["CAT"].isin(selected_cat)
    & data["SKU PLAIN"].isin(selected_sku)
    & data["Signal(AMZ)"].isin(selected_signal_amz)
    & data["Action(AMZ)"].isin(selected_action_amz)
    & data["Signal 2025"].isin(selected_signal_2025)
    & data["Action 2025"].isin(selected_action_2025)
].copy()

filtered = filtered.dropna(how="all", subset=NUMERIC_COLUMNS)

st.subheader("Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    st.metric(
        "DEC-25 Revenue",
        format_currency(filtered["DEC-25 REVENUE"].sum()),
    )
    st.metric(
        "DEC-25 Ad Spend",
        format_currency(filtered["DEC-25 ADVT SPEND"].sum()),
    )

with kpi_col2:
    spend_ratio = (
        filtered["DEC-25 ADVT SPEND"].sum() / filtered["DEC-25 REVENUE"].sum()
        if filtered["DEC-25 REVENUE"].sum()
        else 0
    )
    st.metric("DEC-25 Spend % of Revenue", format_percent(spend_ratio))
    st.metric(
        "2025 Revenue",
        format_currency(filtered["REVENUE 2025"].sum()),
    )

with kpi_col3:
    st.metric(
        "2025 Ad Spend",
        format_currency(filtered["ADVT SPEND 2025"].sum()),
    )
    spend_ratio_2025 = (
        filtered["ADVT SPEND 2025"].sum() / filtered["REVENUE 2025"].sum()
        if filtered["REVENUE 2025"].sum()
        else 0
    )
    st.metric("2025 Spend % of Revenue", format_percent(spend_ratio_2025))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Top SKUs by Dec-25 Revenue")
    top_revenue = (
        filtered.groupby("SKU PLAIN", as_index=False)["DEC-25 REVENUE"]
        .sum()
        .sort_values("DEC-25 REVENUE", ascending=False)
        .head(10)
    )
    st.bar_chart(top_revenue, x="SKU PLAIN", y="DEC-25 REVENUE", height=320)

with right:
    st.subheader("Top SKUs by Dec-25 Ad Spend")
    top_spend = (
        filtered.groupby("SKU PLAIN", as_index=False)["DEC-25 ADVT SPEND"]
        .sum()
        .sort_values("DEC-25 ADVT SPEND", ascending=False)
        .head(10)
    )
    st.bar_chart(top_spend, x="SKU PLAIN", y="DEC-25 ADVT SPEND", height=320)

st.subheader("Revenue vs Ad Spend (Dec-25)")
st.scatter_chart(
    filtered,
    x="DEC-25 REVENUE",
    y="DEC-25 ADVT SPEND",
    color="Signal(AMZ)",
    size=80,
    height=360,
)

summary_left, summary_right = st.columns(2)

with summary_left:
    st.subheader("Signal (AMZ) Mix")
    signal_counts = (
        filtered["Signal(AMZ)"].value_counts().reset_index().rename(
            columns={"index": "Signal(AMZ)", "Signal(AMZ)": "Count"}
        )
    )
    st.bar_chart(signal_counts, x="Signal(AMZ)", y="Count", height=300)

with summary_right:
    st.subheader("Signal 2025 Mix")
    signal_2025_counts = (
        filtered["Signal 2025"].value_counts().reset_index().rename(
            columns={"index": "Signal 2025", "Signal 2025": "Count"}
        )
    )
    st.bar_chart(signal_2025_counts, x="Signal 2025", y="Count", height=300)

st.subheader("Filtered Dataset")
st.dataframe(filtered, use_container_width=True, hide_index=True)
