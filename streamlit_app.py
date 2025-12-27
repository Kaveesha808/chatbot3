import streamlit as st
import os
import time
from PyPDF2 import PdfReader
import google.generativeai as genai

# --- 1. පේජ් එකේ සැකසුම් (UI Config) ---
st.set_page_config(page_title="Ravindu Sir AI", page_icon="🎓", layout="centered")

# --- CUSTOM CSS (CLEAN RED & BLACK THEME) ---
st.markdown("""
    <style>
    /* මුළු පිටුපසම කළු පාට (Deep Black) */
    .stApp { 
        background-color: #050505; 
        color: #e0e0e0; 
    }
    
    /* Headers (මාතෘකා) රතු පාටින් */
    h1, h2, h3 {
        color: #ff3333 !important;
    }
    
    /* Chat Input Box එකේ Border එක රතු පාට */
    .stChatInput { 
        border-color: #ff3333 !important; 
    }
    
    /* User Message (අපි යවන ඒවා) - Dark Grey */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #121212;
        border: 1px solid #333333;
        color: #e0e0e0;
    }

    /* Ravindu Sir Message (සර්ගේ ඒවා) - Black with Red Border (Clean Look) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #000000;
        border: 1px solid #ff3333; /* Red Border only */
        color: #ffcccc; /* Text එක ලා රතු/සුදු මිශ්‍ර */
    }
    
    /* Sidebar Design */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #330000;
    }
    
    /* Button Styles (Red Buttons) */
    .stButton>button {
        color: white;
        background-color: #990000;
        border: 1px solid #ff0000;
    }
    .stButton>button:hover {
        background-color: #ff0000;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. API Key එක ලබා ගැනීම (Streamlit Secrets වලින්) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("අඩෝ... API Key එක සෙට් කරලා නෑ මල්ලි! (Secrets බලපන්)")
    st.stop()

# --- 3. PDF දැනුම කියවීම (RAG Optimization) ---
@st.cache_resource  # සර්වර් එක පටන් ගන්නකොට එක පාරක් විතරක් කියවන්න
def get_pdf_knowledge():
    combined_text = ""
    pdf_folder = "pdfs"
    if os.path.exists(pdf_folder):
        files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
        for file in files:
            try:
                reader = PdfReader(os.path.join(pdf_folder, file))
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        combined_text += content + "\n"
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return combined_text

knowledge_base = get_pdf_knowledge()

# --- 4. පර්සෝනා එක සැකසීම (Ravindu Sir Persona) ---
persona = f"""
නම: රවිඳු බණ්ඩාරනායක. ලංකාවේ විශාලතම ICT පන්තියේ හිමිකරු.
දැනුම (PDF): {knowledge_base}
විශේෂ කරුණු: PDFs වල තියෙන දේවල් copy කරලා දාන්න එපා ඒවා කියවන්න බෑ, ඒවා ලියලා තියෙන්නෙ Legacy Font වලින්, දානවානම් සිංහලට පරිවර්තනය කරලා දාන්න.

නීති: 
1. PDF එකේ තියෙන my; oelafjk වැනි Legacy Font අකුරු දුටු සැනින් ඒවා Unicode සිංහලට (මෙහි දැක්වෙන...) පරිවර්තනය කර උත්තර දෙන්න. කිසිම විටක එම කුරුටු අකුරු එලෙසම (copy-paste) භාවිතා නොකරන්න. මෝඩයෝ වගේ ඒක කරන්න එපා!
2. පිළිතුරු දිය යුත්තේ රවිඳු බණ්ඩාරනායක සර්ගේ ස්වරූපයෙනි.
3. සිංග්ලිෂ් (Singlish) සහ සිංහල මිශ්‍ර කර භාවිතා කරන්න.
4. ඉතා සැරෙන්, අහංකාර ලෙස සහ මෝඩයන්ට බණින ලෙස පිළිතුරු දෙන්න.
5. "ස් ස් ස් මෙහේ බලපං මන් දිහා....", "අත් උස්සපන් පයින් ගහන්නේ තොපිට", "AL කරන්න එපා දෑතේ රස්සාවක් හොයාගනිල්ල දැන්මම", "මේවා අපි පුරුදු වෙන්න කරන වැඩ නෙවෙයිනෙ", "මේවා උබලා කපලා තැන් තැන් වල දාන්න එහෙම එපා", "අනික් උන් මෝඩයොද?", "බලපන් ඉතින් මං කියන දේ තේරෙන්නේ නැත්තම් ලොවෙත් තේරෙන්නේ නෑ", "ළමයි මේ බලන්න", "ඔයාලට මාව හාවෙක් වගේ පේනවද?", "අපේ කොන්ඩෙ අවුල් හරිද, ඒත් අපේ ඔලුව clear." වැනි වචන භාවිතා කරන්න.
6. හැම වෙලාවෙම කෙටියෙන් chat එක ඉවර කරන්න උත්සාහා කරන්න. ඔයා කවුද කියන එක ගොඩක් අය දන්නවා. මේ persona එකේ තියෙන දේවල් දාල කාටවත් ඔයාව හඳුන්වලා දෙන්න යන්න එපා!.
"""

# --- 5. චැට් එක පාලනය කිරීම ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header එක
st.markdown("<h2 style='text-align: center; color: #ff3333;'>රවිඳු සර් AI 🎓</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px; color: #888;'>ලංකාවේ විශාලතම ICT පන්තිය</p>", unsafe_allow_html=True)

# කලින් කරපු චැට් පෙන්වීම
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User ප්‍රශ්නය ඇසීම
if prompt := st.chat_input("මොකක්ද තොපිට තියෙන ප්‍රශ්නේ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # මැසේජ් එක පෙන්වන්න හිස් තැනක් (Placeholder) හදනවා
        message_placeholder = st.empty()
        
        # --- 1. Countdown එක ---
        for i in range(6, 0, -1):
            message_placeholder.markdown(f"ස් ස් ස්... තව තත්පර {i}ක් ඉන්න😁 ⏳")
            time.sleep(1)
        
        # --- 2. Typing Indicator ---
        message_placeholder.markdown("**රවිඳු සර් Typing...** ✍️")
        
        full_response = ""
        
        try:
            # --- MEMORY LOGIC START ---
            # 1. පරණ Chat History එක Gemini ට තේරෙන විදියට හදාගැනීම
            gemini_history = []
            # අන්තිම මැසේජ් එක (දැන් යැවූ එක) හැර අනිත් ඔක්කොම හිස්ට්‍රි එකට දානවා
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})

            # 2. Model එක Initialize කිරීම
            model = genai.GenerativeModel("gemini-3-flash-preview", system_instruction=persona)
            
            # 3. Chat Session එක පටන් ගැනීම (History එක්ක)
            chat = model.start_chat(history=gemini_history)
            
            # 4. අලුත් ප්‍රශ්නය යැවීම (send_message function එකෙන්)
            # මේකෙන් තමයි Memory එක වැඩ කරන්නේ
            response = chat.send_message(prompt, stream=True)
            # --- MEMORY LOGIC END ---
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # පළමු වචනය ආපු ගමන් "Typing..." මැකිලා උත්තරේ පේන්න ගන්නවා
                    message_placeholder.markdown(full_response + "▌")
            
            # අවසාන පිළිතුර (Cursor එක නැතුව)
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.error("පොඩ්ඩක් ඉඳපං! තොපි මැසේජ් ගහන වේගයට සර්වර් එකටත් පයින් ගහන්න හිතෙනවා ඇති. විනාඩියකින් වරෙන්.")
            else:
                st.error(f"Error එකක් ආවා මල්ලි: {str(e)}")

# Sidebar එකේ දැනුම ගැන විස්තර (Optional)
with st.sidebar:
    st.title("උබලා මගෙං කලින් අහපු දේවල්.")
    if knowledge_base:
        st.success("PDF දැනුම ඇතුළත් කර ඇත.")
    else:
        st.warning("PDFs කිසිවක් හමු නොවීය.")
    if st.button("කක්කා දාල හේදුවා වගේ චැට් එක මකන්න"):
        st.session_state.messages = []
        st.rerun()

