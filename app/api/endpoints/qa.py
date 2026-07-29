from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.session import get_db_session
from app.models.qa import ApprovalHistory, IssueReport, QAReport, ValidationMetric
from app.schemas.qa import (
    AutoFixResult,
    IssueReportResponse,
    QARepairRequest,
    QAReportResponse,
    QARunRequest,
    ValidationMetricResponse,
)
from modules.qa.engine import QAEngine

router = APIRouter()


@router.post("/run", response_model=QAReportResponse)
async def run_qa(request: QARunRequest, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Run the QA pipeline for a project."""
    engine = QAEngine(db)
    report = await engine.run_pipeline(request.project_id, request.modules)

    stmt = (
        select(QAReport)
        .where(QAReport.id == report.id)
        .options(selectinload(QAReport.scores), selectinload(QAReport.issues), selectinload(QAReport.performance))
    )
    res = await db.execute(stmt)
    return res.scalars().first()


@router.post("/repair", response_model=List[AutoFixResult])
async def repair_issues(request: QARepairRequest, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Automatically fix identified safe issues."""
    engine = QAEngine(db)
    return await engine.run_autofix(request.project_id, request.issue_ids)


@router.post("/revalidate", response_model=QAReportResponse)
async def revalidate_project(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Revalidate a project after repairs or manual reviews."""
    engine = QAEngine(db)
    report = await engine.run_pipeline(project_id)

    stmt = (
        select(QAReport)
        .where(QAReport.id == report.id)
        .options(selectinload(QAReport.scores), selectinload(QAReport.issues), selectinload(QAReport.performance))
    )
    res = await db.execute(stmt)
    return res.scalars().first()


@router.get("/report", response_model=QAReportResponse)
async def get_report(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Get the latest QA report for a project."""
    stmt = (
        select(QAReport)
        .where(QAReport.project_id == project_id)
        .options(selectinload(QAReport.scores), selectinload(QAReport.issues), selectinload(QAReport.performance))
        .order_by(QAReport.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/issues", response_model=List[IssueReportResponse])
async def get_issues(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Get all outstanding issues for a project."""
    stmt = (
        select(IssueReport)
        .join(QAReport)
        .where(QAReport.project_id == project_id)
        .where(IssueReport.is_fixed.is_(False))  # use is_(False) not == False
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/history", response_model=List[QAReportResponse])
async def get_history(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Get the QA history for a project."""
    stmt = (
        select(QAReport)
        .where(QAReport.project_id == project_id)
        .options(selectinload(QAReport.scores), selectinload(QAReport.issues), selectinload(QAReport.performance))
        .order_by(QAReport.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/metrics", response_model=List[ValidationMetricResponse])
async def get_metrics(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Get QA validation metrics for a project."""
    stmt = select(ValidationMetric).where(ValidationMetric.project_id == project_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/approval", response_model=List[Dict[str, Any]])
async def get_approval(project_id: int, db: AsyncSession = Depends(get_db_session)) -> Any:
    """Get approval history for a project."""
    stmt = (
        select(ApprovalHistory)
        .where(ApprovalHistory.project_id == project_id)
        .order_by(ApprovalHistory.created_at.desc())
    )
    result = await db.execute(stmt)
    approvals = result.scalars().all()
    return [{"id": a.id, "project_id": a.project_id, "status": a.status, "notes": a.notes} for a in approvals]
