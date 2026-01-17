from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).with_name("SKU WISE AD SPEND.xlsx")

st.set_page_config(page_title="SKU Wise Ad Spend", layout="wide")


@st.cache_data(show_spinner="Loading SKU WISE AD SPEND...")
def load_data() -> pd.DataFrame:
    df = pd.read_excel(
        DATA_PATH,
        engine="openpyxl",
        header=2,
        usecols="A,B,DV,DX,DZ,EE,EF,EI,EK,EM,EN,EO",
    )
    df = df.rename(
        columns={
            "CAT": "Category",
            "SKU PLAIN": "SKU",
            "DEC-25 REVENUE": "Dec 25 Revenue",
            "DEC-25 ADVT SPEND": "Dec 25 Ad Spend",
            "% of Revenue (Spend)": "Dec 25 Spend % of Revenue",
            "Signal(AMZ)": "Signal (AMZ)",
            "Action(AMZ)": "Action (AMZ)",
            "REVENUE 2025": "Revenue 2025",
            "ADVT SPEND 2025": "Ad Spend 2025",
            "% of Revenue 2025": "% of Revenue 2025",
            "Signal 2025": "Signal 2025",
            "Action 2025": "Action 2025",
        }
    )
    df = df.dropna(how="all")

    numeric_cols = [
        "Dec 25 Revenue",
        "Dec 25 Ad Spend",
        "Dec 25 Spend % of Revenue",
        "Revenue 2025",
        "Ad Spend 2025",
        "% of Revenue 2025",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def format_currency(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"${value:,.0f}"


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"{value * 100:,.2f}%"


df = load_data()

st.title("SKU Wise Ad Spend")
st.caption("Dataset: SKU WISE AD SPEND")

with st.sidebar:
    st.header("Filters")
    categories = sorted(df["Category"].dropna().unique())
    skus = sorted(df["SKU"].dropna().unique())
    amz_signals = sorted(df["Signal (AMZ)"].dropna().unique())
    signals_2025 = sorted(df["Signal 2025"].dropna().unique())

    selected_categories = st.multiselect("Category", categories, default=categories)
    selected_skus = st.multiselect("SKU", skus, default=skus)
    selected_amz_signals = st.multiselect(
        "Signal (AMZ)", amz_signals, default=amz_signals
    )
    selected_signals_2025 = st.multiselect(
        "Signal 2025", signals_2025, default=signals_2025
    )

filtered_df = df[
    df["Category"].isin(selected_categories)
    & df["SKU"].isin(selected_skus)
    & df["Signal (AMZ)"].isin(selected_amz_signals)
    & df["Signal 2025"].isin(selected_signals_2025)
]

kpi_cols = st.columns(5)

kpi_cols[0].metric(
    "Revenue 2025", format_currency(filtered_df["Revenue 2025"].sum())
)
kpi_cols[1].metric(
    "Ad Spend 2025", format_currency(filtered_df["Ad Spend 2025"].sum())
)
kpi_cols[2].metric(
    "% of Revenue 2025",
    format_percent(filtered_df["% of Revenue 2025"].mean()),
)
kpi_cols[3].metric(
    "Dec 25 Revenue", format_currency(filtered_df["Dec 25 Revenue"].sum())
)
kpi_cols[4].metric(
    "Dec 25 Ad Spend", format_currency(filtered_df["Dec 25 Ad Spend"].sum())
)

st.divider()

chart_cols = st.columns((2, 2, 1))

with chart_cols[0]:
    revenue_by_sku = (
        filtered_df.groupby("SKU", as_index=False)["Revenue 2025"].sum().sort_values(
            "Revenue 2025", ascending=False
        )
    )
    fig_revenue = px.bar(
        revenue_by_sku,
        x="Revenue 2025",
        y="SKU",
        orientation="h",
        title="Revenue 2025 by SKU",
    )
    fig_revenue.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_revenue, use_container_width=True)

with chart_cols[1]:
    spend_by_sku = (
        filtered_df.groupby("SKU", as_index=False)["Ad Spend 2025"].sum().sort_values(
            "Ad Spend 2025", ascending=False
        )
    )
    fig_spend = px.bar(
        spend_by_sku,
        x="Ad Spend 2025",
        y="SKU",
        orientation="h",
        title="Ad Spend 2025 by SKU",
        color="Ad Spend 2025",
        color_continuous_scale="Blues",
    )
    fig_spend.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_spend, use_container_width=True)

with chart_cols[2]:
    signal_breakdown = (
        filtered_df["Signal 2025"].value_counts().reset_index(name="Count")
    )
    fig_signal = px.pie(
        signal_breakdown,
        values="Count",
        names="Signal 2025",
        title="Signal 2025 Mix",
        hole=0.5,
    )
    fig_signal.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_signal, use_container_width=True)

st.subheader("Revenue vs Ad Spend")

scatter_fig = px.scatter(
    filtered_df,
    x="Ad Spend 2025",
    y="Revenue 2025",
    color="Signal 2025",
    hover_data=["SKU", "Category", "Signal (AMZ)", "Action 2025"],
    size="Dec 25 Revenue",
    title="Revenue 2025 vs Ad Spend 2025",
)
scatter_fig.update_layout(height=520, margin=dict(l=0, r=0, t=50, b=0))

st.plotly_chart(scatter_fig, use_container_width=True)

st.subheader("December 2025 Snapshot")

snapshot = filtered_df[[
    "SKU",
    "Dec 25 Revenue",
    "Dec 25 Ad Spend",
    "Dec 25 Spend % of Revenue",
    "Signal (AMZ)",
    "Action (AMZ)",
]]

st.dataframe(
    snapshot.sort_values("Dec 25 Revenue", ascending=False),
    use_container_width=True,
    hide_index=True,
)
