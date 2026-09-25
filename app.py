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

WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")

if not WAREHOUSE_ID:
    st.error(
        "Error in Warehouse ID is unable to find the SQL warehouse."
    )
    st.stop()
else :
      print(f" warehouse ID: {WAREHOUSE_ID}")

cfg = Config(profile=os.getenv("DATABRICKS_CONFIG_PROFILE"))
HTTP_PATH = f"/sql/1.0/warehouses/{WAREHOUSE_ID}"


def run_query(query: str) -> pd.DataFrame:
    with sql.connect(
        server_hostname=cfg.host,
        http_path=HTTP_PATH,
        credentials_provider=lambda: cfg.authenticate,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            value = cursor.connection.session
            print(f"value: {value}  query: {query}  ")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=columns)


@st.cache_data(ttl=600, show_spinner="Loading catalogs testing...")
def list_catalogs()  -> list[str]:
    dbtest = run_query("SHOW CATALOGS")["dbacademy"]
    return dbtest



@st.cache_data(ttl=600, show_spinner="Loading schemas...")
def list_schemas(catalog: str) -> list[str]:
    return run_query(f"SHOW SCHEMAS IN `{catalog}`")
   


@st.cache_data(ttl=600, show_spinner="Loading tables...")
def load_table(catalog: str, schema: str) -> list[str]:
   return run_query(f"SHOW TABLES IN `{catalog}`.`{schema}`")
  


@st.cache_data(ttl=300, show_spinner="Running query...")
def get_data(catalog: str, schema: str, table: str, row_limit: int) -> pd.DataFrame:
    full_name = f"`{catalog}`.`{schema}`.`{table}`"
    return run_query(f"SELECT FirstName,LastName FROM `{full_name}` LIMIT {row_limit}")


try:
    catalogs = list_catalogs()

except Exception as e:
     print(f"Error: {e}")


schemas = list_schemas(catalogs)
table = load_table(catalogs, schema)
df=get_data(catalogs, schema, table, row_limit)
row_limit = 100

if not table:
    st.info("Select a catalog, schema, and table from the sidebar to preview and visualize data.")
    st.stop()

df = load_table(catalogs, schema, table, row_limit)

print(f"Preview: `{catalogs}`.`{schema}`.`{table}`")
print(f"{len(df)} rows loaded")


