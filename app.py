import streamlit as st
import os

# Set up page configuration
st.set_page_config(
    page_title="My Streamlit App",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded"
)

quiz_data = "data/istqb/ctai/en/quiz_data.json"

# Load quiz data from JSON file
def load_quiz_data(file_path):
    import json
    with open(file_path, 'r') as f:
        return json.load(f)

quiz_data = load_quiz_data(quiz_data)

# Initialize Session State
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

st.title("🧠 Python Interactive Quiz")
st.write("Test your knowledge and learn from detailed explanations for every option!")
st.markdown("---")

total_questions = len(quiz_data)

if not st.session_state.quiz_complete:
    # Progress Bar
    st.progress(st.session_state.current_q / total_questions)
    
    current_item = quiz_data[st.session_state.current_q]
    
    st.subheader(f"Question {st.session_state.current_q + 1} of {total_questions}")
    st.write(f"### {current_item['question']}")

    # Radio button selection
    selected_option = st.radio(
        "Choose your answer:",
        current_item["options"],
        index=None,
        key=f"q_{st.session_state.current_q}",
        disabled=st.session_state.submitted  # Freeze choice after submitting
    )

    # State 1: Before Submitting
    if not st.session_state.submitted:
        if st.button("Submit Answer", type="primary"):
            st.session_state.submitted = True
            st.session_state.user_answers[st.session_state.current_q] = selected_option
            
            if selected_option == current_item["answer"]:
                st.session_state.score += 1
            
            st.rerun()

    # State 2: After Submitting (Display instant option explanations)
    else:
        is_correct = (selected_option == current_item["answer"])
        
        if is_correct:
            st.success(f"🎉 **Correct!**")
        else:
            st.error(f"❌ **Incorrect!** The correct answer was **{current_item['answer']}**.")

        # Breakdown of all options
        st.write("#### 💡 Option Breakdown:")
        for option in current_item["options"]:
            explanation = current_item["explaination"][option]
            if option == current_item["answer"]:
                st.info(f"**{option} (Correct Answer):** {explanation}")
            elif option == selected_option:
                st.warning(f"**{option} (Your Choice):** {explanation}")
            else:
                st.write(f"- **{option}:** {explanation}")

        # Next Question / Finish Button
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
    # Final Results Screen
    st.progress(1.0)
    st.success("🎉 You've completed the quiz!")
    
    score = st.session_state.score
    percentage = (score / total_questions) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Final Score", f"{score} / {total_questions}")
    col2.metric("Percentage", f"{percentage:.1f}%")

    if percentage == 100:
        st.balloons()
        st.write("🏆 **Perfect score! You mastered every concept!**")
    elif percentage >= 70:
        st.write("👏 **Great job! High score achieved!**")
    else:
        st.write("📚 **Keep practicing! Review the detailed explanations below.**")

    # Detailed Final Breakdown
    with st.expander("🔍 Detailed Answer Breakdown", expanded=True):
        for idx, q in enumerate(quiz_data):
            user_ans = st.session_state.user_answers.get(idx, "No Answer")
            correct_ans = q["answer"]
            
            st.markdown(f"### Q{idx+1}: {q['question']}")
            
            if user_ans == correct_ans:
                st.markdown(f"✅ **You selected:** `{user_ans}` (Correct)")
            else:
                st.markdown(f"❌ **You selected:** `{user_ans}` | **Correct:** `{correct_ans}`")

            # Display explanation for user choice vs correct choice
            st.caption(f"**Why '{correct_ans}' is correct:** {q['explaination'][correct_ans]}")
            if user_ans != correct_ans:
                st.caption(f"**Why '{user_ans}' is incorrect:** {q['explaination'][user_ans]}")
            
            st.divider()

    # Restart Quiz
    if st.button("Restart Quiz"):
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.user_answers = {}
        st.session_state.quiz_complete = False
        st.session_state.submitted = False
        st.rerun()