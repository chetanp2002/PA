"""
src/project_data.py
Stores structured data for Project Demos, Images, and Metadata.
"""

PROJECT_MEDIA = {
    # 1. REPOBOT AI
    "repobot": {
        "keywords": ["repo", "bot", "github analysis", "flask", "groq"], # 👈 Ye words query me dikhe to ye project milega
        "demo": "https://www.youtube.com/watch?v=YOUR_VIDEO_LINK",
        "image": "https://raw.githubusercontent.com/chetan-pawar/repobot/main/assets/banner.png",
        "github": "https://github.com/chetan-pawar/repobot",
        "description": "A GenAI tool analyzing 500+ GitHub files using Flask and Groq AI."
    },

    # 2. JOBMATE (ATS TOOL)
    "jobmate": {
        "keywords": ["job", "mate", "ats", "resume", "scanner", "hiring tool"],
        "demo": "https://jobmate-live.vercel.app/",
        "image": "https://raw.githubusercontent.com/chetan-pawar/jobmate/main/assets/ui_preview.png",
        "github": "https://github.com/chetan-pawar/jobmate",
        "description": "An ATS-optimization tool using LangChain and Gemini Pro."
    },

    # 3. CILOW AI (INTERNSHIP)
    "cilow": {
        "keywords": ["cilow", "kortix", "agent", "infrastructure", "rust", "internship"],
        "image": "https://your-portfolio.com/images/cilow-arch.png",
        "description": "Built core agent infrastructure using Rust and Kubernetes at Cilow AI."
    },

    # 4. AIRLINE PREDICTION
    "airline": {
        "keywords": ["airline", "passenger", "loyalty", "scikit", "ml", "prediction"],
        "github": "https://github.com/chetan-pawar/airline-prediction",
        "description": "ML model to predict passenger loyalty using 2016-2019 reviews."
    },

    # 5. FINANCIAL CHATBOT
    "finance": {
        "keywords": ["finance", "stock", "market", "phi", "yfinance", "chatbot", "trading"],
        "github": "https://github.com/chetan-pawar/finance-bot",
        "description": "Real-time stock insights chatbot built with Streamlit and PHI."
    }
}

def smart_find_project(query: str) -> dict | None:
    """
    Smartly finds the right project data by matching keywords.
    No more manual if-else statements!
    """
    query = query.lower()
    
    for key, data in PROJECT_MEDIA.items():
        # 1. Check if exact key name is in query (e.g., "repobot")
        if key in query:
            return {"name": key, **data}
        
        # 2. Check keywords (e.g., "ats tool" -> matches "jobmate")
        for keyword in data.get("keywords", []):
            if keyword in query:
                return {"name": key, **data}
                
    return None