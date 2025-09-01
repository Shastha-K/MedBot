import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import logging
import tkinter as tk
from tkinter import scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyaudio
from google.cloud import speech
import queue
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Running without image support.")

os.environ["ALSA_LOG_LEVEL"] = "0"
os.environ["PA_ALSA_PLUGHW"] = "1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = "circular-gist-455506-g1"
REGION = "us-east1"
ENDPOINT_ID = "--Your_Endpoint_ID--"
SERVICE_ACCOUNT_FILE = "----"  
MAX_TOKENS = 4096
IMAGE_PATH = "medbot_image.jpg"  # image of eyes on the Splash Screen

# Servo pins 
# S1_PIN = 22
# S2_PIN = 23
# S3_PIN = 24
# S4_PIN = 25
# S5_PIN = 8

SAMPLE_RATE = 16000
CHUNK_SIZE = 512
DEVICE_INDEX = None

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)
except FileNotFoundError:
    logger.error(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
    exit()

try:
    model = GenerativeModel(model_name=f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{ENDPOINT_ID}")
    logger.info(f"Successfully loaded model from endpoint {ENDPOINT_ID}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

def estimate_tokens(text):
    return len(text) // 4 + 1

# def move_servo(pin, angles, delay_time=1):
#     for angle in angles:
#         pulse = int(600 + (angle / 180.0) * 1800)
#         logger.info(f"Moving servo on pin {pin} to angle {angle} with pulse {pulse} µs")
#         pi.set_servo_pulsewidth(pin, pulse)
#         time.sleep(delay_time)
#         pi.set_servo_pulsewidth(pin, 0)

def get_default_device_index():
    p = pyaudio.PyAudio()
    try:
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                logger.info(f"Found input device: {dev['name']} (index: {i})")
                return i
        logger.error("No input devices found.")
        return None
    finally:
        p.terminate()

class MicrophoneStream:
    def __init__(self, rate=SAMPLE_RATE, chunk=CHUNK_SIZE):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self._audio_interface = None
        self._audio_stream = None

    def __enter__(self):
        try:
            self._audio_interface = pyaudio.PyAudio()
            device_index = DEVICE_INDEX if DEVICE_INDEX is not None else get_default_device_index()
            if device_index is None:
                raise ValueError("No valid audio input device found.")
            self._audio_stream = self._audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self._chunk,
                stream_callback=self._callback
            )
            self.closed = False
            logger.info("Microphone stream opened")
            return self
        except Exception as e:
            logger.error(f"Failed to open microphone: {e}")
            self.__exit__(None, None, None)
            raise

    def _callback(self, in_data, frame_count, time_info, status):
        if in_data and not self.closed:
            self._buff.put(in_data)
        return (None, pyaudio.paContinue)

    def __exit__(self, type, value, traceback):
        self.closed = True
        if self._audio_stream:
            self._audio_stream.stop_stream()
            self._audio_stream.close()
        if self._audio_interface:
            self._audio_interface.terminate()
        logger.info("Microphone stream closed")

    def generator(self):
        while not self.closed:
            try:
                chunk = self._buff.get(timeout=1.0)
                if chunk is None:
                    continue
                if len(chunk) != self._chunk * 2:
                    logger.warning(f"Unaligned chunk size: {len(chunk)}, expected {self._chunk * 2}")
                    continue
                yield chunk
            except queue.Empty:
                continue

def transcribe_streaming():
    try:
        client = speech.SpeechClient(credentials=credentials)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-IN",
            enable_automatic_punctuation=True,
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream() as stream:
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in stream.generator()
            )
            responses = client.streaming_recognize(streaming_config, requests)

            transcript = ""
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                entry_prompt.delete("1.0", tk.END)
                entry_prompt.insert(tk.END, transcript)
                if result.is_final:
                    break
            return transcript
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

def start_listening():
    try:
        logger.info("Starting speech recognition...")
        transcript = transcribe_streaming()
        entry_prompt.delete("1.0", tk.END)
        entry_prompt.insert(tk.END, transcript)
    except Exception as e:
        logger.error(f"Speech recognition failed: {e}")
        messagebox.showerror("Error", f"Speech recognition failed: {str(e)}")

def generate_response():
    prompt = entry_prompt.get("1.0", tk.END).strip()
    if not prompt:
        messagebox.showwarning("Warning", "Please enter a prompt!")
        return

    try:
        response = model.generate_content(prompt)
        logger.info("Generation successful")

        prompt_tokens = estimate_tokens(prompt)
        response_tokens = estimate_tokens(response.text)
        total_tokens = prompt_tokens + response_tokens
        remaining_tokens = MAX_TOKENS - total_tokens

        response_text.config(state=tk.NORMAL)
        response_text.insert(tk.END, f"User: {prompt}\n")
        response_text.insert(tk.END, f"Bot: {response.text}\n")
        response_text.insert(tk.END, f"Tokens used: {total_tokens} (Prompt: {prompt_tokens}, Response: {response_tokens})\n")
        response_text.insert(tk.END, f"Tokens remaining: {remaining_tokens}\n")

        # Comment out servo actions since pigpio is not available
        # prompt_lower = prompt.lower()
        # if any(condition in prompt_lower for condition in ["cold", "cough", "fever", "headache", "body pain"]):
        #     move_servo(S2_PIN, [0, 80, 0])
        #     move_servo(S1_PIN, [80, 0, 80])
        #     response_text.insert(tk.END, "Action: Dispensed Pill A\n")
        # else:
        #     move_servo(S3_PIN, [0, 80, 0])
        #     move_servo(S4_PIN, [70, 0, 70])
        #     response_text.insert(tk.END, "Action: Dispensed Pill B\n")
        # move_servo(S5_PIN, [0, 120, 0])

        response_text.insert(tk.END, "-" * 50 + "\n")
        response_text.see(tk.END)
        response_text.config(state=tk.DISABLED)

        entry_prompt.delete("1.0", tk.END)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        messagebox.showerror("Error", f"Generation failed: {str(e)}")

def start_chatbot():
    logger.info("Switching to chatbot page")
    splash_frame.pack_forget()
    chatbot_frame.pack(fill=tk.BOTH, expand=True)

def on_closing():
    logger.info("Closing MedBot")
    # pi.stop()  # Comment out since pigpio is not available
    if messagebox.askokcancel("Quit", "Do you want to exit?"):
        root.destroy()

# GUI Setup with ttkbootstrap
root = ttk.Window(themename="flatly")  
root.title("MedBot Chatbot")
root.geometry("800x560")

splash_frame = ttk.Frame(root)
splash_frame.pack(fill=tk.BOTH, expand=True)

if PIL_AVAILABLE:
    try:
        image = Image.open(IMAGE_PATH)
        image = image.resize((700, 450), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        image_label = ttk.Label(splash_frame, image=photo)
        image_label.image = photo
        image_label.pack(pady=20)
        logger.info("Splash image loaded successfully")
    except Exception as e:
        logger.error(f"Image load failed: {e}")
        image_label = ttk.Label(splash_frame, text="Welcome to MedBot", font=("Helvetica", 16, "bold"))
        image_label.pack(pady=20)
else:
    image_label = ttk.Label(splash_frame, text="Welcome to MedBot", font=("Helvetica", 16, "bold"))
    image_label.pack(pady=20)

start_button = ttk.Button(splash_frame, text="Start MedBot", command=start_chatbot, style="primary.TButton")
start_button.pack(pady=10)
logger.info("Created splash page with Start MedBot button")

# Chatbot Frame
chatbot_frame = ttk.Frame(root)

label_prompt = ttk.Label(chatbot_frame, text="Your Message:", font=("Helvetica", 12))
label_prompt.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky=tk.W)

entry_prompt = scrolledtext.ScrolledText(
    chatbot_frame, height=4, width=50, font=("Helvetica", 10),
    relief="sunken", borderwidth=1
)
entry_prompt.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky=tk.EW)

btn_listen = ttk.Button(chatbot_frame, text="Start Listening", command=start_listening, style="info.TButton")
btn_listen.grid(row=2, column=0, pady=10, padx=5, sticky=tk.W)

btn_generate = ttk.Button(chatbot_frame, text="Send Message", command=generate_response, style="success.TButton")
btn_generate.grid(row=2, column=1, pady=10, padx=5, sticky=tk.E)
logger.info("Created Start Listening and Send buttons")

label_response = ttk.Label(chatbot_frame, text="Chat History:", font=("Helvetica", 12))
label_response.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky=tk.W)

response_text = scrolledtext.ScrolledText(
    chatbot_frame, height=12, width=60, font=("Helvetica", 10),
    state=tk.DISABLED, relief="sunken", borderwidth=1
)
response_text.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))

chatbot_frame.grid_rowconfigure(4, weight=1)
chatbot_frame.grid_columnconfigure(0, weight=1)
chatbot_frame.grid_columnconfigure(1, weight=1)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
