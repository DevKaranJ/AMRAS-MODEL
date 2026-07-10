import pytest

from modules.optimization.agents import (
    AIRoutingAgent,
    BenchmarkAgent,
    CacheOptimizationAgent,
    CostOptimizationAgent,
    CPUSchedulerAgent,
    DeploymentAgent,
    GPUSchedulerAgent,
    OptimizationManagerAgent,
    PerformanceLearningAgent,
    QAAgent,
    StorageOptimizationAgent,
)


@pytest.mark.asyncio
async def test_optimization_manager() -> None:
    agent = OptimizationManagerAgent()
    result = await agent.run_optimization(project_id=10)
    assert result["status"] == "success"
    assert result["project_id"] == 10
    assert "optimizations_applied" in result


@pytest.mark.asyncio
async def test_gpu_scheduler() -> None:
    agent = GPUSchedulerAgent()
    result = await agent.schedule(required_vram=4096.0)
    assert result["status"] == "scheduled"
    assert result["allocated_vram_mb"] == 4096.0
    assert "assigned_gpu_id" in result


@pytest.mark.asyncio
async def test_cpu_scheduler() -> None:
    agent = CPUSchedulerAgent()
    result = await agent.schedule(required_threads=4)
    assert result["status"] == "scheduled"
    assert result["assigned_threads"] == 4


@pytest.mark.asyncio
async def test_performance_learning() -> None:
    agent = PerformanceLearningAgent()
    result = await agent.generate_recommendations()
    assert len(result) > 0
    assert "recommendation" in result[0]


@pytest.mark.asyncio
async def test_cache_optimization() -> None:
    agent = CacheOptimizationAgent()
    result = await agent.optimize()
    assert result["status"] == "success"
    assert result["items_removed"] > 0


@pytest.mark.asyncio
async def test_storage_optimization() -> None:
    agent = StorageOptimizationAgent()
    result = await agent.optimize()
    assert result["status"] == "success"
    assert result["files_compressed"] >= 0


@pytest.mark.asyncio
async def test_ai_routing() -> None:
    agent = AIRoutingAgent()
    result = await agent.route_request("ocr", {"priority": "speed"})
    assert "selected_model" in result
    assert "provider" in result


@pytest.mark.asyncio
async def test_cost_optimization() -> None:
    agent = CostOptimizationAgent()
    result = await agent.estimate_cost({"gpu_hours": 2})
    assert result["total_estimated_cost"] > 0
    assert "recommendation" in result


@pytest.mark.asyncio
async def test_benchmark_agent() -> None:
    agent = BenchmarkAgent()
    result = await agent.run_benchmark("database")
    assert result["status"] == "completed"
    assert result["component"] == "database"


@pytest.mark.asyncio
async def test_deployment_agent() -> None:
    agent = DeploymentAgent()
    result = await agent.prepare_package("docker")
    assert result["status"] == "ready"
    assert result["target_env"] == "docker"
    assert "package_path" in result


@pytest.mark.asyncio
async def test_qa_agent() -> None:
    agent = QAAgent()
    result = await agent.validate({"change": "use_local_llm"})
    assert result["valid"] is True
    assert result["risk_level"] in ["low", "medium", "high"]
