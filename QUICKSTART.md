# Quick Reference - Sinhala Fact-Checking System

## 🎬 Quick Start

```powershell
# 1. First time setup (5 min)
cd e:\sinhala_agentic_ai_fact_check_system
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure API key
# Edit .env file, add your GOOGLE_API_KEY

# 3. Launch
streamlit run app.py
```

## 📋 File Guide

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web UI (START HERE) |
| `main.py` | Python CLI & batch processing |
| `src/workflow.py` | LangGraph state machine |
| `src/search.py` | Multi-source search logic |
| `src/vector_store.py` | Qdrant local vector DB |
| `src/cache.py` | 24h result cache |
| `.env` | API keys (you fill this) |

## 🔧 Common Commands

```powershell
# Activate environment
venv\Scripts\Activate.ps1

# Install new package
pip install package_name

# Verify installation
python config.py

# Test imports
python -c "from src.workflow import FactCheckingWorkflow; print('OK')"

# Run CLI
python main.py

# Launch Streamlit (main interface)
streamlit run app.py

# Clear cache
rm qdrant_data -r -Force

# Deactivate environment
deactivate
```

## 🔑 API Keys Needed

| Service | Required | Limit | Cost |
|---------|----------|-------|------|
| Google Gemini | ✅ Yes | Varies | Free tier available |
| Tavily Search | ⚪ Optional | 1000/month | Free |
| Brave Search | ⚪ Optional | 2000/month | Free |

## 📊 System Flow

```
Input Statement
    ↓
Classify Domain (Flash model)
    ↓
Retrieve from Qdrant Vector Store
    ↓
Check Sufficiency (Thinking model)
    ├─ YES → Analyze directly (Pro model)
    └─ NO → Web Search → Analyze
    ↓
Extract Verdict (true/false/insufficient)
    ↓
Output + Cache Result
```

## 💻 Python Code Examples

### Single Statement
```python
from main import verify_statement

result = verify_statement("ශ්‍රී ලංකාවේ ජිඩීපී වර්ධනය විය")
print(f"Verdict: {result['verdict']}")
print(f"Analysis: {result['analysis']}")
```

### Batch Processing
```python
import asyncio
from main import verify_batch

statements = [
    "Claim 1",
    "Claim 2",
    "Claim 3"
]

results = asyncio.run(verify_batch(statements))
for i, r in enumerate(results):
    print(f"{i+1}. {r['verdict']}")
```

### Direct Workflow
```python
from src.workflow import FactCheckingWorkflow
from src.vector_store import QdrantVectorStore
from src.search import MultiSourceSearch

vector_store = QdrantVectorStore("./qdrant_data")
search = MultiSourceSearch()
workflow = FactCheckingWorkflow(vector_store, search)

result = workflow.verify("Your claim here")
```

## 🎨 Streamlit UI Guide

| Section | What It Shows |
|---------|---------------|
| **Sidebar** | API quotas, vector DB stats, cache size |
| **Input Area** | Text field for Sinhala/English claims |
| **Verdict** | ✅ True / ❌ False / ⚠️ Insufficient |
| **Analysis** | Detailed explanation from Gemini |
| **Details** | Domain, search source, cache hit, timestamp |
| **History** | Last 10 verified claims |

## ⚡ Performance Tips

1. **Fastest**: Cached results (instant)
2. **Fast**: Qdrant retrieval (1-2s)
3. **Medium**: Web search fallback (3-5s)
4. **Batch mode**: 10 parallel claims ~10-15s

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| API key error | Edit `.env`, restart streamlit |
| Module not found | Run `pip install -r requirements.txt` |
| Qdrant error | Delete `qdrant_data` folder |
| Slow first run | Normal (models loading), try same claim again |
| Rate limit hit | Use DuckDuckGo fallback (automatic) |

## 📞 Support

**Error**: Check [SETUP.md](SETUP.md) Troubleshooting section

**Code**: Review docstrings in [src/](src/) files

**Docs**: See [README.md](README.md) for architecture

## 🎯 Next Level

- Add custom vector documents: `src/vector_store.py`
- Change search order: `src/search.py` 
- Customize prompts: `src/workflow.py`
- Add authentication: `app.py` (Streamlit Secrets)
- Deploy to cloud: Follow Streamlit Cloud docs

---

**Last Updated**: Dec 2025  
**Status**: ✅ Production Ready  
**Version**: 0.1.0
