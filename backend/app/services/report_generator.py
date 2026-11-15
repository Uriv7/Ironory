"""PDF Inspection Report Generator for Ironory using ReportLab.

Generates official B2B Industrial Quality Inspection Reports and Certificates
including machine metadata, AI confidence, detected defects, and human supervisor sign-offs.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.app.models.inspection import Inspection


class QualityReportGenerator:
    """Generates official inspection PDF reports."""

    @classmethod
    def generate_pdf(
        cls,
        inspection: Inspection,
        organization_name: str = "Ironory Industrial Operations",
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )

        elements = []

        # Header Banner
        header_table = Table(
            [
                [
                    Paragraph("<b>IRONORY</b> &bull; Industrial Visual Inspection", title_style),
                    Paragraph(
                        f"<b>Report ID:</b> {inspection.id[:8].upper()}<br/>"
                        f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                        subtitle_style,
                    ),
                ]
            ],
            colWidths=[4.2 * inch, 3.0 * inch],
        )
        header_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ])
        )
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=15))

        # Overview Metadata Table
        product_name = inspection.product.name if inspection.product else "N/A"
        product_sku = inspection.product.sku if inspection.product else "N/A"
        product_category = inspection.product.category if inspection.product else "Steel Surface"

        overview_data = [
            [
                Paragraph("<b>Organization:</b>", body_style),
                Paragraph(organization_name, body_style),
                Paragraph("<b>Inspection Status:</b>", body_style),
                Paragraph(f"<b>{inspection.status.value.upper()}</b>", body_style),
            ],
            [
                Paragraph("<b>Product Name:</b>", body_style),
                Paragraph(product_name, body_style),
                Paragraph("<b>Session Created:</b>", body_style),
                Paragraph(inspection.created_at.strftime("%Y-%m-%d %H:%M"), body_style),
            ],
            [
                Paragraph("<b>SKU / Part Code:</b>", body_style),
                Paragraph(product_sku, body_style),
                Paragraph("<b>Category:</b>", body_style),
                Paragraph(product_category, body_style),
            ],
        ]

        overview_table = Table(overview_data, colWidths=[1.4 * inch, 2.2 * inch, 1.6 * inch, 2.0 * inch])
        overview_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elements.append(overview_table)
        elements.append(Spacer(1, 15))

        # AI Inspection Results Section
        elements.append(Paragraph("Automated Deep Learning Inspection Results", section_style))
        elements.append(Spacer(1, 6))

        if inspection.result:
            res = inspection.result
            verdict = "DEFECT DETECTED" if res.is_defective else "QUALITY PASSED"
            verdict_color = "#ef4444" if res.is_defective else "#10b981"

            ai_summary_data = [
                [
                    Paragraph("<b>Primary Model:</b>", body_style),
                    Paragraph(f"{res.model_name.upper()} (v{res.model_version})", body_style),
                    Paragraph("<b>AI Verdict:</b>", body_style),
                    Paragraph(f"<font color='{verdict_color}'><b>{verdict}</b></font>", body_style),
                ],
                [
                    Paragraph("<b>Predicted Defect:</b>", body_style),
                    Paragraph(f"<b>{res.predicted_class.replace('_', ' ').title()}</b>", body_style),
                    Paragraph("<b>Model Confidence:</b>", body_style),
                    Paragraph(f"<b>{res.confidence * 100.0:.2f}%</b>", body_style),
                ],
                [
                    Paragraph("<b>Inference Latency:</b>", body_style),
                    Paragraph(f"{res.inference_time_ms} ms", body_style),
                    Paragraph("<b>Anomaly Score:</b>", body_style),
                    Paragraph(f"{res.anomaly_score:.4f}" if res.anomaly_score else "N/A", body_style),
                ],
            ]

            ai_table = Table(ai_summary_data, colWidths=[1.4 * inch, 2.2 * inch, 1.6 * inch, 2.0 * inch])
            ai_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ])
            )
            elements.append(ai_table)
            elements.append(Spacer(1, 12))

            # Defect Bounding Boxes Table
            if res.defects:
                elements.append(Paragraph("Localized Defect Regions", section_style))
                elements.append(Spacer(1, 5))

                defect_rows = [
                    [
                        Paragraph("<b>#</b>", body_style),
                        Paragraph("<b>Defect Class</b>", body_style),
                        Paragraph("<b>Severity</b>", body_style),
                        Paragraph("<b>Bounding Box (X, Y, W, H)</b>", body_style),
                        Paragraph("<b>Confidence</b>", body_style),
                    ]
                ]

                for i, d in enumerate(res.defects):
                    defect_rows.append([
                        Paragraph(str(i + 1), body_style),
                        Paragraph(d.defect_type.replace("_", " ").title(), body_style),
                        Paragraph(f"<b>{d.severity}</b>", body_style),
                        Paragraph(f"[{d.bbox_x}, {d.bbox_y}, {d.bbox_w}, {d.bbox_h}]", body_style),
                        Paragraph(f"{d.confidence * 100.0:.1f}%", body_style),
                    ])

                defect_table = Table(defect_rows, colWidths=[0.5 * inch, 1.8 * inch, 1.2 * inch, 2.4 * inch, 1.3 * inch])
                defect_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("PADDING", (0, 0), (-1, -1), 4),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ])
                )
                elements.append(defect_table)
                elements.append(Spacer(1, 15))
        else:
            elements.append(Paragraph("<i>No AI prediction record available for this inspection session.</i>", body_style))
            elements.append(Spacer(1, 15))

        # Human Review / Sign-off Section
        elements.append(Paragraph("Quality Supervisor Review & Compliance Sign-Off", section_style))
        elements.append(Spacer(1, 6))

        if inspection.review:
            rev = inspection.review
            decision_color = "#10b981" if "APPROVE" in rev.decision.value else "#ef4444"
            review_data = [
                [
                    Paragraph("<b>Supervisor Decision:</b>", body_style),
                    Paragraph(f"<font color='{decision_color}'><b>{rev.decision.value}</b></font>", body_style),
                    Paragraph("<b>Final Defect Status:</b>", body_style),
                    Paragraph("DEFECTIVE" if rev.is_defective else "NON-DEFECTIVE", body_style),
                ],
                [
                    Paragraph("<b>Supervisor Notes:</b>", body_style),
                    Paragraph(rev.notes or "No remarks provided.", body_style),
                    Paragraph("<b>Sign-Off Timestamp:</b>", body_style),
                    Paragraph(rev.created_at.strftime("%Y-%m-%d %H:%M UTC"), body_style),
                ],
            ]
        else:
            review_data = [
                [
                    Paragraph("<b>Supervisor Decision:</b>", body_style),
                    Paragraph("<i>PENDING HUMAN REVIEW</i>", body_style),
                    Paragraph("<b>Sign-Off Status:</b>", body_style),
                    Paragraph("Awaiting Quality Assurance sign-off", body_style),
                ]
            ]

        rev_table = Table(review_data, colWidths=[1.6 * inch, 2.2 * inch, 1.6 * inch, 1.8 * inch])
        rev_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )
        elements.append(rev_table)
        elements.append(Spacer(1, 20))

        # Footer notes
        footer_text = (
            "<b>Ironory Quality Inspection Platform</b> &bull; Academic Deep Learning Project INT422 &bull; "
            "Surface Defect Inspection Specification ISO 9001:2015 Compliant Logging"
        )
        elements.append(Paragraph(footer_text, subtitle_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
