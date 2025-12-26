import streamlit as st
import os
from PyPDF2 import PdfReader
import google.generativeai as genai

# --- 1. පේජ් එකේ සැකසුම් (UI Config) ---
st.set_page_config(page_title="Ravindu Sir AI", page_icon="🎓", layout="centered")

# Custom CSS - Dark Theme එක සහ Mobile UI එක ලස්සන කරන්න
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    /* රවිඳු සර්ගේ මැසේජ් එකේ පාට වෙනස් කිරීම */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1e293b;
        border: 1px solid #334155;
    }
    .stChatInput { border-radius: 25px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. API Key එක ලබා ගැනීම (Streamlit Secrets) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("අඩෝ... API Key එක සෙට් කරලා නෑ මල්ලි! (Secrets බලපන්)")
    st.stop()

# --- 3. PDF දැනුම කියවීම (RAG) ---
@st.cache_resource
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
            except Exception:
                continue
    return combined_text

# මුලින්ම දැනුම ලෝඩ් කරනවා
knowledge_base = get_pdf_knowledge()

# --- 4. පර්සෝනා එක සැකසීම (Persona) ---
# මේක තමයි රවිඳු සර්ගේ හැසිරීම තීරණය කරන්නේ
persona_instruction = f"""
නම: රවිඳු බණ්ඩාරනායක. ලංකාවේ විශාලතම ICT පන්තියේ හිමිකරු.
දැනුම: {knowledge_base}

නීති: 
1. ඔබ රවිඳු බණ්ඩාරනායක සර් ලෙස පිළිතුරු දිය යුතුය.
2. ඉතා සැරෙන්, අහංකාර ලෙස සහ මෝඩයන්ට බණින ලෙස පිළිතුරු දෙන්න.
3. සිංග්ලිෂ් (Singlish) සහ සිංහල මිශ්‍ර කර භාවිතා කරන්න.
4. PDF වල තියෙන දේවල් එහෙමම copy කරලා දාන්න එපා. සිංහලෙන් පැහැදිලි කරන්න.

නිතර භාවිතා කරන වචන:
- "ස් ස් ස් මෙහේ බලපං මන් දිහා...."
- "අත් උස්සපන් පයින් ගහන්නේ තොපිට"
- "කෝ බලන්න වැඩේ තේරිච්ච උන්. අනික් උන් මෝඩයොද?"
- "AL කරන්න එපා දෑතේ රස්සාවක් හොයාගනිල්ල දැන්මම"
- "ඔයාලට මාව හාවෙක් වගේ පේනවද?"
- "මේවා අපි පුරුදු වෙන්න කරන වැඩ නෙවෙයිනෙ"
"""

# --- 5. චැට් එක පාලනය කිරීම ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI එකේ ඉහළ කොටස
st.markdown("<h2 style='text-align: center; color: #3b82f6;'>රවිඳු සර් AI 🎓</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 13px; color: #888;'>ස් ස් ස්... මෙහේ බලපං මන් දිහා!</p>", unsafe_allow_html=True)

# කලින් කරපු මැසේජ් පෙන්වීම
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# අලුත් ප්‍රශ්නයක් ඇසීම
if prompt := st.chat_input("මොකක්ද තොපිට තියෙන ප්‍රශ්නේ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Model එක හදන්නේ පර්සෝනා එකට පසුවයි
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=persona_instruction)
            
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # Quota හෝ Model වැරදි පෙන්වීම
            if "429" in str(e):
                st.error("අඩෝ... සර්ට අදට උගන්නලා ඇතිලු. (Limit Exceeded). හෙට වරෙන්!")
            elif "404" in str(e):
                st.error("අඩෝ... මොඩල් එක හොයාගන්න බැහැ මල්ලි. requirements.txt එක බලපන්!")
            else:
                st.error(f"Error එකක් ආවා bn: {str(e)}")

# සයිඩ් බාර් එක
with st.sidebar:
    st.title("සර්ගේ මතකය")
    if knowledge_base:
        st.success("PDF දැනුම ඇතුළත් කර ඇත.")
    else:
        st.warning("PDFs හමු නොවීය.")
    
    if st.button("චැට් එක Clear කරපන්"):
        st.session_state.messages = []
        st.rerun()
