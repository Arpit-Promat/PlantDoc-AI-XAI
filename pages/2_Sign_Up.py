import streamlit as st
from streamlit_auth import api_post

st.set_page_config(page_title="Sign Up | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("<style>body{background:#f7fbf8}.card{padding:34px;border:1px solid #dce8dc;border-radius:28px;background:#fff;box-shadow:0 20px 60px rgba(20,80,40,.10)}h1{font-family:Arial,sans-serif}</style>", unsafe_allow_html=True)

st.markdown("## 🌿 ATHARVADRISHTI")
st.markdown("# Create your account")
st.caption("Secure your plant-health workflow with email verification, mobile verification and optional 2FA.")

with st.form("signup"):
    name = st.text_input("Full name")
    email = st.text_input("Email address")
    phone = st.text_input("Mobile number", placeholder="+919876543210")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Create account", use_container_width=True)

if submitted:
    response, data = api_post("/api/product-auth/register", {"name": name, "email": email, "phone": phone, "password": password})
    if response is not None and response.ok:
        st.session_state["verify_email"] = data.get("email", email)
        st.session_state["verify_phone"] = data.get("phone", phone)
        st.success("Account created. Verification codes have been processed.")
        st.switch_page("pages/3_Verify.py")
    else:
        st.error(data.get("error", "Unable to create account."))

if st.button("Back to home", use_container_width=True):
    st.switch_page("streamlit_app.py")
