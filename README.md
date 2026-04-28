# 🎵 Swaras — Hindusthani Swara Recognition Web App

<div align="center">

![Swaras Banner](https://img.shields.io/badge/Swaras-WebApp-7F77DD?style=for-the-badge&logo=react&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![ML](https://img.shields.io/badge/ML-TensorFlow%20Lite-EF9F27?style=for-the-badge&logo=tensorflow&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-0F6E56?style=for-the-badge)

<br/>

> **A modern web application for real-time Hindusthani swara detection and raga recognition, powered by FastAPI (Python backend) and React (frontend).**

<br/>

[✨ Features](#-features) • [🏗️ Architecture](#️-architecture) • [🚀 Getting Started](#-getting-started) • [🧠 ML Pipeline](#-ml-pipeline) • [📁 Project Structure](#-project-structure) • [🛠️ Tech Stack](#-tech-stack) • [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

| Feature                   | Description                                               |
|---------------------------|-----------------------------------------------------------|
| 🎙️ Real-time Detection    | Live microphone or file upload audio analysis             |
| 🎼 12-Swara Recognition   | Detects all shuddha, komal, and tivra swaras             |
| 🔍 Tonic Auto-detection   | Identifies "Sa" tonic                                    |
| 🏷️ Raga Classification    | Recognizes performed raga                                |
| 📄 Export Notation        | Download sargam sheet or MusicXML                        |
| 📁 File Support           | Analyze `.mp3` / `.wav` uploads                          |
| 🌐 Runs in Browser        | No installation needed; works on most platforms           |

---

## 🏗️ Architecture

```
             ┌─────────────┐          ┌─────────────┐
             │ React Frontend │<──────▶│ FastAPI Backend │
             └─────────────┘   HTTP   └─────────────┘
                   ▲                         │
                   │                         ▼
           (Microphone / File)     ML Model (TensorFlow/TFLite)
```

- **Frontend:** Built using React. Handles UI, audio input, and communicating with the backend.
- **Backend:** FastAPI serves as the REST API, runs ML inference, and manages data.
- **ML Model:** Swara and raga recognition is performed using a pre-trained (TFLite/Keras) model.

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v18+ recommended)
- **Python** 3.10+ (with FastAPI, Uvicorn, etc.)
- [Optional] **ffmpeg** (audio processing if needed)

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Cyberknp/Swaras.git
cd Swaras
```

---

### 2️⃣ Setup Backend (FastAPI)

```bash
# In the project root
cd backend

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

---

### 3️⃣ Setup Frontend (React)

```bash
# In the project root
cd frontend

npm install
npm start
```

Open your browser to [http://localhost:3000](http://localhost:3000) to use the app. The frontend will interact with the backend via REST API (default: http://localhost:8000).

---

### 4️⃣ (Optional) Model Training

- Training and exporting the ML model is managed with Python (see `backend/ml/` or `docs/`).
- Use the provided scripts or notebooks for training and quantization.
- Place the final TFLite model in the backend as described in the FastAPI docs.

---

## 📁 Project Structure

```
Swaras/
├── backend/       # FastAPI backend + ML
│   ├── main.py    # FastAPI app entry
│   ├── ml/        # ML scripts, model weights, utils
│   ├── requirements.txt
│   └── ...
├── frontend/      # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
└── README.md
```

---

## 🧠 ML Pipeline

**Feature Extraction:** Uses librosa, essentia, etc. to get MFCC, chroma, pitch.  
**Model:** CRNN (CNN + LSTM) for swara/raga classification.  
**Inference:** Python (FastAPI) loads TFLite/keras model for prediction via API.

---

## 🛠️ Tech Stack

| Layer       | Technology      |
|-------------|----------------|
| **Frontend** | React, JavaScript/TypeScript, HTML5, CSS3 |
| **Backend**  | FastAPI, Python 3.10+, Uvicorn            |
| **ML**       | TensorFlow/Keras, TFLite                   |

---

## 🤝 Contributing

Pull requests are welcome!  
1. Fork the repo.
2. Create a new branch (`feature/your-feature-name`).
3. Commit your changes.
4. Open a PR.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.

---

<div align="center">

⭐ Star this repo if you found it useful! Made with ❤️ for Hindusthani Classical Music 🎶

</div>
