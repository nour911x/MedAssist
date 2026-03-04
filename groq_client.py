#Ce fichier gere la communication avec l'intelligence artificielle. On utilise l'API Groq qui heberge le modele Llama 4 de Meta. On a deux fonctions : une pour poser des questions, une pour analyser.
import os
import re
from groq import Groq
from dotenv import load_dotenv
#On charge les variables du fichier .env dans l'environnement
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

#le prompt des questions
QUESTION_PROMPT = """Tu es un assistant medical. Le patient decrit ses symptomes.
Pose 1 a 2 questions courtes pour mieux comprendre (depuis quand, intensite, autres symptomes...).
Sois direct et professionnel. Pas de JSON."""

# le prompt d'analyse 
ANALYSIS_PROMPT = """Tu es un assistant medical specialise en triage.

A partir de la conversation, reponds UNIQUEMENT en JSON valide :

{
  "symptoms": ["symptome1", "symptome2"],
  "risk_level": "low" ou "medium" ou "high",
  "confidence": nombre entre 0 et 1,
  "explanation": "explication courte pour le patient",
  "specialty": "specialite medicale",
  "chronologie": "depuis quand, comment ca a commence",
  "medicaments": ["medicament1", "medicament2"] ou [] si aucun,
  "signes_alerte": ["signe a surveiller 1", "signe 2"]
}

Regles :
- low = surveillance a domicile
- medium = consultation recommandee
- high = urgence medicale
- Si le patient n'a pas mentionne de medicaments, mets []
- Si le patient n'a pas precise la chronologie, mets "Non precise"
- Pas de texte hors JSON.
"""


def ask_questions(messages):
    """Pose des questions au patient pour mieux comprendre."""
    #On appelle l'API Groq via le client
    response = client.chat.completions.create(
        model=MODEL,
    #On envoie le prompt systeme (QUESTION_PROMPT) suivi de tous les messages de la conversation.  
        messages=[{"role": "system", "content": QUESTION_PROMPT}] + messages,
    #paramètre d’aléatoire du modèle.
        temperature=0.3,
    #limiter la longueur de la reponse 
        max_completion_tokens=300
    )
    return response.choices[0].message.content

#fonction d'analyse finale des symptômes.
def analyze(messages):
    """Analyse finale : retourne le JSON de diagnostic."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": ANALYSIS_PROMPT}] + messages,
        temperature=0.3,
        max_completion_tokens=800
    )
    #On recupere la reponse brute du LLM
    content = response.choices[0].message.content
    #la regex cherche tout ce qui est entre { et }
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        return match.group()
        #Si on a trouve un JSON, on le retourne.
    return "{}"
    #Si on n'a rien trouve, on retourne un JSON vide. 
