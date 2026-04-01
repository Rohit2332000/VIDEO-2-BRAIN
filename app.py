
# --- THIS MUST BE THE FIRST THING IN YOUR SCRIPT ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# --- END OF FIX ---


import streamlit as st
from streamlit import spinner

from supporting_functions import(
    extract_video_id,
    get_transcript,
    translate_transcript,
    get_important_topics,
    generate_notes,
    create_chunks,
    create_vector_store,
    rag_answer
)

#------Sidebar------#
with st.sidebar:
    st.title("🎬 Learnify AI")
    st.markdown("---")
    st.markdown("Transform any YouTube video into key topics, a podcast, or a chatbot.")
    st.markdown("### Input Details")

    youtube_url=st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    language=st.text_input("Video Language Code",placeholder="e.g., en, hi, es, fr",value="en")

    task_option=st.radio(
    "Choose what you want to generate:",
        ["Chat with video","Notes for you"]
    )

    submit_button=st.button("✨ Start Processing")
    st.markdown("---")

st.title("Youtube Content Synthesizer")
st.markdown("Paste a video link and select a task from the sidebar.")



#------Preprocessing Flow-----#
if submit_button:
    if youtube_url and language:
        video_id=extract_video_id(youtube_url)
        if video_id:
            with spinner("Step 1/3 : Fetching Transcript...."):
                full_transcript=get_transcript(video_id,language)

                if language !='en':
                    with spinner("Step 1.5/3: Translating Transcript into English,This may take few moments......"):
                        full_transcript=translate_transcript(full_transcript)


            if task_option=='Notes for you':
                with spinner("Step 2/3: Extracting important topics..."):
                    imp_topics=get_important_topics(full_transcript)
                    st.subheader("Important Topics")
                    st.write(imp_topics)
                    st.markdown("---")

                with spinner("Step 3/3:Generating notes for you...."):
                    notes=generate_notes(full_transcript)
                    st.subheader('Notes for you')
                    st.write(notes)

                st.success("Summary and Notes Generated")

            if task_option=='Chat with video':
                with st.spinner("2/3: Creating Chunks and Vector store...."):
                    chunks=create_chunks(full_transcript)
                    vectorstore=create_vector_store(chunks)
                    st.session_state.vector_store=vectorstore
                st.session_state.messages=[]
                st.success('Video is ready to chat')

# chatbot session#

if task_option=='Chat with video' and "vector_store" in st.session_state:
    st.divider()
    st.subheader("Chat with video")


    #Display the entire history
    for message in st.session_state.get('messages',[]):
        with st.chat_message(message['role']):
            st.write(message['content'])

    #user_input
    prompt=st.chat_input("Ask me anything about the video")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        with st.chat_message('user'):
            st.write(prompt)

        with st.chat_message('assistant'):
            response=rag_answer(prompt,st.session_state.vector_store)
            st.write(response)
        st.session_state.messages.append(({'role':'assistant','content':response}))
