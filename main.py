import streamlit as st
from dotenv import load_dotenv
import os
from langchain.schema import SystemMessage
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from supabase import create_client





@st.cache_resource
def init():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase= create_client(url, key)
    # load the OpenAI API key from the enviroment variable
    if os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is get")


@st.cache_data
def call_openai(input, _template_name):
    chain = LLMChain(llm=OpenAI(temperature=0.9), prompt=_template_name)
    response = chain.run(input)
    return response




def main():
    init()
    header = st.container()
    header.title("Job Prep Cards 🤖")
    header.subheader(
        "Discover the ultimate job interview preparation app, designed "
        "to empower you with the skills and confidence needed to land the job of your dreams."
    )

    interview_question = None
    label = "Enter your topic here:"
    topic = header.text_input(
        label=label,
        key="user_input",
        label_visibility="hidden",
        placeholder=label,
    )

    topic_template = PromptTemplate(
        input_variables=["prompt"],
        template=
            "Generate a question about a specific topic, that could be asked in a job interview."
            " ChatGPT should not ask for personal experiences etc. The topic is: {prompt}"
       ,
    )

    if topic:
        with st.spinner("Generating a Question"):
            interview_question = call_openai(topic, topic_template)
            st.write(interview_question)

    if interview_question:
        answer_label = "write your answer "
        user_answer = st.text_input(
            label=answer_label,
            key="user_answer",
            label_visibility="hidden",
            placeholder=answer_label,
        )

        if user_answer:
            script_template = PromptTemplate(
                input_variables=["prompt"],
                template="What is a good summary of the correct answer to: {prompt}?",
            )

            compare_text_template = PromptTemplate(
                input_variables=["prompt1", "prompt2"],
                template=
                    "Compare the user's answer to your own summary. Judge the user's answer and respond with a "
                    "percentage that corresponds to your judgement. The user's answer was: {prompt1} and your "
                    " own answer was: {prompt2}",
                
            )

            with st.spinner("Loding"):
                script = call_openai(interview_question, script_template)
                compare_text = call_openai({'prompt1':"user_answer",'prompt2': "ai_answer"}, compare_text_template )
                st.write(script)
                st.write(compare_text)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Job Prep Cards",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    main()
