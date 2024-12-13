import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'light_rag')))
import logging
from light_rag.lightrag import LightRAG
from light_rag.lightrag.llm import ollama_model_complete, ollama_embedding
from light_rag.lightrag.utils import EmbeddingFunc
import pdfplumber

# Define constants and paths
WORKING_DIR = "./data"
OUTPUTS_DIR = "./outputs"
PDF_PATH = os.path.join(WORKING_DIR, "Post_Production_Handbook_2014.pdf")
GRAPH_SAVE_PATH = os.path.join(OUTPUTS_DIR, "lightrag_index.pkl")

# Ensure directories exist
os.makedirs(WORKING_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# Initialize LightRAG
rag = LightRAG(
    working_dir=WORKING_DIR,
    chunk_token_size=1200,
    llm_model_func=ollama_model_complete,
    llm_model_name="llama3.2",
    llm_model_max_async=4,
    llm_model_max_token_size=32768,
    llm_model_kwargs={"host": "http://localhost:11434", "options": {"num_ctx": 32768}},
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(texts, embed_model="nomic-embed-text", host="http://localhost:11434"),
    ),
)

def index_pdf():
    pdf_text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            pdf_text += page.extract_text() + "\n"

    logging.info("Indexing PDF content...")
    rag.insert(pdf_text)
    rag.save(GRAPH_SAVE_PATH)
    logging.info(f"Indexing complete. Graph saved to {GRAPH_SAVE_PATH}")

if __name__ == "__main__":
    index_pdf()
