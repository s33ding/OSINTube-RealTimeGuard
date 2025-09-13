import streamlit as st

def is_authenticated():
    """Check if user is authenticated - server-side validation"""
    return st.session_state.get('authenticated', False) and st.session_state.get('user_email') == 'roberto.diniz@iesb.edu.br'

def get_current_user():
    """Get current user email"""
    if is_authenticated():
        return st.session_state.get('user_email')
    return None

def logout_user():
    """Logout user - clear server-side session"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.id_token = None
    
    # Clear any client-side storage
    logout_js = """
    <script>
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = '/';
    </script>
    """
    st.markdown(logout_js, unsafe_allow_html=True)
