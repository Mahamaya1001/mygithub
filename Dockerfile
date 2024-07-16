#check the python version & go to docker hub site to get the images
# Use a slim Python image
FROM python:3.12-slim
LABEL maintainer="arun.in"

ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /gen_AI

# Expose the necessary port
EXPOSE 8502 

# Copy the requirements file
COPY requirements.txt .

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libopenblas-dev \
    libomp-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install Python packages
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt

# Add a non-root user
RUN adduser --disabled-password --no-create-home webapp

# Copy the application code
COPY . . 

# Set the PATH environment variable
ENV PATH="/py/bin:$PATH"

# Switch to the non-root user
USER webapp

# Set the entry point and command for the container
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py" ]