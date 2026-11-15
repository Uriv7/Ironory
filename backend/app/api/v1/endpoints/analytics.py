"""Tenant-isolated quality inspection analytics endpoints for Ironory."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import case, desc, func
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.inspection import (
    Defect,
    Inspection,
    InspectionResult,
    InspectionStatus,
)
from backend.app.models.organization import Organization
from backend.app.security.tenant import get_current_tenant

router = APIRouter(prefix="/analytics", tags=["Quality Analytics & Metrics"])


@router.get(
    "/overview",
    status_code=status.HTTP_200_OK,
    summary="Get Operational Quality Overview",
    description="Calculates live organization KPIs including pass rate, total inspections, defect counts, and review backlog."
)
def get_analytics_overview(
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    # Total inspections
    total_inspections = (
        db.query(func.count(Inspection.id))
        .filter(Inspection.organization_id == current_org.id)
        .scalar()
        or 0
    )

    # Defect breakdown from results
    results_query = (
        db.query(
            func.count(InspectionResult.id).label("total_results"),
            func.sum(case((InspectionResult.is_defective == True, 1), else_=0)).label("defective_count"),
            func.avg(InspectionResult.inference_time_ms).label("avg_inference_time"),
            func.avg(InspectionResult.confidence).label("avg_confidence"),
        )
        .join(Inspection, InspectionResult.inspection_id == Inspection.id)
        .filter(Inspection.organization_id == current_org.id)
        .first()
    )

    defective_count = int(results_query.defective_count or 0)
    passed_count = total_inspections - defective_count if total_inspections >= defective_count else 0
    pass_rate = round((passed_count / total_inspections * 100.0), 1) if total_inspections > 0 else 0.0

    # Pending reviews
    pending_reviews = (
        db.query(func.count(Inspection.id))
        .filter(
            Inspection.organization_id == current_org.id,
            Inspection.status == InspectionStatus.REQUIRES_REVIEW,
        )
        .scalar()
        or 0
    )

    return {
        "total_inspections": total_inspections,
        "total_defective": defective_count,
        "total_passed": passed_count,
        "pass_rate_percentage": pass_rate,
        "pending_reviews": pending_reviews,
        "avg_inference_time_ms": round(float(results_query.avg_inference_time or 0.0), 1),
        "avg_confidence": round(float(results_query.avg_confidence or 0.0), 4),
    }


@router.get(
    "/defect-distribution",
    status_code=status.HTTP_200_OK,
    summary="Defect Category Distribution",
    description="Aggregates defect classification frequencies across all inspected parts for Pareto analysis."
)
def get_defect_distribution(
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(
            Defect.defect_type,
            func.count(Defect.id).label("count"),
            func.avg(Defect.confidence).label("avg_confidence"),
        )
        .join(InspectionResult, Defect.result_id == InspectionResult.id)
        .join(Inspection, InspectionResult.inspection_id == Inspection.id)
        .filter(Inspection.organization_id == current_org.id)
        .group_by(Defect.defect_type)
        .order_by(desc("count"))
        .all()
    )

    total_defects = sum(row.count for row in rows) or 1
    return [
        {
            "defect_type": row.defect_type,
            "count": row.count,
            "percentage": round((row.count / total_defects) * 100.0, 1),
            "avg_confidence": round(float(row.avg_confidence or 0.0), 4),
        }
        for row in rows
    ]


@router.get(
    "/trends",
    status_code=status.HTTP_200_OK,
    summary="Historical Quality & Volume Trends",
    description="Returns daily inspection volume and defect rates for time-series trend analysis."
)
def get_quality_trends(
    days: int = Query(14, ge=1, le=90),
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    start_date = datetime.utcnow() - timedelta(days=days)

    inspections = (
        db.query(
            func.date(Inspection.created_at).label("inspection_date"),
            func.count(Inspection.id).label("total_runs"),
            func.sum(case((InspectionResult.is_defective == True, 1), else_=0)).label("defects"),
        )
        .outerjoin(InspectionResult, Inspection.id == InspectionResult.inspection_id)
        .filter(
            Inspection.organization_id == current_org.id,
            Inspection.created_at >= start_date,
        )
        .group_by(func.date(Inspection.created_at))
        .order_by(func.date(Inspection.created_at))
        .all()
    )

    return [
        {
            "date": str(row.inspection_date),
            "total_runs": int(row.total_runs),
            "defects": int(row.defects or 0),
            "pass_rate": round(
                ((row.total_runs - (row.defects or 0)) / row.total_runs * 100.0), 1
            )
            if row.total_runs > 0
            else 100.0,
        }
        for row in inspections
    ]
