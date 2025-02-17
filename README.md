# 🛒 Voice-Powered POS System (Proof of Concept)

This is a **proof of concept** for a voice-controlled point-of-sale (POS) system designed for small neighborhood stores. The system allows the seller to dictate sold items while moving around the store. The items are automatically added to the POS interface using **speech recognition** and a **local Large Language Model (LLM)** for product inference.

## 🚀 Features

- **Voice Command Processing**: Sellers dictate orders, and the system converts speech into structured product data.
- **Local AI Processing**:
  - Speech recognition via **Vosk Server**.
  - Local **LLM (DeepSeek or similar)** infers product names and quantities.
- **Seamless POS Integration**:
  - The processed data is sent to the POS front-end (React app) via API.
  - The seller can review and confirm items before checkout.
- **Offline-Friendly**: Runs on a **local network** without requiring cloud services.

---

## 🏗️ Project Structure

- **Backend (Python + FastAPI)**: Handles audio processing, LLM inference, and product data management.
- **Frontend (React)**: Displays the POS interface with automatically added products.
- **Android App**: Captures audio and sends it to the backend.
- **Database (SQLite/PostgreSQL)**: Stores the product catalog.

---

## 📦 Tech Stack

| Component          | Technology      |
|-------------------|----------------|
| Backend API       | Python + FastAPI |
| Speech-to-Text    | Vosk Server     |
| LLM Processing    | DeepSeek (or Llama2, GPT4All) |
| Database         | SQLite (or PostgreSQL) |
| Frontend (POS)   | React + Redux / React Query |
| Mobile App       | Android (Kotlin/Java) |

---

## 🔧 Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Vosk Server installed locally
- DeepSeek or LLM model running locally

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/voice-pos.git
cd voice-pos
