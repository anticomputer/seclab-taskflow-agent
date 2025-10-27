# SPDX-FileCopyrightText: 2025 GitHub
# SPDX-License-Identifier: MIT

import os
import shutil
import subprocess
import sys
import tempfile

def read_file_list(list_path):
    """
    Reads a file containing file paths, ignoring empty lines and lines starting with '#'.
    Returns a list of relative file paths.
    """
    with open(list_path, "r") as f:
        lines = [line.strip() for line in f]
    return [line for line in lines if line and not line.startswith("#")]

def copy_files_to_dir(file_list, dest_dir):
    """
    Copies files to dest_dir, preserving their relative paths.
    """
    for rel_path in file_list:
        abs_src = os.path.abspath(rel_path)
        abs_dest = os.path.abspath(os.path.join(dest_dir, rel_path))
        os.makedirs(os.path.dirname(abs_dest), exist_ok=True)
        shutil.copy2(abs_src, abs_dest)

def write_dockerfile(dest_dir, entrypoint):
    """
    Writes a Dockerfile that installs Python dependencies, GitHub CLI, and CodeQL CLI.
    """
    dockerfile = f'''
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    unzip \\
    git \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (debian)
RUN apt-get update \\
    && install -m 0755 -d /etc/apt/keyrings \\
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \\
    && chmod a+r /etc/apt/keyrings/docker.asc \\
    && echo \\
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \\
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \\
    tee /etc/apt/sources.list.d/docker.list > /dev/null \\
    && apt-get update && apt-get install -y docker-ce-cli \\
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \\
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \\
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \\
    && apt-get update \\
    && apt-get install -y gh \\
    && rm -rf /var/lib/apt/lists/*

# Install CodeQL CLI
ENV CODEQL_VERSION=2.23.0
RUN curl -Ls -o /tmp/codeql.zip https://github.com/github/codeql-cli-binaries/releases/download/v$CODEQL_VERSION/codeql-linux64.zip \\
    && unzip /tmp/codeql.zip -d /opt \\
    && mv /opt/codeql /opt/codeql-cli \\
    && ln -s /opt/codeql-cli/codeql /usr/local/bin/codeql \\
    && rm /tmp/codeql.zip

COPY . /app

# Install CodeQL pack dependencies
RUN codeql pack install /app/mcp_servers/codeql/queries/mcp-cpp
RUN codeql pack install /app/mcp_servers/codeql/queries/mcp-js

# Install Python dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

ENTRYPOINT ["python", "{entrypoint}"]
'''
    with open(os.path.join(dest_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile)

def get_image_digest(image_name, tag):
    result = subprocess.run(
        ["docker", "buildx", "imagetools", "inspect", f"{image_name}:{tag}"],
        stdout=subprocess.PIPE, check=True, text=True
    )
    for line in result.stdout.splitlines():
        if line.strip().startswith("Digest:"):
            return line.strip().split(":", 1)[1].strip()
    return None

def build_and_push_image(dest_dir, image_name, tag):
    # Build
    subprocess.run([
        "docker", "buildx", "build", "--platform", "linux/amd64", "-t", f"{image_name}:{tag}", dest_dir
    ], check=True)
    # Push
    subprocess.run([
        "docker", "push", f"{image_name}:{tag}"
    ], check=True)
    print(f"Pushed {image_name}:{tag}")
    digest = get_image_digest(image_name, tag)
    print(f"Image digest: {digest}")
    with open("/tmp/digest.txt", "w") as f:
        f.write(digest)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python build_and_publish_docker.py <file_list.txt> <entrypoint.py> <ghcr_username/repo> <tag>")
        print("Example: python build_and_publish_docker.py files.txt main.py ghcr.io/anticomputer/my-python-app latest")
        sys.exit(1)

    file_list_path = sys.argv[1]
    entrypoint_py = sys.argv[2]
    image_name = sys.argv[3]
    tag = sys.argv[4]

    # Read file paths
    file_list = read_file_list(file_list_path)

    with tempfile.TemporaryDirectory() as build_dir:
        # Copy files
        copy_files_to_dir(file_list, build_dir)
        # Write Dockerfile
        write_dockerfile(build_dir, entrypoint_py)
        # Build and push image
        build_and_push_image(build_dir, image_name, tag)
