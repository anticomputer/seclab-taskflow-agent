#!/bin/bash
set -e

echo "🚀 Setting up Seclab Taskflow Agent development environment..."

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment and install dependencies
echo "📥 Installing Python dependencies..."
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# GitHub Copilot Token (required)
# Get a token from a GitHub account with Copilot access
COPILOT_TOKEN=

# Optional: GitHub Personal Access Token for GitHub MCP tools
GITHUB_PERSONAL_ACCESS_TOKEN=

# Optional: CodeQL database base path
CODEQL_DBS_BASE_PATH=/workspaces/seclab-taskflow-agent/my_data

# Optional: MCP server configurations
# Add any additional environment variables needed for your MCP servers here

EOF
    echo "⚠️  Please configure your .env file with required tokens!"
fi

# If running in Codespaces, add secrets to .env
if [ -n "$CODESPACES" ]; then
    echo "🔐 Running in Codespaces - injecting secrets from Codespaces settings..."
    if [ -n "$COPILOT_TOKEN" ]; then
        echo "COPILOT_TOKEN=${COPILOT_TOKEN}" >> .env
        echo "✅ COPILOT_TOKEN added from Codespaces secrets"
    fi
    if [ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
        echo "GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_PERSONAL_ACCESS_TOKEN}" >> .env
        echo "✅ GITHUB_PERSONAL_ACCESS_TOKEN added from Codespaces secrets"
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Create optional data directories
mkdir -p my_data

echo "✅ Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "Configure your .env file with COPILOT_TOKEN"
echo ""
echo "💡 Remember to activate the virtual environment: source .venv/bin/activate"
