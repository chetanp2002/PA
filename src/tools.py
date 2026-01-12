import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_core.tools import tool
from src.config import Config
import requests
from datetime import datetime, timezone

# Global Cache to stop duplicates
EMAIL_CACHE = {}

@tool
def get_resume_download_link():
    """Returns the direct download link for Chetan's Resume PDF."""
    return "Here is the direct link: https://chetanp-portfolio.netlify.app/resume.pdf"

@tool
def get_github_activity():
    """
    Fetches Chetan's LATEST public activity from GitHub API directly.
    It compares the latest event date with today's date to verify real-time activity.
    """
    # 👇 Ensure this is your correct GitHub username
    username = "chetanp2002" 
    url = f"https://api.github.com/users/{username}/events/public"
    
    try:
        # 1. Fetch Data
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            events = response.json()
            
            if events:
                latest = events[0]
                
                # 2. Extract Dates (YYYY-MM-DD format)
                # GitHub returns UTC time, so we compare with UTC today
                event_date_str = latest.get('created_at', '').split('T')[0]
                today_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                
                # 3. Extract Details
                event_type = latest.get('type', 'Unknown Event')
                repo_name = latest.get('repo', {}).get('name', 'Unknown Repo')
                
                details = ""
                # If it's a code push, get the specific commit message
                if event_type == "PushEvent":
                    commits = latest.get('payload', {}).get('commits', [])
                    if commits:
                        details = f" - Commit: '{commits[0]['message']}'"
                
                # 4. LOGIC: Compare Dates
                if event_date_str == today_date_str:
                    return (
                        f"✅ **YES! He is coding RIGHT NOW (Today).**\n"
                        f"- **Date:** Today ({event_date_str})\n"
                        f"- **Action:** {event_type} on **{repo_name}**\n"
                        f"{details}"
                    )
                else:
                    return (
                        f"❌ **No commits today.**\n\n"
                        f"His last public activity was on **{event_date_str}**.\n"
                        f"- **Repo:** {repo_name}\n"
                        f"- **Action:** {event_type}{details}"
                    )
            else:
                return "No public GitHub activity found."
        else:
            return f"GitHub API Error: Status {response.status_code}"
            
    except Exception as e:
        return f"Error fetching GitHub data: {str(e)}"
@tool
def send_contact_email(recruiter_email: str, message: str):
    """
    Sends a REAL email to Chetan.
    
    IMPORTANT RULES FOR AI:
    1. DO NOT call this tool with placeholder emails like 'example@example.com'.
    2. Only call this tool AFTER the user has explicitly provided their email address.
    """
    global EMAIL_CACHE
    
    # 🛑 1. VALIDATION CHECK (Stop Hallucinations)
    if "example.com" in recruiter_email or "email" in recruiter_email and "@" not in recruiter_email:
        return "❌ ERROR: You did not provide a valid recruiter email. Please ASK the user for their email address first."
    
    if len(message) < 5 or "insert message" in message.lower():
        return "❌ ERROR: Message is too short or generic. Please ASK the user for a specific message."

    # 🛑 2. DUPLICATE CHECK (Stronger)
    current_time = time.time()
    # Unique Key based on Recruiter Email only (Spam Protection)
    cache_key = recruiter_email.strip().lower()
    
    if cache_key in EMAIL_CACHE:
        last_sent = EMAIL_CACHE[cache_key]
        # 2 Minutes Block Time
        if current_time - last_sent < 120:
            print(f"✋ Blocked duplicate email from {recruiter_email}")
            return f"✅ Email already sent to Chetan from {recruiter_email}. (Duplicate blocked)."

    EMAIL_CACHE[cache_key] = current_time

    # 📨 3. SEND EMAIL
    try:
        sender_email = Config.EMAIL_SENDER
        sender_password = Config.EMAIL_PASSWORD
        receiver_email = Config.EMAIL_RECEIVER

        if not sender_email or not sender_password:
            return "System Error: Email setup incomplete."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"🚀 JOB OPPORTUNITY: {recruiter_email}"

        body = f"""
        Hello Chetan,
        
        You have a new hiring inquiry!
        
        --------------------------------------------------
        📧 From: {recruiter_email}
        💬 Message:
        {message}
        --------------------------------------------------
        
        Sent via your AI Portfolio Agent.
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()

        return f"✅ Done! I have successfully emailed Chetan with your details ({recruiter_email}). He will reply shortly."

    except Exception as e:
        return f"❌ Email Failed. Error: {str(e)}"