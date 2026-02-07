# 🚀 Setup Guide - Sinhala Fact-Checking System

## Step 1: Install Python

### Windows
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
```powershell
python --version
```

### Alternative: Using Windows Package Manager
```powershell
winget install Python.Python.3.11
```

## Step 2: Create Virtual Environment

```powershell
# Navigate to project
cd e:\sinhala_agentic_ai_fact_check_system

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# If you get permission error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Expected output**: All packages should install without errors.

## Step 4: Configure API Keys

```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit .env with your keys
# Open in editor and fill in:
# - GOOGLE_API_KEY (required)
# - TAVILY_API_KEY (optional, 1000/month free)
# - BRAVE_API_KEY (optional, 2000/month free)
```

### Getting API Keys

**Google Gemini** (Required):
1. Visit https://makersuite.google.com/app/apikeys
2. Create new API key
3. Copy to `.env`

**Tavily** (Optional):
1. Visit https://tavily.com
2. Sign up free (1000/month)
3. Copy API key

**Brave Search** (Optional):
1. Visit https://api.search.brave.com
2. Sign up free (2000/month)
3. Copy subscription token

## Step 5: Run the Streamlit App

```powershell
# Make sure venv is activated
venv\Scripts\Activate.ps1

# Launch Streamlit
streamlit run app.py
```

**Expected**: Browser opens at `http://localhost:8501`

## Step 6: Test the System

In the Streamlit app, paste a Sinhala claim:
```
ශ්‍රී ලංකාවේ ජිඩීපී වර්ධනය විය
```

Click "සත්‍යාපනය" and observe:
- ✅ Verdict (true/false/insufficient)
- 📊 Domain classification
- 🔍 Search source (Tavily/Brave/DuckDuckGo)
- ⏱️ Processing time
- 💾 Cache status

## 📊 Project Structure

```
e:\sinhala_agentic_ai_fact_check_system\
├── app.py                    # Streamlit UI
├── main.py                   # CLI entry point
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── .env.example             # API key template
├── README.md                # Main documentation
├── SETUP.md                 # This file
│
├── src/                     # Core modules
│   ├── __init__.py
│   ├── models.py           # State machine definition
│   ├── workflow.py         # LangGraph workflow
│   ├── gemini_router.py    # Model selection
│   ├── vector_store.py     # Qdrant integration
│   ├── search.py           # Multi-source search
│   ├── cache.py            # Result caching
│   └── async_processor.py  # Batch processing
│
├── data/                   # User documents
├── qdrant_data/           # Vector database
└── venv/                  # Virtual environment (created later)
```

## 🎯 Next: Verify Installation

```powershell
# Activate venv
venv\Scripts\Activate.ps1

# Test imports
python -c "import langgraph; import google.generativeai; import qdrant_client; print('All imports OK!')"

# Run system validation
python config.py
```

Expected output:
```
✓ Environment variables validated
✓ Directories ensured
```

## ⚙️ Advanced Configuration

### Adjust Cache TTL (24 hours default)
Edit `app.py`, line ~40:
```python
st.session_state.cache = SimpleCache(ttl_hours=48)  # Change to 48
```

### Adjust Concurrent Requests
Edit `src/async_processor.py`, line ~8:
```python
self.max_concurrent = 20  # Increase from 10
```

### Switch Search Providers
Edit `src/search.py` to change fallback order or add custom providers.

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not set"
```powershell
# Verify .env exists
Get-Content .env

# Should show:
# GOOGLE_API_KEY=your_actual_key_here
# NOT:
# GOOGLE_API_KEY=your_google_api_key_here
```

### "ModuleNotFoundError"
```powershell
# Ensure venv is activated (shows (venv) in prompt)
venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### "Qdrant connection failed"
```powershell
# Delete corrupted database
Remove-Item -Recurse -Force qdrant_data

# App will auto-recreate on next run
```

### Rate limiting issues
Reduce concurrent requests in `src/async_processor.py`:
```python
self.max_concurrent = 5  # From 10
```

## 📈 Performance Tips

1. **Enable cache hits**: Keep app running, verify same claims multiple times
2. **Batch processing**: Use `main.py` for 10+ claims (runs in parallel)
3. **Use DuckDuckGo**: Falls back automatically if Tavily/Brave exhausted
4. **Monitor quotas**: Check Streamlit sidebar for real-time API usage

## 🚀 Deployment

### Local network access
```powershell
streamlit run app.py --server.address 0.0.0.0
```
Access from other machines on network: `http://your-ip:8501`

### Headless (server mode)
```powershell
streamlit run app.py --logger.level=error --client.showErrorDetails=false
```

## 📚 Further Reading

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Gemini API](https://ai.google.dev/)
- [Qdrant Docs](https://qdrant.tech/)
- [Streamlit Guide](https://docs.streamlit.io/)

## ✅ Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] All packages installed from requirements.txt
- [ ] .env file configured with GOOGLE_API_KEY
- [ ] `python config.py` passes all checks
- [ ] `streamlit run app.py` launches successfully
- [ ] Sidebar shows all system status metrics
- [ ] Can input a Sinhala claim and get a verdict
- [ ] Cache working (try same claim twice)

## 🎉 You're Ready!

Once all items checked, run:
```powershell
streamlit run app.py
```

Your Sinhala fact-checking system is live! 🚀
