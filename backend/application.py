import logging

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from pyathena import connect

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Athena configuration
ATHENA_DATABASE = "default"
ATHENA_OUTPUT = "s3://graystumbucket/Queries/"
REGION = "us-east-1"


# Helper function to execute Athena queries
def query_athena(sql_query):
    """
    Execute a query on Athena and return the results as a Pandas DataFrame.
    """
    conn = connect(s3_staging_dir=ATHENA_OUTPUT, region_name=REGION)
    cursor = conn.cursor()
    cursor.execute(sql_query)

    # Fetch results
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    # Create a Pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)
    return df


@app.route("/search", methods=["GET"])
def search():
    """
    Search endpoint to filter Athena data.
    """
    year = request.args.get("year")
    month = request.args.get("month")
    shelter = request.args.get("shelter")

    # Build the query
    query = "SELECT * FROM homeless_data WHERE 1=1"
    if year:
        query += f" AND Year = '{year}'"
    if month:
        query += f" AND Month = '{month}'"
    if shelter:
        shelter = shelter.replace("'", "''")
        query += f" AND Shelter = '{shelter}'"
    query += " LIMIT 100;"

    try:
        results = query_athena(query)
        return jsonify(results.to_dict(orient="records"))
    except Exception as e:
        logging.error(f"Error executing search query: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/visualize", methods=["GET"])
def visualize():
    """
    Generate a visualization for anxiety levels over time.
    """
    query = """
    SELECT encounter_date, AVG(CAST(anxiety_lvl AS DOUBLE)) as avg_anxiety
    FROM homeless_data
    WHERE anxiety_lvl IS NOT NULL
    GROUP BY encounter_date
    ORDER BY encounter_date;
    """
    try:
        results = query_athena(query)
        return jsonify(results.to_dict(orient="records"))
    except Exception as e:
        logging.error(f"Error executing visualization query: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/all", methods=["GET"])
def get_all_data():
    """
    Fetch all rows from the homeless_data table.
    """
    query = "SELECT * FROM homeless_data LIMIT 1000;"
    try:
        results = query_athena(query)
        return jsonify(results.to_dict(orient="records"))
    except Exception as e:
        logging.error(f"Error fetching all data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/shelter_analysis", methods=["GET"])
def shelter_analysis():
    """
    Endpoint to fetch average anxiety levels grouped by shelter.
    """
    query = """
    SELECT Shelter, AVG(CAST(Anxiety_Lvl AS DOUBLE)) AS avg_anxiety
    FROM homeless_data
    WHERE Anxiety_Lvl IS NOT NULL
    GROUP BY Shelter
    ORDER BY avg_anxiety DESC;
    """
    try:
        results = query_athena(query)
        return jsonify(results.to_dict(orient="records"))
    except Exception as e:
        logging.error(f"Error executing shelter analysis query: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
