import json
# les mots critiques
CRITICAL_KEYWORDS = [
    "douleur thoracique",
    "difficulte a respirer",
    "perte de connaissance",
    "saignement abondant",
    "paralysie"
]

# les combinaisons critiques (inspirees des protocoles de triage medical)
CRITICAL_COMBOS = [
    (["douleur thoracique", "essoufflement"], "Suspicion syndrome coronarien"),
    (["paralysie", "mal de tete"], "Suspicion AVC"),
    (["fievre", "confusion"], "Suspicion meningite"),
    (["douleur thoracique", "palpitations"], "Suspicion cardiaque"),
]

VALID_RISKS = ["low", "medium", "high"]

#La fonction validate_response()
def validate_response(raw_json, original_text):
    try:
        data = json.loads(raw_json) #On essaie de parser le JSON
    except:
        return None, "Erreur JSON" #Si json.loads echoue, on attrape l'exception et on retourne une erreur propre 

    # Verification champs obligatoires
    required = ["symptoms", "risk_level", "confidence", "explanation", "specialty"]
    for field in required:
        if field not in data:
            return None, f"Champ manquant: {field}"
    #On verifie que risk_level est bien "low", "medium" ou "high". 
    if data["risk_level"] not in VALID_RISKS:
        return None, "Niveau de risque invalide"
    #On passe le texte du patient en minuscules . Comme ca, "Douleur Thoracique" et "douleur thoracique" sont traites pareil.
    text = original_text.lower()

    # Regle 1 : mot critique 
    for word in CRITICAL_KEYWORDS:
        if word in text:
            data["risk_level"] = "high" #On FORCE le niveau de risque a "high
            data["confidence"] = max(0.8, float(data["confidence"]))#➤ On met la confiance a minimum 80%. 
            break

    # Regle 2 : combinaison de symptomes 
    data["critical_alert"] = None
    for combo, raison in CRITICAL_COMBOS:
        if all(mot in text for mot in combo):
            data["risk_level"] = "high"
            data["critical_alert"] = raison #On stocke la raison medicale pour l'afficher a l'ecran.
            break

    # les Champs optionnels 
    if "chronologie" not in data:
        data["chronologie"] = ""
    if "medicaments" not in data:
        data["medicaments"] = []
    if "signes_alerte" not in data:
        data["signes_alerte"] = []

    return data, None
