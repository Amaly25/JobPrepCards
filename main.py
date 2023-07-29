import streamlit as st
from dotenv import load_dotenv
import os
from langchain.schema import SystemMessage
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain


# langchain.chains is going to allow us to run topic through our prompt template and then go and generate output


def init():
    load_dotenv()
    # load the OpenAI API key from the enviroment variable
    if os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is get")


@st.cache_data
def call_openai(input, _template_name):
    llm = OpenAI(temperature=0.9)
    chain = LLMChain(llm=llm, prompt=_template_name)
    response = chain.run(prompt=input)
    return response


def main():
    init()
    header = st.container()
    header.title("Job Interview Preparation..Your own knowledge Tester 🤖")
    header.subheader(
        "Discover the ultimate job interview preparation app, designed to empower you with the skills and confidence needed to land the job of your dreams."
    )

    messages = [
        SystemMessage(content=("You are a helpful assistant")),
    ]

    response = None
    label = "Enter your topic here:"
    prompt = header.text_input(
        label=label,
        key="user_input",
        label_visibility="hidden",
        placeholder=label,
    )

    title_template = PromptTemplate(
        input_variables=["prompt"],
        template="write a an interview question about {prompt}",
    )

    if prompt:
        with st.spinner("Generating a Question"):
            response = call_openai(prompt, title_template)
            st.write(response)

    if response:
        label2 = "write your answer "
        prompt1 = st.text_input(
            label=label2,
            key="user_answer",
            label_visibility="hidden",
            placeholder=label2,
        )

        if prompt1:
            script_template = PromptTemplate(
                input_variables=["prompt"],
                template="write me a appropriate answer based on this topic: {prompt} ",
            )

            compare_text_template = PromptTemplate(
                input_variables=["prompt"],
                template="compare the user answer in the input prompt1 based on the script_templat AI Answer and give a percentaage of the correctness of the users answer: {prompt}",
            )

            with st.spinner("Loding"):
                script = call_openai(response, script_template)
                comper_text = call_openai(prompt1, compare_text_template)
                st.write(script)
                st.write(comper_text)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Your own knowledge Tester",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    main()
