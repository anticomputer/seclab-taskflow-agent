# Use Ubuntu 24.04 as base image to match the current environment
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install system dependencies
# Note: Python and Git are installed via devcontainer features
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspaces/seclab-taskflow-agent

# The rest of the setup will be done in post-create script
