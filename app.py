from flask import Flask, request, render_template, jsonify
import os
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer, util
import ollama
import logging

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize embedding model and Ollama client
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
client = ollama.Client()

# Global dictionary to store uploaded PDF texts
uploaded_texts = {}

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Helper functions
def extract_text_from_pdf(file_path):
    """Extract text from the PDF file."""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join([page.extract_text() for page in reader.pages])
            return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def find_similar_context(query, pdf_text):
    """Find the most similar context to the query in the PDF content."""
    sentences = pdf_text.split(". ")
    sentence_embeddings = embedding_model.encode(sentences, convert_to_tensor=True)
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(query_embedding, sentence_embeddings)
    best_idx = np.argmax(similarity_scores).item()
    return sentences[best_idx]

# Routes
@app.route("/")
def home():
    """Render the home page."""
    return render_template("chat.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Handle PDF upload and extraction."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    pdf_text = extract_text_from_pdf(file_path)

    if "Error extracting text" in pdf_text:
        return jsonify({"error": pdf_text}), 500

    uploaded_texts["pdf_text"] = pdf_text  # Store text in the global dictionary
    return render_template("chat.html", message="PDF uploaded and text extracted")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat queries."""
    pdf_text = uploaded_texts.get("pdf_text")  # Retrieve PDF content
    if not pdf_text:
        return jsonify({"reply": "No PDF content available. Please upload a PDF first."}), 400

    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided."}), 400

    # Retrieve context from the PDF
    context = find_similar_context(user_input, pdf_text)
    logging.debug(f"Context: {context}")

    # Send context and query to the model
    prompt = f"The following context is extracted from the PDF:\n{context}\n\nUser's question: {user_input}"
    logging.debug(f"Prompt: {prompt}")
    try:
        response = client.generate(model="llama3.2", prompt=prompt)
        logging.debug(f"Response: {response}")
        reply = response.get("response", "Sorry, I couldn't generate a response.")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
