# Veya AI - Personal Life Intelligence Companion

**Patchamomma 2026 Hackathon Submission**
**Category:** Personal Life Intelligence

Veya AI is a deeply personalized "Living Twin" designed to help busy professionals optimize their life across their most important anchors (e.g., Work, Health, Family, Learning). It ingests schedule data, analyzes behavioral patterns, and provides actionable insights and dynamic planning to prevent burnout and protect what matters most.

---

## 🚀 Live Demo

**Access the live web application here:**
👉 [https://veya-ai-986238160974.us-central1.run.app](https://veya-ai-986238160974.us-central1.run.app)

*Test Accounts:*
1. **Vaibhav** (Mid-Senior Exec, highly stressed)
   - Username: `vaibhav`
   - Password: `password123`
2. **Meera** (Product Manager)
   - Username: `test@veya.ai`
   - Password: `password123`

---

## ✨ Key Features

1. **The "Living Twin" Persona Engine**
   Veya creates a semantic vector graph of your life (Household Orbit, Life Anchors, Relationships). It remembers that your kid needs help with math or that you're prioritizing health.
2. **Context-Aware Dynamic Planning**
   Veya analyzes your upcoming schedule and cross-references it with your energy levels and relationships. If you have 5 hours of back-to-back meetings, Veya will suggest and block a 30-minute recovery walk or protect your family dinner.
3. **Actionable Insights & Health Metrics**
   Real-time monitoring of Cognitive Load, Energy Capacity, and Relational Deficits based on your daily data.
4. **Multi-Agent Conversational AI**
   Chat with Veya naturally. A sophisticated multi-agent system routes your queries (e.g., modifying calendar events, asking for advice, pulling from RAG memory).

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Web Speech API (for voice interactions)
- **Backend Core:** Python 3.12, FastAPI
- **Database:** SQLite (with schema dynamically prepared for Cloud SQL migration)
- **AI / LLM:** Google Gemini API, Custom Multi-Agent Orchestration Framework
- **Google Cloud Services Used:**
  - **Google Cloud Run:** Fully managed serverless deployment
  - **Vertex AI / Vector Search:** Under-the-hood preparation for RAG memory
  - **Secret Manager:** Environment & API key management
  - **Cloud Build / Artifact Registry:** CI/CD and containerization
  - (Planned) *Cloud SQL:* Relational data scaling

---

## 🏗️ Repository Structure

- `/veya_web` - Static frontend assets (HTML, CSS, JS)
- `/veya_server` - FastAPI server (`main.py`) running the REST endpoints
- `/veya_agents` - The Multi-Agent logic (`agent_system.py`, `gemini_engine.py`, `rag_agent.py`)
- `/veya_data` - Database schema setup, Synthetic data generators, Mock connectors
- `seed_vaibhav.py` - Script to generate the test user profile and mock calendar states
- `Dockerfile` & `requirements.txt` - Deployment configurations

---

## ⚙️ Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/priyankadevgan1992/veya-ai-patchamomma.git
   cd veya-ai-patchamomma
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # source venv/bin/activate    # On Mac/Linux
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **Initialize Database and Seed Test Data:**
   ```bash
   python seed_vaibhav.py
   ```

5. **Run the FastAPI Server:**
   ```bash
   python -m uvicorn veya_server.main:app --host 0.0.0.0 --port 8080 --reload
   ```

6. **Access locally:**
   Open `http://localhost:8080` in your web browser.

---

*Built with ❤️ for Patchamomma 2026*
