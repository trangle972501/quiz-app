import streamlit as st
from constants.cert_constant import CertificateType

# Set up page config at the very top
st.set_page_config(page_title="Certification Portal", page_icon="🎓", layout="wide")

#Initialize Session State
if "selected_exam" not in st.session_state:
    st.session_state.selected_exam = None
if "current_quiz_data" not in st.session_state:
    st.session_state.current_quiz_data = []

st.title("🎓 Certification Exam Portal")
st.write("Choose a category and select an exam to start practicing.")
st.markdown("---")

# Top Category Naviagtion Tab
categories = CertificateType.get_names()
category_tab = st.tabs(categories)

for idx, tab in enumerate(category_tab):
    with tab:
        cat_name = categories[idx]
        st.write("")

        # Safely fetch items for this category
        cert_group = CertificateType.from_name(cat_name)
        items = getattr(cert_group, "items", []) if cert_group else []

        if not items:
            st.info(f"No exams available under {cat_name} yet.")
            continue

        cols = st.columns(4)
        items = CertificateType.from_name(cat_name).items

        for item_idx, item in enumerate(items):
            col = cols[item_idx % 4]
            with col:
                with st.container(border=True):
                    st.markdown(f"### `Exam`")
                    st.subheader(item["name"])
                    st.write(item["description"])

                    #Learn more button switches to app.py using streamlit switch_page
                    if st.button("Learn more", key=f"btn_{cat_name}_{item_idx}", use_container_width=True, type="primary"):
                        #1. Store category and exam type in session state
                        st.session_state.selected_category = cat_name          # e.g., "ISTQB"
                        st.session_state.selected_exam_type = item["key"]  # e.g., "CTFL" or "CT-GenAI"
                        
                        # 2. Reset quiz navigation variables
                        st.session_state.selected_exam = None
                        st.session_state.current_quiz_data = []
                        st.session_state.current_q = 0
                        st.session_state.score = 0
                        st.session_state.user_answers = {}
                        st.session_state.quiz_complete = False
                        st.session_state.submitted = False
                        
                        # 3. Switch to the quiz application page
                        st.switch_page("pages/exam.py")