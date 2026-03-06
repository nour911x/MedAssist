* MedAssist

Assistant intelligent d'orientation medicale. MedAssist guide le patient a travers un questionnaire medical structure, analyse ses symptomes et fournit une orientation avec niveau de risque, conseils pratiques et rapport PDF.

* Fonctionnalites

- Chat medical intelligent: l'IA pose des questions ciblees comme un medecin pour comprendre les symptomes
- Analyse avec niveau de risque: classification en 3 niveaux (risque faible, consultation recommandee, urgence medicale)
- Triple verification de securite : mots critiques + combinaisons dangereuses + evaluation IA 
- Detection d'absurdite : refuse les descriptions physiquement impossibles
-Rapport PDF : fiche patient exportable pour le medecin
-Message WhatsApp: envoi d'un message d'urgence pre-rempli au contact via deep linking (`wa.me`)
- Historique des consultations : sauvegarde locale avec detection d'aggravation si les symptomes reviennent

 Technologies

- Python + Streamlit(interface web)
- Groq API avec Llama 4 Scout (modele IA)
- FPDF2  (generation PDF)
- WhatsApp Deep Linking (`wa.me`) pour l'envoi de messages

*  Structure du projet



app.py              # Interface Streamlit + logique principale
groq_client.py      # Communication avec l'API Groq (prompts + appels)
validator.py        # Validation du JSON + regles de securite medicale
emergency.py        # Generation du message d'urgence
history.py          # Historique des consultations (JSON local)
pdf_export.py       # Generation du rapport PDF
requirements.txt    # Dependances Python
.env                # Cle API Groq (non versionne)


* Installation


# Cloner le projet
git clone <url-du-repo>
cd MedAssist

# Creer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dependances
pip install -r requirements.txt


# Lancement


streamlit run app.py


* Architecture


Patient → Chat (3 echanges) → Analyse IA → Validation  → Resultats + PDF + WhatsApp


1. Le patient decrit ses symptomes
2. L'IA pose des questions ciblees (max 3 echanges)
3. L'IA genere une analyse 
4. Le validator verifie : mots critiques, combinaisons dangereuses, flag urgent de l'IA
5. Les resultats sont affiches avec niveau de risque, conseils, signes d'alerte
6. Le patient peut exporter en PDF ou envoyer un message WhatsApp

* Ameliorations prevues

- RAG (Retrieval Augmented Generation) : connecter une base de protocoles medicaux pour des reponses plus fiables
- API Gmail: envoi automatique du rapport PDF par email au medecin
- Base de donnees distante : historique accessible depuis n'importe quel appareil avec authentification
