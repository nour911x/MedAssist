import streamlit as st
import urllib.parse
import html
from groq_client import ask_questions, analyze
from validator import validate_response
from history import load_history, save_consultation, check_aggravation
from emergency import generate_emergency_message
from pdf_export import generate_pdf

st.set_page_config(page_title="MedAssist", page_icon="🏥", layout="centered")

MAX_QUESTIONS = 3


ACCENT = "#2a7886"
ACCENT_LIGHT = "#e6f2f4"

st.markdown(f"""
<style>
    /* Titre principal */
    .main-title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {ACCENT};
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }}
    .sub-title {{
        font-size: 0.88rem;
        color: #7a8a8e;
        margin-bottom: 1.2rem;
    }}
    /* Disclaimer discret */
    .disclaimer {{
        background: {ACCENT_LIGHT};
        border-left: 3px solid {ACCENT};
        padding: 0.5rem 0.8rem;
        font-size: 0.75rem;
        color: #4a6a6e;
        margin-bottom: 1.5rem;
        border-radius: 0 4px 4px 0;
    }}
    /* Bandeau de risque */
    .risk-banner {{
        padding: 1rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 1rem;
        letter-spacing: 0.2px;
    }}
    .risk-low {{
        background: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #a5d6a7;
    }}
    .risk-medium {{
        background: #fff8e1;
        color: #e65100;
        border: 1px solid #ffe082;
    }}
    .risk-high {{
        background: #ffebee;
        color: #b71c1c;
        border: 1px solid #ef9a9a;
    }}
    /* Carte de section */
    .section-card {{
        background: #fff;
        border: 1px solid #e4e8ea;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
    }}
    .section-title {{
        font-weight: 600;
        font-size: 0.78rem;
        color: {ACCENT};
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .section-content {{
        font-size: 0.9rem;
        color: #3a3a3a;
        line-height: 1.6;
    }}
    .section-content ul {{
        padding-left: 1.2rem;
        margin: 0;
    }}
    .section-content li {{
        margin-bottom: 0.25rem;
    }}
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: #f5f8f9;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        border-radius: 6px;
        background: {ACCENT};
        color: white;
        border: none;
        font-weight: 500;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: #1f5f6b;
        color: white;
    }}
    .sidebar-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {ACCENT};
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 0.3rem;
    }}
    /* Historique items */
    .history-item {{
        padding: 0.4rem 0.5rem;
        font-size: 0.82rem;
        border-bottom: 1px solid #e8ecee;
        color: #4a4a4a;
    }}
    /* Dividers plus subtils */
    hr {{
        border: none;
        border-top: 1px solid #e8ecee;
        margin: 1rem 0;
    }}
    /* Message urgence */
    .urgence-label {{
        font-weight: 600;
        font-size: 0.85rem;
        color: #c62828;
        margin-bottom: 0.4rem;
    }}
</style>
""", unsafe_allow_html=True)


st.markdown('<p class="main-title">MedAssist</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Orientation medicale intelligente</p>', unsafe_allow_html=True)
st.markdown('<div class="disclaimer">Cet outil ne remplace pas un avis medical. En cas d\'urgence, appelez le 15 (SAMU).</div>', unsafe_allow_html=True)


with st.sidebar:
    if st.button("Nouvelle consultation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.result = None
        st.session_state.user_count = 0
        st.rerun()

    st.divider()

    st.markdown('<div class="sidebar-label">Contact d\'urgence</div>', unsafe_allow_html=True)
    contact_name = st.text_input("Nom", value="Mon contact", label_visibility="collapsed", placeholder="Nom du contact")
    contact_phone = st.text_input("Telephone", label_visibility="collapsed", placeholder="Numero WhatsApp (ex: 33612345678)")
    location = st.text_input("Localisation", label_visibility="collapsed", placeholder="Localisation (optionnel)")

    st.divider()

    st.markdown('<div class="sidebar-label">Historique</div>', unsafe_allow_html=True)
    history = load_history()
    icons = {"low": "🟢", "medium": "🟠", "high": "🔴"}

    if history:
        for entry in reversed(history[-5:]):
            icon = icons.get(entry["risk_level"], "⚪")
            st.markdown(f'<div class="history-item">{icon} {entry["date"][:10]} — {", ".join(entry["symptoms"][:2])}</div>', unsafe_allow_html=True)
    else:
        st.caption("Aucun historique")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.result = None
    st.session_state.user_count = 0



if not st.session_state.messages and st.session_state.result is None:
    with st.chat_message("assistant"):
        st.write("Bonjour ! Decrivez vos symptomes, je vais vous poser quelques questions puis vous donner mon analyse.")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if st.session_state.result is None:
    user_input = st.chat_input("Decrivez vos symptomes...")
else:
    user_input = None

if user_input and st.session_state.result is None:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.user_count += 1

    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    if st.session_state.user_count < MAX_QUESTIONS:
        with st.spinner("MedAssist reflechit..."):
            response = ask_questions(api_messages)

        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

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

if st.session_state.result:
    r = st.session_state.result

    st.divider()

    if r.get("critical_alert"):
        st.error(f"Alerte critique : {r['critical_alert']}")

    risk_css = {"low": "risk-low", "medium": "risk-medium", "high": "risk-high"}
    risk_texts = {"low": "Risque faible", "medium": "Consultation recommandee", "high": "Urgence medicale"}
    risk_class = risk_css[r["risk_level"]]
    st.markdown(f'<div class="risk-banner {risk_class}">{risk_texts[r["risk_level"]]}</div>', unsafe_allow_html=True)

    col_spec, col_symp = st.columns(2)
    with col_spec:
        st.markdown(f'<div class="section-card"><div class="section-title">Specialite recommandee</div><div class="section-content">{html.escape(r["specialty"])}</div></div>', unsafe_allow_html=True)
    with col_symp:
        symptoms_html = "".join(f"<li>{html.escape(s)}</li>" for s in r["symptoms"])
        st.markdown(f'<div class="section-card"><div class="section-title">Symptomes detectes</div><div class="section-content"><ul>{symptoms_html}</ul></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-card"><div class="section-title">Explication</div><div class="section-content">{html.escape(r["explanation"])}</div></div>', unsafe_allow_html=True)

    if r.get("conseils"):
        conseils_html = "".join(f"<li>{html.escape(c)}</li>" for c in r["conseils"])
        st.markdown(f'<div class="section-card"><div class="section-title">Conseils pratiques</div><div class="section-content"><ul>{conseils_html}</ul></div></div>', unsafe_allow_html=True)

    if r.get("medicaments"):
        meds_html = "".join(f"<li>{html.escape(m)}</li>" for m in r["medicaments"])
        st.markdown(f'<div class="section-card"><div class="section-title">Medicaments mentionnes</div><div class="section-content"><ul>{meds_html}</ul></div></div>', unsafe_allow_html=True)

    if r.get("signes_alerte"):
        alertes_html = "".join(f"<li>{html.escape(s)}</li>" for s in r["signes_alerte"])
        st.markdown(f'<div class="section-card"><div class="section-title">Signes d\'alerte a surveiller</div><div class="section-content"><ul>{alertes_html}</ul></div></div>', unsafe_allow_html=True)

    if r["risk_level"] in ["medium", "high"]:
        st.divider()
        st.markdown('<div class="urgence-label">Message d\'urgence</div>', unsafe_allow_html=True)
        msg = generate_emergency_message(r, contact_name, location)
        st.code(msg)
        if contact_phone:
            phone = contact_phone.strip().replace(" ", "").replace("+", "")
            wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
            st.link_button("Envoyer via WhatsApp", wa_url)

    st.divider()
    pdf_path = generate_pdf(r)
    with open(pdf_path, "rb") as f:
        st.download_button(
            "Telecharger le rapport PDF",
            f,
            "rapport_medassist.pdf",
            "application/pdf"
        )

    aggravation = check_aggravation(r["symptoms"])
    if aggravation:
        st.caption(f"Symptomes similaires detectes le {aggravation['date']} (risque precedent : {aggravation['previous_risk']})")
