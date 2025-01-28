from flask import Flask, request, render_template, jsonify
import ollama
import PyPDF2
import os

app = Flask(__name__)

# Initialize the Ollama client
client = ollama.Client()

# Define the path to store uploaded PDFs
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variable to store extracted PDF text
pdf_text = ""

# Load the desired model (ensure it's already pulled via the CLI or API)
MODEL_NAME = "llama3.2"  # Update with the correct model name

# Helper function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

@app.route("/")
def home():
    """Render the chat interface."""
    return render_template("chat.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Handle PDF upload and extraction."""
    global pdf_text

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded PDF file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Extract text from the uploaded PDF
    pdf_text = extract_text_from_pdf(filepath)

    if "Error extracting text" in pdf_text:
        return jsonify({"error": pdf_text}), 500

    return jsonify({"message": "PDF uploaded and text extracted", "text": pdf_text[:500]})  # Displaying first 500 characters for brevity

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests."""
    global pdf_text

    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided."}), 400

    # If user asks about the PDF content
    if "pdf" in user_input.lower():
        if not pdf_text:
            return jsonify({"reply": "No PDF content available. Please upload a PDF first."})
        return jsonify({"reply": f"PDF Content (first 500 characters): {pdf_text[:500]}"})

    # Otherwise, handle it with Ollama model as usual
    try:
        response = client.complete(
            model=MODEL_NAME,
            prompt=user_input
        )
        reply = response.get("response", "Sorry, I couldn't generate a response.")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
