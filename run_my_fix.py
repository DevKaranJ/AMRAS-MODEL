# I think the core issue is tests/conftest.py override not using AsyncSession properly for some tests
with open("tests/conftest.py", "r") as f:
    content = f.read()

print("Checking conftest...")
