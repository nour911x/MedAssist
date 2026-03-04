#cette fonctionnalité permet de garder un historique des consultations pour detecter si les symptomes reviennent ou s'aggravent.
import json
import os
from datetime import datetime

FILE = "history.json"

#on charge l'historique des consultations depuis le fichier JSON.
def load_history():
    #On verifie si le fichier existe
    if not os.path.exists(FILE):
    #Si le fichier n'existe pas, on retourne une liste vide 
        return []
     #On ouvre le fichier en lecture ("r") avec l'encodage UTF-8 pour gerer les accents. 
    with open(FILE, "r", encoding="utf-8") as f:
    #json.load() lit le fichier et le transforme en liste Python de dictionnaires   
        return json.load(f)


def save_consultation(result): #Sauvegarde une nouvelle consultation dans l'historique
    history = load_history() #On charge d'abord l'historique existant.

    entry = {
        "date": datetime.now().isoformat(), #datetime.now() donne la date et l'heure actuelles. isoformat() la convertit en texte au format ISO (ex: "2026-03-04T14:30:00").
        "symptoms": result["symptoms"],#On copie la liste des symptomes du resultat
        "risk_level": result["risk_level"] #On copie le niveau de risque.
    }

    history.append(entry) #On ajoute la nouvelle consultation a la fin de la liste.

    with open(FILE, "w", encoding="utf-8") as f: #On ouvre le fichier en ecriture 
        json.dump(history, f, indent=2) #json.dump() ecrit la liste complete dans le fichier. indent=2 ajoute de l'indentation pour la lisibilite

    return entry

# la fonction check_aggravation donne a MedAssist sa memoire. Elle verifie si les symptomes actuels sont deja apparus dans une consultation precedente
def check_aggravation(current_symptoms): #Prend en parametre la liste des symptomes de la consultation actuelle.
    """Verifie si les memes symptomes sont apparus avant."""
    history = load_history()
    if not history:
        return None #Si pas d'historique, rien a comparer, on retourne None

    current_set = {s.lower() for s in current_symptoms} #On transforme les symptomes actuels en un ensemble (set) Python, en minuscules. 
    #On parcourt les 10 dernieres consultations en commencant par la plus recente
    for past in reversed(history[-10:]):
        # On transforme aussi les symptomes de la consultation passee en set.
        past_set = {s.lower() for s in past["symptoms"]}
        #L'operateur & fait l'intersection des deux ensembles = les symptomes en commun. 
        common = current_set & past_set
        if common: #Si l'intersection n'est pas vide ça veut dire il y a des symptomes en commun
            return {
                "date": past["date"][:10], #[:10] prend les 10 premiers caracteres de la date ISO, soit "2026-03-04" 
                "previous_risk": past["risk_level"], #Le niveau de risque de la consultation precedente
                "common_symptoms": list(common) #La liste des symptomes en commun. list() convertit le set en liste.
            }

    return None
