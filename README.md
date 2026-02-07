# 📧 InboxZero AI: Intelligent Email Dashboard

**InboxZero AI** is a privacy-first email assistant that runs locally on your machine. It connects to your inbox, uses **Llama 3** (via Ollama) to read and understand your emails, and organizes them into a modern, real-time dashboard.

## 🚀 Features
* **🔒 Privacy First:** All AI processing happens locally. No data is sent to OpenAI or third-party clouds.
* **🧠 AI Classification:** Uses Llama 3 to intelligently categorize emails as `URGENT`, `BILL`, `SOCIAL`, or `PROMOTION`.
* **⚡ Real-Time Dashboard:** Built with **NiceGUI** for a reactive, modern interface.
* **📩 Secure Auth:** Uses App Passwords and Environment Variables for security.

## 🛠️ Tech Stack
* **Python 3.10+**
* **UI:** [NiceGUI](https://nicegui.io/) (Modern Material Design)
* **AI Engine:** [Ollama](https://ollama.com/) (Running Llama 3)
* **Protocol:** IMAP over SSL

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/MalindaBotheju/InboxZero-AI.git](https://github.com/MalindaBotheju/InboxZero-AI.git)
    cd InboxZero-AI
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Secrets:**
    Create a `.env` file in the root folder:
    ```ini
    EMAIL_USER=your_email@gmail.com
    EMAIL_PASS=your_app_password
    IMAP_SERVER=imap.gmail.com
    ```

4.  **Run the App:**
    ```bash
    python3 dashboard.py
    ```

## 📸 Screenshots
*(You can upload a screenshot of your dashboard here later)*

---
*Built by Malinda Botheju.*
