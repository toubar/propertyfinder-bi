import streamlit as st
import pandas as pd
import re
import altair as alt

# -------------------- Setup --------------------
st.set_page_config(page_title="Real Estate BI", layout="wide")
st.title("🏡 Real Estate Listings BI Dashboard")

def format_price_millions(val):
    if pd.isnull(val): return "-"
    return f"{val/1_000_000:.1f}M"

# -------------------- Load & Clean Data --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_real_estate_listings.csv")

    def extract_number(x):
        if pd.isnull(x): return None
        x = str(x).replace(",", "")
        numbers = re.findall(r"\d+", x)
        return int("".join(numbers)) if numbers else None

    df["Price_EGP_Clean"] = df["Price_EGP"].apply(extract_number)
    df["Area_sqm_Clean"] = df["Area_sqm"].apply(extract_number)
    df["Down_Payment_Clean"] = df["Down_Payment"].apply(extract_number)
    df["Price_per_sqm"] = df.apply(
        lambda row: row["Price_EGP_Clean"] / row["Area_sqm_Clean"]
        if row["Price_EGP_Clean"] and row["Area_sqm_Clean"] else None, axis=1
    )
    df["Bedrooms"] = pd.to_numeric(df["Bedrooms"], errors="coerce").fillna(0).astype(int)
    df["Bathrooms"] = pd.to_numeric(df["Bathrooms"], errors="coerce").fillna(0).astype(int)
    df["Location_Main"] = df["Location"].apply(lambda x: str(x).split(",")[0].strip())
    return df

df = load_data()

# -------------------- Sidebar Filters (Drill-Down Optional) --------------------
st.sidebar.header("🔍 Optional Filters")

locations = sorted(df["Location_Main"].dropna().unique().tolist())
property_types = sorted(df["Property_Type"].dropna().unique().tolist())
max_price = int(df["Price_EGP_Clean"].max() or 0)

selected_locations = st.sidebar.multiselect("Filter by Location", locations, default=locations)
selected_types = st.sidebar.multiselect("Filter by Property Type", property_types, default=property_types)
bedroom_min = st.sidebar.slider("Minimum Bedrooms", 0, int(df["Bedrooms"].max()), 0)
price_range = st.sidebar.slider("Price Range (EGP)", 0, max_price, (0, max_price))

filtered_df = df[
    df["Location_Main"].isin(selected_locations) &
    df["Property_Type"].isin(selected_types) &
    (df["Bedrooms"] >= bedroom_min) &
    (df["Price_EGP_Clean"].between(price_range[0], price_range[1]))
]

# -------------------- KPI Cards --------------------
st.markdown("### 📊 Market Overview")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg. Price", format_price_millions(filtered_df["Price_EGP_Clean"].mean()))
with col2:
    st.metric("Avg. Area", f"{int(filtered_df['Area_sqm_Clean'].mean())} sqm")
with col3:
    st.metric("Avg. Price / sqm", f"{int(filtered_df['Price_per_sqm'].mean()):,} EGP/sqm")
with col4:
    st.metric("Total Listings", f"{len(filtered_df)}")

# -------------------- Price by Location --------------------
st.markdown("### 🗺️ Average Price by Location")
price_by_location = filtered_df.groupby("Location_Main").agg(
    avg_price=("Price_EGP_Clean", "mean"),
    avg_area=("Area_sqm_Clean", "mean"),
    avg_price_sqm=("Price_per_sqm", "mean"),
    count=("Listing_URL", "count")
).reset_index()

# Sort by avg_price (numeric)
price_by_location = price_by_location.sort_values("avg_price", ascending=False)

st.dataframe(
    price_by_location[["Location_Main", "avg_price", "avg_price_sqm", "count"]]
    .rename(columns={"Location_Main": "Location", "avg_price": "Avg Price (EGP)", "avg_price_sqm": "Price/sqm (EGP)", "count": "Listings"}),
    use_container_width=True
)

bar_chart = alt.Chart(price_by_location).mark_bar().encode(
    x=alt.X("Location_Main", sort="-y"),
    y="avg_price",
    tooltip=["Location_Main", "avg_price", "avg_price_sqm", "count"]
).properties(title="Avg. Price by Location", height=400)

st.altair_chart(bar_chart, use_container_width=True)

# -------------------- Listings Count per Location --------------------
st.markdown("### 📍 Listings Count per Location")
location_counts = filtered_df["Location_Main"].value_counts().reset_index()
location_counts.columns = ["Location", "Count"]
st.dataframe(location_counts, use_container_width=True)

bar_count_chart = alt.Chart(location_counts).mark_bar().encode(
    x=alt.X("Location", sort="-y"),
    y="Count",
    tooltip=["Location", "Count"]
).properties(title="Listings Count per Location", height=400)

st.altair_chart(bar_count_chart, use_container_width=True)

# -------------------- Price per sqm by Property Type --------------------
st.markdown("### 🏷️ Avg. Price per sqm by Property Type")
price_by_type = filtered_df.groupby("Property_Type").agg(
    avg_price=("Price_EGP_Clean", "mean"),
    avg_area=("Area_sqm_Clean", "mean"),
    avg_price_sqm=("Price_per_sqm", "mean"),
    count=("Listing_URL", "count")
).reset_index()

# Sort by avg_price_sqm (numeric)
price_by_type = price_by_type.sort_values("avg_price_sqm", ascending=False)

st.dataframe(
    price_by_type[["Property_Type", "avg_price", "avg_price_sqm", "count"]]
    .rename(columns={"Property_Type": "Property Type", "avg_price": "Avg Price (EGP)", "avg_price_sqm": "Price/sqm (EGP)", "count": "Listings"}),
    use_container_width=True
)

bar_price_sqm = alt.Chart(price_by_type).mark_bar().encode(
    x=alt.X("Property_Type", sort="-y"),
    y="avg_price_sqm",
    tooltip=["Property_Type", "avg_price", "avg_price_sqm", "count"]
).properties(title="Avg. Price per sqm by Property Type", height=400)

st.altair_chart(bar_price_sqm, use_container_width=True)

# -------------------- Bedroom Distribution --------------------
st.markdown("### 🛏️ Listings by Bedroom Count")
bedroom_dist = filtered_df["Bedrooms"].value_counts().sort_index().reset_index()
bedroom_dist.columns = ["Bedrooms", "Count"]

bar_bedroom = alt.Chart(bedroom_dist).mark_bar().encode(
    x=alt.X("Bedrooms:O", title="Bedrooms"),
    y="Count",
    tooltip=["Bedrooms", "Count"]
).properties(title="Listings by Bedrooms", height=400)

st.altair_chart(bar_bedroom, use_container_width=True)

# -------------------- Price Buckets --------------------
st.markdown("### 💰 Listings by Price Range")
bins = [0, 5_000_000, 10_000_000, 20_000_000, 30_000_000, 50_000_000]
labels = ["<5M", "5–10M", "10–20M", "20–30M", "30M+"]

filtered_df["Price_Bucket"] = pd.cut(filtered_df["Price_EGP_Clean"], bins=bins, labels=labels, include_lowest=True)
bucket_dist = filtered_df["Price_Bucket"].value_counts().sort_index().reset_index()
bucket_dist.columns = ["Price Range", "Count"]

bar_bucket = alt.Chart(bucket_dist).mark_bar().encode(
    x="Price Range",
    y="Count",
    tooltip=["Price Range", "Count"]
).properties(title="Listings by Price Range", height=400)

st.altair_chart(bar_bucket, use_container_width=True)

# -------------------- Preview Listings --------------------
st.markdown("### 📋 Preview Listings")
st.dataframe(filtered_df[["Listing_URL", "Location", "Property_Type", "Price_EGP_Clean", "Area_sqm_Clean", "Bedrooms", "Bathrooms"]], use_container_width=True)
