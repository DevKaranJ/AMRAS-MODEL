with open("tests/test_memory.py", "r") as f:
    content = f.read()

content = content.replace("def __init__(self, value):", "def __init__(self, value: 'Any') -> None:")
content = content.replace("def scalar_one_or_none(self):", "def scalar_one_or_none(self) -> 'Any':")
content = content.replace("def mock_session():", "def mock_session() -> 'Any':")
content = content.replace("async def test_", "async def test_")
for line in content.split("\n"):
    if line.startswith("async def test_"):
        content = content.replace(line, line.replace("):", ") -> None:"))

with open("tests/test_memory.py", "w") as f:
    f.write("from typing import Any\n" + content)

with open("tests/test_memory_api.py", "r") as f:
    content2 = f.read()

for line in content2.split("\n"):
    if line.startswith("async def test_"):
        content2 = content2.replace(line, line.replace("):", ") -> None:"))

with open("tests/test_memory_api.py", "w") as f:
    f.write(content2)
