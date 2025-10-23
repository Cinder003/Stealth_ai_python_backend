#!/bin/bash

# Test script for the Unified Code Generation Platform

BASE_URL="http://localhost:6000/api/v1"

echo "Testing Unified Code Generation Platform API"
echo "=============================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$BASE_URL/health" | jq '.'
echo ""
echo ""

# Test 2: Simple Component Generation
echo "2. Generating a simple React button component..."
curl -s -X POST "$BASE_URL/generate_code" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a modern button component with primary and secondary variants, loading state, and disabled state",
    "code_type": "component",
    "framework": "react",
    "styling": "tailwindcss"
  }' | jq '{success, total_files, total_lines, generation_time_seconds, files: [.files[] | {path, size_bytes}]}'
echo ""
echo ""

# Test 3: Production React App
echo "3. Generating a production-ready React app..."
curl -s -X POST "$BASE_URL/generate_code" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a counter app with increment, decrement, and reset buttons. Include dark mode toggle.",
    "code_type": "frontend",
    "framework": "react",
    "production_ready": true,
    "styling": "tailwindcss"
  }' | jq '{success, total_files, total_lines, generation_time_seconds, framework_detected}'
echo ""
echo ""

# Test 4: Node.js Backend API
echo "4. Generating a Node.js REST API..."
curl -s -X POST "$BASE_URL/generate_code" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple REST API for managing tasks with CRUD operations",
    "code_type": "backend",
    "framework": "express",
    "production_ready": true
  }' | jq '{success, total_files, total_lines, generation_time_seconds}'
echo ""
echo ""

# Test 5: Metrics
echo "5. Checking metrics..."
echo "(First few lines only)"
curl -s "$BASE_URL/metrics" | head -n 20
echo ""
echo ""

echo "=============================================="
echo "All tests completed!"
echo ""
echo "View full API docs at: http://localhost:6000/docs"
echo "View Grafana dashboards at: http://localhost:3001 (admin/admin)"
echo ""

