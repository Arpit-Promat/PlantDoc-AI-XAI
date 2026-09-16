import streamlit as st
from streamlit_auth import api_post

st.set_page_config(page_title="ATHARVADRISHTI", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--ink:#10251a;--muted:#6b7e71;--green:#1d7b46;--green2:#2fa564;--paper:#f7faf5;--card:#fff;--line:#dce8dc}
html,body,.stApp{background:var(--paper);color:var(--ink);font-family:'DM Sans',sans-serif}
.block-container{max-width:1240px!important;padding:1.5rem 2rem 0!important}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:10px 0 24px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:11px}.brand-leaf{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;background:#10251a;color:#dff7ad;font-size:21px}.brand-title{font:700 16px 'Space Grotesk';letter-spacing:.13em}.brand-sub{font-size:9px;color:var(--muted);letter-spacing:.16em}
.hero{padding:48px 0 70px}.hero h1{font:700 clamp(48px,6vw,82px)/.94 'Space Grotesk';letter-spacing:-.06em;margin:18px 0}.hero h1 span{color:var(--green2)}.hero p{max-width:630px;color:var(--muted);font-size:17px;line-height:1.8}.badge{display:inline-flex;padding:8px 13px;border-radius:99px;background:#eaf5e6;color:var(--green);font-size:12px;font-weight:800}
.art{min-height:480px;border-radius:38px;background:linear-gradient(145deg,#183b27,#28603f 50%,#73ac60);display:grid;place-items:center;position:relative;overflow:hidden;box-shadow:0 30px 75px rgba(20,80,40,.18)}.phone{width:260px;height:450px;border:7px solid #101713;border-radius:42px;background:#d7ead1;box-shadow:0 30px 60px rgba(0,0,0,.22);display:flex;align-items:stretch;justify-content:center;padding:8px}.phone-screen{flex:1;border-radius:33px;background:linear-gradient(160deg,#8bb866,#dbe8bb);display:flex;align-items:center;justify-content:center;font-size:120px;position:relative}.scan{position:absolute;inset:65px 28px;border:2px solid rgba(255,255,255,.9);border-radius:22px}.disease{position:absolute;bottom:22px;left:20px;right:20px;padding:12px;border-radius:16px;background:rgba(255,255,255,.94);font-size:11px;color:#245234;font-weight:800}.float{position:absolute;padding:12px 14px;border-radius:14px;background:#fff;color:#285037;font-size:11px;font-weight:800;box-shadow:0 14px 30px rgba(0,0,0,.15)}.float.a{top:50px;right:22px}.float.b{bottom:62px;left:22px}
.login-card{background:#fff;border:1px solid var(--line);border-radius:24px;padding:26px;box-shadow:0 22px 55px rgba(20,80,40,.12)}.login-card h3{font:700 30px 'Space Grotesk';margin:0 0 5px}.login-card p{color:var(--muted);font-size:13px}.login-help{padding:10px 12px;border-radius:12px;background:#eef8ef;color:#2c7443;font-size:11px;margin-bottom:12px}
.feature-strip{margin:0 -2rem;padding:38px 2rem;background:#eef4ea;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.feature{padding:0 18px;border-right:1px solid #d4e3d5}.feature:last-child{border-right:0}.feature h4{margin:8px 0 4px;font-size:15px}.feature p{color:var(--muted);font-size:11px;line-height:1.55}.icon{font-size:25px}
.secure{padding:80px 0}.secure h2{font:700 46px 'Space Grotesk';letter-spacing:-.05em;margin:10px 0}.secure p{color:var(--muted);line-height:1.7}.step{height:100%;padding:20px;border:1px solid var(--line);border-radius:18px;background:#fff}.step strong{font-size:14px}.step p{font-size:11px;margin:8px 0}.step .mini{padding:9px 11px;background:#f1f7ee;border-radius:10px;font-size:11px;color:#557261;margin-top:8px}
.green-band{margin:0 -2rem;padding:34px 2rem;background:#123a24;color:#eaf6e8;text-align:center}.green-band h2{font:700 28px 'Space Grotesk';margin:0 0 5px}.green-band p{color:#bdd4c2;font-size:12px}.footer{text-align:center;padding:20px 0 5px;color:#7a8b80;font-size:10px}
@media(max-width:900px){.hero{padding-top:28px}.art{min-height:400px}}
</style>
""", unsafe_allow_html=True)

col_nav1,col_nav2,col_nav3,col_nav4=st.columns([3,1,1,1])
with col_nav1: st.markdown('<div class="brand"><div class="brand-leaf">🌿</div><div><div class="brand-title">ATHARVADRISHTI</div><div class="brand-sub">AI for Healthier Crops</div></div></div>',unsafe_allow_html=True)
with col_nav2:
    if st.button("Features",use_container_width=True): st.session_state['section']='features'
with col_nav3:
    if st.button("Login",use_container_width=True): st.switch_page("pages/1_Login.py")
with col_nav4:
    if st.button("Get Started",use_container_width=True): st.switch_page("pages/2_Sign_Up.py")

st.markdown('<div class="hero">',unsafe_allow_html=True)
hero1,hero2=st.columns([1.05,.95],gap="large")
with hero1:
    st.markdown('<span class="badge">AI-Powered Plant Disease Detection</span>',unsafe_allow_html=True)
    st.markdown('<h1>Smarter Insights for <span>Healthier Crops</span></h1>',unsafe_allow_html=True)
    st.markdown('<p>ATHARVADRISHTI uses advanced AI to detect plant diseases, provide expert guidance and help farmers make better decisions for higher yield and healthier crops.</p>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a: st.markdown('🌿\n\n**Detect Diseases**\n\nwith AI')
    with b: st.markdown('🛡️\n\n**Get Expert**\n\nGuidance')
    with c: st.markdown('📈\n\n**Improve Yield**\n\n& Productivity')
    x,y=st.columns(2)
    with x:
        if st.button("Start Now →",use_container_width=True,type="primary"): st.switch_page("pages/1_AI_Scanner.py")
    with y:
        if st.button("Learn More",use_container_width=True): st.session_state['section']='features'
with hero2:
    st.markdown('<div class="art"><div class="float a">⚡ AI-Powered Analysis</div><div class="phone"><div class="phone-screen">🌿<div class="scan"></div><div class="disease">◒ &nbsp; Disease Detected · Tomato Early Blight</div></div></div><div class="float b">🧠 Explainable AI</div></div>',unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)

st.markdown('<div class="login-card">',unsafe_allow_html=True)
st.markdown('### Welcome Back')
st.caption('Login to your account to continue')
identity=st.text_input('Email or Mobile Number',key='landing_identity',label_visibility='collapsed',placeholder='Email or Mobile Number')
password=st.text_input('Password',type='password',key='landing_password',label_visibility='collapsed',placeholder='Password')
if st.button('Login',use_container_width=True,type='primary'):
    r,d=api_post('/api/product-auth/login',{'email':identity,'password':password})
    if r is not None and r.ok:
        if d.get('two_factor_required'):
            st.session_state['login_email']=identity
            st.switch_page('pages/4_Two_Factor.py')
        else:
            st.session_state['access_token']=d.get('access_token','')
            st.switch_page('pages/1_AI_Scanner.py')
    else: st.error(d.get('error','Login failed. Configure the authentication API.'))
if st.button('Sign Up',use_container_width=True): st.switch_page('pages/2_Sign_Up.py')
st.markdown('<div class="login-help">🛡️ Email verification + Mobile verification + OTP-based 2FA available</div>',unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)

st.markdown('<div class="feature-strip">',unsafe_allow_html=True)
fcols=st.columns(6)
features=[('🧠','AI Disease Detection','Identify plant diseases with AI.'),('🛡️','Secure & Reliable','Layered account verification.'),('🌱','Farm Management','Manage farms and crops.'),('📋','Expert Guidance','Observation-focused guidance.'),('📈','Analytics & Reports','Track crop health trends.'),('📱','Multi-Device Access','Use the platform anywhere.')]
for c,(ic,title,desc) in zip(fcols,features):
    with c: st.markdown(f'<div class="feature"><div class="icon">{ic}</div><h4>{title}</h4><p>{desc}</p></div>',unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)

st.markdown('<div class="secure">',unsafe_allow_html=True)
st.markdown('<div class="badge">SECURE ACCESS</div><h2>Multi-Layer Authentication</h2><p>Your account can be protected by email verification, mobile number verification and OTP-based two-factor authentication.</p>',unsafe_allow_html=True)
steps=st.columns(4)
for c,i,t,d in zip(steps,['1','2','3','4'],['Sign Up / Login','Email Verification','Mobile Verification','Two-Factor Authentication'],['Create or access your account.','Verify the code sent to your inbox.','Verify the OTP sent to your mobile.','Add an extra OTP security layer.']):
    with c: st.markdown(f'<div class="step"><strong>{i}. {t}</strong><p>{d}</p><div class="mini">✓ Security step</div></div>',unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)

st.markdown('<div class="green-band"><h2>Together for a Greener Tomorrow</h2><p>Better technology. Healthier crops. Stronger farmers.</p></div><div class="footer">© 2026 ATHARVADRISHTI · Intelligent Plant Health Analysis</div>',unsafe_allow_html=True)
