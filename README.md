# සිංහල සත්‍ය සෙවුම්කරු (Sinhala Fact-Checking System)

Advanced Agentic AI system for verifying Sinhala misinformation using a 4-agent workflow.

## 🤖 4-Agent Architecture

1.  **Domain Classification Agent**: Identifies if the claim is Political, Economic, or Health-related.
2.  **Data Retrieval Agent**: Searches vector database (historical context) and the web (real-time news) using Tavily/Brave.
3.  **Fact Analysis Agent**: Analyzes retrieved evidence against the claim using advanced reasoning (Gemini Pro/Thinking).
4.  **Verdict Agent**: Generates a final True/False/Insufficient verdict with a Sinhala explanation.

## 🚀 Features

- **Multi-Source Retrieval**: Combines Vector Search (Qdrant) + Web Search (Tavily/Brave/DDG).
- **Sinhala Native**: Optimized prompts for Sinhala language processing.
- **Production Ready**: Includes Docker support and CI/CD pipeline.
- **Agentic Workflow**: Built with LangGraph for robust state management.

## 🛠️ Setup & Installation

### Prerequisites

1.  **Python 3.10+**
2.  **Git** (Required for version control)
3.  **Visual C++ Redistributable** (Required for vector search libraries on Windows)
    - Download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Hansa23/sinhala_agentic_ai_fact_check_system.git
    cd sinhala_agentic_ai_fact_check_system
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    TAVILY_API_KEY=your_tavily_key
    # Optional
    QDRANT_PATH=./qdrant_data
    ```

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 🐳 Docker (Production)

To run in a container:

```bash
docker build -t sinhala-fact-check .
docker run -p 8501:8501 --env-file .env sinhala-fact-check
```

## 🧪 Testing

Run the verification script:
```bash
python test_system.py
```
