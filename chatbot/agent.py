from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import JSONLoader
from langchain.memory import ConversationBufferMemory

class Agent:
    loader = JSONLoader(file_path='muebles.json', jq_schema='.[].product', text_content=False)
    documents = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0).split_documents(loader.load())
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOpenAI()
    
    template = """Responde de forma casual, hablando poco (menos de 150 caracteres), nunca repitiendo mensajes. Eres una asistente de Whatsapp llamada Esperanza en una tienda de muebles modernos llamada LifestyleGarden. Tu trabajo es escuchar y entender bien lo que quiere el cliente, haz preguntas si es necesario. Toma en cuenta que las respuestas deben ser concisas y útiles y utiliza el historial de conversacion para responder. Incluye los URL de los productos relacionados a tu respuesta. MAX_CHARACTERS=200
    
    chat_history:{chat_history}
    
    context:{context}
    
    question:{question}
    
    answer:"""
    
    prompt = PromptTemplate(template=template, input_variables=["context", "question", "chat_history"])
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory, combine_docs_chain_kwargs={"prompt": prompt})
    
    @classmethod
    def query(cls, query):
        result = cls.chain({"question": query})
        return result["answer"]

agent_instance = Agent()
