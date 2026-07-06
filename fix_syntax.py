with open("tests/test_memory.py", "r") as f:
    content = f.read()

content = content.replace("mock_session: Any) -> None:", "mock_session: Any) -> None:")  # Check if valid
with open("tests/test_memory.py", "w") as f:
    f.write(content)
