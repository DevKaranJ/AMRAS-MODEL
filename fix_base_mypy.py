
file_path = "app/models/base.py"
with open(file_path, "r") as f:
    content = f.read()

# Replace Base with typing Any if needed, but wait, usually sqlalchemy DeclarativeBase is supported if mypy sqlalchemy plugin is used or ignoring is set.
# But let's check what mypy error says: `app/models/base.py:8: error: Class cannot subclass "DeclarativeBase" (has type "Any")  [misc]`
# This is a common issue with Mypy and SQLAlchemy 2.0 without the plugin, or it just needs `type: ignore`.
# Only replace the exact declaration if it doesn't already have the type: ignore annotation
if "class Base(DeclarativeBase):  # type: ignore" not in content:
    content = content.replace("class Base(DeclarativeBase):", "class Base(DeclarativeBase):  # type: ignore")

with open(file_path, "w") as f:
    f.write(content)
