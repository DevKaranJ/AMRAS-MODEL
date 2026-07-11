
file_path = "modules/optimization/agents.py"
with open(file_path, "r") as f:
    content = f.read()

# Add list import if missing (it should be there but maybe we appended)
# Actually, the first chunk had `from typing import Any, Dict, List`.
# Let's check why mypy and ruff complained... Oh, I used append (`>>`) and it might have appended at the end without realizing the top already had it?
# No, `List` was probably removed by ruff if it was unused in chunk 1.
if "from typing import Any, Dict" in content:
    content = content.replace("from typing import Any, Dict", "from typing import Any, Dict, List")

with open(file_path, "w") as f:
    f.write(content)
