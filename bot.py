import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key=os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

def generate_questions(topic):
    prompt = f"""You are an interviewer who generates questions for interviews. Generate 5 interview questions on the topic of {topic}.
    Do not number the questions. Do not give me a header just give me 5 questions with a line break in between each question."""
    response = model.generate_content(prompt)
    questions = response.text.strip().split('\n')
    
    questions = [q.strip() for q in questions if q.strip()]
    
    return questions

def grade_answer(question, answer):
    prompt = f"Grade the following answer to the question '{question}' on a scale of 1-10: {answer}"
    response = model.generate_content(prompt)
    grade = response.text.strip()
    return grade

def main():
    st.title("AI Interviewer Bot")

    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = False

    def toggle_admin_mode():
        st.session_state.admin_mode = not st.session_state.admin_mode

    st.sidebar.button("Toggle Admin Mode", on_click=toggle_admin_mode)

    if st.session_state.admin_mode:
        st.subheader("Admin Panel")
        topic = st.text_input("Enter the topic for the interview questions:")
        
        if st.button("Generate Questions"):
            if topic:
                st.session_state.questions = generate_questions(topic)
                st.session_state.topic = topic
                st.write("Generated Questions:")
                for i, question in enumerate(st.session_state.questions, 1):
                    st.write(f"{i}. {question}")
            else:
                st.error("Please enter a topic.")
    else:
        st.subheader("Take the Interview")

        if 'questions' not in st.session_state:
            st.write("No interview questions available. Please wait for the admin to configure the questions.")

        if 'answers' not in st.session_state:
            st.session_state.answers = []

        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0

        if st.button("Start Interview"):
            if 'questions' in st.session_state:
                st.session_state.current_question_index = 0
                st.session_state.answers = []
        
        if 'questions' in st.session_state:
            question_index = st.session_state.current_question_index
            if question_index < len(st.session_state.questions):
                question = st.session_state.questions[question_index]
                st.write(f"Question {question_index + 1}: {question}")
                answer = st.text_input("Your Answer:", key=f"answer_{question_index}")

                if st.button(f"Submit Answer for Question {question_index + 1}"):
                    grade = grade_answer(question, answer)
                    st.write(f"Grade for your answer: {grade}")
                    st.session_state.answers.append((question, answer, grade))
                    st.session_state.current_question_index += 1

                    
            else:
                st.write("You have completed all the questions.")

if __name__ == "__main__":
    main()
