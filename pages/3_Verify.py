import streamlit as st
from streamlit_native_auth import get_user_by_email, verify_otp, mark_email_verified, mark_mobile_verified, issue_otp, set_2fa_channel, set_2fa_enabled

st.set_page_config(page_title="Verify Account | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("""
<style>
.stApp{background:#f7faf5}.block-container{max-width:720px;padding-top:3rem}
.card{padding:30px;border:1px solid #dce8dc;border-radius:26px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}
.title{font:700 34px Arial,sans-serif;color:#10251a}.muted{color:#6b7e71}.ok{padding:12px 14px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("## 🌿 ATHARVADRISHTI")
st.markdown('<div class="title">Verify your account</div>', unsafe_allow_html=True)
st.markdown('<p class="muted">Complete email and mobile verification before secure login.</p>', unsafe_allow_html=True)

email = st.text_input("Email", value=st.session_state.get("verify_email", ""), key="verify_email_input")
email_code = st.text_input("Email verification code", max_chars=6, type="password")
if st.button("Verify Email", use_container_width=True):
    user = get_user_by_email(email)
    if user and verify_otp(user["id"], "email_verification", email_code, "email"):
        mark_email_verified(user["id"])
        st.session_state["email_verified"] = True
        st.success("Email verified successfully.")
    else:
        st.error("Invalid or expired email verification code.")

phone = st.text_input("Mobile number", value=st.session_state.get("verify_phone", ""), key="verify_phone_input")
mobile_code = st.text_input("Mobile verification OTP", max_chars=6, type="password")
if st.button("Verify Mobile", use_container_width=True):
    user = get_user_by_email(email)
    if user and verify_otp(user["id"], "mobile_verification", mobile_code, "sms"):
        mark_mobile_verified(user["id"])
        st.session_state["mobile_verified"] = True
        st.success("Mobile number verified successfully.")
    else:
        st.error("Invalid or expired mobile verification code.")

user = get_user_by_email(email) if email else None
email_done = bool(user and user["email_verified"]) or st.session_state.get("email_verified", False)
mobile_done = bool(user and user["mobile_verified"]) or st.session_state.get("mobile_verified", False)

if email_done and mobile_done and user:
    st.success("Both verification steps are complete.")
    st.markdown("### Optional: Enable 2FA")
    channel = st.selectbox("2FA delivery channel", ["email", "sms"], format_func=lambda x: "Email OTP" if x == "email" else "SMS OTP")
    if st.button("Send 2FA setup code", use_container_width=True):
        set_2fa_channel(user["id"], channel)
        destination = user["email"] if channel == "email" else user["phone"]
        issue_otp(user["id"], "two_factor_setup", channel, destination)
        st.session_state["2fa_setup_sent"] = True
        st.success("2FA setup code sent.")
    if st.session_state.get("2fa_setup_sent"):
        setup_code = st.text_input("2FA setup code", max_chars=6, type="password")
        if st.button("Enable 2FA", use_container_width=True, type="primary"):
            if verify_otp(user["id"], "two_factor_setup", setup_code, channel):
                set_2fa_enabled(user["id"], True)
                st.success("Two-factor authentication enabled.")
            else:
                st.error("Invalid or expired 2FA setup code.")
    st.markdown('<div class="ok">✓ Your account is now ready for secure login.</div>', unsafe_allow_html=True)

if st.button("Resend codes", use_container_width=True):
    user = get_user_by_email(email)
    if user:
        if not user["email_verified"]:
            issue_otp(user["id"], "email_verification", "email", user["email"])
        if not user["mobile_verified"]:
            issue_otp(user["id"], "mobile_verification", "sms", user["phone"])
        st.info("Verification codes have been regenerated.")
    else:
        st.info("Enter the email used during signup.")

if st.button("Go to Login", use_container_width=True):
    st.switch_page("pages/1_Login.py")
