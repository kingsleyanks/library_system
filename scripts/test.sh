#!/bin/bash
# test.sh — runs all tests and reports results

source venv/bin/activate 2>/dev/null

echo "════════════════════════════════════"
echo "  Running Library System Tests"
echo "════════════════════════════════════"

# Run tests and capture exit code
python3 -m pytest tests/ -v 2>&1

# $? captures the exit code of the last command
# 0 = all tests passed, anything else = failures
TEST_RESULT=$?

echo ""
if [ ${TEST_RESULT} -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Some tests failed — exit code: ${TEST_RESULT}"
fi

exit ${TEST_RESULT}