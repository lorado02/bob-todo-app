#!/bin/bash

# Run tests with coverage
echo "Running tests with coverage..."
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html --cov-config=.coveragerc

# Display coverage summary
echo ""
echo "Coverage report generated in htmlcov/index.html"

# Made with Bob
