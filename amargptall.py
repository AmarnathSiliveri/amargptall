import streamlit as st
import os
import json
from streamlit_lottie import st_lottie
import google.generativeai as genai
from io import BytesIO
import requests
import PyPDF2 as pdf
from PIL import Image



genai.configure(api_key=st.secrets['API_KEY'])

## function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

from streamlit_option_menu import option_menu
 ##initialize our streamlit app
st.set_page_config(page_title="AMAR GPT", page_icon='🦅')  # page title
#with st.sidebar:

#code for lottie file animation
def load_lottiefiles(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)

# Use option_menu with the defined styles
selected = option_menu(
    menu_title=None,
    options=["HOME","TEXT CHAT", "IMAGE CHAT" ,"PDF CHAT","CHAT HISTORY","CREDITS"],
    icons=['house',"pen" ,'image','book','chat','person'],
    default_index=0,
    menu_icon='user',
    orientation="horizontal",
    styles="""
    <style>
        .option-menu {
            width: 200px; /* Set the desired width */
            margin-right: 20px; /* Set the desired spacing */
        }
    </style>
"""
)
    # Initialize session state for chat history,image history,pdf history if it doesn't exist
if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
if 'img_history' not in st.session_state:
        st.session_state['img_history'] = []
if  'img_srchistory' not in  st.session_state:
        st.session_state['img_srchistory'] = []
if  'pdf_history' not in  st.session_state:
        st.session_state['pdf_history'] = []
if  'pdf_srchistory' not in  st.session_state:
        st.session_state['pdf_srchistory'] = []


if selected == "HOME":
    st.markdown("""# <span style='color:#0A2647'>Welcome to My Streamlit App *𝐀𝐦𝐚𝐫𝐆𝐏𝐓 🦅*</span>""", unsafe_allow_html=True)

    st.markdown("""#### <span style='color:#0E6363'> Based on Gemini-PRO,GEMINI-PRO-Vision LLM API FROM GOOGLE</span>""", unsafe_allow_html=True)
    
    st.markdown("""## <span style='color:#AE194B'>Introduction</span>""", unsafe_allow_html=True)

    st.markdown(""" <span style='color:#020C0C'>This is an GPT of my Experimentation with Google's GEMINI API.. </span>""", unsafe_allow_html=True)
    
    
    st.markdown("""
    ### <span style='color:#0F0F0F'>Usage:</span>
    <span style='color:#222831'>  🟢 Navigate to TEXT CHAT for the Text based results..</span>
    <br>
    <span style='color:#222831'>  🔵 Navigate to IMAGE CHAT for the IMAGE based results..</span>
    <br>
    <span style='color:#222831'>  🔴 Navigate to PDF CHAT to chat with the PDF'S..</span>
    <br>
    <span style='color:#222831'>  🟣 Explore other sections of the app, such as 'Chat History' and 'Credits.'</span>
    <br>
""", unsafe_allow_html=True)
    
if selected == "TEXT CHAT":
    def get_gemini_response(question):
        response = chat.send_message(question, stream=True)
       # response = model.generate_content(input_text)
        return response

    lottie_hi = load_lottiefiles(r'higpt.json')
    st_lottie(
        lottie_hi, loop=True, quality="high", speed=1.65, key=None, height=450)


    input_text = st.chat_input("Ask the GPT")
    
    if  1 and input_text:
        response = get_gemini_response(input_text)
        
        st.session_state['chat_history'].append(("YOU", input_text))
        st.success("The Response is")

        # Resolve the response to complete iteration
        response.resolve()
        # Handle the Gemini response format
        if hasattr(response, 'parts') and response.parts:
            for part in response.parts:
                # Extract text from each part
                if hasattr(part, 'text') and part.text:
                    text_line = part.text
                    st.write(text_line)
                    st.session_state['chat_history'].append(("TEXT_BOT", text_line))
                elif hasattr(part, 'candidates') and part.candidates:
                    # Handle candidates in the response
                    for candidate in part.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            text_line = candidate.content.text
                            st.write(text_line)
                            st.session_state['chat_history'].append(("TEXT_BOT", text_line))
                        else:
                            st.warning("Invalid response format. Unable to extract text from candidates.")
                else:
                    st.warning("Invalid response format. Unable to extract text from parts.")
        else:
            st.warning("Invalid response format. No parts found.")

if selected == 'CHAT HISTORY':
    st.title("CHAT HISTORY")
    
    # Display chat history with animation
    lottie_chat = load_lottiefiles(r'askchat.json')
    st_lottie(lottie_chat, loop=True, quality="high", speed=1.35, key=None, height=450)
    
    # Create two columns for buttons
    text_history_button, image_history_button, pdf_history_button = st.columns([1, 1, 1])
    # Adjust column ratios as needed

    with text_history_button:

        # Display chat history for text if the button is clicked
        if st.button("Show Text Chat History", use_container_width=True):
            if 'chat_history' in st.session_state and st.session_state['chat_history']:
                st.subheader("Text Chat History:")
                for role, text in st.session_state['chat_history']:
                    if role == "YOU":
                        st.markdown(f"**{role} 👤**: {text} ")
                    elif role == "TEXT_BOT":
                        st.markdown(f"**{role} 🤖**: {text} ")
            else:
                st.error("Text Chat History is empty. Start asking questions to build the history.")

    with image_history_button:
        if st.button("Show Image Chat History", use_container_width=True):
            for history_type, header_text, emoji in [
                ('img_history', "Image Chat History:", "👤"),
                ('img_srchistory', "Image Source", "👤"),
            ]:
                history = st.session_state.get(history_type, [])
                error_message = f"{header_text} is empty. Start asking questions with images to build the history." if "Chat" in header_text else f"{header_text} is empty. Start uploading images to build the history."

                if history:
                    st.subheader(header_text)
                    for role, text in history:
                        role_prefix = emoji if role in ["YOU", "SOURCE"] else "🤖"
                        st.markdown(f"**{role} {role_prefix}**: {text}")
                else:
                    st.error(error_message)


        
    with pdf_history_button:
        # Display pdf history for image if the button is clicked
        if st.button("Show PDF Chat History", use_container_width=True):
            for history_type in ['pdf_history', 'pdf_srchistory']:
                if history := st.session_state.get(history_type):
                    title = "PDF Chat History:" if history_type == 'pdf_history' else "PDF Source History:"
                    st.subheader(title)
                    for role, user_text in history:
                        role_prefix = "👤" if role in ["YOU", "PDFS UPLOADED"] else "🤖"
                        st.markdown(f"**{role} {role_prefix}**:  {user_text} ")
                else:
                    st.error(f"{history_type.capitalize()} is empty. Start asking questions with PDFs to build the history.")

                    

    st.warning("THE CHAT HISTORY WILL BE LOST ONCE THE SESSION EXPIRES")

        

if selected == "IMAGE CHAT":
    vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    def vscontent(input_text_1, image):
        response = vision_model.generate_content([input_text_1, image], stream=True)
        return response
    
    lottie_img=load_lottiefiles(r"imagechat.json")
    st_lottie(
        lottie_img, loop=True, quality="high", speed=1.35, key=None, height=450)

    # Option to choose between file upload and URL input

    option = st.radio("Choose an option", ["Upload Image", "Provide Image URL"])

    if option == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_column_width=True)
                st.session_state['img_srchistory'].append(("SOURCE", option))
            except Exception as e:
              st.error(f"Error loading uploaded image: {str(e)}")


    elif option == "Provide Image URL":
         image_url = st.text_input("Enter Image URL:")
         if image_url:
             try:
                 response = requests.get(image_url)
                 if response.status_code == 200:
                     image = Image.open(BytesIO(response.content))
                     st.image(image, caption='Image from URL', use_column_width=True)
                     st.session_state['img_srchistory'].append(("SOURCE", option))
                 else:
                     st.error(f"Failed to retrieve image from URL. Status code: {response.status_code}")
             except Exception as e:
                 st.error(f"Error loading image from URL: {str(e)}")



                

    
    # Use the vision model
    if 'image' in locals():
        try:
            input_text_1 = st.chat_input("Ask the GPT about the image")
            if input_text_1:
                response = vscontent(input_text_1, image)
                response.resolve()

                st.session_state['img_history'].append(("YOU", input_text_1))
                st.session_state['img_history'].append(("IMAGE_BOT", response.text))
                st.balloons()
                st.markdown(f"**Generated text:** {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")



if selected == "PDF CHAT":
    lottie_cpdf = load_lottiefiles(r"pdfparser.json")
    st_lottie(lottie_cpdf, loop=True, quality="high", speed=1.25, key=None, height=350)
    
    # Define function to get Gemini response
    def get_gemini_response(input):
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input)
        return response.text

    # Define function to extract text from PDF
    def input_pdf_text(uploaded_file):
        with open(uploaded_file, 'rb') as f:
            reader = pdf.PdfReader(f)
            text = ""
            for page in range(len(reader.pages)):
                page = reader.pages[page]
                text += str(page.extract_text())
        return text

    input_prompt = """
      Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {text}?\n
        Question: \n{user_question}\n

        Answer:
    
        """
    
    st.title("Chat with YOUR PDFS")

    uploaded_files = st.file_uploader("Upload Your PDFS", type="pdf", help="please upload the pdf", accept_multiple_files=True)
    st.session_state['pdf_srchistory'].append(("PDFS UPLOADED", uploaded_files))
    
    user_question = st.text_input("HAVE a NICE chat with your PDFS")
    st.session_state["pdf_history"].append(("YOU", user_question))

    if st.button("submit"):
        with st.spinner("Processing..."):
            if uploaded_files is not None:
                for uploaded_file in uploaded_files:
                    text = input_pdf_text(uploaded_file)
                    response = get_gemini_response(text)  # Pass text instead of input_prompt
                    output_Text = response
                    st.write(response)
                    st.balloons()
                    st.session_state["pdf_history"].append(("PDF_BOT", output_Text))
    st.warning("clear the cache at the top left side by clicking --->  ⋮  ")
   



if selected == 'CREDITS':
    lottie_credit = load_lottiefiles(r"thankyou bymonkeymoji.json")
    st_lottie(lottie_credit, loop=True,quality="high", speed=1.25, key=None, height=350)
    st.title("CRAFTED BY :")
    st.subheader("AMARNATH SILIVERI")

# Define your styles
    st.markdown("""
<style>
  .social-icons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
  }

  .social-icon {
    text-align: center;
  }
</style>
""", unsafe_allow_html=True)

# Create a container for social icons
    st.markdown("""
<div class="social-icons">
  <div class="social-icon">
    <a href="https://www.github.com/SilverStark18" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/github.svg" width="32" height="32" alt="GitHub" />
    </a>
    <p>GitHub</p>
  </div>

  <div class="social-icon">
    <a href="http://www.instagram.com/itz..amar." target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/instagram.svg" width="32" height="32" alt="Instagram" />
    </a>
    <p>Instagram</p>
  </div>

  <div class="social-icon">
    <a href="http://www.linkedin.com/in/amarnath-siliveri18" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/linkedin.svg" width="32" height="32" alt="LinkedIn" />
    </a>
    <p>LinkedIn</p>
  </div>

  <div class="social-icon">
    <a href="https://medium.com/@amartalks25603" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/medium.svg" width="32" height="32" alt="Medium" />
    </a>
    <p>Medium</p>
  </div>

  <div class="social-icon">
    <a href="https://www.x.com/Amarsiliveri" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/twitter.svg" width="32" height="32" alt="Twitter" />
    </a>
    <p>Twitter</p>
  </div>

  <div class="social-icon">
    <a href="https://www.threads.net/@itz..amar." target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/danielcranney/readme-generator/main/public/icons/socials/threads.svg" width="32" height="32" alt="Threads" />
    </a>
    <p>Threads</p>
  </div>
</div>
""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.success(" Stay in the loop and level up your knowledge with every follow! ")
    st.success("Do you see icons , click to follow  on SOCIAL")
