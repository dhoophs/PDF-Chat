# Chat with PDF

**Chat with PDF** is a Flask-based application that empowers users to interact with PDF files using Generative AI and Retrieval-Augmented Generation (RAG). Users can upload PDF files, extract their content, and ask questions about the document. By leveraging advanced natural language processing (NLP) techniques, the application identifies the most relevant context from the document and combines it with the power of Generative AI to produce accurate and meaningful responses.

---

## Features

- **PDF Upload and Text Extraction**: Upload a PDF file, and the application extracts the text content for further interaction.
- **Contextual Query Handling**: Ask questions about the PDF, and the app identifies the most relevant context from the document.
- **AI-Powered Responses**: Generates meaningful answers to user queries using a pre-trained language model.
- **User-Friendly Interface**: Built with Flask and styled with HTML/CSS for an intuitive user experience.

---

## Technologies Used

### Backend
- **Python**: Core programming language for the application.
- **Flask**: Web framework for backend development.
- **PyPDF2**: Extracts text from PDF files.
- **Sentence-Transformers**: Embedding model (`all-MiniLM-L6-v2`) used for finding the most relevant sentences in the PDF.
- **Ollama API**: AI model (`llama3.2`) for generating responses based on the extracted context.

### Frontend
- **HTML/CSS**: For building and styling the user interface.

---

## Installation

### Prerequisites
- Python 3.8+
- Pip (Python package manager)

---



