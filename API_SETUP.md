# API Integration Guide

## 🔑 API Keys Setup

All APIs have free tiers. No payment card required initially.

---

## 1️⃣ Google Gemini API (REQUIRED)

### Cost
- **Free**: 60 requests/minute, unlimited free tier
- **Paid**: Optional, only if you exceed free limits

### Setup
1. Visit: https://makersuite.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key
4. Paste in `.env`:
```env
GOOGLE_API_KEY=your_key_here
```

### Models Used
- `gemini-1.5-flash`: Classification & quick tasks (15 RPM)
- `gemini-1.5-pro`: Complex reasoning (2 RPM)
- `gemini-2.0-flash-thinking-exp-01-21`: Decision making (10 RPM)

### Verification
```python
import google.generativeai as genai
genai.configure(api_key="your_key")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello")
print(response.text)
```

---

## 2️⃣ Tavily Search (OPTIONAL)

### Cost
- **Free**: 1000 requests/month
- **Paid**: $10+ monthly for more

### Setup
1. Visit: https://tavily.com
2. Sign up (free account)
3. Dashboard → API Keys
4. Copy API key
5. Add to `.env`:
```env
TAVILY_API_KEY=your_key_here
```

### Used For
- Primary search provider (best quality)
- Domain-specific filtering
- Citation support

### Check Quota
```python
from src.search import MultiSourceSearch
search = MultiSourceSearch()
status = search.get_quota_status()
print(status['tavily'])  # {'used': 42, 'remaining': 958}
```

---

## 3️⃣ Brave Search (OPTIONAL)

### Cost
- **Free**: 2000 requests/month
- **Paid**: $5+ monthly for more

### Setup
1. Visit: https://api.search.brave.com
2. Sign up (free account)
3. Copy Subscription Token
4. Add to `.env`:
```env
BRAVE_API_KEY=your_token_here
```

### Used For
- Secondary search provider (privacy-focused)
- Fallback when Tavily exhausted

### Check Quota
```python
from src.search import MultiSourceSearch
search = MultiSourceSearch()
status = search.get_quota_status()
print(status['brave'])  # {'used': 15, 'remaining': 1985}
```

---

## 4️⃣ DuckDuckGo Search (FREE, NO KEY)

### Cost
- **Unlimited**: No API key needed, no rate limit publicly documented

### Setup
- Already integrated! No configuration needed.
- Works as final fallback

### Used For
- Final fallback when Tavily & Brave exhausted
- Always available offline (when privacy mode used)

### Example
```python
from duckduckgo_search import DDGS

ddgs = DDGS()
results = list(ddgs.text("Sri Lanka economy", max_results=10))
print(results)
```

---

## 📊 Search Provider Fallback Chain

```
Input Query
    ↓
Try Tavily (1000/month)
    ↓ Success
    └─→ Return Results
    ↓ Exhausted or Error
Try Brave (2000/month)
    ↓ Success
    └─→ Return Results
    ↓ Exhausted or Error
Try DuckDuckGo (Unlimited)
    ↓ Success
    └─→ Return Results
    ↓ Error (rare)
    └─→ Empty results with error message
```

---

## 💾 Quota Management

### Check All Quotas
```python
from src.search import MultiSourceSearch

search = MultiSourceSearch()
status = search.get_quota_status()

print(f"Tavily: {status['tavily']['remaining']}/1000")
print(f"Brave: {status['brave']['remaining']}/2000")
print(f"DuckDuckGo: {status['duckduckgo']['remaining']}")
```

### View in Streamlit UI
Open `streamlit run app.py` and check the left sidebar:
```
📊 Search Quota
- Tavily: 842/1000
- Brave: 1985/2000
- DuckDuckGo: ♾️ Unlimited
```

### Rate Limiting
The system automatically:
1. Checks quota before each search
2. Tracks usage in real-time
3. Falls back to next provider if limit reached
4. Logs which provider was used

---

## 🔐 Security Best Practices

### Do NOT
❌ Commit `.env` file to GitHub
❌ Share API keys in emails/chats
❌ Hardcode keys in source code
❌ Post keys in error messages

### Do
✅ Use `.env` file (git-ignored)
✅ Create separate API keys per environment (dev/prod)
✅ Rotate keys regularly
✅ Use minimal required scopes
✅ Enable rate limiting

### .env Template
```env
# Required
GOOGLE_API_KEY=sk-...

# Optional (leave empty to use fallback)
TAVILY_API_KEY=tvly-...
BRAVE_API_KEY=brave-...
```

---

## 🧪 Testing API Connections

### Test All APIs
```powershell
# With venv activated
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

# Test Gemini
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('test')
print('✓ Gemini OK')

# Test Tavily (if configured)
if os.getenv('TAVILY_API_KEY'):
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
    print('✓ Tavily configured')

# Test Brave (if configured)
if os.getenv('BRAVE_API_KEY'):
    print('✓ Brave configured')

# Test DuckDuckGo
from duckduckgo_search import DDGS
ddgs = DDGS()
print('✓ DuckDuckGo OK')
"
```

---

## 💰 Cost Calculation

### Monthly Cost (Typical Usage)

For **1000 fact-checks/month**:

| Service | Requests | Cost |
|---------|----------|------|
| Gemini Flash | 1000 | Free (within quota) |
| Tavily | 1000 | Free (1000/month tier) |
| Brave | 0 (Tavily used) | Free |
| DuckDuckGo | 0 (fallback only) | Free |
| **TOTAL** | | **$0** |

For **10,000 fact-checks/month**:

| Service | Requests | Cost |
|---------|----------|------|
| Gemini Flash | 10,000 | Free (within quota) |
| Tavily | 1000 | Free (1000/month) |
| Brave | 2000 | Free (2000/month) |
| DuckDuckGo | 7000 | Free |
| **TOTAL** | | **$0** |

### If you exceed free tiers:

Gemini: ~$1-5/month (depends on model usage)
Tavily: ~$10/month for additional 2000
Brave: ~$5/month for additional 2000

---

## 🔄 Token Counting

### Approximate Tokens Per Claim

```
Input: "ශ්‍රී ලංකාවේ ජිඩීපී වර්ධනය විය"
    ↓
Gemini Processing:
├─ Flash (classify): ~20 tokens
├─ Thinking (decide): ~50 tokens
├─ Pro (analyze): ~200 tokens
└─ Total: ~270 tokens/claim

Cost at $0.075/M tokens: $0.00002 per claim
1000 claims: $0.02
```

---

## 🚨 Troubleshooting

### "Invalid API key"
- Check `.env` file exists
- Verify key is copied completely
- No extra spaces or quotes around key

### "Rate limit exceeded"
- Check `search.get_quota_status()`
- System automatically falls back to next provider
- DuckDuckGo fallback always works

### "Module 'tavily' not found"
```powershell
pip install tavily-python
```

### "Google API error"
- Verify API is enabled in Google Cloud Console
- Check key has Generative Language API enabled
- Try refreshing key

---

## 📚 Resources

- [Gemini API Docs](https://ai.google.dev/)
- [Tavily Search Docs](https://docs.tavily.com/)
- [Brave Search Docs](https://api.search.brave.com/docs)
- [DuckDuckGo Docs](https://duckduckgo.com/duckduckgo-help-pages/)

---

## ✅ Verification Checklist

- [ ] Google API key added to `.env`
- [ ] `python config.py` shows "Environment variables validated"
- [ ] Streamlit sidebar shows search quotas
- [ ] Can make a fact-check without errors
- [ ] System falls back to DuckDuckGo when other limits hit

**All set!** Your API integrations are ready. 🚀
