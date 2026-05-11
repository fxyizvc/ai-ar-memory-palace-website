# 🧠 AI & AR Memory Palace Web App

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)
![HuggingFace](https://img.shields.io/badge/AI-HuggingFace_Transformers-orange.svg)
![ThreeJS](https://img.shields.io/badge/3D-Trimesh_&_Model_Viewer-purple.svg)

Welcome to the **Memory Palace Web App**! This is a cutting-edge educational asset management platform designed to automatically process, summarize, and convert study materials (PDFs, PPTs) into **interactive 3D summary cards** using Artificial Intelligence.

---

## 🚀 What it Does

This application revolutionizes how students interact with study materials. Instead of reading through long, dense PDFs or PowerPoint presentations, administrators can upload these files, and the system will automatically:
1. **Extract** the text from the documents.
2. **Summarize** the extracted text using advanced AI (HuggingFace's BART model).
3. **Generate a 3D model** (`.glb`) of a card, with the AI-generated summary dynamically textured onto its surface.
4. **Organize & Store** the resulting 3D models and original documents via Google Drive integration, categorized by College, Branch, and Semester.

Users can then view these interactive 3D summaries directly in their browser using WebAR/3D technology!

---

## ✨ Key Features

- 🤖 **AI-Powered Summarization**: Utilizes the state-of-the-art `facebook/bart-large-cnn` model for abstractive text summarization.
- 🧊 **Procedural 3D Generation**: Automatically crafts 3D meshes (cards) and UV-maps text textures onto them using `trimesh` and `Pillow`.
- ☁️ **Google Drive Cloud Integration**: Automates the uploading, securing, and serving of heavy 3D assets and PDFs via the Google Drive API.
- 🗄️ **Smart Asset Organization**: Organizes resources geographically (by college coordinates) and academically (by branch and semester) in a MongoDB database.
- 🕶️ **WebAR Viewer Integration**: Seamlessly displays generated `.glb` models on the frontend using Google's `<model-viewer>`.
- 🔐 **Secure Admin Portal**: Session-based authentication with Flask-Login to protect the AI generation pipeline and database management.

---

## 🛠️ Technology Stack

**Backend Framework:**
- **Python** with **Flask**
- **MongoDB** (via `Flask-PyMongo`)

**Artificial Intelligence & Data Processing:**
- **HuggingFace `transformers`** (powered by PyTorch)
- `PyMuPDF (fitz)` & `python-pptx` for document text extraction.

**3D Modeling & Rendering:**
- `trimesh` for geometry creation.
- `Pillow (PIL)` for dynamic texture generation.

**Cloud & Integrations:**
- **Google Drive API** (`google-api-python-client`)

**Frontend UI:**
- HTML5 / CSS3 / JavaScript
- Flask Templates (Jinja2)
- `<model-viewer>` web component

---

## ⚙️ The Core Workflow (How it Works)

1. **Upload**: The Admin uploads a lecture note (PDF/PPT) via the `/admin/generator` dashboard.
2. **Extraction**: The system parses the document and extracts the raw textual content.
3. **Summarization**: The text is fed into the HuggingFace BART model, which condenses the material into a concise summary.
4. **Texture Creation**: The summary text is drawn onto a 2D image canvas.
5. **3D Generation**: A 3D bounding box is created. The 2D image is mapped as a texture onto the face of the 3D model.
6. **Cloud Sync**: Both the original file and the 3D `.glb` model are uploaded directly to a Google Drive folder.
7. **Viewing**: Users can browse the portal and interact with the 3D model directly in the browser!

---

## 📂 Project Structure

- `app/admin/` - Core routing, admin dashboard, and UI logic.
- `app/auth/` - Authentication, login/logout, and security routing.
- `app/services/` - The Brains of the Operation:
  - `ai_summarizer.py` - AI NLP logic.
  - `google_drive.py` - Cloud API integrations.
  - `model_generator.py` - 3D mesh and texture creation logic.
- `app/models.py` - Database models and schemas.
- `run.py` - Application entry point.

---

## 💻 Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fxyizvc/ai-ar-memory-palace-website.git
   cd ai-ar-memory-palace-website
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables & Credentials:**
   - Ensure your `credentials.json` for Google Drive API is in the root directory.
   - Configure your `config.py` with your MongoDB URI and Secret Keys.

5. **Run the Application:**
   ```bash
   python run.py
   ```
   *The app will be available at `http://127.0.0.1:5000/`*

---
*This project demonstrates a unique intersection of Web Development, Natural Language Processing, Procedural 3D Modeling, and Cloud Architecture.*
