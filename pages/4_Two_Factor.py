import streamlit as st
from streamlit_auth import api_post

st.set_page_config(page_title="Two-Factor Authentication | ATHARVADRISHTI", page_icon="🛡", layout="centered")
st.markdown("<style>div[data-testid='stForm']{border:1px solid #dce8dc;border-radius:24px;padding:20px;background:#fff}</style>", unsafe_allow_html=True)

st.markdown("## 🛡 ATHARVADRISHTI")
st.title("Two-Factor Authentication")
st.caption("Enter the one-time security code sent to your verified channel.")

email = st.text_input("Account email", value=st.session_state.get("login_email", ""))
code = st.text_input("6-digit security code", max_chars=6, type="password")

if st.button("Verify 2FA", use_container_width=True, type="primary"):
    r, d = api_post("/api/product-auth/2fa/verify", {"email": email, "code": code})
    if r is not None and r.ok:
        st.session_state["access_token"] = d.get("access_token", "")
        st.success("Two-factor verification successful.")
        st.switch_page("pages/1_AI_Scanner.py")
    else:
        st.error(d.get("error", "Invalid or expired two-factor code."))

if st.button("Back to Login", use_container_width=True):
    st.switch_page("pages/1_Login.py")
