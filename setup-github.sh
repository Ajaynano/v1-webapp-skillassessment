#!/bin/bash
# GitHub repository setup script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Skill Management Portal"
else
    print_status "Git repository already initialized"
fi

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    print_status "GitHub CLI detected. You can create repository with:"
    echo "gh repo create skill-management-portal --public --source=. --remote=origin --push"
else
    print_warning "GitHub CLI not found. Please create repository manually at:"
    echo "https://github.com/new"
fi

print_status "Setup GitHub secrets for CI/CD:"
echo "1. Go to: https://github.com/your-username/skill-management-portal/settings/secrets/actions"
echo "2. Add these secrets:"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"

print_status "GitHub Actions workflows created:"
echo "- .github/workflows/deploy.yml (Backend SAM deployment)"
echo "- .github/workflows/deploy-frontend.yml (Frontend deployment)"

print_status "Setup complete! Push to main branch to trigger deployment."