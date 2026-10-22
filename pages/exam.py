import math
import streamlit as st
import os
import random
from utils.json_util import JsonUtil

# Set up page configuration
st.set_page_config(
    page_title="Active Exam Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Check if user came from home page; if not, redirect them back
if "selected_category" not in st.session_state or "selected_exam_type" not in st.session_state:
    st.warning("⚠️ Please select an exam from the Home page first.")
    if st.button("⬅️ Go to Home"):
        st.switch_page("home.py")
    st.stop()

category = st.session_state.selected_category
exam_type = st.session_state.selected_exam_type

# Initialize Session State Variables
if "selected_exam" not in st.session_state:
    st.session_state.selected_exam = None
if "current_quiz_data" not in st.session_state:
    st.session_state.current_quiz_data = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_complete" not in st.session_state:
    st.session_state.quiz_complete = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# 2. Load exams dynamically using the passed category and exam_type
@st.cache_data
def load_all_exams(cat, e_type):
    return JsonUtil.chunk_exams(cat, e_type)

exams_pool = load_all_exams(category, exam_type)

# IF NO EXAMS ARE FOUND, REDIRECT TO THE UNAVAILABLE PAGE
if not exams_pool:
    st.switch_page("pages/unavailable.py")

# --- SCREEN 1: EXAM SELECTION MENU ---
if st.session_state.selected_exam is None:
    st.title(f"📚 {category} - {exam_type}: Select an Exam")
    st.write("Choose an exam below. Each exam is locked to 40 questions and randomly shuffled!")
    st.markdown("---")
    
    # Back button to return to home page catalog
    if st.button("⬅️ Back to Home Catalog"):
        st.session_state.pop("selected_category", None)
        st.session_state.pop("selected_exam_type", None)
        st.switch_page("home.py")

    for exam_name, question_list in exams_pool.items():
        col1, col2 = st.columns([3, 1])
        col1.subheader(exam_name)
        col2.write(f"📝 {len(question_list)} Questions")
        
        if col1.button(f"Start {exam_name}", key=exam_name, type="primary"):
            st.session_state.selected_exam = exam_name
            
            # Shuffle the order of the questions for this attempt
            st.session_state.current_quiz_data = random.sample(question_list, len(question_list))
            
            # Reset states
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_complete = False
            st.session_state.submitted = False
            st.rerun()
        st.divider()

# --- SCREEN 2: ACTIVE QUIZ OR RESULTS ---
else:
    active_exam_name = st.session_state.selected_exam
    quiz_data = st.session_state.current_quiz_data
    total_questions = len(quiz_data)
    
    if st.button("⬅️ Back to Exam Menu"):
        st.session_state.selected_exam = None
        st.rerun()

    st.title(f"🧠 {active_exam_name}")
    st.markdown("---")

    if not st.session_state.quiz_complete:
        st.progress(st.session_state.current_q / total_questions)
        
        current_item = quiz_data[st.session_state.current_q]
        correct_answers = current_item["answer"]  
        is_multi_answer = len(correct_answers) > 1
        
        st.subheader(f"Question {st.session_state.current_q + 1} of {total_questions}")
        formatted_question = current_item['question'].replace("\n", "  \n")
        st.markdown(f"### {formatted_question}")

        selected_options = []
        if is_multi_answer:
            st.info("ℹ️ **Multiple Choice:** This question has more than one correct answer. Check all that apply:")
            for opt in current_item["options"]:
                chk_key = f"chk_{st.session_state.selected_exam}_{st.session_state.current_q}_{opt}"
                if st.checkbox(opt, key=chk_key, disabled=st.session_state.submitted):
                    selected_options.append(opt)
        else:
            selected_option = st.radio(
                "Choose your answer:",
                current_item["options"],
                index=None,
                key=f"q_{st.session_state.current_q}_{st.session_state.selected_exam}",
                disabled=st.session_state.submitted
            )
            if selected_option is not None:
                selected_options = [selected_option]

        # SUBMISSION LOGIC
        if not st.session_state.submitted:
            if st.button("Submit Answer", type="primary"):
                if not selected_options:
                    st.warning("⚠️ Please select at least one option before submitting!")
                else:
                    st.session_state.submitted = True
                    st.session_state.user_answers[st.session_state.current_q] = selected_options

                    if is_multi_answer:
                        if set(selected_options) == set(correct_answers):
                            st.session_state.score += 1
                    else:
                        if selected_options[0] == correct_answers[0]:
                            st.session_state.score += 1
                    st.rerun()

        # POST-SUBMISSION FEEDBACK
        else:
            if is_multi_answer:
                is_correct = set(selected_options) == set(correct_answers)
            else:
                is_correct = (selected_options[0] == correct_answers[0])
            
            if is_correct:
                st.success("🎉 **Correct!**")
            else:
                st.error("❌ **Incorrect!**")

            st.write("#### 💡 Explanation:")
            for opt in selected_options:
                st.info(f"**Your Answer:** {opt}\n\n{current_item['explaination'].get(opt, 'No explanation available.')}")

            if not is_correct:
                st.warning("**Correct Answer(s):**")
                for ans in correct_answers:
                    st.caption(f"- `{ans}:` {current_item['explaination'][ans]}")

            is_last_question = (st.session_state.current_q + 1 == total_questions)
            button_label = "View Results" if is_last_question else "Next Question ➡️"
            
            if st.button(button_label, type="primary"):
                st.session_state.submitted = False
                if is_last_question:
                    st.session_state.quiz_complete = True
                else:
                    st.session_state.current_q += 1
                st.rerun()

    else:
        # Results Screen
        st.progress(1.0)
        st.success("🎉 You've completed this exam!")
        
        score = st.session_state.score
        percentage = (score / total_questions) * 100
        
        col1, col2 = st.columns(2)
        col1.metric("Final Score", f"{score} / {total_questions}")
        col2.metric("Percentage", f"{percentage:.1f}%")

        if percentage >= 70:
            st.balloons()
            st.write("🏆 **Great job! You passed the exam!**")
        else:
            st.write("📚 **Keep practicing! Review the concepts below.**")

        if st.button("🔄 Retake Exam (Reshuffle Questions)", type="primary"):
            question_list = exams_pool[active_exam_name]
            st.session_state.current_quiz_data = random.sample(question_list, len(question_list))
            
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_complete = False
            st.session_state.submitted = False
            st.rerun()