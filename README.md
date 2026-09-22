# My Databricks App

A simple Databricks App built with Python and Streamlit.

## Files

- app.py - Streamlit application
- app.yml - Databricks App startup command
- requirements.txt - Python dependencies

## Run

Deploy this folder as a Databricks App. Databricks will install the dependencies and use app.yml to start Streamlit.

## Databricks connection

The app browses Unity Catalog catalogs/schemas/tables and displays table data using a SQL warehouse.

To enable this:
1. In the Databricks Apps UI, attach a SQL warehouse as a resource to this app. This automatically injects a `DATABRICKS_WAREHOUSE_ID` environment variable and app auth credentials.
2. Redeploy the app.

For local development, set `DATABRICKS_WAREHOUSE_ID` plus standard Databricks auth env vars (e.g. `DATABRICKS_HOST` and `DATABRICKS_TOKEN`, or a configured CLI profile) before running `streamlit run app.py`.
