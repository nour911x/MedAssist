#Cette fonctionnalite permet au patient de generer un message pret a envoyer a un proche.
EMERGENCY_NUMBER = "15"


def generate_emergency_message(result, contact="Proche", location=""):
    symptoms = " et ".join(result["symptoms"])

    if result["risk_level"] == "high":
        message = f"Bonjour {contact}, j'ai besoin d'aide, j'ai {symptoms}. Tu peux venir vite ?"
        if location:
            message += f" Je suis a {location}."
        message += f" Si tu n'arrives pas, appelle le {EMERGENCY_NUMBER}."

    elif result["risk_level"] == "medium":
        message = f"Bonjour {contact}, je ne me sens pas bien, j'ai {symptoms}. Tu peux passer me voir ?"
        if location:
            message += f" Je suis a {location}."

    else:
        message = f"Bonjour {contact}, je voulais te prevenir, j'ai {symptoms}. Rien de grave mais je prefere que tu sois au courant."

    return message
