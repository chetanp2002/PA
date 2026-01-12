import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "chetanp2002") # Default agar .env mein na ho
    RESUME_LINK = "https://chetanp-portfolio.netlify.app/resume.pdf"