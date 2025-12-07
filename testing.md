1. Requirements

Before testing, install dependencies:
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt

This project uses:

pytest

pytest-flask

Verify installation: pip install pytest pytest-flask

3. Test Structure

All test scripts are inside:

tests/
│ test_api_endpoints.py
│ test_data_integrity.py
│ test_routing_api.py
│ conftest.py

Tests do NOT require real API keys and do not depend on live data.

4. Configuration

Make sure .env exists : copy .env.example .env
Add: AMBEE_API_KEY=dummy_value

5. Run All Tests

From the project root:

pytest -v