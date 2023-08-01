from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.document_loaders import JSONLoader
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI


class Agent:
    loader = JSONLoader(file_path='muebles.json', jq_schema='.[].product', text_content=False)
    documents = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0).split_documents(loader.load())
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    condense_question_template = """
    Dada la siguiente historia de chat y una pregunta de seguimiento, reformula la pregunta
    O finaliza la conversación si parece que ha terminado.
    Historia de chat:
    "{chat_history}"
    Pregunta de seguimiento:
    "{question}"
    Pregunta independiente:
    """

    condense_question_prompt = PromptTemplate(template=condense_question_template, input_variables=["chat_history", "question"])

    qa_template = """
    Eres una asistente de Whatsapp llamada Esperanza trabajando para una tienda de muebles modernos. Utiliza el siguiente contexto, incluyendo nombres de productos, descripciones y palabras clave, para mostrar al comprador lo que está disponible, ayudar a encontrar lo que desea y responder cualquier pregunta. Incluye URL de los productos al final de tu respuesta. Se concisa y directa al punto.

    No pasa nada si no sabes la respuesta.
    Contexto:
    "{context}"
    Pregunta:
    "{question}"

    Respuesta útil:
    """

    qa_prompt = PromptTemplate(template=qa_template, input_variables=["context", "question"])

    
    qa_prompt = PromptTemplate(template=qa_template, input_variables=["context", "question"])

        # define two LLM models from OpenAI
    llm = OpenAI(temperature=0)
     
    streaming_llm = OpenAI(
        verbose=True,
        max_tokens=150,
        temperature=0.2
    )
     
# use the LLM Chain to create a question creation chain
    question_generator = LLMChain(
        llm=llm,
        prompt=condense_question_prompt
    )
     
# use the streaming LLM to create a question answering chain
    doc_chain = load_qa_chain(
        llm=streaming_llm,
        chain_type="stuff",
        prompt=qa_prompt
    )
    
    chatbot = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator
    )

    chat_history = []
 
    @classmethod
    def query(cls, query):
        result = cls.chatbot({"question": query, "chat_history": cls.chat_history})
        cls.chat_history.append((result["question"], result["answer"]))
        return result["answer"]

agent_instance = Agent()
