import os
import requests
import tempfile
import shutil
import time

# --- Community Imports (These work for you) ---
from langchain_community.document_loaders import TextLoader, WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

# --- FlashRank Import (This works for you) ---
from langchain_community.document_compressors import FlashrankRerank

# --- Core Imports ---
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from src.config import Config

DB_PATH = "./chroma_db_store"
MODEL_CACHE_PATH = "./model_cache"
SEARCH_CACHE = {}

class SearchInput(BaseModel):
    query: str = Field(description="Query to search (e.g. 'experience', 'projects', 'salary').")

def build_rag_tool():
    # 1. CLEANUP
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
        except OSError:
            pass

    docs = []
    
    # --- LOAD SOURCES ---
    # Brain Dump
    if os.path.exists("brain_dump.txt"):
        try:
            print("🧠 Loading Brain Dump...")
            txt_loader = TextLoader("brain_dump.txt", encoding="utf-8")
            txt_docs = txt_loader.load()
            for doc in txt_docs: doc.metadata["source"] = "PRIVATE_NOTES"
            docs.extend(txt_docs)
        except Exception as e: print(f"⚠️ Brain Dump Error: {e}")

    # Resume
    if Config.RESUME_LINK:
        try:
            print("📄 Loading Resume...")
            response = requests.get(Config.RESUME_LINK, timeout=10)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(response.content)
                    temp_path = temp_pdf.name
                loader = PyPDFLoader(temp_path)
                pdf_docs = loader.load()
                for doc in pdf_docs: doc.metadata["source"] = "RESUME_PDF"
                docs.extend(pdf_docs)
                os.remove(temp_path)
        except: pass

    # Website
    try:
        print("🌐 Loading Website...")
        loader = WebBaseLoader("https://chetanp-portfolio.netlify.app/")
        web_docs = loader.load()
        for doc in web_docs: doc.metadata["source"] = "PORTFOLIO_WEBSITE"
        docs.extend(web_docs)
    except: pass

    if not docs:
        @tool("search_info", args_schema=SearchInput)
        def search_info(query: str): return "No data found."
        return search_info

    # --- PROCESSING ---
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    
    print(f"⏳ Embedding {len(splits)} chunks...")
    embeddings = FastEmbedEmbeddings(cache_dir=MODEL_CACHE_PATH)
    
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings,
        persist_directory=DB_PATH,
        collection_name="chetan_manual_rerank"
    )

    # 👇 INITIALIZE RERANKER (Model Load)
    print("🚀 Initializing FlashRank Reranker...")
    reranker = FlashrankRerank(model="ms-marco-MiniLM-L-12-v2")

    @tool("search_info", args_schema=SearchInput)
    def search_info(query: str):
        """Searches using Manual Reranking Logic."""
        global SEARCH_CACHE
        current_time = time.time()
        
        # Cache Check
        if query in SEARCH_CACHE:
            last_time, last_result = SEARCH_CACHE[query]
            if current_time - last_time < 5:
                print(f"✋ Using Cached Result for '{query}'")
                return last_result

        try:
            print(f"\n🔍 Deep Search for '{query}'...")
            
            # STEP 1: Get LOTS of documents (Top 20) using basic search
            # We bypass 'as_retriever' to avoid dependency issues
            initial_docs = vectorstore.similarity_search(query, k=20)
            
            if not initial_docs: return "No info found."

            print(f"   -> Retrieved {len(initial_docs)} raw docs. Reranking now...")

            # STEP 2: Manually Rerank them (The Magic Step) 🪄
            # This sorts them by true relevance
            reranked_docs = reranker.compress_documents(documents=initial_docs, query=query)
            
            # Keep only Top 5
            top_docs = reranked_docs[:5]

            final_output = ""
            for i, doc in enumerate(top_docs):
                source = doc.metadata.get("source", "Unknown")
                score = doc.metadata.get("relevance_score", "N/A")
                
                print(f"   ⭐ Rank {i+1}: {source} (Score: {score})")
                final_output += f"\n--- SOURCE: {source} ---\n{doc.page_content}\n"
            
            SEARCH_CACHE[query] = (current_time, final_output)
            return final_output
            
        except Exception as e:
            return f"Error: {e}"

    return search_info