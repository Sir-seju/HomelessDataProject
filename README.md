# Homeless Data Analytics Platform

A cloud-native geospatial data analytics platform for analyzing homelessness patterns, demographics, and mental health indicators across shelter facilities.

---

## Project Background

This project was developed as a **technical pilot for an interview with a GeoSpatial Data Analytics company**. The challenge was to demonstrate end-to-end data engineering and cloud architecture capabilities by building a functional analytics platform that could:

- Ingest and process heterogeneous datasets (demographics + mental health indicators)
- Store data efficiently for analytical queries at scale
- Provide real-time visualization and exploration capabilities
- Deploy infrastructure using modern DevOps practices

The solution showcases expertise in **AWS serverless architecture**, **ETL pipeline design**, **data lake patterns**, and **full-stack development** - demonstrating the ability to translate raw data into actionable insights through well-architected cloud infrastructure.

---

## Architecture Overview

```
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                        AWS Cloud                             │
                                    │                                                              │
┌──────────────┐                    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│   Raw Data   │ ───Upload───────────▶ │     S3      │───▶│   Lambda    │───▶│  S3 (Parquet)   │  │
│   (CSV)      │                    │  │  (Landing)  │    │   (ETL)     │    │  (Data Lake)    │  │
└──────────────┘                    │  └─────────────┘    └─────────────┘    └────────┬────────┘  │
                                    │                                                  │          │
                                    │                                                  ▼          │
┌──────────────┐                    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│   React      │◀────API─────────────── │  Elastic    │◀───│    Flask    │◀───│     Athena      │  │
│   Frontend   │                    │  │  Beanstalk  │    │   Backend   │    │   (Analytics)   │  │
└──────────────┘                    │  └─────────────┘    └─────────────┘    └─────────────────┘  │
       │                            │                                                              │
       │                            │  ┌──────────────────────────────────────────────────────┐   │
       └──S3 Static Hosting─────────│  │                    Terraform IaC                      │   │
                                    │  │    (VPC, IAM, Elastic Beanstalk, Lambda, Athena)      │   │
                                    │  └──────────────────────────────────────────────────────┘   │
                                    │                                                              │
                                    └─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React, Chart.js, Axios |
| **Backend API** | Flask, Flask-CORS, PyAthena |
| **ETL Pipeline** | AWS Lambda, Pandas, PyArrow |
| **Data Storage** | S3 (CSV landing, Parquet data lake) |
| **Analytics Engine** | AWS Athena (Presto SQL) |
| **Infrastructure** | Terraform, AWS Elastic Beanstalk |
| **CI/CD** | GitLab CI/CD |
| **Deployment** | S3 Static Hosting, Elastic Beanstalk |

---

## Project Structure

```
HomelessDataProject/
├── backend/                    # Flask REST API
│   ├── application.py          # Main API endpoints
│   ├── requirements.txt        # Python dependencies
│   └── .elasticbeanstalk/      # EB deployment config
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── App.js              # Main application component
│   │   └── components/         # Reusable components
│   ├── public/                 # Static assets
│   └── package.json            # Node dependencies
│
├── etl-lambda/                 # Serverless ETL
│   ├── lambda_function.py      # Lambda handler
│   ├── scripts/
│   │   └── process_csvs.py     # Data processing logic
│   ├── Dockerfile              # Container deployment option
│   └── requirements.txt
│
├── terraform/                  # Infrastructure as Code
│   ├── homeless-backend/       # Backend infrastructure
│   │   ├── main.tf
│   │   ├── dev-vpc/            # VPC configuration
│   │   ├── iam/                # IAM roles and policies
│   │   └── data/dynamodb/      # DynamoDB tables
│   └── modules/                # Reusable Terraform modules
│       ├── vpc/
│       ├── elasticbeanstalk-alb/
│       └── terraform-aws-security-group/
│
├── data/                       # Data utilities
│   └── automation/
│       └── s3_upload.py        # Test data upload script
│
├── docs/                       # Documentation
├── .gitlab-ci.yml              # CI/CD pipeline
└── README.md
```

---

## Features

### Data Ingestion & Processing
- **Automated ETL**: S3 event-triggered Lambda function processes incoming CSV files
- **Data Normalization**: Standardizes homeless IDs, dates, and demographics across datasets
- **Parquet Conversion**: Transforms CSV to columnar Parquet format for efficient querying
- **Partitioning**: Data partitioned by Year/Month for optimized Athena performance

### Analytics API
- **Search Endpoint** (`/search`): Filter data by year, month, and shelter
- **Visualization Endpoint** (`/visualize`): Anxiety level trends over time
- **Shelter Analysis** (`/shelter_analysis`): Compare anxiety levels across shelters
- **Bulk Data** (`/all`): Retrieve full dataset for exploration

### Interactive Dashboard
- **Data Search**: Filter and explore records by multiple criteria
- **Trend Visualization**: Line charts showing anxiety levels over time
- **Shelter Comparison**: Bar charts comparing mental health metrics across facilities
- **Responsive Design**: Mobile-friendly interface

---

## Data Model

The platform merges two primary datasets:

**Anxiety Data**
| Field | Type | Description |
|-------|------|-------------|
| Homeless_ID | STRING | Unique identifier (normalized) |
| Encounter_Date | TIMESTAMP | Date of assessment |
| Anxiety_Lvl | INTEGER | Anxiety level (1-10 scale) |

**Demographics Data**
| Field | Type | Description |
|-------|------|-------------|
| HID | STRING | Homeless identifier |
| Registration_Date | DATE | Shelter registration date |
| First_Name, Last_Name | STRING | Name fields |
| Date_Of_Birth | DATE | Birth date |
| Gender | STRING | Gender identity |
| Race1 | STRING | Primary race/ethnicity |
| Shelter | STRING | Current shelter facility |

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.12+
- AWS CLI configured
- Terraform 1.0+

### Local Development

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python application.py
# API available at http://localhost:5000
```

**Frontend**
```bash
cd frontend
npm install
npm start
# App available at http://localhost:3000
```

### Infrastructure Deployment

```bash
cd terraform/homeless-backend

# Initialize and deploy VPC
cd dev-vpc && terraform init && terraform apply

# Deploy IAM roles
cd ../iam && terraform init && terraform apply

# Deploy Elastic Beanstalk
cd .. && terraform init && terraform apply
```

---

## API Reference

### Search Data
```http
GET /search?year=2019&month=06&shelter=Happy%20Shelter
```

### Get Anxiety Trends
```http
GET /visualize
```
Returns average anxiety levels grouped by encounter date.

### Shelter Analysis
```http
GET /shelter_analysis
```
Returns average anxiety levels grouped by shelter facility.

---

## CI/CD Pipeline

The GitLab CI/CD pipeline automates:

1. **Test Stage**: Runs backend unit tests
2. **Build Stage**: Builds React production bundle
3. **Deploy Stage**:
   - Backend → AWS Elastic Beanstalk
   - Frontend → S3 Static Hosting
   - ETL Lambda → AWS Lambda function update

Deploy jobs are manual (`when: manual`) for controlled releases.

---

## Key Engineering Decisions

| Decision | Rationale |
|----------|-----------|
| **Athena over RDS** | Serverless, pay-per-query model ideal for analytical workloads |
| **Parquet format** | Columnar storage reduces query costs by 30-90% vs CSV |
| **Year/Month partitioning** | Enables partition pruning for time-based queries |
| **Elastic Beanstalk** | Managed platform simplifies deployment while allowing customization |
| **Terraform modules** | Reusable infrastructure patterns for consistency |

---

## Future Enhancements

- [ ] Add authentication (AWS Cognito)
- [ ] Implement geospatial visualization with Mapbox/Leaflet
- [ ] Add predictive analytics for shelter capacity planning
- [ ] Enable real-time data streaming with Kinesis
- [ ] Add data quality monitoring with Great Expectations

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Author

**Uwasan Maku** - Senior DevSecOps Engineer

[LinkedIn](https://www.linkedin.com/in/uwasan-maku) | [GitHub](https://github.com/Sir-seju)
