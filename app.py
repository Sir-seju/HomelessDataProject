from flask import Flask, jsonify, render_template, request
from pyathena import connect
import pandas as pd
import plotly.express as px
import os

# Initialize Flask app
app = Flask(__name__)

# Athena configuration
ATHENA_DATABASE = "default"
ATHENA_OUTPUT = "s3://graystumbucket/Queries/"
REGION = "us-east-1"

def query_athena(sql_query):
    """
    Execute a query on Athena and return the results as a Pandas DataFrame.
    """
    conn = connect(s3_staging_dir=ATHENA_OUTPUT, region_name=REGION)
    df = pd.read_sql(sql_query, conn)
    return df

@app.route("/")
def index():
    """
    Home page.
    """
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    """
    Search endpoint to filter Athena data.
    """
    year = request.args.get("year")
    month = request.args.get("month")
    shelter = request.args.get("shelter")

    # Start building the query
    query = "SELECT * FROM homeless_data WHERE 1=1"
    
    # Add conditions dynamically
    if year:
        query += f" AND Year = '{year}'"
    if month:
        query += f" AND Month = '{month}'"
    if shelter:
        # Escape single quotes in the shelter string
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
    SELECT Encounter_Date, AVG(CAST(Anxiety_Lvl AS DOUBLE)) as avg_anxiety
    FROM homeless_data
    WHERE Anxiety_Lvl IS NOT NULL
    GROUP BY Encounter_Date
    ORDER BY Encounter_Date;
    """
    results = query_athena(query)

    # Generate a Plotly visualization
    fig = px.line(results, x="Encounter_Date", y="avg_anxiety", title="Average Anxiety Level Over Time")
    fig.update_layout(template="plotly_dark")

    # Render the chart as HTML
    return fig.to_html()

if __name__ == "__main__":
    app.run(debug=True)