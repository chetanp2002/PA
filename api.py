from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.graph import app_graph
from langchain_core.messages import HumanMessage
import uvicorn

app = FastAPI()

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "1"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Prepare Input
        inputs = {"messages": [HumanMessage(content=request.message)]}
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # 2. Run the Agent Brain
        result = app_graph.invoke(inputs, config)
        
        # 3. Extract Final Answer
        last_message = result["messages"][-1].content
        
        # 4. 🧠 EXTRACT THINKING LOGS (The Glass Box Logic)
        thoughts = []
        for msg in result["messages"]:
            # A. Agar Agent ne Tool call kiya
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for call in msg.tool_calls:
                    tool_name = call['name']
                    # Thoda formatting taaki sundar dikhe
                    if tool_name == "get_github_activity":
                        thoughts.append(f"🛠️ **Checking GitHub:** Fetching live API data...")
                    elif tool_name == "get_resume_download_link":
                        thoughts.append(f"📄 **Resume:** Retrieving PDF link...")
                    elif tool_name == "send_contact_email":
                        thoughts.append(f"📧 **Email:** Preparing to send email...")
                    else:
                        thoughts.append(f"🛠️ **Tool Call:** Using `{tool_name}`...")
            
            # B. Agar Tool ne Jawab diya
            if msg.type == "tool":
                thoughts.append(f"✅ **Data Received:** Tool `{msg.name}` execution complete.")

        # 5. Send Response + Thoughts to Frontend
        return {
            "response": last_message,
            "thoughts": thoughts 
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)