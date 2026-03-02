from datetime import datetime

EMERGENCY_NUMBER = "15"  # SAMU


def generate_emergency_message(analysis, contact_name="Contact d'urgence", location=""):
    risk_labels = {"low": "FAIBLE", "medium": "MODERE", "high": "ELEVE"}
    symptoms_list = ", ".join(analysis["symptoms"])
    risk = risk_labels.get(analysis["risk_level"], "INCONNU")

    message = (
        f"ALERTE SANTE\n\n"
        f"Bonjour {contact_name},\n\n"
        f"Je ne me sens pas bien et j'ai besoin d'aide.\n\n"
        f"Symptomes : {symptoms_list}\n"
        f"Niveau de risque estime : {risk}\n"
        f"Specialite conseillee : {analysis['specialty']}\n"
        f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    )

    if location:
        message += f"Localisation : {location}\n"

    message += (
        f"\nMerci de m'aider ou d'appeler le {EMERGENCY_NUMBER} si necessaire.\n\n"
        f"Ce message a ete genere par MedAssist (outil d'aide, pas un diagnostic medical)."
    )

    return message
