import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# DB connection
warehouse = "postgresql://user1:IgiGkzZBqdpyGfr3F5aclDLHdzwU4iX9@dpg-d0k14ct6ubrc73asal2g-a.oregon-postgres.render.com/datawarehouse_j4rf"
engine = create_engine(warehouse, client_encoding='utf8')
connection = engine.connect()

# Load and cache data
@st.cache_data
def load_data():
    query = """
        SELECT "Product", "Quantity Ordered", "Price Each", "Order Date", "Purchase Address",
               TO_CHAR("Order Date"::timestamp, 'HH24:MI:SS') AS "Order Time"
        FROM sales_data;
    """
    result = connection.execute(text(query))
    df = pd.DataFrame(result.mappings().all())
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Total Price"] = df["Quantity Ordered"] * df["Price Each"]
    return df

df = load_data()

# ----- UI Layout -----
st.title("📦 Sales Dashboard")
st.markdown("Interactive dashboard for monitoring sales data.")

# ---- Sidebar Filters ----
st.sidebar.header("🔍 Filter Data")

# Unique filter values
products = df["Product"].unique()
addresses = df["Purchase Address"].unique()
min_date, max_date = df["Order Date"].min(), df["Order Date"].max()

selected_product = st.sidebar.multiselect("Select Product(s)", products, default=products)
selected_address = st.sidebar.multiselect("Select Address(es)", addresses, default=addresses)
date_range = st.sidebar.date_input("Select Order Date Range", [min_date, max_date])

# Filter data
filtered_df = df[
    (df["Product"].isin(selected_product)) &
    (df["Purchase Address"].isin(selected_address)) &
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1])
]

# ---- KPIs ----
st.subheader("📈 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🧾 Total Orders", len(filtered_df))
with col2:
    st.metric("📦 Total Quantity", int(filtered_df["Quantity Ordered"].sum()))
with col3:
    st.metric("💰 Total Revenue", f"${filtered_df['Total Price'].sum():,.2f}")

# ---- Charts ----
st.subheader("🛍️ Quantity Ordered per Product")
quantity_chart = filtered_df.groupby("Product")["Quantity Ordered"].sum().sort_values(ascending=False)
st.bar_chart(quantity_chart)

st.subheader("💲 Average Price per Product")
price_chart = filtered_df.groupby("Product")["Price Each"].mean()
st.bar_chart(price_chart)

# ---- Raw Data Table ----
st.subheader("📋 Filtered Sales Records")
st.dataframe(filtered_df)

