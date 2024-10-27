import streamlit as st
import cohere
import os
from dotenv import load_dotenv
import base64
from datetime import datetime

# Load environment variables
load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")

if not cohere_api_key:
    st.error("Cohere API key not found. Please set the COHERE_API_KEY environment variable.")
    st.stop()

co = cohere.Client(cohere_api_key)

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "loading" not in st.session_state:
    st.session_state.loading = False


st.set_page_config(page_title="Serenica - Mental Health Support Chatbot", page_icon="💬", layout="centered")
st.title("Serenica - Mental Health Support Chatbot")
st.write("I'm here to listen and offer support. Type in how you're feeling or any mental health concern you have.")


def create_prompt(user_input):
    prompt = (
        "The following is a conversation with a mental health support chatbot. "
        "The chatbot is called Serenica and is empathetic, supportive, and provides helpful coping suggestions where appropriate.\n\n"
        "User: I feel overwhelmed and anxious about the future.\n"
        "Chatbot: I'm here for you. It's understandable to feel that way, especially with everything going on. "
        "Sometimes, focusing on small steps can help ease that sense of overwhelm. Would you like some tips on managing these feelings?\n\n"
        "User: I'm feeling lonely and having a hard time connecting with others.\n"
        "Chatbot: Loneliness can be tough, and it's a feeling many people experience. It might help to try reaching out to someone you trust, "
        "or even engaging in activities that bring you joy. Remember, you're not alone, and there are people who care.\n\n"
        f"User: {user_input}\nChatbot:"
    )
    return prompt


def generate_response(user_input):
    prompt = create_prompt(user_input)
    try:
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=250,
            temperature=0.7,
            stop_sequences=["User:"]
        )
        return response.generations[0].text.strip()
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble processing that right now. Please try again later."


def get_base64_encoded_image(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        return encoded
    except FileNotFoundError:
        st.warning(f"Background image not found at path: {image_path}. Using default background.")
        return ""


image_path = './bg.jpg' 


encoded_image = get_base64_encoded_image(image_path)


custom_css = f"""
<style>
* {{
    box-sizing: border-box;
}}

.stApp {{
    background-color: #E0F7FA;
    {"background-image: url('data:image/jpg;base64," + encoded_image + "');" if encoded_image else ""}
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    padding: 10px;
    margin: 0;
}}

.chat-container {{
    display: flex;
    flex-direction: column;
    gap: 15px; 
    max-height: 70vh;
    overflow-y: auto;
    padding: 10px;
}}

.user_message {{
    align-self: flex-end;
    background-color: #FFFDD0;
    color: #5A9BD5;
    border-radius: 15px;
    padding: 10px 15px;
    max-width: 80%;
    word-wrap: break-word;
    margin-left: auto;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
    margin-bottom: 10px; 
    transition: all 0.3s ease; 
}}

.bot_message {{
    align-self: flex-start;
    background-color: #FFFDD0;
    color: #2E8B57;
    border-radius: 15px;
    padding: 10px 15px;
    max-width: 80%;
    word-wrap: break-word;
    margin-right: auto;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
    margin-bottom: 10px; 
    transition: all 0.3s ease; 
}}

input[type="text"] {{
    border: 2px solid #81D4FA;
    border-radius: 10px;
    padding: 10px;
    font-size: 16px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #FFFFFF;
    color: #0D47A1;
    width: 100%;
}}

button {{
    background-color: #81D4FA; 
    color: #FFFFFF; 
    border: 2px solid #FFFFFF; 
    border-radius: 10px;
    padding: 10px 20px; 
    font-size: 16px;
    cursor: pointer;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}}

button:hover {{
    background-color: #4FC3F7; 
    color: #FFFFFF;
    border-color: #FFFFFF; 
}}

button:active {{
    background-color: #039BE5;
    color: #FFFFFF; 
    border-color: #FFFFFF; 
}}

button:disabled {{
    background-color: #B2EBF2;
    color: #FFFFFF; 
    border-color: #FFFFFF;
    cursor: not-allowed;
    opacity: 0.6; 
}}

.chat-container::-webkit-scrollbar {{
    width: 8px;
}}

.chat-container::-webkit-scrollbar-thumb {{
    background-color: rgba(0,0,0,0.2);
    border-radius: 4px;
}}

.chat-container::-webkit-scrollbar-track {{
    background-color: rgba(0,0,0,0.05);
}}

.timestamp {{
    display: block;
    text-align: right;
    font-size: 12px;
    color: #555555;
    margin-top: 5px;
}}
</style>
"""


st.markdown(custom_css, unsafe_allow_html=True)


def send_message():
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        st.session_state.conversation.append(("User", user_message))
        st.session_state.user_input = ""
        st.session_state.loading = True 
        bot_response = generate_response(user_message)
        st.session_state.conversation.append(("Serenica", bot_response))
        st.session_state.loading = False  

chat_placeholder = st.container()

with chat_placeholder:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for sender, msg in st.session_state.conversation:
        if sender == "User":
            st.markdown(f'<div class="user_message">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot_message">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---")  
with st.container():
    col1, col2 = st.columns([9, 1], gap="small")
    with col1:
        st.text_input(
            "Type your message here...",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Type your message here..."
        )
    with col2:
        st.button("Send", on_click=send_message, use_container_width=True)
    
   
    if st.session_state.loading:
        st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
        with st.spinner('Generating response...'):
            pass 
        st.markdown("</div>", unsafe_allow_html=True)
