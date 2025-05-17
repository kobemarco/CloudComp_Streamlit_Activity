import streamlit as st

import pandas as pd
import numpy as np

from sqlalchemy import create_engine, inspect
from sqlalchemy import text

warehouse = "postgresql://user1:IgiGkzZBqdpyGfr3F5aclDLHdzwU4iX9@dpg-d0k14ct6ubrc73asal2g-a.oregon-postgres.render.com/datawarehouse_j4rf"
engine = create_engine(warehouse,  client_encoding='utf8')
connection = engine.connect()

@st.cache_data
def load_data():
    query_ext = """
        SELECT "Product", count(*) AS count
        FROM sales_data
        GROUP BY "Product";
    """
    result = connection.execute(text(query_ext))
    return pd.DataFrame(result.mappings().all())

df = load_data()



st.title("Sales Dashboard")
st.subheader("Product with Highest Sales")
st.bar_chart(df.set_index('Product'))

