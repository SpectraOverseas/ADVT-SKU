import pandas as pd
import streamlit as st

DATA_PATH = "SKU WISE AD SPEND.xlsx"
USECOLS = "A,B,DV,DX,DZ,EE,EF,EI,EK,EM,EN,EO"

st.set_page_config(
    page_title="SKU Wise Ad Spend Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .metric-label {
            font-size: 0.85rem;
            color: #666666;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1f1f1f;
        }
        .metric-subtext {
            font-size: 0.8rem;
            color: #888888;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.6rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_excel(
        DATA_PATH,
        header=2,
        usecols=USECOLS,
        engine="openpyxl",
    )
    df = df.rename(columns=lambda col: str(col).strip())
    numeric_cols = [
        "DEC-25 REVENUE",
        "DEC-25 ADVT SPEND",
        "% of Revenue (Spend)",
        "REVENUE 2025",
        "ADVT SPEND 2025",
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
    return f"{value:.2%}"


def render_metric(label: str, value: str, subtext: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.spinner("Loading dashboard..."):
    data = load_data()

st.title("SKU Wise Ad Spend")
st.caption("Dataset: SKU WISE AD SPEND")

st.sidebar.header("Filters")
category_options = sorted(data["CAT"].dropna().unique())
sku_options = sorted(data["SKU PLAIN"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Category (CAT)", category_options, default=category_options
)
selected_skus = st.sidebar.multiselect(
    "SKU (SKU PLAIN)", sku_options, default=sku_options
)

signal_amz_options = sorted(data["Signal(AMZ)"].dropna().unique())
action_amz_options = sorted(data["Action(AMZ)"].dropna().unique())

selected_signal_amz = st.sidebar.multiselect(
    "Signal (AMZ)", signal_amz_options, default=signal_amz_options
)
selected_action_amz = st.sidebar.multiselect(
    "Action (AMZ)", action_amz_options, default=action_amz_options
)

signal_2025_options = sorted(data["Signal 2025"].dropna().unique())
action_2025_options = sorted(data["Action 2025"].dropna().unique())

selected_signal_2025 = st.sidebar.multiselect(
    "Signal 2025", signal_2025_options, default=signal_2025_options
)
selected_action_2025 = st.sidebar.multiselect(
    "Action 2025", action_2025_options, default=action_2025_options
)

filtered = data[
    data["CAT"].isin(selected_categories)
    & data["SKU PLAIN"].isin(selected_skus)
    & data["Signal(AMZ)"].isin(selected_signal_amz)
    & data["Action(AMZ)"].isin(selected_action_amz)
    & data["Signal 2025"].isin(selected_signal_2025)
    & data["Action 2025"].isin(selected_action_2025)
].copy()

if filtered.empty:
    st.warning("No rows match the selected filters. Please adjust your selections.")
    st.stop()


revenue_2025_total = filtered["REVENUE 2025"].sum()
spend_2025_total = filtered["ADVT SPEND 2025"].sum()
roas_2025 = spend_2025_total / revenue_2025_total if revenue_2025_total else 0

revenue_dec_total = filtered["DEC-25 REVENUE"].sum()
spend_dec_total = filtered["DEC-25 ADVT SPEND"].sum()
roas_dec = spend_dec_total / revenue_dec_total if revenue_dec_total else 0

metric_cols = st.columns(3)
with metric_cols[0]:
    render_metric("Revenue 2025", format_currency(revenue_2025_total), "Total revenue")
with metric_cols[1]:
    render_metric("Ad Spend 2025", format_currency(spend_2025_total), "Total spend")
with metric_cols[2]:
    render_metric("Spend % of Revenue 2025", format_percent(roas_2025), "Spend / Revenue")

metric_cols = st.columns(3)
with metric_cols[0]:
    render_metric("Dec-25 Revenue", format_currency(revenue_dec_total), "Monthly revenue")
with metric_cols[1]:
    render_metric("Dec-25 Ad Spend", format_currency(spend_dec_total), "Monthly spend")
with metric_cols[2]:
    render_metric("Dec-25 Spend %", format_percent(roas_dec), "Spend / Revenue")

st.markdown('<div class="section-title">Top SKUs</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    top_revenue = (
        filtered.groupby("SKU PLAIN", as_index=False)["REVENUE 2025"]
        .sum()
        .sort_values("REVENUE 2025", ascending=False)
        .head(10)
    )
    st.bar_chart(top_revenue, x="SKU PLAIN", y="REVENUE 2025", height=320)

with right:
    top_spend = (
        filtered.groupby("SKU PLAIN", as_index=False)["ADVT SPEND 2025"]
        .sum()
        .sort_values("ADVT SPEND 2025", ascending=False)
        .head(10)
    )
    st.bar_chart(top_spend, x="SKU PLAIN", y="ADVT SPEND 2025", height=320)

st.markdown('<div class="section-title">Revenue vs. Ad Spend (2025)</div>', unsafe_allow_html=True)

scatter_data = filtered[["REVENUE 2025", "ADVT SPEND 2025", "Signal 2025", "SKU PLAIN"]].copy()
scatter_data = scatter_data.dropna(subset=["REVENUE 2025", "ADVT SPEND 2025"])

if scatter_data.empty:
    st.info("No data available for the scatter plot after filtering.")
else:
    st.scatter_chart(
        scatter_data,
        x="REVENUE 2025",
        y="ADVT SPEND 2025",
        color="Signal 2025",
        size=None,
        height=360,
    )

st.markdown('<div class="section-title">Filtered Data</div>', unsafe_allow_html=True)

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)
