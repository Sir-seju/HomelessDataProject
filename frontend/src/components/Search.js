import axios from 'axios';
import React, { useState } from 'react';
import './Search.css';

function Search() {
    const [year, setYear] = useState('');
    const [month, setMonth] = useState('');
    const [results, setResults] = useState([]);
    const [error, setError] = useState('');

    const handleSearch = async () => {
        try {
            const response = await axios.get(
                `http://homelessdatabackend-homeless-backend.us-east-1.elasticbeanstalk.com/search?year=${year}&month=${month}`
            );
            setResults(response.data);
            setError('');
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to fetch data. Please try again.');
        }
    };

    return (
        <div className="search-container">
            <h2 className="title">Search Homeless Data</h2>
            <div className="form">
                <div className="form-group">
                    <label htmlFor="year">Year:</label>
                    <input
                        id="year"
                        type="text"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="month">Month:</label>
                    <input
                        id="month"
                        type="text"
                        value={month}
                        onChange={(e) => setMonth(e.target.value)}
                    />
                </div>
                <button className="search-button" onClick={handleSearch}>
                    Search
                </button>
            </div>
            {error && <p className="error">{error}</p>}
            <div className="results">
                {results.length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th>Homeless ID</th>
                                <th>Encounter Date</th>
                                <th>First Name</th>
                                <th>Last Name</th>
                                <th>Shelter</th>
                                <th>Anxiety Level</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results.map((result, index) => (
                                <tr key={index}>
                                    <td>{result.homeless_id}</td>
                                    <td>{result.encounter_date}</td>
                                    <td>{result.first_name}</td>
                                    <td>{result.last_name}</td>
                                    <td>{result.shelter}</td>
                                    <td>{result.anxiety_lvl}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No results found.</p>
                )}
            </div>
        </div>
    );
}

export default Search;