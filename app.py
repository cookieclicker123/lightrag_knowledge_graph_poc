import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'light_rag')))
import logging
from light_rag.lightrag import LightRAG, QueryParam
from light_rag.lightrag.llm import ollama_model_complete, ollama_embedding
from light_rag.lightrag.utils import EmbeddingFunc
import gradio as gr

# Define constants and paths
OUTPUTS_DIR = "./outputs"
OUTPUT_FILE = os.path.join(OUTPUTS_DIR, "output_queries.txt")

# Configure logging
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# Load LightRAG with the existing data directory
rag = LightRAG(
    working_dir="./data",
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

# Function to query LightRAG
def query_rag(input_text, mode):
    try:
        result = rag.query(input_text, param=QueryParam(mode=mode))
        with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
            file.write(f"Mode: {mode}\nQuery: {input_text}\nResponse: {result}\n\n")
        logs = f"Query executed successfully in mode '{mode}'"
    except Exception as e:
        result = "An error occurred during the query execution."
        logs = f"Error: {e}"
    return result, logs

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center;'>LightRAG Gradio Demo for TV Post-Production</h1>")
    
    with gr.Row():
        with gr.Column(scale=1):
            query_input = gr.Textbox(label="Enter your query")
            mode_dropdown = gr.Dropdown(choices=["naive", "local", "global", "hybrid"], label="Select Query Mode")
            submit_button = gr.Button("Submit")
        with gr.Column(scale=2):
            result_output = gr.Textbox(label="LLM Response", lines=20, interactive=True)
            logs_output = gr.Textbox(label="Terminal Logs", lines=10, interactive=True)

        submit_button.click(query_rag, inputs=[query_input, mode_dropdown], outputs=[result_output, logs_output])

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()
