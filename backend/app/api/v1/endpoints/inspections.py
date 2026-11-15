import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form, Response, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.membership import OrganizationMembership, OrganizationRole
from backend.app.models.inspection import Inspection, InspectionStatus, ReviewDecision
from backend.app.security.tenant import get_current_user, get_current_tenant, get_current_tenant_membership
from backend.app.security.rbac import require_roles
from backend.app.repositories.product_repository import ProductRepository
from backend.app.repositories.inspection_repository import InspectionRepository
from backend.app.services.image_processor import ImageProcessorService
from backend.app.services.storage import get_storage_service
from backend.app.core.exceptions import NotFoundException, ValidationException
from backend.app.schemas.inspection import (
    InspectionResponse,
    InspectionImageResponse,
    InspectionResultResponse,
    DefectResponse,
    InspectionReviewResponse,
    HumanReviewRequest,
    BatchInspectionResponse,
)

router = APIRouter(prefix="/inspections", tags=["Quality Inspection Sessions"])


def _to_inspection_response(inspection: Inspection) -> InspectionResponse:
    img_resp = None
    if inspection.image:
        img_resp = InspectionImageResponse(
            id=inspection.image.id,
            storage_key=inspection.image.storage_key,
            original_filename=inspection.image.original_filename,
            file_size_bytes=inspection.image.file_size_bytes,
            width=inspection.image.width,
            height=inspection.image.height,
            mime_type=inspection.image.mime_type,
            checksum_sha256=inspection.image.checksum_sha256,
        )

    res_resp = None
    if inspection.result:
        defects = [
            DefectResponse(
                id=d.id,
                defect_type=d.defect_type,
                severity=d.severity,
                bbox_x=d.bbox_x,
                bbox_y=d.bbox_y,
                bbox_w=d.bbox_w,
                bbox_h=d.bbox_h,
                confidence=d.confidence,
            )
            for d in inspection.result.defects
        ]
        res_resp = InspectionResultResponse(
            id=inspection.result.id,
            model_name=inspection.result.model_name,
            model_version=inspection.result.model_version,
            predicted_class=inspection.result.predicted_class,
            confidence=inspection.result.confidence,
            is_defective=inspection.result.is_defective,
            anomaly_score=inspection.result.anomaly_score,
            inference_time_ms=inspection.result.inference_time_ms,
            created_at=inspection.result.created_at,
            defects=defects,
        )

    rev_resp = None
    if inspection.review:
        rev_resp = InspectionReviewResponse(
            id=inspection.review.id,
            reviewer_id=inspection.review.reviewer_id,
            decision=inspection.review.decision,
            final_class=inspection.review.final_class,
            is_defective=inspection.review.is_defective,
            notes=inspection.review.notes,
            created_at=inspection.review.created_at,
        )

    return InspectionResponse(
        id=inspection.id,
        organization_id=inspection.organization_id,
        product_id=inspection.product_id,
        inspector_id=inspection.inspector_id,
        status=inspection.status,
        error_message=inspection.error_message,
        created_at=inspection.created_at,
        image=img_resp,
        result=res_resp,
        review=rev_resp,
    )


@router.post(
    "/upload",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Inspection Asset & Create Session",
    description="Validates image integrity and dimensions, stores file securely, and enqueues an automated inspection run."
)
async def upload_inspection_image(
    product_id: str = Form(...),
    file: UploadFile = File(...),
    async_mode: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_org: Organization = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InspectionResponse:
    product_repo = ProductRepository(db)
    product = product_repo.get_by_id_and_org(product_id, current_org.id)
    if not product:
        raise NotFoundException(f"Product '{product_id}' not found in your organization.")

    if not product.is_active:
        raise ValidationException("Cannot conduct inspection on an archived product.")

    # Read and validate image content
    content = await file.read()
    content_type = file.content_type or "image/jpeg"
    metadata = ImageProcessorService.validate_and_extract_metadata(content, content_type)

    # Store file in tenant-isolated storage
    storage = get_storage_service()
    storage_key = storage.save(
        file_obj=io.BytesIO(content),
        tenant_id=current_org.id,
        original_filename=file.filename or "inspection_asset.jpg",
        subfolder="inspections",
    )

    # Create inspection record
    inspection_repo = InspectionRepository(db)
    inspection = inspection_repo.create_inspection(
        org_id=current_org.id,
        product_id=product.id,
        inspector_id=current_user.id,
    )

    # Attach image metadata
    inspection_repo.attach_image(
        inspection=inspection,
        storage_key=storage_key,
        original_filename=file.filename or "inspection_asset.jpg",
        metadata=metadata,
    )

    # Execute automated AI inference (asynchronously or synchronously)
    from backend.app.services.inspection_execution_service import InspectionExecutionService
    if async_mode:
        background_tasks.add_task(
            InspectionExecutionService.execute_inspection_background,
            inspection.id,
            current_org.id,
        )
    else:
        try:
            inspection = InspectionExecutionService.execute_inspection(inspection.id, current_org.id, db)
        except Exception:
            # Fallback to keeping inspection in QUEUED state if model is initializing
            pass

    return _to_inspection_response(inspection)


@router.get(
    "",
    response_model=List[InspectionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Inspection Sessions",
    description="Retrieves a paginated list of visual inspection sessions for the current tenant."
)
def list_inspections(
    product_id: Optional[str] = Query(None),
    status: Optional[InspectionStatus] = Query(None),
    is_defective: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> List[InspectionResponse]:
    repo = InspectionRepository(db)
    inspections = repo.list_inspections(
        org_id=current_org.id,
        product_id=product_id,
        status=status,
        is_defective=is_defective,
        skip=skip,
        limit=limit,
    )
    return [_to_inspection_response(i) for i in inspections]


@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Inspection Session Details",
    description="Fetches full inspection lifecycle state, original visual asset metadata, and AI predictions."
)
def get_inspection(
    inspection_id: str,
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> InspectionResponse:
    repo = InspectionRepository(db)
    inspection = repo.get_by_id_and_org(inspection_id, current_org.id)
    if not inspection:
        raise NotFoundException(f"Inspection '{inspection_id}' not found in your organization.")
    return _to_inspection_response(inspection)


@router.post(
    "/{inspection_id}/review",
    response_model=InspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Human Review Sign-Off",
    description="Allows a Quality Manager to confirm or override an AI inspection prediction. Requires Quality Manager or Admin."
)
def submit_human_review(
    inspection_id: str,
    payload: HumanReviewRequest,
    current_org: Organization = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(require_roles([OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.QUALITY_MANAGER])),
    db: Session = Depends(get_db),
) -> InspectionResponse:
    repo = InspectionRepository(db)
    inspection = repo.get_by_id_and_org(inspection_id, current_org.id)
    if not inspection:
        raise NotFoundException(f"Inspection '{inspection_id}' not found in your organization.")

    repo.add_human_review(
        inspection=inspection,
        reviewer_id=current_user.id,
        payload=payload,
    )
    return _to_inspection_response(inspection)


@router.get(
    "/{inspection_id}/image",
    summary="Secure Image Stream",
    description="Streams the raw uploaded surface inspection asset with tenant authorization checks."
)
def get_inspection_image_stream(
    inspection_id: str,
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    repo = InspectionRepository(db)
    inspection = repo.get_by_id_and_org(inspection_id, current_org.id)
    if not inspection or not inspection.image:
        raise NotFoundException(f"Image for inspection '{inspection_id}' not found.")

    storage = get_storage_service()
    image_bytes = storage.get(inspection.image.storage_key)
    return Response(content=image_bytes, media_type=inspection.image.mime_type)


@router.get(
    "/{inspection_id}/overlay",
    summary="Secure Grad-CAM Overlay Stream",
    description="Streams the Grad-CAM activation heatmap overlay for the specified inspection session."
)
def get_inspection_overlay_stream(
    inspection_id: str,
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    repo = InspectionRepository(db)
    inspection = repo.get_by_id_and_org(inspection_id, current_org.id)
    if not inspection:
        raise NotFoundException(f"Inspection '{inspection_id}' not found.")

    storage = get_storage_service()
    overlay_key = f"{current_org.id}/overlays/{inspection.id}_gradcam_overlay.jpg"
    try:
        overlay_bytes = storage.get(overlay_key)
        return Response(content=overlay_bytes, media_type="image/jpeg")
    except Exception:
        # Fallback to original image if overlay not generated
        if inspection.image:
            image_bytes = storage.get(inspection.image.storage_key)
            return Response(content=image_bytes, media_type=inspection.image.mime_type)
        raise NotFoundException(f"Overlay for inspection '{inspection_id}' not available.")


@router.get(
    "/{inspection_id}/report.pdf",
    summary="Download Official Inspection PDF Report",
    description="Generates an official ISO-compliant PDF inspection certificate including AI predictions and quality review sign-offs."
)
def download_inspection_report(
    inspection_id: str,
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    from backend.app.services.report_generator import QualityReportGenerator

    repo = InspectionRepository(db)
    inspection = repo.get_by_id_and_org(inspection_id, current_org.id)
    if not inspection:
        raise NotFoundException(f"Inspection '{inspection_id}' not found.")

    pdf_bytes = QualityReportGenerator.generate_pdf(
        inspection=inspection,
        organization_name=current_org.name,
    )

    headers = {
        "Content-Disposition": f'attachment; filename="Ironory_Report_{inspection.id[:8].upper()}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.post(
    "/batch",
    response_model=BatchInspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch Upload & Process Product Inspections",
    description="Ingests up to 20 surface defect inspection images simultaneously, running automated AI inference across the batch."
)
async def upload_batch_inspection_images(
    product_id: str = Form(..., description="Target Product ID"),
    files: List[UploadFile] = File(..., description="List of inspection images (max 20)"),
    async_mode: bool = Form(False, description="Run inference in background task queue"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    if not files or len(files) == 0:
        raise ValidationException("At least one image must be provided.")
    if len(files) > 20:
        raise ValidationException("Maximum 20 images allowed per batch inspection request.")

    product_repo = ProductRepository(db)
    product = product_repo.get_by_id_and_org(product_id, current_org.id)
    if not product:
        raise NotFoundException(f"Product '{product_id}' not found in organization.")

    repo = InspectionRepository(db)
    storage = get_storage_service()
    successful = []
    failed_count = 0

    from backend.app.services.inspection_execution_service import InspectionExecutionService

    for f in files:
        try:
            content = await f.read()
            content_type = f.content_type or "image/jpeg"
            metadata = ImageProcessorService.validate_and_extract_metadata(content, content_type)

            storage_key = storage.save(
                file_obj=io.BytesIO(content),
                tenant_id=current_org.id,
                original_filename=f.filename or "batch_inspection_asset.jpg",
                subfolder="inspections",
            )

            inspection = repo.create_inspection(
                org_id=current_org.id,
                product_id=product.id,
                inspector_id=current_user.id,
            )

            repo.attach_image(
                inspection=inspection,
                storage_key=storage_key,
                original_filename=f.filename or "batch_inspection_asset.jpg",
                metadata=metadata,
            )

            if async_mode:
                background_tasks.add_task(
                    InspectionExecutionService.execute_inspection_background,
                    inspection.id,
                    current_org.id,
                )
            else:
                try:
                    inspection = InspectionExecutionService.execute_inspection(inspection.id, current_org.id, db)
                except Exception:
                    pass

            successful.append(_to_inspection_response(inspection))
        except Exception:
            failed_count += 1

    return BatchInspectionResponse(
        batch_size=len(files),
        successful_count=len(successful),
        failed_count=failed_count,
        inspections=successful,
    )


@router.get(
    "/export/csv",
    summary="Export Inspection Audit Log to CSV",
    description="Generates an ISO 9001 audit-compliant CSV summary of all inspection records for the organization."
)
def export_inspections_csv(
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    current_org: Organization = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    repo = InspectionRepository(db)
    inspections = repo.list_inspections(
        org_id=current_org.id,
        product_id=product_id,
        skip=0,
        limit=5000,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Inspection ID",
        "Created At (UTC)",
        "Product ID",
        "Status",
        "Original Filename",
        "Predicted Class",
        "Confidence (%)",
        "Is Defective",
        "Anomaly Score",
        "Inference Time (ms)",
        "Review Decision",
        "Final Verified Class",
        "Reviewer Notes",
    ])

    for ins in inspections:
        pred_class = ins.result.predicted_class if ins.result else "N/A"
        conf = f"{ins.result.confidence * 100:.2f}%" if ins.result else "N/A"
        is_def = str(ins.result.is_defective) if ins.result else "N/A"
        anomaly = f"{ins.result.anomaly_score:.4f}" if (ins.result and ins.result.anomaly_score is not None) else "N/A"
        inf_time = str(ins.result.inference_time_ms) if ins.result else "N/A"
        filename = ins.image.original_filename if ins.image else "N/A"
        rev_dec = ins.review.decision.value if ins.review else "PENDING"
        final_cls = ins.review.final_class if ins.review else pred_class
        notes = ins.review.notes if ins.review else ""

        writer.writerow([
            ins.id,
            ins.created_at.isoformat(),
            ins.product_id,
            ins.status.value,
            filename,
            pred_class,
            conf,
            is_def,
            anomaly,
            inf_time,
            rev_dec,
            final_cls,
            notes,
        ])

    csv_data = output.getvalue()
    headers = {
        "Content-Disposition": f'attachment; filename="Ironory_Inspections_{current_org.id[:8]}.csv"'
    }
    return Response(content=csv_data, media_type="text/csv", headers=headers)

