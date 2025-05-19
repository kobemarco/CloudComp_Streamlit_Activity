import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import create_engine, inspect
from sqlalchemy import text

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Database connection
warehouse = "postgresql://user1:IgiGkzZBqdpyGfr3F5aclDLHdzwU4iX9@dpg-d0k14ct6ubrc73asal2g-a.oregon-postgres.render.com/datawarehouse_j4rf"
engine = create_engine(warehouse, client_encoding='utf8')
connection = engine.connect()

@st.cache_data
def load_data():
    query_ext = """
        SELECT 
            "Product",
            COUNT(*) AS count,
            SUM(CAST("Quantity Ordered" AS INTEGER)) as total_quantity,
            AVG(CAST(REPLACE(REPLACE(REPLACE("Price Each", '$', ''), ' USD', ''), ',', '') AS DECIMAL)) as avg_price,
            SUM(CAST("Quantity Ordered" AS INTEGER) * 
                CAST(REPLACE(REPLACE(REPLACE("Price Each", '$', ''), ' USD', ''), ',', '') AS DECIMAL)) as total_revenue
        FROM sales_data
        GROUP BY "Product"
        ORDER BY count DESC;
    """
    result = connection.execute(text(query_ext))
    return pd.DataFrame(result.mappings().all())

# Load data
df = load_data()

# Dashboard Header
st.title("📊 Sales Analytics Dashboard")
st.markdown("---")

# Top metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Products", len(df))
with col2:
    st.metric("Total Revenue", f"${df['total_revenue'].sum():,.2f}")
with col3:
    st.metric("Average Price", f"${df['avg_price'].mean():,.2f}")

st.markdown("---")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Product Sales Distribution")
    fig = px.pie(df, values='total_quantity', names='Product', 
                 title='Sales Distribution by Quantity')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Products by Revenue")
    fig = px.bar(df.head(10), x='Product', y='total_revenue',
                 title='Top 10 Products by Revenue',
                 labels={'total_revenue': 'Revenue ($)', 'Product': 'Product Name'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Additional Analysis
st.markdown("---")
st.subheader("Detailed Product Analysis")

# Interactive filters
selected_product = st.selectbox(
    "Select a product to analyze:",
    options=df['Product'].unique()
)

# Display selected product details
product_data = df[df['Product'] == selected_product]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", f"{product_data['count'].values[0]:,}")
with col2:
    st.metric("Total Quantity", f"{product_data['total_quantity'].values[0]:,}")
with col3:
    st.metric("Total Revenue", f"${product_data['total_revenue'].values[0]:,.2f}")

# Data table
st.markdown("---")
st.subheader("Raw Data")
st.dataframe(df.style.format({
    'total_revenue': '${:,.2f}',
    'avg_price': '${:,.2f}'
}))
