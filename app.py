import os

import pandas as pd
import plotly.express as px
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

st.set_page_config(
    page_title="Databricks Data Explorer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Databricks Data Explorer")
st.write("Browse a Unity Catalog table and visualize it.")

WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")

if not WAREHOUSE_ID:
    st.error(
        "DATABRICKS_WAREHOUSE_ID is not set.\n\n"
        "In the Databricks Apps UI, attach a SQL warehouse as a resource to this app "
        "and redeploy. For local development, set DATABRICKS_WAREHOUSE_ID plus standard "
        "Databricks auth env vars (DATABRICKS_HOST / DATABRICKS_TOKEN, or a configured CLI profile)."
    )
    st.stop()

cfg = Config()
HTTP_PATH = f"/sql/1.0/warehouses/{WAREHOUSE_ID}"


def run_query(query: str) -> pd.DataFrame:
    with sql.connect(
        server_hostname=cfg.host,
        http_path=HTTP_PATH,
        credentials_provider=lambda: cfg.authenticate,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=columns)


@st.cache_data(ttl=600, show_spinner="Loading catalogs...")
def list_catalogs() -> list[str]:
    return sorted(run_query("SHOW CATALOGS")["catalog"].tolist())


@st.cache_data(ttl=600, show_spinner="Loading schemas...")
def list_schemas(catalog: str) -> list[str]:
    df = run_query(f"SHOW SCHEMAS IN `{catalog}`")
    return sorted(df["databaseName"].tolist())


@st.cache_data(ttl=600, show_spinner="Loading tables...")
def list_tables(catalog: str, schema: str) -> list[str]:
    df = run_query(f"SHOW TABLES IN `{catalog}`.`{schema}`")
    return sorted(df["tableName"].tolist())


@st.cache_data(ttl=300, show_spinner="Running query...")
def load_table(catalog: str, schema: str, table: str, row_limit: int) -> pd.DataFrame:
    full_name = f"`{catalog}`.`{schema}`.`{table}`"
    return run_query(f"SELECT * FROM {full_name} LIMIT {row_limit}")


st.sidebar.header("Browse data")
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()

try:
    catalogs = list_catalogs()
except Exception as e:
    st.error(f"Could not connect to the SQL warehouse: {e}")
    st.stop()

if not catalogs:
    st.warning("No catalogs are visible to this app's identity.")
    st.stop()

catalog = st.sidebar.selectbox("Catalog", catalogs)
schemas = list_schemas(catalog) if catalog else []
schema = st.sidebar.selectbox("Schema", schemas) if schemas else None
tables = list_tables(catalog, schema) if schema else []
table = st.sidebar.selectbox("Table", tables) if tables else None
row_limit = st.sidebar.slider("Row limit", min_value=10, max_value=5000, value=500, step=10)

if not table:
    st.info("Select a catalog, schema, and table from the sidebar to preview and visualize data.")
    st.stop()

df = load_table(catalog, schema, table, row_limit)

st.subheader(f"Preview: `{catalog}`.`{schema}`.`{table}`")
st.caption(f"{len(df):,} rows loaded")
st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("Visualize")

if df.empty:
    st.info("This table returned no rows to visualize.")
    st.stop()

all_cols = df.columns.tolist()
numeric_cols = df.select_dtypes(include="number").columns.tolist()

chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Pie", "Histogram"])

col1, col2, col3 = st.columns(3)
with col1:
    x_col = st.selectbox("X axis", all_cols)
with col2:
    y_col = st.selectbox("Y axis", numeric_cols) if chart_type != "Histogram" else None
with col3:
    color_col = st.selectbox("Color / group by (optional)", ["(none)"] + all_cols)
    color_col = None if color_col == "(none)" else color_col

fig = None
if chart_type == "Bar" and y_col:
    fig = px.bar(df, x=x_col, y=y_col, color=color_col)
elif chart_type == "Line" and y_col:
    fig = px.line(df, x=x_col, y=y_col, color=color_col)
elif chart_type == "Scatter" and y_col:
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col)
elif chart_type == "Pie" and y_col:
    fig = px.pie(df, names=x_col, values=y_col)
elif chart_type == "Histogram":
    fig = px.histogram(df, x=x_col, color=color_col)

if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("This chart type needs a numeric Y axis column.")
