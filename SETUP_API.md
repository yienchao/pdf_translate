# API Key Setup - Option 2 (Environment Variable)

## ✅ Your API Key is Already Configured!

Your Anthropic API key has been set up in **`start_with_api.bat`**

---

## 🚀 To Start the App with API Key:

**Just double-click:**
```
start_with_api.bat
```

The app will:
1. Load your API key from the environment
2. Start Streamlit
3. Open in your browser at http://localhost:8501
4. Show "✅ API Key loaded from environment" in the sidebar

---

## 🔒 Security Notes:

Your API key files are protected:
- ✅ `.env.example` - Added to `.gitignore` (won't be committed)
- ✅ `start_with_api.bat` - Added to `.gitignore` (won't be committed)

**This means your API key is safe and won't be pushed to GitHub!**

---

## 📝 How It Works:

The batch file sets the environment variable before starting Streamlit:
```batch
set ANTHROPIC_API_KEY=sk-ant-api03-...
streamlit run app.py
```

The app checks for the environment variable first:
```python
env_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if env_api_key:
    st.session_state["anthropic_api_key"] = env_api_key
```

---

## 🎯 Next Steps:

1. **Double-click** `start_with_api.bat`
2. **Upload** a French PDF
3. **Click** "🤖 Auto-Translate with AI"
4. **Download** the translated PDF!

The API will automatically translate using Claude Haiku 4.5 - no manual translation needed!
