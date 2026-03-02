import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Tu es un assistant medical de triage. Analyse les symptomes decrits et reponds UNIQUEMENT en JSON valide avec cette structure exacte :
{
  "symptoms": ["symptome1", "symptome2"],
  "risk_level": "low" ou "medium" ou "high",
  "confidence": nombre entre 0.0 et 1.0,
  "explanation": "explication courte en francais",
  "specialty": "specialite medicale recommandee"
}

Regles :
- "low" = surveillance a domicile
- "medium" = consultation medicale recommandee
- "high" = urgence medicale
- Si les symptomes sont vagues, mets une confiance basse
- Reponds UNIQUEMENT avec le JSON, rien d'autre"""


def analyze_symptoms(symptoms_text):
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": symptoms_text}
        ],
        temperature=0.3,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content
