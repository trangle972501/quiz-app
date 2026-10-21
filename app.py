import math

import streamlit as st
import os
import random

# Set up page configuration
st.set_page_config(
    page_title="My Streamlit App",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded"
)

quiz_data_path = "data/istqb/ctai/en/quiz_data.json"

# Load quiz data from JSON file
def load_quiz_data(file_path):
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def chunk_exams():
    # Group questions into chunks of <target_count> to form seperate exams
    target_count = 5
    all_questions = load_quiz_data(quiz_data_path)
    if not all_questions:
        return {}
    exams_pool = {}
    total_available = len(all_questions)

    #Calaculate how many full exams we can make from unique questions
    num_exams = max(1, math.ceil(total_available / target_count))
    print(f"Total available questions: {total_available}, Target count per exam: {target_count}, Number of exams: {num_exams}")

    for i in range(num_exams):
        start_idx = i * target_count
        end_idx = start_idx + target_count
        chunk = all_questions[start_idx:end_idx]

        # Rule: if a chunk is shorter than target_count, resuse previous questions to fill it up
        if len(chunk) < target_count and total_available > 0:
            needed = target_count - len(chunk)
            chunk.extend(random.choices(chunk, k=needed))
        exams_pool[f"Exam {i + 1} ({target_count} Questions)"] = chunk

    return exams_pool

exams_pool = chunk_exams()

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

if not exams_pool:
    st.error("⚠️ Could not find or read `exams.json`. Make sure it's in the same folder as `app.py`.")
    st.stop()

# --- SCREEN 1: EXAM SELECTION MENU ---
if st.session_state.selected_exam is None:
    st.title("📚 Select an Exam")
    st.write("Choose an exam below. Each exam is locked to 40 questions (reusing questions if your pool is small) and randomly shuffled!")
    st.markdown("---")
    
    for exam_name, question_list in exams_pool.items():
        col1, col2 = st.columns([3, 1])
        col1.subheader(exam_name)
        col2.write(f"📝 {len(question_list)} Questions")
        
        if col1.button(f"Start {exam_name}", key=exam_name, type="primary"):
            st.session_state.selected_exam = exam_name
            
            # Shuffle the order of the 40 questions for this attempt
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
        correct_answers = current_item["answer"]  # Handles your list format
        is_multi_answer = len(correct_answers) > 1
        
        st.subheader(f"Question {st.session_state.current_q + 1} of {total_questions}")
        # Replace \n with Markdown line breaks
        formatted_question = current_item['question'].replace("\n", "  \n")
        st.markdown(f"### {formatted_question}")

       # DYNAMIC UI: Checkboxes for multi-answer, Radio buttons for single-answer
        selected_options = []
        if is_multi_answer:
            st.info("ℹ️ **Multiple Choice:** This question has more than one correct answer. Check all that apply:")
            # Loop through options and display each as an open checkbox
            for opt in current_item["options"]:
                # Unique key for each checkbox per question
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

                    # GRADING LOGIC: Increment score if correct
                    if is_multi_answer:
                        # Exact set matching (order doesn't matter))
                        if set(selected_options) == set(correct_answers):
                            st.session_state.score += 1
                    else:
                        if selected_option == correct_answers[0]:
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
            # Uses your JSON key spelling "explaination"
            for opt in selected_options:
                st.info(f"**Your Answer:** {opt}\n\n{current_item['explaination'].get(opt, 'No explanation available.')}")

            # if wrong or missing answers, show the correct answer
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