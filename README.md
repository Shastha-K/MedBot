# MedBot – AI-Powered Health Assistant & Pill Dispenser
MedBot is an intelligent healthcare assistant that combines **AI-driven medical chatbot** with a **Raspberry Pi–controlled pill dispenser**.
It uses **Google Vertex AI** for generating responses and **Google Cloud Speech-to-Text** for voice input.

🏆 3rd Place Winner – Engineering Clinics Expo 2025 (500+ projects)


## Features

- 🎤 Voice Input – Converts speech to text using Google Cloud Speech API
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
   1. Dataset Preparation
     - Collected datasets:
     - PubMedQA → medical Q&A.
     - A-Z Medicine Dataset of India(Kaggle)\
   2. Preprocessing: 
     Converted into instruction–response JSONL (Vertex AI requires this format):
     ```
     {"input_text": "What is the treatment for diabetes?", "output_text": "Diabetes is managed with lifestyle changes, monitoring, and medications like metformin."}
     {"input_text": "What are side effects of aspirin?", "output_text": "Stomach pain, nausea, heartburn, and bleeding risk."}
     ```
     
     Uploaded dataset to Google Cloud Storage bucket (gs://your-bucket/medbot_dataset.jsonl).\

   3. Vertex AI Model Selection
     - Vertex supports custom fine-tuning of models like Llama / Gemini.
     - MedBot was built on Gemini Flash 2.0 lite.\

   4. Model Fine-Tuning and Deployement
     - The JSONL files are uploaded in buckets for fine-tuning.
     - The model can be accessed via a CLI but for our use case we deployed it in a bucket.\

4. GUI Endpoint
   1. 
