import re

file_path = "app/models/__init__.py"
with open(file_path, "r") as f:
    content = f.read()

models = [
    "Benchmarks",
    "OptimizationHistory",
    "PerformanceProfiles",
    "ResourceUsage",
    "CostReports",
    "ModelBenchmarks",
    "InferenceCache",
    "DeploymentProfiles",
    "ArchiveHistory",
    "DependencyGraph",
]

all_match = re.search(r"__all__\s*=\s*\[([\s\S]*?)\]", content)
if all_match:
    current_all = all_match.group(1)
    for model in models:
        if f'"{model}"' not in current_all:
            current_all += f'    "{model}",\n'

    new_content = content[: all_match.start(1)] + "\n" + current_all + content[all_match.end(1) :]
    with open(file_path, "w") as f:
        f.write(new_content)
