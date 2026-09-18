import streamlit as st
from streamlit_native_auth import create_user, issue_otp

st.set_page_config(page_title="Sign Up | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("""
<style>
.stApp{background:#f7faf5}.block-container{max-width:620px;padding-top:3rem}
.auth-card{padding:32px;border:1px solid #dce8dc;border-radius:28px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}
.auth-title{font:700 34px Arial,sans-serif;color:#10251a}.muted{color:#6b7e71}.hint{padding:12px 14px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown("## 🌿 ATHARVADRISHTI")
st.markdown('<div class="auth-title">Create your account</div>', unsafe_allow_html=True)
st.markdown('<p class="muted">Build a secure plant-health workspace with verified contact details.</p>', unsafe_allow_html=True)

with st.form("signup"):
    name = st.text_input("Full name")
    email = st.text_input("Email address")
    phone = st.text_input("Mobile number", placeholder="+919876543210")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")

if submitted:
    if password != confirm:
        st.error("Passwords do not match.")
    else:
        user, error = create_user(name, email, phone, password)
        if error:
            st.error(error)
        else:
            issue_otp(user["id"], "email_verification", "email", user["email"])
            issue_otp(user["id"], "mobile_verification", "sms", user["phone"])
            st.session_state["verify_email"] = user["email"]
            st.session_state["verify_phone"] = user["phone"]
            st.success("Account created. Verification codes have been generated.")
            if st.session_state.get("dev_last_otp"):
                st.info("Development OTP mode is enabled; check the latest generated code in the app log or secret-controlled demo flow.")
            st.switch_page("pages/3_Verify.py")

if st.button("Back to home", use_container_width=True):
    st.switch_page("streamlit_app.py")
st.markdown('<div class="hint">🛡️ You must verify both email and mobile before login. OTP-based 2FA can then be enabled.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
