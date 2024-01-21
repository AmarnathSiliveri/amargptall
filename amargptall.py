import streamlit as st
import os
import json
from streamlit_lottie import st_lottie
import google.generativeai as genai
from dotenv import load_dotenv
from io import BytesIO
import requests
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PIL import Image
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()  ## loading all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
                if history := st.session_state.get(history_type):
                    st.subheader(header_text)
                    for role, text in history:
                        role_prefix = emoji if role in ["YOU", "SOURCE"] else "🤖"
                        st.markdown(f"**{role} {role_prefix}**: {text} ")
                else:
                    st.error(f"{header_text} is empty. Start asking questions with images to build the history." if "Chat" in header_text else f"{header_text} is empty. Start uploading images to build the history.")

        
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
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            st.session_state['img_srchistory'].append(("SOURCE", option))

    elif option == "Provide Image URL":
        image_url = st.text_input("Enter Image URL:")
        if image_url:
            try:
                response = requests.get(image_url)
                image = Image.open(BytesIO(response.content))
                st.image(image, caption='Image from URL', use_column_width=True)
                st.session_state['img_history'].append(("SOURCE", option))
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
    st_lottie(lottie_cpdf, loop=True,quality="high", speed=1.25, key=None, height=350)

    def get_pdf_text(pdf_docs):
     text=""
     for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
     return  text



    def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks


    def get_vector_store(text_chunks):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")


    def get_conversational_chain():

        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """

        model = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.3)

        prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        return chain

    def main1():
        
        st.header("Chat with PDF using Gemini💁")

        user_question = st.chat_input("Ask a Question from the PDF Files")

        if user_question:
            user_input(user_question)
            #st.session_state['pdf_history'].append(("YOU", user_question))

        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        
        if st.button("Submit & Process") :
                    with st.spinner("Processing..."):
                        raw_text = get_pdf_text(pdf_docs)
                        text_chunks = get_text_chunks(raw_text)
                        get_vector_store(text_chunks)
                        st.success("Done")
                        pdf_names = [pdf.name for pdf in pdf_docs]
                        st.session_state["pdf_srchistory"].append(("PDFS UPLOADED", pdf_names))
                        st.balloons()
                        
                        

    def user_input(user_question):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        
        new_db = FAISS.load_local("faiss_index", embeddings)
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        
        response1 = chain( {"input_documents":docs, "question": user_question} , return_only_outputs=True)
        
        print(response1)
        st.write("Reply: ", response1["output_text"])
        
        output_Text = response1["output_text"]
        st.session_state["pdf_history"].append(("YOU", user_question))
        st.session_state["pdf_history"].append(("PDF_BOT", output_Text))
    if __name__ == "__main__":
        main1()


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