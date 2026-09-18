import streamlit as st
from streamlit_native_auth import current_user, is_authenticated, session_logout
from streamlit_scan_history import dashboard_stats, list_scans, scans_to_csv

st.set_page_config(
    page_title="Dashboard | ATHARVADRISHTI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp{background:#f5f9f2}
    .block-container{max-width:1200px;padding-top:2.5rem}
    .hero{padding:26px 28px;border-radius:24px;background:linear-gradient(135deg,#123a24,#2f8051);color:#efffed}
    .hero h1{margin:0;font-size:38px}
    .hero p{margin:8px 0 0;color:#cde5d0}
    .card{padding:20px;border:1px solid #d8e7d9;border-radius:18px;background:#fff}
    .muted{color:#6a7d70}
    </style>
    """,
    unsafe_allow_html=True,
)

if not is_authenticated():
    st.warning("Please log in to view your personal ATHARVADRISHTI dashboard.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/1_Login.py")
    if st.button("Back to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

user = current_user() or {}
user_id = int(user["id"])
scans = list_scans(user_id, 100)
stats = dashboard_stats(scans)

st.markdown(
    f"""
    <div class="hero">
        <h1>📊 ATHARVADRISHTI Dashboard</h1>
        <p>Welcome, {user.get("name", "User")}. Track your plant-health analyses in one place.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Scans", stats["total"])
c2.metric("Completed", stats["completed"])
c3.metric("Rejected", stats["rejected"])
c4.metric("Avg. Confidence", f'{stats["average_confidence"]:.2f}%' if stats["average_confidence"] is not None else "—")
c5.metric("Healthy Predictions", stats["healthy"])

st.write("")
st.markdown("### 🌿 Recent Scan History")

if not scans:
    st.info("No scans saved yet. Start your first plant-health analysis from the AI Scanner.")
else:
    table = [
        {
            "ID": s["id"],
            "File": s["filename"],
            "Prediction": s["prediction"] or "Not accepted",
            "Confidence": f'{s["confidence"]:.2f}%' if s["confidence"] is not None else "—",
            "Status": s["status"].title(),
            "Created": s["created_at"],
        }
        for s in scans
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Export Scan History (CSV)",
        data=scans_to_csv(scans),
        file_name="atharvadrishti_scan_history.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.write("")
st.markdown("### 🧠 Product Insights")
insight1, insight2 = st.columns(2)
with insight1:
    st.markdown('<div class="card"><b>Condition-related predictions</b><br><span class="muted">These are model classifications and should be treated as visual decision support, not a standalone biological diagnosis.</span></div>', unsafe_allow_html=True)
with insight2:
    st.markdown('<div class="card"><b>Confidence-aware workflow</b><br><span class="muted">Rejected or uncertain results should be rechecked with a clearer image or additional observations.</span></div>', unsafe_allow_html=True)

st.write("")
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("🔬 Open AI Scanner", use_container_width=True, type="primary"):
        st.switch_page("pages/1_AI_Scanner.py")
with b2:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
with b3:
    if st.button("🚪 Logout", use_container_width=True):
        session_logout()
        st.switch_page("streamlit_app.py")
