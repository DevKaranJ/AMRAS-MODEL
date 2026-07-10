#!/bin/bash
poetry run mypy app/api/endpoints/qa.py app/models/qa.py app/schemas/qa.py modules/qa/ tests/api/test_qa_endpoints.py tests/modules/test_qa.py
