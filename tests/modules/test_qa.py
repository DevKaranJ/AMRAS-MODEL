import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.qa.engine import QAEngine


@pytest.mark.asyncio
async def test_qa_engine_pipeline(db_session: AsyncSession) -> None:
    engine = QAEngine(db_session)
    report = await engine.run_pipeline(project_id=1)

    assert report is not None
    assert report.project_id == 1
    assert report.status == "passed"
    assert report.overall_grade in ["A", "B"]

    # Reload report to ensure it has scores without causing MissingGreenlet
    await db_session.refresh(report, ["scores"])

    # Check that scores were generated
    assert report.scores is not None
    assert report.scores.overall_score > 0
    assert report.scores.story_score == 92.5
    assert report.scores.narration_score == 98.0
    assert report.scores.rendering_score == 99.0


@pytest.mark.asyncio
async def test_qa_engine_pipeline_subset(db_session: AsyncSession) -> None:
    engine = QAEngine(db_session)
    report = await engine.run_pipeline(project_id=1, modules=["story", "ocr"])

    assert report is not None
    assert report.project_id == 1

    await db_session.refresh(report, ["scores"])

    assert report.scores is not None
    assert report.scores.story_score == 92.5
    assert report.scores.narration_score == 0.0  # Not executed


@pytest.mark.asyncio
async def test_qa_engine_autofix(db_session: AsyncSession) -> None:
    engine = QAEngine(db_session)
    results = await engine.run_autofix(project_id=1, issue_ids=[1, 2, 3])

    assert len(results) == 3
    for result in results:
        assert result["success"] is True
        assert "Repaired" in result["action_taken"]


@pytest.mark.asyncio
async def test_qa_engine_autofix_empty(db_session: AsyncSession) -> None:
    engine = QAEngine(db_session)
    results = await engine.run_autofix(project_id=1, issue_ids=[])

    assert len(results) == 0
