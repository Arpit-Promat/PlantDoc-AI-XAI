import streamlit as st
from streamlit_auth import api_post

st.set_page_config(page_title="Verify Account | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("<style>div[data-testid='stVerticalBlockBorderWrapper']{border-radius:24px}</style>", unsafe_allow_html=True)

st.markdown("## 🌿 ATHARVADRISHTI")
st.title("Verify your account")
st.caption("Complete both email and mobile verification before secure login.")

email = st.text_input("Email", value=st.session_state.get("verify_email", ""))
email_code = st.text_input("Email verification code", max_chars=6, type="password")
if st.button("Verify Email", use_container_width=True):
    r, d = api_post("/api/product-auth/verify-email", {"email": email, "code": email_code})
    if r is not None and r.ok:
        st.session_state["email_verified"] = True
        st.success("Email verified successfully.")
    else:
        st.error(d.get("error", "Email verification failed."))

phone = st.text_input("Mobile number", value=st.session_state.get("verify_phone", ""))
mobile_code = st.text_input("Mobile verification OTP", max_chars=6, type="password")
if st.button("Verify Mobile", use_container_width=True):
    r, d = api_post("/api/product-auth/verify-mobile", {"phone": phone, "code": mobile_code})
    if r is not None and r.ok:
        st.session_state["mobile_verified"] = True
        st.success("Mobile number verified successfully.")
    else:
        st.error(d.get("error", "Mobile verification failed."))

if st.session_state.get("email_verified") and st.session_state.get("mobile_verified"):
    st.success("Both verification steps are complete. You can now log in.")

col1, col2 = st.columns(2)
with col1:
    if st.button("Resend codes", use_container_width=True):
        r, d = api_post("/api/product-auth/resend", {"email": email})
        st.info(d.get("message", d.get("error", "Verification codes processed.")))
with col2:
    if st.button("Go to Login", use_container_width=True):
        st.switch_page("pages/1_Login.py")
