# DevOps & Deployment Guide for "Memory Site"

Based on the analysis of your project, you have a **Flask backend** heavily reliant on **Machine Learning (`transformers`, `torch`)**, **MongoDB**, and **Google Drive API**. This stack has specific needs—especially regarding high memory requirements for the AI models and careful handling of secrets.

Here is the step-by-step guide to properly DevOps and deploy this project.

---

## Step 1: Application Readiness (Security & Secrets)

Currently, your `config.py` contains hardcoded, sensitive information (MongoDB password, Gmail App Password). The first rule of DevOps is never to hardcode secrets.

1. **Create a `.env` file** locally (and ensure it's in your `.gitignore`!):
   ```env
   SECRET_KEY=your-secure-random-string
   MONGO_URI=mongodb+srv://jagankk:<YOUR_PASSWORD>@cluster0.kqm7txf.mongodb.net/arProjectDB?retryWrites=true&w=majority
   MAIL_PASSWORD=your_gmail_app_password
   ```
2. **Update `config.py`** to strictly use `os.environ.get()` for these values.
3. **Google Drive Credentials:** You have `credentials.json` and `token.json`. For production, you will need a secure way to inject these. Usually, this means encoding the JSON strings as Base64 environment variables and decoding them on server startup, or utilizing a Cloud Secret Manager.

> [!WARNING] 
> Your `config.py` currently contains an active Gmail App password (`tpld ...`) and a MongoDB password. You should immediately delete these from the codebase, revoke the Gmail app password in your Google Account settings, and generate a new one.

---

## Step 2: Containerization (Docker)

Because your project uses heavy libraries like PyTorch and PyMuPDF, your environment is complex. **Docker** ensures that "it works on my machine" translates to "it works on the server."

You need to create a `Dockerfile`. Here is a recommended starting point:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for PyMuPDF, trimesh, Pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir keeps the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8000

# Command to run the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "run:app"]
```
*Note: We use `gunicorn` with an increased `--timeout 120` because AI summarization and 3D model generation might take longer than a standard 30-second web request.*

---

## Step 3: Choosing the Right Hosting Infrastructure

**Critical Requirement:** Your app uses `torch` and `transformers` (BART model). This requires **at least 4GB of RAM (ideally 8GB+)**. Free tiers on services like Heroku, Render, or Vercel **will crash** due to Out Of Memory (OOM) errors.

### Recommended Options:
1. **DigitalOcean Droplet / AWS EC2 (VPS - Recommended for cost-efficiency):**
   - Get a Linux machine (Ubuntu) with at least 4GB RAM (e.g., ~$20-25/month).
   - You install Docker on it and run your container.
   - Use **Nginx** as a reverse proxy to route traffic to your Docker container and handle SSL (HTTPS) via Let's Encrypt.
2. **Managed Container Services (Easier but pricier):**
   - **Render:** You can deploy the Docker container directly, but you'll need the "Pro" tier or higher to get enough RAM.
   - **Google Cloud Run:** Fully managed, scale-to-zero. You can configure it with up to 8GB/16GB/32GB RAM. It's a great fit since you already use Google Drive API, but cold starts (initial load time) might be slow because the AI model has to load into memory on the first request.

---

## Step 4: Database Setup

You are already using **MongoDB Atlas**, which is great. 
- **Action:** Before you go live, ensure you go to your MongoDB Atlas dashboard -> Network Access, and allow the IP address of your production server. If you use a dynamic IP service like Render/Cloud Run, you might need to allow access from anywhere (`0.0.0.0/0`), but make sure your DB password is extremely secure.

---

## Step 5: Setting up CI/CD (GitHub Actions)

Continuous Integration and Continuous Deployment (CI/CD) automates your deployments so you don't have to manually SSH into a server every time you update the code.

1. Go to your GitHub repository and create a `.github/workflows/deploy.yml` file.
2. **The Workflow Steps:**
   - **Trigger:** On push to the `main` branch.
   - **Build:** Check out the code, build the Docker image.
   - **Push:** Push the Docker image to a registry (like Docker Hub or GitHub Container Registry).
   - **Deploy:** SSH into your server (using GitHub Secrets for your SSH key), pull the new image, and restart the container.

---

## Step 6: Domain & SSL (HTTPS)

For security (and for AR/camera APIs to work in browsers), your site must have an SSL certificate (`https://`).
- Buy a domain name (Namecheap, Cloudflare, etc.).
- Point the domain's A-record to your server's IP.
- If using a VPS, use **Certbot (Let's Encrypt)** with Nginx to get a free, auto-renewing SSL certificate.

---

### What should we do right now?

If you are ready to start this process, **I can do the following for you right now**:
1. Clean up `config.py` and create a `.env` template to secure your passwords.
2. Generate the exact `Dockerfile`, `.dockerignore`, and `docker-compose.yml` files for your project so you can test the production setup locally.
3. Write a GitHub Actions workflow file to start automating things.

Let me know which of these you'd like me to set up first!
