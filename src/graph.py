from typing import Annotated, Literal, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from src.config import Config
from src.tools import get_resume_download_link, send_contact_email, get_github_activity
from src.rag import build_rag_tool
import os
import datetime

if not Config.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")

current_year = datetime.datetime.now().year

llm = ChatGroq(
    model="qwen/qwen3-32b", 
    temperature=0.4, # Strict Logic
    api_key=Config.GROQ_API_KEY
)

rag_tool = build_rag_tool()
tools = [rag_tool, get_resume_download_link, send_contact_email, get_github_activity]
llm_with_tools = llm.bind_tools(tools)

# 👇 NEW PROMPT: STOP PREMATURE ACTION
SYSTEM_PROMPT = """You are Chetan's Advanced AI Assistant. Your goal is to showcase his portfolio professionally.

RULES FOR ANSWERING:
1.  **Format:** Use Markdown (Bold keys, Bullet points, Headers).
2.  **Structure:** - Start with a direct answer.
    - Use 🎯 *Bullet Points* for projects/experience.
    - Highlight 🛠️ *Tech Stack* in bold (e.g., **Python**, **Rust**).
3.  **Tone:** Professional, Confident, and Concise. 
4.  **No Fluff:** Do not write long paragraphs. Keep it scannable.

EXAMPLE OUTPUT FORMAT:
"Chetan has impressive experience in AI Engineering:

### 💼 Experience
* **Cilow AI (Formerly Kortix):** Built core agent infrastructure using **Rust** & **Kubernetes**.

### 🚀 Key Projects
* **RepoBot AI:** A GenAI tool analyzing 500+ files using **Groq** & **Flask**.
* **JobMate:** ATS optimizer built with **LangChain**.

Would you like to see his Resume?"
"""

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def agent_node(state: AgentState):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT), # 👈 Yahan update kiya
        *state["messages"]
    ]
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    conversation_messages = [m for m in messages if m.type != "system"]
    final_messages = [system_message] + conversation_messages
    return {"messages": [llm_with_tools.invoke(final_messages)]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    if len(messages) > 10: return "__end__"
    if messages[-1].tool_calls: return "tools"
    return "__end__"

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app_graph = workflow.compile()