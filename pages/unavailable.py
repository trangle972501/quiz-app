import streamlit as st

# Set up page configuration
st.set_page_config(
    page_title="Exam Unavailable",
    page_icon="🚧",
    layout="centered"
)

# Center-aligned friendly UI message
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h1 style='text-align: center;'>🚧</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Exam Under Construction</h2>", unsafe_allow_html=True)
    
    # Retrieve details if passed from session state
    category = st.session_state.get("selected_category", "Selected")
    exam_type = st.session_state.get("selected_exam_type", "Course")
    
    st.info(f"We are currently building and verifying the question bank for **{category} - {exam_type}**. Please check back soon!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action button to return to home catalog
    if st.button("⬅️ Back to Home Catalog", use_container_width=True, type="primary"):
        # Clean up navigation states
        st.session_state.pop("selected_category", None)
        st.session_state.pop("selected_exam_type", None)
        st.session_state.selected_exam = None
        st.session_state.current_quiz_data = []
        
        st.switch_page("home.py")