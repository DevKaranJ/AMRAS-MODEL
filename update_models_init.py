
file_path = "app/models/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

new_imports = """
from app.models.optimization import (
    Benchmarks,
    OptimizationHistory,
    PerformanceProfiles,
    ResourceUsage,
    CostReports,
    ModelBenchmarks,
    InferenceCache,
    DeploymentProfiles,
    ArchiveHistory,
    DependencyGraph,
)
"""

# Check if the import block exists by looking for the from statement, not just any occurrence
if "from app.models.optimization import" not in content:
    with open(file_path, "a") as f:
        f.write(new_imports)
