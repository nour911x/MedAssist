#Ce fichier genere un PDF professionnel que le patient peut imprimer et donner a son medecin. Il contient les symptomes, la chronologie, les medicaments, les signes d'alerte et l'historique
from fpdf import FPDF
from datetime import datetime
from history import load_history


def _safe(text):
    """Gere les caracteres speciaux pour FPDF."""
    # FPDF ne supporte pas tous les caracteres Unicode. Cette fonction convertit en latin-1 et remplace les caracteres non supportes par "?". 
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_pdf(result): #Fonction principale. Prend le resultat de l'analyse en parametre et genere un PDF.
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

   #Titre du rapport
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "MedAssist - Fiche patient", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Generee le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Bandeau de risque colore
    colors = {"low": (46, 204, 113), "medium": (243, 156, 18), "high": (231, 76, 60)}
    labels = {"low": "Surveillance a domicile", "medium": "Consultation recommandee", "high": "Urgence medicale"}

    r, g, b = colors.get(result["risk_level"], (0, 0, 0))
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, f"  {labels[result['risk_level']]} (confiance : {result['confidence']:.0%})", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    #  Symptomes 
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Symptomes rapportes", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for s in result["symptoms"]:
        pdf.cell(5)
        pdf.cell(0, 6, _safe(f"- {s}"), ln=True)
    pdf.ln(4)

    #  Chronologie 
    if result.get("chronologie"):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Chronologie", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _safe(result["chronologie"]))
        pdf.ln(4)

    #  Medicaments pris 
    if result.get("medicaments"):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Medicaments pris / en cours", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for med in result["medicaments"]:
            pdf.cell(5)
            pdf.cell(0, 6, _safe(f"- {med}"), ln=True)
        pdf.ln(4)

    #  Signes d'alerte 
    if result.get("signes_alerte"):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(200, 30, 30)
        pdf.cell(0, 8, "Signes d'alerte a surveiller", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for signe in result["signes_alerte"]:
            pdf.cell(5)
            pdf.cell(0, 6, _safe(f"- {signe}"), ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

    # Explication 
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Analyse", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _safe(result["explanation"]))
    pdf.ln(4)

    # Specialite 
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Specialite recommandee", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _safe(result["specialty"]), ln=True)
    pdf.ln(4)

    # Historique des consultations 
    history = load_history()
    if len(history) > 1:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Historique des consultations", ln=True)

        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(30, 7, "Date", border=1)
        pdf.cell(35, 7, "Risque", border=1)
        pdf.cell(0, 7, "Symptomes", border=1, ln=True)

        pdf.set_font("Helvetica", "", 9)
        for entry in history[-5:]:
            pdf.cell(30, 7, entry["date"][:10], border=1)
            pdf.cell(35, 7, _safe(labels.get(entry["risk_level"], "?")), border=1)
            pdf.cell(0, 7, _safe(", ".join(entry["symptoms"][:3])), border=1, ln=True)
        pdf.ln(4)

    #  Disclaimer 
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4,
        "Ce document est genere par MedAssist, un outil d'aide a l'orientation medicale. "
        "Il ne constitue pas un diagnostic medical. Les informations sont basees sur les "
        "declarations du patient et une analyse par intelligence artificielle."
    )

    filename = "rapport_medassist.pdf"
    pdf.output(filename)
    return filename
