import axios from "axios";
import "chart.js/auto";
import React, { useState } from "react";
import { Bar, Line } from "react-chartjs-2";
import "./App.css"; // Ensure this file exists for custom styling

function App() {
  const [searchResults, setSearchResults] = useState([]);
  const [chartData, setChartData] = useState(null);
  const [shelterChartData, setShelterChartData] = useState(null);
  const [year, setYear] = useState("");
  const [shelter, setShelter] = useState("");
  const [month, setMonth] = useState("");

  const preprocessData = (data) => {
    return data.map((item) => ({
      ...item,
      date_of_birth: new Date(item.date_of_birth).toISOString().split("T")[0], // Format to YYYY-MM-DD
      encounter_date: new Date(item.encounter_date).toISOString().split("T")[0], // Format to YYYY-MM-DD
      registration_date: new Date(item.registration_date).toISOString().split("T")[0], // Format to YYYY-MM-DD
    }));
  };

  const fetchSearchResults = async () => {
    try {
      const response = await axios.get(
        `http://homelessdatabackend-homeless-backend.us-east-1.elasticbeanstalk.com/search?year=${year}&month=${month}&shelter=${shelter}`
      );
      setSearchResults(preprocessData(response.data));
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await axios.get("http://homelessdatabackend-homeless-backend.us-east-1.elasticbeanstalk.com/visualize");

      // Preprocess the data to format the dates
      const dates = response.data.map((item) =>
        new Date(item.encounter_date).toISOString().split("T")[0]
      );
      const avgAnxiety = response.data.map((item) => item.avg_anxiety);

      setChartData({
        labels: dates, // Use the formatted dates
        datasets: [
          {
            label: "Average Anxiety Levels",
            data: avgAnxiety,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            borderWidth: 2,
            tension: 0.4,
          },
        ],
      });
    } catch (error) {
      console.error("Error fetching trends:", error);
    }
  };

  const fetchShelterAnalysis = async () => {
    try {
      const response = await axios.get("http://homelessdatabackend-homeless-backend.us-east-1.elasticbeanstalk.com/shelter_analysis");

      const shelters = response.data.map((item) => item.Shelter);
      const avgAnxiety = response.data.map((item) => item.avg_anxiety);

      setShelterChartData({
        labels: shelters,
        datasets: [
          {
            label: "Average Anxiety Levels by Shelter",
            data: avgAnxiety,
            backgroundColor: "rgba(153, 102, 255, 0.6)",
            borderColor: "rgba(153, 102, 255, 1)",
            borderWidth: 1,
          },
        ],
      });
    } catch (error) {
      console.error("Error fetching shelter analysis data:", error);
    }
  };


  return (
    <div className="container">
      <header>
        <h1>Homeless Data Project</h1>
      </header>

      {/* Search Section */}
      <section className="search-section">
        <h2>Search Data</h2>
        <div className="search-inputs">
          <label>
            Year:
            <input
              type="text"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              placeholder="Enter year (e.g., 2019)"
            />
          </label>
          <label>
            Month:
            <input
              type="text"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              placeholder="Enter month (e.g., 01)"
            />
          </label>
          <label>
            Shelter:
            <input
              type="text"
              value={shelter}
              onChange={(e) => setShelter(e.target.value)}
              placeholder="Enter shelter name"
            />
          </label>
          <button onClick={fetchSearchResults}>Search</button>
        </div>

        {/* Search Results Table */}
        {searchResults.length > 0 && (
          <div className="table-container">
            <h3>Search Results</h3>
            <table>
              <thead>
                <tr>
                  {Object.keys(searchResults[0]).map((key) => (
                    <th key={key}>{key.replace("_", " ").toUpperCase()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {searchResults.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, idx) => (
                      <td key={idx}>{value}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Visualization Section */}
      <section className="visualize-section">
        <h2>Visualize Anxiety Trends</h2>
        <button onClick={fetchTrends}>View Trends</button>
        {chartData && (
          <div className="chart-container">
            <Line data={chartData} />
          </div>
        )}
      </section>

      {/* Shelter Analysis Section */}
      <section className="shelter-analysis-section">
        <h2>Analyze Anxiety Levels by Shelter</h2>
        <button onClick={fetchShelterAnalysis} className="btn btn-success">
          View Shelter Analysis
        </button>
        {shelterChartData && (
          <div className="chart-container">
            <Bar data={shelterChartData} />
          </div>
        )}
      </section>
    </div>
  );
}

export default App;