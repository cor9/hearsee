import streamlit as st
import openai
import os

# Page Configuration
st.set_page_config(
    page_title="HearSee",
    page_icon="hearsee.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Premium Dark Mode
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }

    /* Header & Logo Area */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        flex-direction: column;
    }

    .logo-img {
        max-width: 150px;
        margin-bottom: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    h1 {
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #FFFFFF 0%, #A1A1AA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 0;
    }

    /* File Uploader Customization */
    .stFileUploader section {
        background-color: #18181B;
        border: 2px dashed #27272A;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.2s ease;
    }

    .stFileUploader section:hover {
        border-color: #3B82F6;
        background-color: #1E1E24;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: transform 0.1s, box-shadow 0.2s;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }

    /* Text Area */
    .stTextArea textarea {
        background-color: #18181B;
        border: 1px solid #27272A;
        border-radius: 8px;
        color: #E4E4E7;
    }

    .stTextArea textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 1px #3B82F6;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        color: #52525B;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication logic
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    # Fallback to user input if not in secrets
    api_key = st.text_input("Enter OpenAI API Key", type="password")

if not api_key:
    st.info("Please add your OpenAI API Key to continue.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# Main UI
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("hearsee.png", use_container_width=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>HearSee</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A1A1AA; margin-bottom: 40px;'>Professional Audio Transcription Engine</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Drop your audio file here", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Transcribe Audio", type="primary"):
        with st.spinner('Translating sound to sight... This may take a moment for large files.'):
            try:
                if uploaded_file.size > 25 * 1024 * 1024:
                    st.warning("File is larger than 25MB. Splitting and processing chunks... This will take longer.")

                    from pydub import AudioSegment
                    import tempfile

                    # Create a temporary directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Save uploaded file
                        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(temp_file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Load audio (pydub handles many formats if ffmpeg is installed)
                        try:
                            audio = AudioSegment.from_file(temp_file_path)
                        except Exception as e:
                            st.error(f"Could not process audio file for splitting. Error: {e}")
                            st.stop()

                        # Chunk size: 10 minutes (OpenAI limit is ~25MB, 10 mins of mp3 is safely under)
                        chunk_length_ms = 10 * 60 * 1000
                        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

                        full_transcript = ""

                        progress_bar = st.progress(0)

                        for i, chunk in enumerate(chunks):
                            chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                            chunk.export(chunk_path, format="mp3")

                            with open(chunk_path, "rb") as audio_file:
                                transcript_chunk = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_file,
                                    response_format="text"
                                )
                                full_transcript += transcript_chunk + " "

                            progress_bar.progress((i + 1) / len(chunks))

                        transcript = full_transcript

                else:
                    # Small file path
                    uploaded_file.name = uploaded_file.name # ensure name logic persists

                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=uploaded_file,
                        response_format="text"
                    )

                st.success("Transcription Complete!")
                st.text_area("Transcript", transcript, height=300)

                st.download_button(
                    label="Download Transcript",
                    data=transcript,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcript.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

st.markdown("""
    <div class='footer'>
        Powered by OpenAI Whisper • Deployed with Streamlit
    </div>
""", unsafe_allow_html=True)
