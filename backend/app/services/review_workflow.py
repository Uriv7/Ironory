"""Human Review Workflow Service.

Orchestrates the multi-stage quality review state machine, ensuring human inspector
decisions are recorded with complete traceability, audit logging, and defect reclassification.
"""

from __future__ import annotations

import logging
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import NotFoundException, ValidationException
from backend.app.models.inspection import (
    Inspection,
    InspectionStatus,
    InspectionReview,
    ReviewDecision,
)
from backend.app.services.audit import AuditService

logger = logging.getLogger("ironory.services.review_workflow")


class ReviewWorkflowService:
    """Manages inspector review lifecycle and audit sign-offs."""

    @staticmethod
    def submit_review(
        db: Session,
        inspection_id: str,
        org_id: str,
        reviewer_id: str,
        decision: ReviewDecision,
        final_class: str,
        is_defective: bool,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Inspection:
        """Process and record quality inspector sign-off."""
        inspection = (
            db.query(Inspection)
            .filter(Inspection.id == inspection_id, Inspection.organization_id == org_id)
            .first()
        )
        if not inspection:
            raise NotFoundException(f"Inspection '{inspection_id}' not found.")

        # Check existing review
        existing_review = (
            db.query(InspectionReview)
            .filter(InspectionReview.inspection_id == inspection_id)
            .first()
        )

        original_class = inspection.result.predicted_class if inspection.result else "unknown"
        original_defective = inspection.result.is_defective if inspection.result else False

        if existing_review:
            existing_review.decision = decision
            existing_review.final_class = final_class
            existing_review.is_defective = is_defective
            existing_review.notes = notes
            existing_review.reviewer_id = reviewer_id
        else:
            review = InspectionReview(
                inspection_id=inspection.id,
                reviewer_id=reviewer_id,
                decision=decision,
                final_class=final_class,
                is_defective=is_defective,
                notes=notes,
            )
            db.add(review)

        # Update inspection status to COMPLETED
        inspection.status = InspectionStatus.COMPLETED
        db.commit()
        db.refresh(inspection)

        # Audit trail recording
        AuditService.log(
            db=db,
            action=f"INSPECTION_REVIEW_{decision.value}",
            resource_type="INSPECTION",
            resource_id=inspection.id,
            org_id=org_id,
            actor_id=reviewer_id,
            details={
                "decision": decision.value,
                "original_predicted_class": original_class,
                "final_verified_class": final_class,
                "original_is_defective": original_defective,
                "final_is_defective": is_defective,
                "notes": notes,
            },
            ip_address=ip_address,
        )

        logger.info(
            f"Review recorded for inspection {inspection.id}: {decision.value} "
            f"({original_class} -> {final_class}) by {reviewer_id}"
        )
        return inspection
