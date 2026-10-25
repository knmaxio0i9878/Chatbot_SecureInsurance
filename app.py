from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODELS = [
    "nex-agi/nex-n2.5-pro:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen3-4b:free",
    "qwen/qwen3.8-27b:free",
    "liquid/lfm-2.5-2.6n:free",
    "thinkingmachines/inlinking-small:free",
    "nvdia/nemotron-3.5-lightning:free"
]

# PDF -> Chunks

documents = PyPDFLoader("TechNova_Employee_Handbook_Detailed.pdf").load()

chunks = RecursiveCharacterTextSplitter(
    chunk_size = 800,
    chunk_overlap = 100
).split_documents(documents)

# Embeddings
# embedding_model = HuggingFaceEmbeddings(
#     model_name = "sentence_transformers/all-MiniLM-L6-v2"
# )
embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

# Vector DB
vector_db = Chroma.from_documents(
    documents = chunks,
    embedding = embedding_model,
    persist_directory = "./technovaDB" 
)

retriever = vector_db.as_retriever(
    search_kwargs={"k":3}
)

# RAG Prompt 
prompt = ChatPromptTemplate.from_template("""
    Answer the question using ONLY the provided context.

    If the answer is not availabe in the context, say:
    " I could n ot find this information int the provided documents."

    Answer in maximum 50 words.
    Context:
    {context}

    Quesiton:
    {question}
""")

def ask_llm(context,question):
    for model in MODELS:
        try:
            print("Trying Model:",model)

            llm = ChatOpenAI(
                model = MODELS,
                openai_api_key = API_KEY,
                open_api_base = "https://openrouter.ai/vpi/v1"
            )
            
            chain = prompt | llm

            return chain.invoke({
                "context": context,
                "question": question
            })

        except Exception as e:
            print("Model failed:", model)
            print(e)

    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.json["question"]

    # Retrieve relevant chunks
    results = retriever.invoke(question)

    context = "\n".join(
        document.page_content
        for document in results
    )

    # Send context + question to LLM
    response = ask_llm(context, question)

    if response is None:
        return jsonify({
            "answer": "All AI models are currently unavailable."
        })

    return jsonify({
        "answer": response.content
    })


if __name__ == "__main__":
    app.run(debug=True)
