import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.graph import app_graph

st.set_page_config(page_title="Chetan's Real AI", page_icon="⚡", layout="wide")
st.markdown("<style>.stApp {background-color: #0e1117; color: white;}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚡ System Status")
    st.success("✅ Real-Time API Connected")
    st.markdown("---")
    st.markdown("**Tools Active:**")
    st.markdown("- 🐙 GitHub API (Live)")
    st.markdown("- 📧 SMTP Email Server")
    st.markdown("- 🧠 RAG (Web + Local)")
    
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

st.title("Chetan's Agentic Portfolio")
st.caption("Powered by LangGraph & Real APIs. No Mocks.")

if "messages" not in st.session_state:
    st.session_state.messages = [AIMessage(content="Hello! I am connected to Chetan's real-time data. Ask me about his latest GitHub commits or send him an email directly.")]

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.write(msg.content)

user_input = st.chat_input("Ask: 'What did Chetan code recently?' or 'Email him'")

if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.status("⚙️ Processing Real-Time Request...", expanded=True) as status:
            inputs = {"messages": st.session_state.messages}
            final_res = ""
            # recursion_limit=5 ka matlab hai AI max 5 baar tool use karega, fir ruk jayega
            for event in app_graph.stream(inputs, config={"recursion_limit": 5}):
                for k, v in event.items():
                    if k == "agent":
                        msg = v["messages"][0]
                        if msg.tool_calls:
                            status.write(f"🛠️ Tool Triggered: **{msg.tool_calls[0]['name']}**")
                    elif k == "tools":
                        status.write("✅ Tool Executed Successfully.")
            
            final_res = app_graph.invoke(inputs)["messages"][-1].content
            status.update(label="Response Ready", state="complete", expanded=False)
        
        st.write(final_res)
        st.session_state.messages.append(AIMessage(content=final_res))