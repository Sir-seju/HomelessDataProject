# Use Amazon Lambda Python 3.9 runtime
FROM public.ecr.aws/lambda/python:3.9

# Set working directory
WORKDIR /var/task

# Copy requirements and install dependencies
COPY requirements.txt .
RUN yum install -y gcc libffi-devel python3-devel && \
    pip install --no-cache-dir -r requirements.txt -t . && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    find . -name "*.pyc" -delete && \
    find . -name "*.pyo" -delete

# Copy application code
COPY lambda_function.py .
COPY scripts/ scripts/

# Set the Lambda handler
CMD ["lambda_function.lambda_handler"] 