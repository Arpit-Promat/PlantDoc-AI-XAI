import streamlit as st
from streamlit_native_auth import authenticate, issue_otp, session_login, get_user_by_email

st.set_page_config(page_title="Login | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("""
<style>
.stApp{background:#f7faf5}.block-container{max-width:620px;padding-top:3rem}
.auth-card{padding:30px;border:1px solid #dce8dc;border-radius:24px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}
.auth-title{font:700 34px Arial,sans-serif;color:#10251a}.muted{color:#6b7e71}.security{padding:12px 14px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown("## 🌿 ATHARVADRISHTI")
st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
st.markdown('<p class="muted">Login with your email or mobile number.</p>', unsafe_allow_html=True)

identity = st.text_input("Email or Mobile Number", key="login_identity")
password = st.text_input("Password", type="password", key="login_password")

if st.button("Login", use_container_width=True, type="primary"):
    user, error = authenticate(identity, password)
    if error == "verification_required" and user:
        st.session_state["verify_email"] = user["email"]
        st.session_state["verify_phone"] = user["phone"]
        st.warning("Please complete email and mobile verification first.")
        st.switch_page("pages/3_Verify.py")
    elif error:
        st.error(error)
    elif user:
        if user["two_factor_enabled"]:
            channel = user["two_factor_channel"] if user["two_factor_channel"] in {"email", "sms"} else "email"
            destination = user["email"] if channel == "email" else user["phone"]
            issue_otp(user["id"], "login_2fa", channel, destination)
            st.session_state["pending_2fa_user_id"] = user["id"]
            st.session_state["login_2fa_channel"] = channel
            st.switch_page("pages/4_Two_Factor.py")
        else:
            session_login(user)
            st.success("Login successful.")
            st.switch_page("pages/1_AI_Scanner.py")

c1, c2 = st.columns(2)
with c1:
    if st.button("Create account", use_container_width=True):
        st.switch_page("pages/2_Sign_Up.py")
with c2:
    if st.button("Verify account", use_container_width=True):
        st.switch_page("pages/3_Verify.py")

if st.button("Back to Home", use_container_width=True):
    st.switch_page("streamlit_app.py")

st.markdown('<div class="security">🛡️ Email verification + Mobile verification + OTP-based 2FA</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
