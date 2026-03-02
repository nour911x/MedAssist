import os
from fpdf import FPDF
from datetime import datetime

RISK_LABELS = {
    "low": "Surveillance a domicile",
    "medium": "Consultation recommandee",
    "high": "Urgence medicale",
}
RISK_COLORS = {
    "low": (46, 204, 113),
    "medium": (243, 156, 18),
    "high": (231, 76, 60),
}


def _safe(text):
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_pdf(analysis, history=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "MedAssist - Fiche Patient", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    # Niveau de risque
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Niveau de risque", ln=True)
    r, g, b = RISK_COLORS.get(analysis["risk_level"], (0, 0, 0))
    pdf.set_text_color(r, g, b)
    pdf.set_font("Helvetica", "B", 16)
    label = RISK_LABELS.get(analysis["risk_level"], "Inconnu")
    pdf.cell(0, 10, f"{label} (confiance : {analysis['confidence']:.0%})", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Symptomes
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Symptomes rapportes", ln=True)
    pdf.set_font("Helvetica", "", 12)
    for s in analysis["symptoms"]:
        pdf.cell(0, 8, f"  - {_safe(s)}", ln=True)
    pdf.ln(5)

    # Analyse
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Analyse", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, _safe(analysis["explanation"]))
    pdf.ln(5)

    # Specialite
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Specialite recommandee", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, _safe(analysis["specialty"]), ln=True)
    pdf.ln(5)

    # Historique
    if history:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Historique recent", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for entry in history[-5:]:
            date = entry["date"][:10]
            risk = RISK_LABELS.get(entry["risk_level"], "?")
            symptoms = ", ".join(entry["symptoms"][:3])
            pdf.cell(0, 7, _safe(f"{date} | {risk} | {symptoms}"), ln=True)
        pdf.ln(5)

    # Disclaimer
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(
        0, 5,
        "AVERTISSEMENT : Ce document est genere par MedAssist, un outil d'aide "
        "a l'orientation medicale. Il ne constitue en aucun cas un diagnostic "
        "medical. Consultez un professionnel de sante pour toute decision medicale.",
    )

    output_path = os.path.join(os.path.dirname(__file__), "data", "fiche_patient.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return output_path
