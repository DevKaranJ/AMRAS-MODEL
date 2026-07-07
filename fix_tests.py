with open("tests/test_memory.py", "r") as f:
    content = f.read()

# Fix mock setup for AsyncMock scalar_one_or_none
content = content.replace(
    "mock_session.execute.return_value.scalar_one_or_none.return_value = None",
    "mock_session.execute.return_value.scalar_one_or_none.return_value = None",
)

content = content.replace(
    "mock_session.execute.return_value.scalar_one_or_none.return_value = existing_memory",
    "mock_session.execute.return_value.scalar_one_or_none.return_value = existing_memory",
)

# We need to properly mock async iterator/scalar_one_or_none
# The issue is we need an async method return. We should set `return_value` to a mock that has a `scalar_one_or_none` which is a synchronous method returning the value on the Result object.
# wait, result.scalar_one_or_none() is NOT async in SQLAlchemy 2.0 unless we await the execute.
# Let's fix the tests by replacing the `mock_session` fixture and how execute works.
