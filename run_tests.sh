#!/bin/bash
# Quick start script to run Estimator API tests

echo "=========================================="
echo "Estimator API Test Suite - Quick Start"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

echo "✓ Python found: $(python --version)"
echo ""

# Check if requests module is installed
python -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Installing requests module..."
    pip install requests
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install requests module"
        exit 1
    fi
fi

echo "✓ Requests module is available"
echo ""

# Check if server is running
echo "Checking if server is running at http://10.10.13.27:8002..."
curl -s http://10.10.13.27:8002/ > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Server is not running at http://10.10.13.27:8002"
    echo ""
    echo "Please start the server first:"
    echo "  cd /c/eagleeyeau/eagleeyeau"
    echo "  python manage.py runserver 10.10.13.27:8002"
    echo ""
    exit 1
fi

echo "✓ Server is running"
echo ""

# Check if credentials are configured
if grep -q "your_password_here" test_estimator_api.py; then
    echo "⚠ WARNING: Test credentials need to be configured!"
    echo ""
    echo "Please edit test_estimator_api.py and update:"
    echo "  TEST_CREDENTIALS = {"
    echo "    \"email\": \"your_estimator_email@example.com\","
    echo "    \"password\": \"your_actual_password\""
    echo "  }"
    echo ""
    read -p "Press Enter if you have already updated the credentials, or Ctrl+C to cancel..."
fi

echo ""
echo "=========================================="
echo "Starting Test Suite..."
echo "=========================================="
echo ""

# Run the tests
python test_estimator_api.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Tests completed successfully!"
else
    echo "❌ Tests failed or were interrupted"
fi

exit $EXIT_CODE
