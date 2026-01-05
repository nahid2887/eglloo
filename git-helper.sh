#!/bin/bash

# Git Helper Script - Common Commands

echo "🚀 EagleEyeau Git Helper"
echo "========================"
echo ""
echo "Usage: bash git-helper.sh <command>"
echo ""
echo "Commands:"
echo ""
echo "  setup                 - Initial git setup (first time only)"
echo "  status                - Show current git status"
echo "  push <message>        - Stage, commit, and push changes"
echo "  pull                  - Pull latest changes from develop"
echo "  pull-main             - Pull latest from main branch"
echo "  feature <name>        - Create new feature branch"
echo "  switch <branch>       - Switch to different branch"
echo "  branches              - List all branches"
echo "  log                   - Show commit history"
echo ""

if [ "$1" = "setup" ]; then
    echo "Setting up git configuration..."
    read -p "Enter your name: " name
    read -p "Enter your email: " email
    git config --global user.name "$name"
    git config --global user.email "$email"
    git config --global core.editor vim
    echo "✅ Git configured!"

elif [ "$1" = "status" ]; then
    git status

elif [ "$1" = "push" ]; then
    if [ -z "$2" ]; then
        echo "❌ Please provide a commit message"
        echo "Usage: bash git-helper.sh push 'Your message here'"
        exit 1
    fi
    echo "📝 Staging changes..."
    git add .
    echo "💾 Committing with message: '$2'"
    git commit -m "$2"
    echo "📤 Pushing to remote..."
    git push origin develop
    echo "✅ Changes pushed!"

elif [ "$1" = "pull" ]; then
    echo "📥 Pulling latest changes from develop..."
    git fetch origin
    git pull origin develop
    echo "✅ Updated!"

elif [ "$1" = "pull-main" ]; then
    echo "📥 Pulling latest changes from main..."
    git fetch origin
    git pull origin main
    echo "✅ Updated!"

elif [ "$1" = "feature" ]; then
    if [ -z "$2" ]; then
        echo "❌ Please provide a feature name"
        echo "Usage: bash git-helper.sh feature 'user-authentication'"
        exit 1
    fi
    echo "🌿 Creating feature branch: feature/$2"
    git checkout -b feature/$2
    echo "✅ Branch created! Now make your changes and push."

elif [ "$1" = "switch" ]; then
    if [ -z "$2" ]; then
        echo "❌ Please provide a branch name"
        exit 1
    fi
    git checkout $2
    echo "✅ Switched to $2"

elif [ "$1" = "branches" ]; then
    echo "📋 Local branches:"
    git branch
    echo ""
    echo "📡 Remote branches:"
    git branch -r

elif [ "$1" = "log" ]; then
    git log --oneline -10

else
    echo "❌ Unknown command: $1"
    echo "Run: bash git-helper.sh (no arguments) for help"
fi
