import pytest  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.models.base import Base  # noqa: E402
from app.models.core import Job  # noqa: E402
from modules.production.agents.asset import AssetManagerAgent  # noqa: E402
from modules.production.agents.model import AIModelManagerAgent  # noqa: E402
from modules.production.agents.qa import QAAgent  # noqa: E402
from modules.production.agents.queue import QueueItem, QueueManagerAgent  # noqa: E402
from modules.production.agents.recovery import RecoveryAgent  # noqa: E402
from modules.production.agents.settings import SettingsAgent  # noqa: E402
from modules.production.agents.workflow import PipelineStageConfig, WorkflowManagerAgent  # noqa: E402

pytestmark = pytest.mark.asyncio

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

from typing import AsyncGenerator  # noqa: E402


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


async def test_workflow_manager_agent(db_session: AsyncSession) -> None:
    # Setup dummy job
    job = Job(name="test_job", status="queued")
    db_session.add(job)
    await db_session.flush()  # Ensure ID is generated without detaching/expiring
    job_id = job.id

    agent = WorkflowManagerAgent()
    stages = [PipelineStageConfig(stage_name="ocr"), PipelineStageConfig(stage_name="story", dependencies=["ocr"])]

    result = await agent.execute_pipeline(job_id, stages, db_session)
    assert result["status"] == "started"
    assert result["stages_scheduled"] == 2
    assert result["job_id"] == job_id

    pause_res = await agent.pause_workflow(job_id, db_session)
    assert pause_res["status"] == "paused"
    assert pause_res["job_id"] == job_id

    cancel_res = await agent.cancel_workflow(job_id, db_session)
    assert cancel_res["status"] == "canceled"
    assert cancel_res["job_id"] == job_id

    resume_res = await agent.resume_workflow(job_id, "story", db_session)
    assert resume_res["status"] == "resumed"
    assert resume_res["job_id"] == job_id

    retry_res = await agent.retry_stage(job_id, "ocr", db_session)
    assert retry_res["status"] == "retrying"
    assert retry_res["job_id"] == job_id


async def test_queue_manager_agent() -> None:
    agent = QueueManagerAgent()
    item = QueueItem(job_id=1, project_id=1, queue_name="render")

    res = await agent.enqueue(item)
    assert res["status"] == "enqueued"

    q_status = await agent.get_queue_status("render")
    assert len(q_status) == 1
    assert q_status[0].job_id == 1

    updated = await agent.update_priority(1, "render", 10)
    assert updated is True

    q_status = await agent.get_queue_status("render")
    assert q_status[0].priority == 10


import tempfile  # noqa: E402


async def test_asset_manager_agent(tmp_path: pytest.TempPath) -> None:  # type: ignore[name-defined]
    # Create test file in temporary directory
    test_file_path = tmp_path / "test_file.png"
    test_file_path.write_text("dummy")

    agent = AssetManagerAgent(base_storage_path=str(tmp_path))
    res = await agent.register_asset(1, "image", str(test_file_path))
    assert res["status"] == "registered"

    assets = await agent.get_project_assets(1)
    assert len(assets) == 1
    assert assets[0]["filename"] == "test_file.png"


async def test_model_manager_agent(db_session: AsyncSession) -> None:
    agent = AIModelManagerAgent()
    res = await agent.allocate_gpu("test_model", 4000)
    assert res is True
    install_res = await agent.install_local_model("test_local", "/tmp/model.bin", db_session)
    assert install_res["status"] == "installed"

    models = await agent.list_available_models(db_session)
    assert len(models) == 1
    assert models[0]["name"] == "test_local"


async def test_settings_agent() -> None:
    agent = SettingsAgent()
    settings = await agent.get_global_settings()
    assert isinstance(settings, dict)
    updated = await agent.update_global_settings({"theme": "dark"})
    assert updated["theme"] == "dark"


async def test_recovery_agent() -> None:
    agent = RecoveryAgent()
    res = await agent.scan_for_interrupted_jobs()
    assert res["found"] == 0
    valid = await agent.verify_cache_integrity()
    assert valid is True


async def test_qa_agent() -> None:
    agent = QAAgent()
    errors = await agent.validate_pipeline_configuration({})
    assert len(errors) == 1
    errors2 = await agent.validate_pipeline_configuration({"project_id": 1})
    assert len(errors2) == 0
    valid = await agent.verify_output_assets(1)
    assert valid is True


async def test_queue_manager_agent_priority() -> None:
    agent = QueueManagerAgent()
    await agent.enqueue(QueueItem(job_id=1, project_id=1, queue_name="render", priority=1))
    await agent.enqueue(QueueItem(job_id=2, project_id=1, queue_name="render", priority=10))
    await agent.enqueue(QueueItem(job_id=3, project_id=1, queue_name="render", priority=5))

    # Should dequeue job 2 (highest priority)
    item = await agent.dequeue_highest_priority("render")
    assert item is not None
    assert item.job_id == 2
    assert item.status == "running"


async def test_queue_manager_agent_requeue() -> None:
    agent = QueueManagerAgent()
    item = QueueItem(job_id=1, project_id=1, queue_name="render")

    # Fail 3 times, should requeue each time
    for _ in range(3):
        assert await agent.requeue_failed(item) is True
        assert item.retry_count > 0
        assert item.status == "queued"

    # 4th failure should exceed max retries
    assert await agent.requeue_failed(item) is False
    assert item.status == "failed"
