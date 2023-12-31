import streamlit as st
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from supabase_py import create_client
from audiorecorder import audiorecorder
import openai


@st.cache_resource
def init():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)
    # load the OpenAI API key from the enviroment variable
    if os.getenv("OPENAI_API_KEY") == "":
        print("OPENAI_API_KEY is not set")
        exit(1)
    else:
        print("OPENAI_API_KEY is get")
    return supabase


@st.cache_data
def call_openai(input, _template_name):
    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
    )
    chain = LLMChain(llm=model, prompt=_template_name)
    response = chain.run(input)
    return response


def get_data_base_data(supabase):
    table = supabase.table("jobprep")
    print("")
    print("")
    print("")
    data = table.select("*").execute()
    return data


@st.cache_data
def insert_data_into_database(_supabase, input: dict):
    table = _supabase.table("jobprep")
    insert_data = table.insert(input).execute()
    return insert_data


def main():
    try:
        os.remove("audio.mp3")
        audio = None
    except:
        pass

    supabase = init()
    # data = get_data_base_data(supabase)
    # print(data)

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

    human_message_prompt = HumanMessagePromptTemplate.from_template(
        "Generate a question about a specific topic, that could be asked in a job interview."
        " ChatGPT should not ask for personal experiences etc. The topic is: {prompt}"
    )
    topic_template = ChatPromptTemplate.from_messages([human_message_prompt])

    if topic:
        interview_question = call_openai(topic, topic_template)
        header.write(interview_question)

    if interview_question:
        answer = st.radio("**Enter your answer**:", ("✍️text", "🎙️Record"), index=0)

        if answer == "✍️text":
            answer_label = "write your answer "
            user_answer = header.text_input(
                label=answer_label,
                key="user_answer",
                label_visibility="hidden",
                placeholder=answer_label,
            )

            if user_answer:
                ai_message_prompt = AIMessagePromptTemplate.from_template(
                    interview_question
                )
                compare_text_template = ChatPromptTemplate.from_messages(
                    [
                        human_message_prompt,
                        ai_message_prompt,
                        HumanMessagePromptTemplate.from_template(
                            "Compare the the following answer to your own summary. Judge this answer and respond with a percentage that corresponds to your judgement. Here is the answer: {prompt1}"
                        ),
                    ]
                )

                compare_text = call_openai(
                    {"prompt": topic, "prompt1": user_answer}, compare_text_template
                )
                header.write(compare_text)

                def rerun():
                    st.session_state.user_input = ""
                    st.session_state.user_answer = ""

                st.button(
                    label="next topic",
                    on_click=rerun,
                )

                input = {
                    "topic": topic,
                    "question": interview_question,
                    "answer": user_answer,
                    "aianswer": compare_text,
                }
                database = insert_data_into_database(supabase, input=input)
                print(database)

        if answer == "🎙️Record":
            transcript = None
            wav_file = None

            st.write("Press the microphone button to record  the answwer")
            audio = audiorecorder("🎤 ", " ⏱️ Recording...")

            if len(audio) > 0:
                # to play audio in frontend:
                st.audio(audio.tobytes())

                # to save audio to a file:

                wav_file = open(
                    "audio.mp3", "wb"
                )  # "wb" mode opens the file in binary format for writing while the "rb" option opens the file in binary format for reading.
                wav_file.write(audio.tobytes())
                wav_file.close()

            if wav_file:
                audio_file = open("./audio.mp3", "rb")
                openai.api_key = os.getenv("OPENAI_API_KEY")
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                # print(transcript)
                # st.write(transcript["text"])
                st.write(transcript.get("text", "try again"))

            if transcript:
                ai_message_prompt = AIMessagePromptTemplate.from_template(
                    interview_question
                )
                compare_text_template = ChatPromptTemplate.from_messages(
                    [
                        human_message_prompt,
                        ai_message_prompt,
                        HumanMessagePromptTemplate.from_template(
                            "Compare the the following answer to your own summary. Weite the right answer summary and than Judge this answer and respond with a percentage that corresponds to your judgement. Here is the answer: {prompt2}"
                        ),
                    ]
                )

                compare_text = call_openai(
                    {"prompt": topic, "prompt2": transcript}, compare_text_template
                )
                header.write(compare_text)

                input = {
                    "topic": topic,
                    "question": interview_question,
                    "answer": transcript,
                    "aianswer": compare_text,
                }
                database = insert_data_into_database(supabase, input=input)
                # print(database)

                def rerun():
                    st.session_state.user_input = ""
                    os.remove("audio.mp3")  # Delete the temporary audio file
                if compare_text:
                    st.button(
                        label="next topic",
                        on_click=rerun,
                    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Job Prep Cards",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"]
    {
    background-image: url("https://t4.ftcdn.net/jpg/02/79/86/57/360_F_279865795_okVLwJY5z7C8IaeqSMVMNMQaVwCw446j.jpg");
    background-size: cover;
    }
    [data-testid="stHeader"]{
    background-color: rgba(0, 0, 0, 0);
    }
    </style>
"""
    st.markdown(page_bg_img, unsafe_allow_html=True)

    main()
