import streamlit as st
from groq_client import analyze_symptoms
from validator import validate_response
from history import load_history, save_consultation, check_evolution
from emergency import generate_emergency_message
from pdf_export import generate_pdf

st.set_page_config(page_title="MedAssist", page_icon="🏥", layout="centered")

st.title("🏥 MedAssist")
st.caption("Assistant intelligent d'orientation medicale")
st.warning("⚠️ Cet outil ne remplace pas un avis medical. En cas d'urgence, appelez le 15 (SAMU).")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Parametres")
    contact_name = st.text_input("Contact d'urgence", value="Mon contact")
    location = st.text_input("Localisation (optionnel)")

    st.divider()
    st.header("📋 Historique")
    history = load_history()
    risk_icons = {"low": "🟢", "medium": "🟠", "high": "🔴"}
    if history:
        for entry in reversed(history[-5:]):
            icon = risk_icons.get(entry["risk_level"], "⚪")
            st.caption(f"{icon} {entry['date'][:10]} — {', '.join(entry['symptoms'][:2])}")
    else:
        st.caption("Aucun historique")

# --- Input ---
symptoms = st.text_area(
    "Decrivez vos symptomes :",
    placeholder="Ex: J'ai mal a la tete depuis 2 jours avec de la fievre...",
)

if st.button("🔍 Analyser", type="primary"):
    if not symptoms.strip():
        st.error("Veuillez decrire vos symptomes.")
    else:
        with st.spinner("Analyse en cours..."):
            raw = analyze_symptoms(symptoms)
            result, error = validate_response(raw, symptoms)

        if error:
            st.error(f"Erreur d'analyse : {error}")
        else:
            st.session_state["result"] = result
            save_consultation(result)

# --- Results ---
if "result" in st.session_state:
    r = st.session_state["result"]
    st.divider()

    # Confiance faible
    if r.get("low_confidence"):
        st.warning("⚠️ Confiance faible — veuillez preciser vos symptomes.")

    # Evolution
    evo = check_evolution(r["symptoms"])
    if evo:
        st.info(f"📊 Symptomes similaires detectes le {evo['previous_date'][:10]}")

    # Niveau de risque
    risk_cfg = {
        "low": ("🟢 Surveillance a domicile", "success"),
        "medium": ("🟠 Consultation recommandee", "warning"),
        "high": ("🔴 Urgence medicale", "error"),
    }
    label, lvl = risk_cfg[r["risk_level"]]
    getattr(st, lvl)(f"**{label}** — Confiance : {r['confidence']:.0%}")

    # Details
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Symptomes detectes**")
        for s in r["symptoms"]:
            st.write(f"• {s}")
    with col2:
        st.markdown("**Specialite recommandee**")
        st.info(r["specialty"])

    st.markdown("**Explication**")
    st.write(r["explanation"])

    # Message d'urgence (medium / high)
    if r["risk_level"] in ["medium", "high"]:
        st.divider()
        st.subheader("📨 Message d'urgence")
        msg = generate_emergency_message(r, contact_name, location)
        st.code(msg, language=None)
        st.caption("📞 Numero d'urgence : **15** (SAMU)")

    # Export PDF
    st.divider()
    pdf_path = generate_pdf(r, load_history())
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Telecharger la fiche PDF", f, "fiche_patient.pdf", "application/pdf")
