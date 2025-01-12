# Base image: Ubuntu 22.04 (or your preferred version)
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    python3-pyqt5 \
    software-properties-common \
    wget \
    && apt-get clean

RUN add-apt-repository --yes ppa:kicad/kicad-8.0-releases && \
    apt-get update && \
    apt-get install -y kicad --no-install-recommends && \
    apt-get clean

# Install Python libraries
RUN pip3 install --no-cache-dir \
    streamlit \
    pandas \
    matplotlib \
    plotly \
    numpy \
    scipy \
    ogdf-wheel \
    ogdf-python

# Set the working directory
WORKDIR /app

# Copy your Streamlit app into the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Command to run your Streamlit app
CMD ["streamlit", "run", "app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
