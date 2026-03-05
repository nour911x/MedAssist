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
    required = ["symptoms", "risk_level", "explanation", "specialty"]
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
            data["risk_level"] = "high"
            break

    # Regle 2 : combinaison de symptomes 
    data["critical_alert"] = None
    for combo, raison in CRITICAL_COMBOS:
        if all(mot in text for mot in combo):
            data["risk_level"] = "high"
            data["critical_alert"] = raison #On stocke la raison medicale pour l'afficher a l'ecran.
            break

    # Regle 3 : double verification via le LLM
    # Si le LLM a detecte une urgence que les keywords n'ont pas catchee
    if data.get("urgent") is True and data["risk_level"] != "high":
        data["risk_level"] = "high"

    # les Champs optionnels
    if "medicaments" not in data:
        data["medicaments"] = []
    if "signes_alerte" not in data:
        data["signes_alerte"] = []
    if "conseils" not in data:
        data["conseils"] = []

    # Nettoyage des listes : virer les elements parasites (lettres seules, fragments)
    for key in ["symptoms", "signes_alerte", "conseils", "medicaments"]:
        if key in data and isinstance(data[key], list):
            data[key] = [item.strip() for item in data[key] if isinstance(item, str) and len(item.strip()) > 3]

    return data, None
