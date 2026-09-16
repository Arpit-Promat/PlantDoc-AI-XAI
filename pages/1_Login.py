import streamlit as st
from streamlit_auth import api_post

st.set_page_config(page_title="Login | ATHARVADRISHTI", page_icon="🌿", layout="centered")
st.markdown("<style>div[data-testid='stForm']{border:1px solid #dce8dc;border-radius:24px;padding:20px;background:#fff}</style>", unsafe_allow_html=True)

st.markdown("## 🌿 ATHARVADRISHTI")
st.title("Welcome Back")
st.caption("Login with your email or mobile number. Verified accounts can enable OTP-based 2FA.")

identity = st.text_input("Email or Mobile Number")
password = st.text_input("Password", type="password")

if st.button("Login", use_container_width=True, type="primary"):
    # The Flask product-auth endpoint currently accepts email. Mobile-login can be
    # added to the backend without changing this page's UX when the API is ready.
    r, d = api_post("/api/product-auth/login", {"email": identity, "password": password})
    if r is not None and r.ok:
        if d.get("two_factor_required"):
            st.session_state["login_email"] = identity
            st.session_state["login_2fa_channel"] = d.get("channel", "email")
            st.switch_page("pages/4_Two_Factor.py")
        else:
            st.session_state["access_token"] = d.get("access_token", "")
            st.success("Login successful.")
            st.switch_page("pages/1_AI_Scanner.py")
    else:
        st.error(d.get("error", "Login failed."))

c1, c2 = st.columns(2)
with c1:
    if st.button("Create account", use_container_width=True):
        st.switch_page("pages/2_Sign_Up.py")
with c2:
    if st.button("Verify account", use_container_width=True):
        st.switch_page("pages/3_Verify.py")

if st.button("Back to Home", use_container_width=True):
    st.switch_page("streamlit_app.py")
