# Homeless Data Project

This project is a pilot solution for analyzing and visualizing data related to homelessness. It includes tools to merge and process datasets, serve processed data via a RESTful API, and automate data updates using cloud services. The project leverages Flask, AWS S3, and GitLab CI/CD for seamless deployment and management.

---

## Table of Contents
1. [Overview](#overview)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [Setup Instructions](#setup-instructions)
   - [Backend Setup](#backend-setup)
5. [Usage](#usage)
   - [Running the Backend](#running-the-backend)
6. [GitLab CI/CD Integration](#gitlab-cicd-integration)
7. [Next Steps](#next-steps)
8. [Contributors](#contributors)

---

## Overview
This project integrates two key datasets:
- **SF_HOMELESS_ANXIETY.csv**: Contains data on anxiety levels among homeless individuals.
- **SF_HOMELESS_DEMOGRAPHICS.csv**: Includes demographic information.

The project:
1. Processes and merges datasets using Python and uploads the result to AWS S3.
2. Serves the processed data via a Flask API.
3. Automates deployment and data updates using GitLab CI/CD.

---

## Technologies Used
- **Python**: For data processing and backend API (Flask).
- **AWS S3**: Cloud storage for processed data.
- **GitLab CI/CD**: Continuous integration and deployment pipeline.

---

## Project Structure
```plaintext
project-root/
│
├── backend/
│   ├── app.py                # Flask backend API
│   ├── scripts/
│   │   └── data_alignment.py # Script to merge datasets and upload to S3
│   └── requirements.txt      # Backend dependencies
│
├── .gitlab-ci.yml            # GitLab CI/CD configuration
└── README.md                 # Project documentation


Setup Instructions
Prerequisites
Python: Version 3.9+
AWS CLI: For managing AWS resources.
Backend Setup
Clone the repository:

bash
Copy code
git clone <repository-url>
cd project-root
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r backend/requirements.txt
Add your AWS credentials:

Use environment variables:
bash
Copy code
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=<your-region>
Run the backend API:

bash
Copy code
python backend/app.py
Usage
Running the Backend
The Flask API serves data from AWS S3:

Endpoint: http://127.0.0.1:5000/data
You can query the data through the /data endpoint, which fetches the merged dataset from S3 and returns it as JSON.

GitLab CI/CD Integration
The project uses GitLab CI/CD for automation:

Backend Deployment:
Deployed to AWS Lambda using Zappa.
Dataset Updates:
Automatically merges new datasets and updates S3 using a Python script.
Example .gitlab-ci.yml File
yaml
Copy code
stages:
  - deploy

deploy_backend:
  image: python:3.9
  stage: deploy
  script:
    - pip install zappa
    - zappa deploy production
  only:
    - main

update_dataset:
  image: python:3.9
  stage: deploy
  script:
    - pip install boto3 pandas
    - python backend/scripts/data_alignment.py
  only:
    - main
Next Steps
Automate Dataset Updates:
Use AWS Lambda to trigger updates when new files are uploaded to S3.
Deploy the Application:
Backend: Deploy Flask API to AWS Lambda or AWS Elastic Beanstalk.
Enhance Monitoring and Optimization:
Set up AWS CloudWatch for monitoring.
Optimize API performance and storage costs.

