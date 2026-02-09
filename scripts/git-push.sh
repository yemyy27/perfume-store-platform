#!/bin/bash

# Git Push Automation Script
# Usage: ./scripts/git-push.sh "your commit message"

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Git Push Automation...${NC}"

# Check if commit message provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a commit message${NC}"
    echo "Usage: ./scripts/git-push.sh \"your commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# Show current status
echo -e "${YELLOW}Current git status:${NC}"
git status

# Add all changes
echo -e "${YELLOW}Adding all changes...${NC}"
git add .

# Show what will be committed
echo -e "${YELLOW}Files to be committed:${NC}"
git status --short

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "$COMMIT_MESSAGE"

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push origin main

echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
echo -e "${GREEN}View your code at: https://github.com/yemyy27/perfume-store-platform${NC}"
