"use client";

import { useState, useRef, useEffect } from "react";
import { 
  Send, User, Bot, Terminal, Mic, MicOff, Menu, X, 
  Sun, Moon, Trash2, Activity, ChevronDown, ChevronRight, 
  Briefcase, Github, Mail, Calendar, FileText, Search, PlayCircle 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import axios from "axios";

// --- Types ---
interface Message {
  role: "user" | "ai";
  content: string;
  thoughts?: string[];
}

// --- PROFESSIONAL WELCOME MESSAGE ---
const INITIAL_MESSAGE: Message = { 
  role: "ai", 
  content: "I am **Chetan's Autonomous Portfolio Agent**.\n\nI maintain real-time access to his **development logs, resume data, and calendar**. \n\nYou can utilize the sidebar controls to execute my backend tools:\n\n1.  **Audit Engineering Activity:** Verify live GitHub commits.\n2.  **Evaluate Alignment:** Analyze your Job Description against his skills.\n3.  **Initiate Contact:** Schedule a technical interview or send an email.\n\n**Awaiting your query.**" 
};

// --- COMPONENT: Thinking Logs ---
const ThinkingLogs = ({ logs }: { logs?: string[] }) => {
  const [isOpen, setIsOpen] = useState(false);
  if (!logs || logs.length === 0) return null;

  return (
    <div className="mb-2 max-w-[90%]">
      <button onClick={() => setIsOpen(!isOpen)} className="flex items-center gap-2 text-[10px] text-gray-400 hover:text-purple-400 uppercase tracking-widest font-bold mb-1 transition-all">
        {isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        <Activity size={12} /> System Logic
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden bg-black/5 dark:bg-black/40 border border-gray-200 dark:border-white/5 rounded-lg p-3">
             <div className="space-y-1 font-mono text-[11px] text-gray-600 dark:text-gray-400">
               {logs.map((log, i) => (
                 <div key={i} className="flex gap-2 items-start"><span className="text-purple-500 mt-0.5">➜</span><ReactMarkdown>{log}</ReactMarkdown></div>
               ))}
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// --- COMPONENT: Typewriter ---
const TypewriterEffect = ({ content }: { content: string }) => {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  useEffect(() => {
    let index = 0;
    const intervalId = setInterval(() => {
      setDisplayedText((prev) => prev + content.charAt(index)); index++;
      if (index === content.length) { clearInterval(intervalId); setIsComplete(true); }
    }, 4);
    return () => clearInterval(intervalId);
  }, [content]);
  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{isComplete ? content : displayedText + " ▍"}</ReactMarkdown>;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => scrollRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, loading]);
  
  const clearChat = () => setMessages([INITIAL_MESSAGE]);
  
  // --- ACTION HANDLERS (Populate Input) ---
  const handleAction = (text: string) => setInput(text);

  const startListening = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false; recognition.lang = 'en-US';
      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onresult = (event: any) => setInput(event.results[0][0].transcript);
      recognition.start();
    } else alert("Use Chrome for Voice.");
  };

  const sendMessage = async (text: string = input) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setInput(""); setLoading(true);
    try {
      // Use Environment variable, fallback to localhost for testing
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await axios.post(`${API_URL}/chat`, { message: text });
      setMessages(prev => [...prev, { role: "ai", content: res.data.response, thoughts: res.data.thoughts }]);
    } catch { setMessages(prev => [...prev, { role: "ai", content: "⚠️ Error: Backend disconnected." }]); }
    setLoading(false);
  };

  const theme = {
    bg: isDarkMode ? "bg-[#050505]" : "bg-[#F3F4F6]",
    sidebar: isDarkMode ? "bg-[#0a0a0a] border-white/10" : "bg-white border-gray-200",
    textPrimary: isDarkMode ? "text-gray-200" : "text-gray-800",
    textSecondary: isDarkMode ? "text-gray-400" : "text-gray-500",
    chatUser: isDarkMode ? "bg-white text-black" : "bg-black text-white",
    chatAi: isDarkMode ? "bg-[#111] border-white/10 text-gray-300" : "bg-white border-gray-200 text-gray-800 shadow-sm",
    inputBg: isDarkMode ? "bg-[#0a0a0a] border-white/10" : "bg-white border-gray-200 shadow-sm",
    glow: isDarkMode ? "shadow-purple-900/40" : "shadow-blue-500/20",
  };

  return (
    <div className={`flex h-screen ${theme.bg} ${theme.textPrimary} font-sans overflow-hidden transition-colors duration-500`}>
      {/* Mobile Menu Button */}
      <div className="absolute top-4 left-4 md:hidden z-50">
        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className={`p-2 rounded-lg ${isDarkMode ? "bg-gray-800 text-white" : "bg-white text-black shadow-md"}`}>
           {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* ================= BACKEND TOOLS SIDEBAR ================= */}
      <motion.div initial={{ x: -300 }} animate={{ x: isSidebarOpen ? 0 : 0 }} className={`fixed md:relative z-40 w-80 h-full border-r flex flex-col transition-transform duration-300 ${isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"} ${theme.sidebar}`}>
        
        {/* Simple Profile Header */}
        <div className={`p-6 flex flex-col items-center border-b ${isDarkMode ? "border-white/5" : "border-gray-100"} z-10`}>
          <div className={`w-20 h-20 rounded-full bg-gradient-to-tr from-purple-500 via-indigo-500 to-blue-500 p-[2px] shadow-xl ${theme.glow}`}>
            <div className={`w-full h-full rounded-full flex items-center justify-center overflow-hidden ${isDarkMode ? "bg-black" : "bg-white"}`}>
                <User size={32} className={isDarkMode ? "text-gray-400" : "text-gray-300"} />
            </div>
          </div>
          <h2 className={`mt-3 text-lg font-bold tracking-tight ${theme.textPrimary}`}>Chetan Pawar</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-[10px] text-purple-400 font-medium uppercase tracking-wider">AI Engineer</span>
          </div>
        </div>

        {/* BACKEND TOOLS LIST */}
        <div className="flex-1 p-4 space-y-6 overflow-y-auto">
            
            {/* Group 1: Analysis Tools */}
            <div>
              <h3 className={`text-[10px] font-bold uppercase tracking-widest mb-3 opacity-50`}>Analysis Tools</h3>
              <div className="space-y-2">
                
                {/* 🛠️ get_github_activity */}
                <button onClick={() => handleAction("Run a live audit of your GitHub activity.")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-white/5 border-white/5 text-gray-300" : "hover:bg-gray-50 border-gray-100 text-gray-700"}`}>
                   <Github size={16} className="text-white group-hover:scale-110 transition-transform" /> 
                   <span>GitHub Live Audit</span>
                </button>

                {/* 🛠️ analyze_resume_fit */}
                <button onClick={() => handleAction("Check my fit for this Job Description: [PASTE JD HERE]")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-purple-500/10 border-purple-500/20 text-purple-200" : "hover:bg-purple-50 border-purple-100 text-purple-800"}`}>
                   <Briefcase size={16} className="text-purple-500 group-hover:scale-110 transition-transform" /> 
                   <span>JD Match Analyzer</span>
                </button>

                {/* 🛠️ get_project_media_assets */}
                <button onClick={() => handleAction("Show me project demos and media assets.")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-white/5 border-white/5 text-gray-300" : "hover:bg-gray-50 border-gray-100 text-gray-700"}`}>
                   <PlayCircle size={16} className="text-pink-500 group-hover:scale-110 transition-transform" /> 
                   <span>Project Media Lookup</span>
                </button>
              </div>
            </div>

            {/* Group 2: Knowledge & Search */}
            <div>
              <h3 className={`text-[10px] font-bold uppercase tracking-widest mb-3 opacity-50`}>Knowledge Base</h3>
              <div className="space-y-2">
                
                {/* 🛠️ get_resume_download_link */}
                <button onClick={() => handleAction("Provide the download link for the resume.")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-white/5 border-white/5 text-gray-300" : "hover:bg-gray-50 border-gray-100 text-gray-700"}`}>
                   <FileText size={16} className="text-blue-500 group-hover:scale-110 transition-transform" /> 
                   <span>Get Resume PDF</span>
                </button>

                 {/* 🛠️ get_web_search_tool */}
                 <button onClick={() => handleAction("Search the web for current AI trends matching your skills.")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-white/5 border-white/5 text-gray-300" : "hover:bg-gray-50 border-gray-100 text-gray-700"}`}>
                   <Search size={16} className="text-yellow-500 group-hover:scale-110 transition-transform" /> 
                   <span>Web Search Agent</span>
                </button>
              </div>
            </div>

            {/* Group 3: Contact Actions */}
            <div>
              <h3 className={`text-[10px] font-bold uppercase tracking-widest mb-3 opacity-50`}>Actions</h3>
              <div className="space-y-2">
                
                {/* 🛠️ schedule_meeting */}
                <button onClick={() => handleAction("I want to schedule an interview.")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-white/5 border-white/5 text-gray-300" : "hover:bg-gray-50 border-gray-100 text-gray-700"}`}>
                   <Calendar size={16} className="text-green-500 group-hover:scale-110 transition-transform" /> 
                   <span>Schedule Interview</span>
                </button>

                 {/* 🛠️ send_contact_email */}
                 <button onClick={() => handleAction("Draft an email to Chetan.")} className={`w-full flex items-center gap-3 p-2.5 rounded-lg border transition-all text-sm group ${isDarkMode ? "hover:bg-white/5 border-white/5 text-gray-300" : "hover:bg-gray-50 border-gray-100 text-gray-700"}`}>
                   <Mail size={16} className="text-orange-500 group-hover:scale-110 transition-transform" /> 
                   <span>Send Email</span>
                </button>
              </div>
            </div>
        </div>

        {/* Footer */}
        <div className={`p-4 border-t text-[10px] text-center opacity-40 ${isDarkMode ? "border-white/5" : "border-gray-200"}`}>
            System v2.4 • Powered by LangGraph
        </div>
      </motion.div>

      {/* ================= CHAT AREA ================= */}
      <div className={`flex-1 flex flex-col relative w-full ${theme.bg}`}>
        <div className={`h-14 border-b flex items-center justify-end px-6 sticky top-0 z-20 backdrop-blur-md ${isDarkMode ? "border-white/5 bg-[#050505]/80" : "border-gray-200 bg-white/80"}`}>
          <div className="flex items-center gap-2">
             <button onClick={clearChat} title="Reset Session" className={`p-2 rounded-full transition-all ${isDarkMode ? "bg-gray-800 text-red-400 hover:bg-red-500/20" : "bg-gray-100 text-red-500 hover:bg-red-100"}`}><Trash2 size={16} /></button>
             <button onClick={() => setIsDarkMode(!isDarkMode)} title="Toggle Theme" className={`p-2 rounded-full transition-all ${isDarkMode ? "bg-gray-800 text-yellow-400 hover:bg-gray-700" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>{isDarkMode ? <Sun size={16} /> : <Moon size={16} />}</button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-8 space-y-6 scrollbar-thin">
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                
                {msg.role === "ai" && msg.thoughts && <div className="ml-12 w-full"><ThinkingLogs logs={msg.thoughts} /></div>}
                
                <div className={`flex gap-4 max-w-[85%] sm:max-w-[75%] ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                   {msg.role === "ai" && <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-lg ${isDarkMode ? "bg-gradient-to-br from-indigo-600 to-purple-700" : "bg-black"}`}><Bot size={20} className="text-white" /></div>}
                   <div className={`rounded-2xl p-4 sm:px-6 shadow-sm border ${msg.role === "ai" ? theme.chatAi : theme.chatUser}`}>
                     {msg.role === "ai" ? (idx === messages.length - 1 && !loading ? <TypewriterEffect content={msg.content} /> : <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>) : <p className="text-[15px] font-medium">{msg.content}</p>}
                   </div>
                   {msg.role === "user" && <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${isDarkMode ? "bg-gray-800" : "bg-gray-200"}`}><User size={20} className={isDarkMode ? "text-gray-400" : "text-gray-600"} /></div>}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {loading && <div className="flex gap-4 ml-2"><div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${isDarkMode ? "bg-gradient-to-br from-indigo-600 to-purple-700" : "bg-black"}`}><Bot size={20} className="text-white" /></div><div className={`px-4 py-3 rounded-2xl flex items-center gap-1 ${isDarkMode ? "bg-[#111] border border-white/10" : "bg-white border border-gray-200"}`}><span className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce"></span><span className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce delay-100"></span><span className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce delay-200"></span></div></div>}
          <div ref={scrollRef} />
        </div>

        <div className={`p-4 border-t ${isDarkMode ? "bg-[#050505] border-white/5" : "bg-gray-50 border-gray-200"} z-30`}>
          <div className="max-w-3xl mx-auto flex items-center gap-3">
             <button onClick={startListening} className={`p-3 rounded-xl transition-all border ${isListening ? "bg-red-500 text-white animate-pulse border-red-600" : isDarkMode ? "bg-gray-800 text-gray-400 border-gray-700 hover:text-white" : "bg-white text-gray-500 border-gray-200 shadow-sm"}`}>{isListening ? <MicOff size={20} /> : <Mic size={20} />}</button>
            <div className={`flex-1 flex items-center rounded-xl border px-2 py-1 ${theme.inputBg}`}><div className="p-3 text-gray-400"><Terminal size={18} /></div><input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && sendMessage()} placeholder={isListening ? "Listening..." : "Execute command or ask query..."} className={`flex-1 bg-transparent focus:outline-none px-2 text-sm ${theme.textPrimary}`} disabled={loading} /></div>
            <button onClick={() => sendMessage()} disabled={loading || !input.trim()} className={`p-3.5 rounded-xl transition-all shadow-lg ${isDarkMode ? "bg-white text-black hover:bg-gray-200" : "bg-black text-white hover:bg-gray-800"} disabled:opacity-50 disabled:cursor-not-allowed`}><Send size={18} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}