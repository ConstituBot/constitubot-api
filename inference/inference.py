import os
import nest_asyncio
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

nest_asyncio.apply()
load_dotenv()

class AnswerBot:
    def __init__(self, page_url):
        self.__page_loader = WebBaseLoader(web_path=page_url, continue_on_failure=True)
        self.__groq_api_key = os.getenv("GROQ_API_KEY")
        self.__vector = None

    def load_documents(self):
        return self.__page_loader.load()

    async def get_answer(self, prompt):
        response = ""
        
        try:
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception as e:
            return "Error: Unable to initialize embeddings. Check embedding service configuration."

        docs = self.load_documents()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = text_splitter.split_documents(docs)

        try:
            self.__vector = FAISS.from_documents(documents, embeddings)
        except Exception as e:
            return "Error: Unable to initialize vector store. Check FAISS setup."

        llm = ChatGroq(groq_api_key=self.__groq_api_key, model_name='mixtral-8x7b-32768')
        prompt_template = ChatPromptTemplate.from_template("""
            Escreva somente em português a resposta da questão a seguir. Pense passo a passo antes de responder.
            <context>
            {context}
            </context>
            Question: {input}
        """)

        document_chain = create_stuff_documents_chain(llm, prompt_template)
        retriever = self.__vector.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        try:
            if prompt:
                response = retrieval_chain.invoke({"input": prompt})["answer"]
        except Exception as e:
            return "Error: Unable to retrieve response."

        return response

answer_bot = AnswerBot('https://normas.leg.br/?urn=urn:lex:br:federal:constituicao:1988-10-05;1988')

async def get_answer_from_bot(prompt):
    return await answer_bot.get_answer(prompt)
