
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

if "OptimizationHistory" not in content:
    with open(file_path, "a") as f:
        f.write(new_imports)
