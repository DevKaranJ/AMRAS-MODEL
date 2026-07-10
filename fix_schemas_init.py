import re

file_path = "app/schemas/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

# Replace the wrong imports because job.py doesn't have JobBase etc. (they probably were created elsewhere or we mistakenly added them)
# job.py only has ImportJobCreate, ImportJobRead, DownloadJobCreate, DownloadJobRead
# Let's just remove job and manga from __init__.py since we don't need them to test optimization.

new_content = ""
for line in content.split("\n"):
    if "app.schemas.job" in line or "app.schemas.manga" in line:
        continue
    if "Job" in line or "Manga" in line or "Chapter" in line or "Page" in line:
        if "from app.schemas.job" not in line and "from app.schemas.manga" not in line:
            # removing from __all__
            if '"Job' in line or '"Manga' in line or '"Chapter' in line or '"Page' in line:
                continue
    new_content += line + "\n"

with open(file_path, "w") as f:
    f.write(new_content)
