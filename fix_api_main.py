
file_path = "app/api/main.py"
with open(file_path, "r") as f:
    content = f.read()

imports = """
from app.api.endpoints.optimization import router as optimization_router
from app.api.endpoints.deployment import router as deployment_router
"""

registrations = """
app.include_router(optimization_router, prefix="/optimization", tags=["optimization"])
app.include_router(deployment_router, prefix="/deployment", tags=["deployment"])
"""

if "optimization_router" not in content:
    # insert imports before setup_logging
    idx = content.find("setup_logging()")
    if idx != -1:
        content = content[:idx] + imports + "\n" + content[idx:]

    # insert registrations before @app.exception_handler(AmrasException)
    idx2 = content.find("@app.exception_handler(AmrasException)")
    if idx2 != -1:
        content = content[:idx2] + registrations + "\n" + content[idx2:]

    with open(file_path, "w") as f:
        f.write(content)
