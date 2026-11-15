#!/bin/bash
# Ironory — Comprehensive Test Suite Runner
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Running Ironory Automated Verification Suite ==="
cd "$ROOT_DIR"

# 1. Backend Pytest Suite
echo "1. Running Backend Unit & Integration Tests..."
.venv/bin/pytest backend/tests -v

# 2. Frontend Type Checking
echo "2. Running Frontend TypeScript Verification..."
cd "$ROOT_DIR/frontend"
npm run type-check

# 3. Frontend Production Build Check
echo "3. Running Frontend Production Build Verification..."
npm run build

echo "=== All Ironory Foundation Verification Checks Passed Successfully! ==="
