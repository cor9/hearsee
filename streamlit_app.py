import streamlit as st
import openai
import os
import requests
import tempfile
from pydub import AudioSegment

# Page Configuration
st.set_page_config(
    page_title="Hear-See",
    page_icon="logo.png",
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

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #0E1117;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #18181B;
        border-radius: 8px;
        color: #A1A1AA;
        border: 1px solid #27272A;
        padding: 0 20px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #27272A;
        color: #FAFAFA;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FAFAFA !important;
        border: none !important;
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
        width: 100%;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }

    /* Inputs */
    .stTextInput input {
        background-color: #18181B;
        border: 1px solid #27272A;
        border-radius: 8px;
        color: #FAFAFA;
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

# Helper function to process audio
def process_audio(file_path, original_filename):
    try:
        # Check size (approximate)
        file_size = os.path.getsize(file_path)

        if file_size > 25 * 1024 * 1024:
            st.warning("File is larger than 25MB. Splitting and processing chunks... This will take longer.")

            with tempfile.TemporaryDirectory() as temp_dir:
                # Load audio
                try:
                    audio = AudioSegment.from_file(file_path)
                except Exception as e:
                     # Check if it was pydub issue or ffmpeg issue
                    st.error(f"Could not process audio file. Ensure format is supported. Error: {e}")
                    return None

                # Chunk size: 10 minutes
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

                return full_transcript

        else:
            # Small file processing
            with open(file_path, "rb") as audio_file:
                # Often need explicit name for API if file_path is generic
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript

    except Exception as e:
        st.error(f"An error occurred during transcription: {str(e)}")
        return None

# Main UI
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>Hear-See</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A1A1AA; margin-bottom: 40px;'>Professional Audio Transcription Engine</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📁 Upload File", "🔗 Audio URL", "🎙️ Dictation"])

transcript = None
filename_for_download = "transcript.txt"

# --- Tab 1: Upload File ---
with tab1:
    uploaded_file = st.file_uploader("Drop your audio file here", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])

    if uploaded_file is not None:
        st.audio(uploaded_file)
        if st.button("Transcribe Upload", type="primary", key="btn_upload"):
            with st.spinner('Translating sound to sight...'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_file_path = tmp_file.name

                transcript = process_audio(tmp_file_path, uploaded_file.name)
                filename_for_download = f"{os.path.splitext(uploaded_file.name)[0]}_transcript.txt"
                os.remove(tmp_file_path) # Clean up

# --- Tab 2: URL ---
with tab2:
    url_input = st.text_input("Paste a direct link to an audio file")

    if url_input:
        if st.button("Fetch & Transcribe", type="primary", key="btn_url"):
            try:
                with st.spinner('Downloading audio...'):
                    response = requests.get(url_input, stream=True)
                    response.raise_for_status()

                    # Try to guess extension or default to mp3
                    ext = os.path.splitext(url_input)[1]
                    if not ext: ext = ".mp3"

                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            tmp_file.write(chunk)
                        tmp_file_path = tmp_file.name

                st.audio(tmp_file_path)
                with st.spinner('Translating sound to sight...'):
                    transcript = process_audio(tmp_file_path, "audio_from_url")
                    filename_for_download = "url_audio_transcript.txt"
                    os.remove(tmp_file_path)

            except Exception as e:
                st.error(f"Error fetching URL: {e}")

# --- Tab 3: Dictation ---
with tab3:
    st.info("Click 'Start Recording' below. When finished, it will auto-process.")
    audio_value = st.audio_input("Record Voice")

    if audio_value:
        st.audio(audio_value)
        if st.button("Transcribe Recording", type="primary", key="btn_mic"):
             with st.spinner('Translating sound to sight...'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_value.read())
                    tmp_file_path = tmp_file.name

                transcript = process_audio(tmp_file_path, "recording.wav")
                filename_for_download = "recording_transcript.txt"
                os.remove(tmp_file_path)

# Display Results
if transcript:
    st.divider()
    st.success("Transcription Complete!")
    st.text_area("Transcript", transcript, height=300)

    st.download_button(
        label="Download Transcript",
        data=transcript,
        file_name=filename_for_download,
        mime="text/plain"
    )

st.markdown("""
    <div class='footer'>
        Powered by OpenAI Whisper • Deployed with Streamlit • Designed by AlaCorey
    </div>
""", unsafe_allow_html=True)
