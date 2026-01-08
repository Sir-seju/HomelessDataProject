# Homeless Data Analytics - Frontend

React-based dashboard for visualizing homelessness data and mental health analytics.

## Features

- **Data Search**: Filter records by year, month, and shelter facility
- **Anxiety Trends**: Line chart visualization of anxiety levels over time
- **Shelter Analysis**: Bar chart comparing anxiety levels across shelters
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- React 18
- Chart.js / react-chartjs-2
- Axios for API calls

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm start
# App available at http://localhost:3000

# Build for production
npm run build
```

## Environment

The frontend connects to the Flask backend API. Update the API URL in `src/App.js`:

```javascript
// Development
http://127.0.0.1:5000

// Production (Elastic Beanstalk)
http://homelessdatabackend-homeless-backend.us-east-1.elasticbeanstalk.com
```

## Deployment

Built assets are deployed to S3 for static hosting via GitLab CI/CD.

```bash
# Manual deployment
aws s3 sync build s3://homeless-frontend/ --delete
```

## Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── App.js        # Main application
│   ├── App.css       # Global styles
│   ├── components/
│   │   ├── Search.js         # Search functionality
│   │   └── Visualization.js  # Chart components
│   └── index.js      # Entry point
└── package.json
```
