"""
FraudLens AI - Report Generation Service
Generates professional audit-grade PDF reports of derived investigation findings using ReportLab.
"""

import os
from typing import Dict, Any
from xml.sax.saxutils import escape as xml_escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.config import settings

def _safe_str(val: Any) -> str:
    if val is None:
        return ""
    return xml_escape(str(val))

class ReportService:
    @staticmethod
    def generate_pdf_report(result_data: Dict[str, Any]) -> str:
        """
        Builds and saves a structured PDF report in reports directory.
        Returns the absolute filepath.
        """
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        inv_id = str(result_data.get("investigation_id", "inv_unknown"))
        filename = f"FraudLens_Report_{inv_id}.pdf"
        output_path = os.path.join(settings.REPORTS_DIR, filename)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("<b>FRAUDLENS AI — INVESTIGATION REPORT</b>", title_style))
        elements.append(Paragraph("<i>See the Risk. Understand the Evidence. Act Safely.</i>", body_style))
        elements.append(Spacer(1, 12))

        # 2. Key Metadata Table
        risk_score = result_data.get("risk_score", 0.0)
        risk_level = str(result_data.get("risk_level", "UNKNOWN"))
        risk_color = "#ef4444" if risk_level in ["HIGH_RISK", "LIKELY_SCAM"] else ("#f59e0b" if risk_level in ["SUSPICIOUS", "MODERATE"] else "#10b981")

        meta_data = [
            [Paragraph("<b>Investigation ID:</b>", body_style), Paragraph(_safe_str(inv_id), body_style)],
            [Paragraph("<b>Analysis Type:</b>", body_style), Paragraph(_safe_str(result_data.get("type", "GENERAL")), body_style)],
            [Paragraph("<b>ML Fraud Model:</b>", body_style), Paragraph("XGBoost (xgboost_fraud_model.joblib)", body_style)],
            [Paragraph("<b>Anomaly Model:</b>", body_style), Paragraph("Isolation Forest", body_style)],
            [Paragraph("<b>Risk Score:</b>", body_style), Paragraph(f"<b>{_safe_str(risk_score)}/100</b>", body_style)],
            [Paragraph("<b>Risk Level:</b>", body_style), Paragraph(f"<font color='{risk_color}'><b>{_safe_str(risk_level)}</b></font>", body_style)],
            [Paragraph("<b>Date:</b>", body_style), Paragraph(_safe_str(result_data.get("created_at", "")), body_style)]
        ]
        meta_table = Table(meta_data, colWidths=[130, 410])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # 3. Executive AI Summary
        elements.append(Paragraph("<b>Executive Summary</b>", section_style))
        raw_summary = result_data.get("ai_summary") or result_data.get("summary") or "Investigation completed."
        elements.append(Paragraph(_safe_str(raw_summary), body_style))
        elements.append(Spacer(1, 14))

        # 4. Observed Evidence Table
        elements.append(Paragraph("<b>Auditable Evidence & Observed Signals</b>", section_style))
        evidence_list = result_data.get("evidence", [])
        if evidence_list:
            ev_table_data = [["Category", "Signal", "Observed Value", "Severity", "Explanation"]]
            for ev in evidence_list[:12]:
                ev_table_data.append([
                    Paragraph(_safe_str(ev.get("category", "")), body_style),
                    Paragraph(_safe_str(ev.get("signal", "")), body_style),
                    Paragraph(_safe_str(ev.get("observed_value", "")), body_style),
                    Paragraph(_safe_str(ev.get("severity", "")), body_style),
                    Paragraph(_safe_str(ev.get("explanation", "")), body_style),
                ])
            ev_table = Table(ev_table_data, colWidths=[90, 95, 90, 65, 200])
            ev_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(ev_table)
        else:
            elements.append(Paragraph("No anomalous signals observed.", body_style))

        elements.append(Spacer(1, 14))

        # 5. Per-Transaction XGBoost Detail Table
        transactions_list = result_data.get("transactions", [])
        if transactions_list:
            elements.append(Paragraph("<b>Transaction-Level XGBoost Fraud Analysis</b>", section_style))
            elements.append(Paragraph(
                "Each row shows the XGBoost model's fraud probability alongside the Isolation Forest anomaly score. "
                "Scores ≥ 0.70 are considered high-risk.",
                ParagraphStyle("SubNote", parent=body_style, fontSize=8.5, textColor=colors.HexColor("#64748b"))
            ))
            elements.append(Spacer(1, 6))

            txn_header = [
                Paragraph("<b>Transaction ID</b>", body_style),
                Paragraph("<b>Amount (₹)</b>", body_style),
                Paragraph("<b>XGBoost Score</b>", body_style),
                Paragraph("<b>Anomaly Score</b>", body_style),
                Paragraph("<b>Anomalous?</b>", body_style),
                Paragraph("<b>What Went Wrong</b>", body_style),
            ]
            txn_table_data = [txn_header]
            for t in transactions_list[:50]:  # Cap at 50 rows for PDF length
                xscore = float(t.get("xgboost_score", t.get("fraud_probability", 0.0)))
                ascore = float(t.get("anomaly_score", 0.0))
                is_anom = bool(t.get("is_anomalous", False))
                xscore_str = f"{xscore:.4f}"
                ascore_str = f"{ascore:.4f}"
                anom_str = "YES ⚠" if is_anom else "No"
                what = _safe_str(t.get("what_went_wrong", ""))
                amt_str = f"{float(t.get('amount', 0)):,.2f}"
                txn_table_data.append([
                    Paragraph(_safe_str(t.get("transaction_id", "")), body_style),
                    Paragraph(amt_str, body_style),
                    Paragraph(f"<font color='{'#ef4444' if xscore >= 0.7 else ('#f59e0b' if xscore >= 0.4 else '#10b981')}'><b>{xscore_str}</b></font>", body_style),
                    Paragraph(f"<font color='{'#ef4444' if ascore >= 0.7 else '#94a3b8'}'>{ascore_str}</font>", body_style),
                    Paragraph(f"<font color='{'#ef4444' if is_anom else '#10b981'}'><b>{anom_str}</b></font>", body_style),
                    Paragraph(what[:180] + ("..." if len(what) > 180 else ""), body_style),
                ])

            txn_table = Table(txn_table_data, colWidths=[80, 65, 65, 65, 50, 215])
            txn_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements.append(txn_table)
            elements.append(Spacer(1, 14))

        # 6. Recommendations
        elements.append(Paragraph("<b>Recommended Safety Actions</b>", section_style))
        recs = result_data.get("recommendation", "")
        if isinstance(recs, str):
            rec_items = recs.split("; ") if "; " in recs else [recs]
        else:
            rec_items = recs or []
        for r in rec_items:
            if r:
                elements.append(Paragraph(f"• {_safe_str(r)}", body_style))

        elements.append(Spacer(1, 20))

        # 6. Privacy & Legal Disclaimer
        disclaimer = (
            "<b>Privacy & Compliance Note:</b> In accordance with FraudLens AI privacy standards, "
            "all raw input files, OCR scratchpads, and temporary session caches have been purged. "
            "This report preserves only the derived evidence, verified entity checks, and risk classifications."
        )
        elements.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

        doc.build(elements)
        return output_path
