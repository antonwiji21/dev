import os
import re
import google.generativeai as genai
import google.cloud.texttospeech as tts
import speech_recognition as sr
import keyboard  # Untuk menangkap tombol Shift
from pydub import AudioSegment
from pydub.playback import play
import io

# Atur path kredensial Google Cloud (Ganti sesuai lokasi file JSON)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "isi sesuai kredensial Google Cloud anda"

# Konfigurasi API Key Gemini
genai.configure(api_key="Api Google Gemini anda")

# Inisialisasi model Gemini
model = genai.GenerativeModel("gemini-1.5-pro-latest", system_instruction="Nama Kamu adalah cici, kamu seorang assisten virtual dengan pembawaan yang lucu dan asik !!.")

# Inisialisasi recognizer untuk mengenali suara
recognizer = sr.Recognizer()
mic = sr.Microphone()

def clean_text(text):
    """Membersihkan teks dari karakter yang tidak diperlukan seperti * atau format Markdown."""
    text = re.sub(r'[*_`]', '', text)  # Hapus *, _ dan ` (jika ada)
    text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi berlebihan
    return text

# Fungsi untuk mengubah teks menjadi suara dengan Google TTS (Bahasa Indonesia)
def text_to_speech(text):
    client = tts.TextToSpeechClient()
    
    synthesis_input = tts.SynthesisInput(text=text)
    voice = tts.VoiceSelectionParams(
        language_code="id-ID",
        name="id-ID-Wavenet-A",  # Suara wanita lebih natural
        ssml_gender=tts.SsmlVoiceGender.FEMALE
    )
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.LINEAR16,
        speaking_rate=1.3,  # Meningkatkan kecepatan bicara
        pitch=5.0  # Nada lebih tinggi agar lebih ekspresif
    )

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    
    # Mengonversi audio agar bisa langsung diputar
    audio = AudioSegment.from_file(io.BytesIO(response.audio_content), format="wav")
    play(audio)

# Fungsi untuk menangkap suara pengguna dan memberikan respons
def get_input():
    """Menerima input dari suara jika Shift ditekan, atau teks jika tidak."""
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

        print("\n📝 Ketik input atau tekan Shift Kiri untuk berbicara...")

        while True:
            if keyboard.is_pressed("shift"):
                print("🎤 Merekam... Silakan bicara!")
                
                # Mulai rekaman saat Shift ditekan
                audio = recognizer.listen(source)

                # Tunggu hingga Shift dilepas
                while keyboard.is_pressed("shift"):
                    pass  # Tunggu sampai tombol dilepas
                
                print("🛑 Rekaman selesai. Memproses...")

                try:
                    # Gunakan bahasa Indonesia untuk pengenalan suara
                    user_input = recognizer.recognize_google(audio, language="id-ID")
                    print(f"🗣️ Kamu (suara): {user_input}")
                    return user_input

                except sr.UnknownValueError:
                    print("❌ Maaf, saya tidak bisa mendengar dengan jelas.")
                except sr.RequestError:
                    print("❌ Error pada layanan pengenalan suara.")

            else:
                # Jika Shift tidak ditekan, gunakan input teks
                user_input = input("📝 Kamu (ketik): ")
                return user_input

# Fungsi utama untuk memproses input dan memberikan respons
def listen_and_respond():
    user_input = get_input()

    if user_input:
        # Kirim input ke Gemini dan stream respons dalam bahasa Indonesia
        response = model.generate_content(f"Jawab dalam bahasa Indonesia: {user_input}", stream=True)

        full_response = ""
        for chunk in response:
            text = chunk.text
            text = clean_text(text)  # Bersihkan teks dari simbol mengganggu
            print(f"🤖 AI: {text}", end="", flush=True)
            full_response += text

        # Ubah teks ke suara (Bahasa Indonesia)
        text_to_speech(full_response)

# Loop utama agar asisten terus mendengarkan
while True:
    listen_and_respond()
