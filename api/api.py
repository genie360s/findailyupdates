"""Fulusi Data API — serves latest financial data from PostgreSQL to the Flask web app."""
import os

import psycopg
from flask import Flask, jsonify
from dotenv import load_dotenv

import analysis

load_dotenv()

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db_connection():
    return psycopg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
    )


def latest_rows(table: str):
    """Return all rows from *table* whose DATE(created_at) equals the max date.

    Returns a (rows, column_names) tuple, or raises on DB errors.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT MAX(DATE(created_at)) FROM {table};")
            latest_date = cur.fetchone()[0]
            if not latest_date:
                return None, None

            cur.execute(
                f"SELECT * FROM {table} WHERE DATE(created_at) = %s;",
                (latest_date,),
            )
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]
            return rows, col_names
    finally:
        conn.close()


def table_endpoint(table: str):
    """Generic handler: fetch latest rows from *table* and return as JSON."""
    try:
        rows, col_names = latest_rows(table)
        if rows is None:
            return jsonify({"error": "No data available"}), 404
        if not rows:
            return jsonify({"error": "No data found for the latest date"}), 404
        return jsonify([dict(zip(col_names, row)) for row in rows])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Routes — each delegates to table_endpoint with its table name
# ---------------------------------------------------------------------------

ROUTES = {
    "/api/v1/dse_stock_prices/latest_date":              "dse_stock_prices",
    "/api/v1/uttamis_unit_prices/latest_date":           "uttamis_fund",
    "/api/v1/uttamis_fund/latest_date":                  "uttamis_fund",
    "/api/v1/faida_fund/latest_date":                    "faida_fund",
    "/api/v1/government_bonds/latest_date":              "government_bonds",
    "/api/v1/corporate_bonds/latest_date":               "corporate_bonds",
    "/api/v1/azania_bank/latest_date":                   "azania_bank",
    "/api/v1/baroda_bank/latest_date":                   "bank_of_baroda",
    "/api/v1/bank_of_india/latest_date":                 "bank_of_india",
    "/api/v1/bank_of_tanzania/latest_date":              "bank_of_tanzania",
    "/api/v1/tanzania_commercial_bank/latest_date":      "tanzania_commercial_bank",
    "/api/v1/dcb_bank/latest_date":                      "dcb_commercial_bank",
    "/api/v1/habib_africa_bank/latest_date":             "habib_african_bank",
    "/api/v1/mkombozi_bank/latest_date":                 "mkombozi_bank",
    "/api/v1/national_microfinance_bank/latest_date":    "national_microfinance_bank",
    "/api/v1/amana_bank/latest_date":                    "amana_bank",
    "/api/v1/dasheng_bank/latest_date":                  "dasheng_bank",
    "/api/v1/international_commercial_bank/latest_date": "international_commercial_bank",
}

for route, table in ROUTES.items():
    # Capture table in a default argument to avoid the closure-over-loop-variable trap
    app.add_url_rule(
        route,
        endpoint=route.replace("/", "_").strip("_"),
        view_func=(lambda t: lambda: table_endpoint(t))(table),
        methods=["GET"],
    )


@app.route("/api/v1/best_banks_forex_rates", methods=["GET"])
def get_best_bank_forex_rates():
    return analysis.check_for_best_selling_and_buying_prices()


@app.route("/api/v1/summary_bank_forex_rates", methods=["GET"])
def get_summary_bank_forex_rates():
    return analysis.get_forex_rates_in_summary()


if __name__ == "__main__":
    app.run(debug=True)
