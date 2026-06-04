# config.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
embed_llm = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", output_dimensionality=768)