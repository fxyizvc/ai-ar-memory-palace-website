# Memory Site Project Analysis

Based on the analysis of your codebase, here is a comprehensive overview of the "Memory Site" project, its purpose, functionality, and technology stack.

## 🎯 What it does

The **Memory Site** is a web-based educational asset management application designed to process, summarize, and convert study materials into 3D models. When an administrator uploads a PDF or PowerPoint file (like lecture notes or slides), the application automatically extracts the text, uses Artificial Intelligence to summarize it, creates a text-based texture image, and generates a 3D "card" (`.glb` file) with the summary printed on it. These assets are then uploaded to Google Drive and can be viewed or distributed to users. 

It is designed to organize these materials geographically (by college coordinates) and academically (by branch and semester).

## 🛠️ Technology Stack

- **Backend Framework:** Python with **Flask**
- **Database:** **MongoDB** (using `Flask-PyMongo`)
- **Authentication:** `Flask-Login` and `werkzeug.security` (session-based authentication with hashed passwords)
- **AI & Machine Learning:** HuggingFace `transformers` (using the `facebook/bart-large-cnn` model for abstractive text summarization) powered by PyTorch.
- **3D Modeling & Rendering:** `trimesh` for 3D box generation and UV mapping, `Pillow (PIL)` for dynamic texture generation.
- **Document Processing:** `PyMuPDF (fitz)` for PDF text extraction and `python-pptx` for PowerPoint text extraction.
- **Cloud Storage:** **Google Drive API** (using `google-api-python-client` and `google-auth-oauthlib`) for storing documents and 3D models.
- **Frontend UI:** HTML/CSS/JS using Flask templates (Jinja2) and Google's `<model-viewer>` web component for displaying 3D models directly in the browser.

## ⚙️ Core Workflows

### 1. Admin & Asset Management
- **College Management:** Admins can Add, Edit, or Delete colleges. Each college is associated with its geographical coordinates (latitude, longitude).
- **Material Tracking:** Uploaded materials are organized logically by **College Name/Coordinates**, **Branch** (CSE, ME, CE, EEE), and **Semester** (S1 to S8).

### 2. The AI Generation Pipeline
The core magic of the application happens when an admin visits the Generator (`/admin/generator`) and uploads a PDF or PPT:
1. **Extraction:** The app reads the file and extracts all raw text.
2. **Summarization:** The `ai_summarizer.py` service passes the text to the BART Deep Learning model, generating a concise summary.
3. **Texture Creation:** The `model_generator.py` service uses Pillow to draw the summarized text onto a blank image, creating a "texture".
4. **3D Card Generation:** A 3D box (shaped like a credit card) is created using `trimesh`. The text texture is then precisely UV-mapped to the front face of the 3D card. The final model is saved as a `.glb` file.
5. **Google Drive Sync:** The original document and the newly generated `.glb` 3D model are automatically uploaded to a designated Google Drive folder via the `google_drive.py` service.
6. **Database Logging:** The generated Google Drive URLs and file IDs are stored in MongoDB along with the asset's metadata.

### 3. Serving the Materials
- **Materials Dashboard:** A view where users can browse original study materials organized by semester and branch.
- **3D Models Dashboard:** A view where users can browse the generated 3D summary cards.
- **Proxy Serving:** To circumvent CORS and Authentication issues that block web-based 3D viewers, the app provides a `/admin/serve_model/<file_id>` route that streams the `.glb` files directly from Google Drive securely to the frontend `<model-viewer>`.

## 📂 Project Structure

- `app/admin/routes.py`: Contains the core logic, uploading, processing, and routing.
- `app/auth/routes.py`: Handles user login, logout, and password resets.
- `app/services/`: The core business logic.
  - `ai_summarizer.py`: The HuggingFace Transformers logic.
  - `google_drive.py`: Google Drive API OAuth and upload/stream logic.
  - `model_generator.py`: 3D Trimesh and Pillow texture generation logic.
- `app/models.py`: User schema and authentication utilities.
- `temp/`: A temporary directory used to hold files mid-processing before they get pushed to Google Drive.
