import streamlit as st
from streamlit_native_auth import get_user_by_identity, verify_otp, session_login

st.set_page_config(page_title="Two-Factor Authentication | ATHARVADRISHTI", page_icon="🛡", layout="centered")
st.markdown("""
<style>
.stApp{background:#f7faf5}.block-container{max-width:620px;padding-top:3rem}
.card{padding:30px;border:1px solid #dce8dc;border-radius:24px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}
.title{font:700 34px Arial,sans-serif;color:#10251a}.muted{color:#6b7e71}.hint{padding:12px 14px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("## 🛡️ ATHARVADRISHTI")
st.markdown('<div class="title">Two-Factor Authentication</div>', unsafe_allow_html=True)
channel = st.session_state.get("login_2fa_channel", "email")
st.markdown(f'<p class="muted">Enter the OTP sent to your verified {"email" if channel == "email" else "mobile number"}.</p>', unsafe_allow_html=True)

identity = st.text_input("Email or Mobile Number", value=st.session_state.get("login_identity", ""))
code = st.text_input("6-digit security code", max_chars=6, type="password")

if st.button("Verify 2FA", use_container_width=True, type="primary"):
    user = get_user_by_identity(identity)
    if user and st.session_state.get("pending_2fa_user_id") == user["id"] and verify_otp(user["id"], "login_2fa", code, channel):
        session_login(user)
        st.success("Two-factor verification successful.")
        st.switch_page("pages/1_AI_Scanner.py")
    else:
        st.error("Invalid or expired two-factor code.")

if st.button("Back to Login", use_container_width=True):
    st.switch_page("pages/1_Login.py")
st.markdown('<div class="hint">🛡️ OTP is single-use and expires after 10 minutes.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
