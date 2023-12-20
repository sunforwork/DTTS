import streamlit as st
import subprocess
import tempfile
import sys
import os
from os.path import exists
import requests
import tarfile
from PIL import Image

# Set base path
BASE_PATH = os.getcwd() # /home/user/app
BASE_PATH_MODEL = os.path.join(BASE_PATH, "Model")

# Piper TTS download url
URL_PIPER_DOWNLOAD = "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"

# Thorsten-Voice TTS model files
URL_TV_HOCHDEUTSCH_ONNX = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx"
URL_TV_EMOTIONAL_ONNX = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten_emotional/medium/de_DE-thorsten_emotional-medium.onnx"
URL_TV_HESSISCH_ONNX = "https://huggingface.co/Thorsten-Voice/Hessisch/resolve/main/Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx"

TMP_PIPER_FILENAME = os.path.join(BASE_PATH, "piper.tgz")

##########################
# CHECK OR INSTALL PIPER #
##########################
if os.path.exists(os.path.join(BASE_PATH,"piper")) == False:

    # Piper not downloaded and extracted yet, let's do this first.
    response = requests.get(URL_PIPER_DOWNLOAD)

    if response.status_code == 200:
        with open(TMP_PIPER_FILENAME, 'wb') as f:
            f.write(response.content)

        with tarfile.open(TMP_PIPER_FILENAME, 'r:gz') as tar:
            tar.extractall(BASE_PATH)

    else:
        st.markdown(f"Failed to download Piper TTS from {URL_PIPER_DOWNLOAD} (Status code: {response.status_code})")


#####################################################
# CHECK OR DOWNLOAD: All Thorsten-Voice model files #
#####################################################

# Create "Model" path if not existing
if os.path.exists(BASE_PATH_MODEL) == False:
    os.makedirs(BASE_PATH_MODEL)

    # --- Download "NEUTRAL" TTS model --- #
    response = requests.get(URL_TV_HOCHDEUTSCH_ONNX) 
    if response.status_code == 200:
        with open(os.path.join(BASE_PATH_MODEL, "TV-Neutral.onnx"), 'wb') as f:
            f.write(response.content)

    response = requests.get(URL_TV_HOCHDEUTSCH_ONNX + ".json") 
    if response.status_code == 200:
        with open(os.path.join(BASE_PATH_MODEL, "TV-Neutral.onnx.json"), 'wb') as f:
            f.write(response.content)


    # --- Download "EMOTIONAL" TTS model --- #
    response = requests.get(URL_TV_EMOTIONAL_ONNX) 
    if response.status_code == 200:
        with open(os.path.join(BASE_PATH_MODEL, "TV-Emotional.onnx"), 'wb') as f:
            f.write(response.content)

    response = requests.get(URL_TV_EMOTIONAL_ONNX + ".json") 
    if response.status_code == 200:
        with open(os.path.join(BASE_PATH_MODEL, "TV-Emotional.onnx.json"), 'wb') as f:
            f.write(response.content)


    # --- Download "HESSISCH" TTS model --- #
    response = requests.get(URL_TV_HESSISCH_ONNX) 
    if response.status_code == 200:
        with open(os.path.join(BASE_PATH_MODEL, "TV-Hessisch.onnx"), 'wb') as f:
            f.write(response.content)

    response = requests.get(URL_TV_HESSISCH_ONNX + ".json") 
    if response.status_code == 200:
        with open(os.path.join(BASE_PATH_MODEL, "TV-Hessisch.onnx.json"), 'wb') as f:
            f.write(response.content)


###########################
# MODEL DOWNLOAD FINISHED #
###########################

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .st-emotion-cache-1y4p8pa {padding-top: 0rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('Guude! 👋')
st.header('Kostenlose deutsche Sprachausgabe - Dank "Thorsten-Voice"')

st.subheader('Wofür?')
st.markdown('Die künstlichen [Thorsten-Voice](https://www.Thorsten-Voice.de) Stimmen sind für **Voice Over und Social Media Content Creator** mit Youtube Videos/Shorts, Instagram, Tik Tok, ... geeignet.' +
            ' Für eine andere künstliche Sprachausgabe in **Sprachassistenten**,' +
            ' für **Hobby und Bastelprojekte** oder natürlich auch gerne **einfach nur zum Spaß** um witzige **Sprachnachrichten** zu verschicken.')

#st.image('Thorsten-Voice_transparent_klein.png')

with st.form("my_form"):
   option = st.selectbox(
     'Wie soll die Stimme klingen?',
     ('Normal', 'Fröhlich', 'Wütend', 'Angewidert', 'Betrunken', 'Schläfrig', 'Flüsternd', 'Hessischer Dialekt'))
   
   text = st.text_area("Zu sprechender Text",max_chars=500)
   submitted = st.form_submit_button("Sprechen")
   
   if submitted:
    with st.spinner("Bitte einen Augenblick Gedult - bin gleich soweit ..."):
        filename = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

        # Set Piper TTS command based on choice
        PIPER_CMD = os.path.join(BASE_PATH,"piper","piper")
        SPEAKER_ID = "0"

        match option:
            case "Normal":
                MODEL = "TV-Neutral.onnx"
            case "Hessischer Dialekt":
                MODEL = "TV-Hessisch.onnx"
            case "Fröhlich":
                MODEL = "TV-Emotional.onnx"
                SPEAKER_ID = "0"
            case "Wütend":
                MODEL = "TV-Emotional.onnx"
                SPEAKER_ID = "1"
            case "Angewidert":
                MODEL = "TV-Emotional.onnx"
                SPEAKER_ID = "2"
            case "Betrunken":
                MODEL = "TV-Emotional.onnx"
                SPEAKER_ID = "3"
            case "Schläfrig":
                MODEL = "TV-Emotional.onnx"
                SPEAKER_ID = "5"
            case "Flüsternd":
                MODEL = "TV-Emotional.onnx"
                SPEAKER_ID = "7"

        cmd = "echo '" + text + "' | " + BASE_PATH + "/piper/piper --model " + os.path.join(BASE_PATH_MODEL, MODEL) + " --speaker " + SPEAKER_ID + " --output_file " + filename.name

        result = subprocess.run(cmd, shell=True)
        audio_file = open(filename.name, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes,format="audio/wav")
try:
    st.download_button('Runterladen', audio_bytes, file_name='Thorsten-Voice.wav')
except:
    pass

st.subheader('Mehr Infos?')
st.markdown('Möchtest Du mehr über die Möglichkeiten von **Thorsten-Voice** erfahren? Beispielsweise wie Du meine Stimme' +
            ' auch komplett ohne Internet auf deinem PC mit Windows, Linux, Mac OS oder auf dem Raspberry Pi verwendest.'+ 
            ' Dann sieh gerne auf der Projektwebseite www.Thorsten-Voice.de nach.')