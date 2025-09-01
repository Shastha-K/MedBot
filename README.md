# MedBot – AI-Powered Health Assistant & Pill Dispenser
MedBot is an intelligent healthcare assistant that combines **AI-driven medical chatbot** with a **Raspberry Pi–controlled pill dispenser**.
It uses **Google Vertex AI** for generating responses and **Google Cloud Speech-to-Text** for voice input.

🏆 *3rd Place Winner – Engineering Clinics Expo 2025 (500+ projects)*


## Features

- Voice Input – Converts speech to text using Google Cloud Speech API
- Chatbot Responses – Powered by Vertex AI generative models
- User Interface – Tkinter + ttkbootstrap with splash + chat window
- Chat History – Scrollable user–bot conversation logs
- Pill Dispenser Integration – Raspberry Pi hardware extension 


## Tech Stack

- Python 3.10+
- Tkinter + ttkbootstrap – UI framework
- Vertex AI – AI chatbot backend
- Google Cloud Speech-to-Text – Real-time speech recognition
- PyAudio – Microphone input
- Pillow (PIL) – Image handling in UI


## Setup & Installation

1. Clone the repository
```
git clone https://github.com/yourusername/medbot.git
cd medbot
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Model Training & Fine-Tuning on Vertex AI
   - Dataset Preparation
     - Collected datasets:
     - PubMedQA → medical Q&A.
     - A-Z Medicine Dataset of India(Kaggle)

   - Preprocessing: 
     Converted into instruction–response JSONL (Vertex AI requires this format):
     ```
     {"input_text": "What is the treatment for diabetes?", "output_text": "Diabetes is managed with lifestyle changes, monitoring, and medications like metformin."}
     {"input_text": "What are side effects of aspirin?", "output_text": "Stomach pain, nausea, heartburn, and bleeding risk."}
     ```
     
     Uploaded dataset to Google Cloud Storage bucket (gs://your-bucket/medbot_dataset.jsonl).

   - Vertex AI Model Selection
     - Vertex supports custom fine-tuning of models like Llama / Gemini.
     - MedBot was built on Gemini Flash 2.0 lite.

   - Model Fine-Tuning and Deployement
     - The JSONL files are uploaded in buckets for fine-tuning.
     - The model can be accessed via a CLI but for our use case we deployed it in a bucket.

3. GUI Endpoint
   1. In the gui_endpoint.py file, update the config on the code.
```
PROJECT_ID = "your-project-id"
REGION = "us-east1"
ENDPOINT_ID = "your-endpoint-id"
SERVICE_ACCOUNT_FILE = "/absolute/path/to/medbot-api-key.json"
IMAGE_PATH = "medbot_image.jpg"  # Optional splash image
```
   2. MedBot had a GUI but can also be accessed on the terminal, all using the Vertex AI SDK.

5. Run MedBot
   ```
   python3 gui_endpoint.py
   ```


## How It Works

- Voice Input → Captured via microphone (PyAudio).
- Speech-to-Text → Real-time transcription using Google Cloud Speech API.
- AI Response → Prompt sent to Vertex AI fine-tuned endpoint using the Python SDK.
- UI Display → Response shown in scrollable chat history.
- Pill Dispensing (Optional) → Raspberry Pi triggers servo motors based on detected symptoms.


## Notes

- Raspberry Pi servo code is commented out for macOS; works on Linux/Raspberry Pi OS with pigpio.
- Ensure microphone permissions are enabled for real-time voice input.
- Token usage is logged in the UI (prompt, response, remaining tokens).

 
## References

- [Vertex AI Python SDK Documentation](https://cloud.google.com/python/docs/reference/vertex-ai?utm_source=chatgpt.com)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text?utm_source=chatgpt.com)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html?utm_source=chatgpt.com)
- [ttkbootstrap Documentation](https://ttkbootstrap.readthedocs.io/?utm_source=chatgpt.com)
