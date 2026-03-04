import streamlit as st
from groq_client import ask_questions, analyze
from validator import validate_response
from history import load_history, save_consultation, check_aggravation
from emergency import generate_emergency_message
from pdf_export import generate_pdf

st.set_page_config(page_title="MedAssist", page_icon="🏥")

st.title("🏥 MedAssist")
st.caption("Assistant intelligent d'orientation medicale")

st.warning("⚠️ Cet outil ne remplace pas un avis medical. En cas d'urgence, appelez le 15 (SAMU).")

MAX_QUESTIONS = 2  # Nombre d'echanges avant analyse

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Parametres")
    contact_name = st.text_input("Contact d'urgence", value="Mon contact")
    location = st.text_input("Localisation (optionnel)")

    st.divider()

    if st.button("🔄 Nouvelle consultation"):
        st.session_state.messages = []
        st.session_state.result = None
        st.session_state.user_count = 0
        st.rerun()

    st.divider()
    st.header("📋 Historique")

    history = load_history()
    icons = {"low": "🟢", "medium": "🟠", "high": "🔴"}

    if history:
        for entry in reversed(history[-5:]):
            icon = icons.get(entry["risk_level"], "⚪")
            st.write(f"{icon} {entry['date'][:10]} — {', '.join(entry['symptoms'][:2])}")
    else:
        st.caption("Aucun historique")

# ---------------- Session state ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.result = None
    st.session_state.user_count = 0

# ---------------- Chat ----------------

# Message de bienvenue
if not st.session_state.messages and st.session_state.result is None:
    with st.chat_message("assistant"):
        st.write("Bonjour ! Decrivez vos symptomes, je vais vous poser quelques questions puis vous donner mon analyse.")

# Afficher l'historique du chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input utilisateur
user_input = st.chat_input("Decrivez vos symptomes...")

if user_input and st.session_state.result is None:
    # Afficher le message utilisateur
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.user_count += 1

    # Preparer les messages pour l'API (sans le system prompt)
    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Phase 1 : Poser des questions
    if st.session_state.user_count < MAX_QUESTIONS:
        with st.spinner("MedAssist reflechit..."):
            response = ask_questions(api_messages)

        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Phase 2 : Analyse finale
    else:
        with st.spinner("Analyse en cours..."):
            raw_json = analyze(api_messages)
            all_user_text = " ".join(m["content"] for m in st.session_state.messages if m["role"] == "user")
            result, error = validate_response(raw_json, all_user_text)

        if error:
            st.error(f"Erreur : {error}")
        else:
            st.session_state.result = result
            save_consultation(result)
            st.rerun()

# ---------------- Resultats ----------------
if st.session_state.result:
    r = st.session_state.result

    st.divider()

    # Alerte aggravation
    aggravation = check_aggravation(r["symptoms"])
    if aggravation:
        st.warning(f"⚠️ Symptomes similaires detectes le {aggravation['date']} (risque precedent : {aggravation['previous_risk']})")

    # Alerte critique (combinaison de symptomes)
    if r.get("critical_alert"):
        st.error(f"🚨 Alerte critique : {r['critical_alert']}")

    # Niveau de risque
    risk_labels = {
        "low": "🟢 Surveillance a domicile",
        "medium": "🟠 Consultation recommandee",
        "high": "🔴 Urgence medicale"
    }

    st.subheader(risk_labels[r["risk_level"]])
    st.write(f"Confiance : {r['confidence']:.0%}")

    st.markdown("### 🩺 Symptomes detectes")
    for s in r["symptoms"]:
        st.write(f"- {s}")

    st.markdown("### 🏥 Specialite recommandee")
    st.info(r["specialty"])

    st.markdown("### 💡 Explication")
    st.write(r["explanation"])

    # Message urgence si medium ou high
    if r["risk_level"] in ["medium", "high"]:
        st.divider()
        st.subheader("📨 Message d'urgence")
        msg = generate_emergency_message(r, contact_name, location)
        st.code(msg)

    # Export PDF
    st.divider()
    pdf_path = generate_pdf(r)
    with open(pdf_path, "rb") as f:
        st.download_button(
            "📄 Telecharger le rapport PDF",
            f,
            "rapport_medassist.pdf",
            "application/pdf"
        )
