import os
import re
import fitz  # PyMuPDF
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app import mongo
# Import both of your services
from app.services.ai_summarizer import summarize_text_with_bart
from app.services.model_generator import create_text_texture, generate_3d_card
# Import the Google Drive service
from app.services.google_drive import upload_to_drive
from pptx import Presentation

from flask import send_file
# Ensure you import the new function
from app.services.google_drive import stream_file






# Blueprint setup remains the same
admin_bp = Blueprint('admin', __name__,
                    template_folder='../templates/admin',
                    static_folder='../static')


def validate_college_data(name, coord):
    # Check if fields are empty
    if not name or not coord:
        return False, "Error: Both College Name and Coordinates are required."

    # Regex: Only alphabets and spaces
    if not re.match(r"^[A-Za-z\s]+$", name):
        return False, "Invalid Name: Use alphabets only."
    
    # Regex: float,float (e.g. 11.11,22.22)
    if not re.match(r"^-?\d+(\.\d+)?,-?\d+(\.\d+)?$", coord):
        return False, "Invalid Coordinates: Use 'float,float' format (e.g. 11.83,12.43)."
    
    return True, ""

@admin_bp.route('/home')
@login_required
def home():
    return render_template('admin/home.html')

@admin_bp.route('/add-new')
@login_required
def add_new():
    try:
        colleges_list = list(mongo.db.colleges.find({}))
    except Exception as e:
        flash("Could not fetch college list.")
        colleges_list = []
    return render_template('admin/add_new.html', colleges=colleges_list)

@admin_bp.route('/add', methods=['POST'])
@login_required
def add_new_college():
    name = request.form.get('college_name', '').strip()
    coord = request.form.get('coordinate', '').strip()

    is_valid, error_msg = validate_college_data(name, coord)
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('admin.add_new'))

    try:
        mongo.db.colleges.insert_one({'college_name': name, 'coordinate': coord})
        flash(f'College "{name}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('admin.add_new'))

@admin_bp.route('/edit/<college_id>', methods=['POST'])
@login_required
def edit_college(college_id):
    name = request.form.get('college_name', '').strip()
    coord = request.form.get('coordinate', '').strip()

    is_valid, error_msg = validate_college_data(name, coord)
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('admin.add_new'))

    try:
        mongo.db.colleges.update_one(
            {'_id': ObjectId(college_id)},
            {'$set': {'college_name': name, 'coordinate': coord}}
        )
        flash('College updated successfully!', 'success')
    except Exception as e:
        flash(f'Update failed: {e}', 'error')
        
    return redirect(url_for('admin.add_new'))

@admin_bp.route('/delete/<college_id>')
@login_required
def delete_college(college_id):
    try:
        mongo.db.colleges.delete_one({'_id': ObjectId(college_id)})
        flash('College deleted successfully!', 'success')
    except Exception as e:
        flash(f'Delete failed: {e}', 'error')
    return redirect(url_for('admin.add_new'))

@admin_bp.route('/generator')
@login_required
def generator():
    summary = session.pop('summary', None)
    glb_path = session.pop('glb_path', None)

    college_data = {}
    try:
        # Fetch using your field names: 'college_name' and 'coordinate'
        colleges_cursor = mongo.db.colleges.find({}, {'college_name': 1, 'coordinate': 1, '_id': 0})

        # Create a dictionary mapping each college name to its coordinate string
        college_data = {doc['college_name']: doc['coordinate'] for doc in colleges_cursor if 'coordinate' in doc}

    except Exception as e:
        flash("Could not connect to the database to fetch college data.")
        print(f"Error fetching college data: {e}")

    return render_template('admin/generator.html',
                           summary=summary,
                           glb_path=glb_path,
                           college_data=college_data)

@admin_bp.route('/materials')
@login_required
def materials():
    try:
        # 1. Fetch Colleges
        colleges = list(mongo.db.colleges.find({}, {'college_name': 1, 'coordinate': 1}))
        
        def clean_coord(c): return str(c).replace(" ", "").strip().lower() if c else ""

        coord_to_college = {}
        for c in colleges:
            if c.get('coordinate'):
                coord_to_college[clean_coord(c.get('coordinate'))] = c.get('college_name')
        
        college_names = sorted(list(set(c['college_name'] for c in colleges if 'college_name' in c)))

        # 2. Fetch Assets
        assets_cursor = mongo.db.assets.find({}, {
            'filename': 1, 
            'pdf_url': 1,
            'semester': 1, 
            'coordinate': 1,
            'branch': 1
        })
        assets = list(assets_cursor)

        # Extract unique branches for the dropdown
        branch_names = sorted(list(set(str(a.get('branch', '')).strip() for a in assets if a.get('branch'))))

        # 3. Group by Semester
        materials_by_sem = {str(i): [] for i in range(1, 9)}
        materials_by_sem['Other'] = []

        for asset in assets:
            raw_coord = asset.get('coordinate')
            asset['college_name'] = coord_to_college.get(clean_coord(raw_coord), 'Unknown')

            raw_sem = str(asset.get('semester', ''))
            match = re.search(r'(\d+)', raw_sem)
            
            target_bucket = 'Other'
            if match:
                sem_num = int(match.group(1))
                if 1 <= sem_num <= 8:
                    target_bucket = str(sem_num)
            
            materials_by_sem[target_bucket].append(asset)

    except Exception as e:
        print(f"Error fetching materials: {e}")
        materials_by_sem = {str(i): [] for i in range(1, 9)}
        materials_by_sem['Other'] = []
        college_names = []
        branch_names = []
        
    return render_template('admin/materials.html', 
                           materials_by_sem=materials_by_sem, 
                           colleges=college_names,
                           branches=branch_names)


@admin_bp.route('/models')
@login_required
def models():
    try:
        # 1. Fetch Colleges
        colleges = list(mongo.db.colleges.find({}, {'college_name': 1, 'coordinate': 1}))
        
        def clean_coord(c): return str(c).replace(" ", "").strip().lower() if c else ""

        coord_to_college = {}
        for c in colleges:
            if c.get('coordinate'):
                coord_to_college[clean_coord(c.get('coordinate'))] = c.get('college_name')
        
        college_names = sorted(list(set(c['college_name'] for c in colleges if 'college_name' in c)))

        # 2. Fetch Assets
        assets_cursor = mongo.db.assets.find({}, {
            'filename': 1, 
            'glb_url': 1,
            'glb_id': 1,
            'semester': 1, 
            'coordinate': 1,
            'branch': 1
        })
        assets = list(assets_cursor)

        # Extract unique branches for the dropdown
        branch_names = sorted(list(set(str(a.get('branch', '')).strip() for a in assets if a.get('branch'))))

        # 3. Group by Semester
        models_by_sem = {str(i): [] for i in range(1, 9)}
        models_by_sem['Other'] = []

        for asset in assets:
            raw_coord = asset.get('coordinate')
            asset['college_name'] = coord_to_college.get(clean_coord(raw_coord), 'Unknown')

            raw_sem = str(asset.get('semester', ''))
            match = re.search(r'(\d+)', raw_sem)
            
            target_bucket = 'Other'
            if match:
                sem_num = int(match.group(1))
                if 1 <= sem_num <= 8:
                    target_bucket = str(sem_num)
            
            models_by_sem[target_bucket].append(asset)

    except Exception as e:
        print(f"Error fetching models: {e}")
        models_by_sem = {str(i): [] for i in range(1, 9)}
        models_by_sem['Other'] = []
        college_names = []
        branch_names = []
        
    return render_template('admin/models.html', 
                           models_by_sem=models_by_sem, 
                           colleges=college_names,
                           branches=branch_names)

@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    uploaded_files = request.files.getlist('files')
    if not uploaded_files or uploaded_files[0].filename == '':
        flash('No files selected!', 'error')
        return redirect(url_for('admin.generator'))

    ALLOWED_EXTENSIONS = {'.pdf', '.ppt', '.pptx'}
    coordinate = request.form.get("coordinate")
    semester = request.form.get("semester")
    branch = request.form.get("branch")

    if not coordinate:
        flash('Coordinate is required for asset upload!', 'error')
        return redirect(url_for('admin.generator'))

    for file in uploaded_files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Server-side validation check
        if file_ext not in ALLOWED_EXTENSIONS:
            flash(f"Error: '{file.filename}' is not a supported format. Only PDF and PPT are allowed.", 'error')
            return redirect(url_for('admin.generator'))

        try:
            # Setup directories and paths
            temp_dir = 'temp'
            models_dir = os.path.join('app', 'static', 'models')
            os.makedirs(temp_dir, exist_ok=True)
            os.makedirs(models_dir, exist_ok=True)

            file_basename = os.path.splitext(file.filename)[0]
            glb_filename = f"{file_basename}.glb"
            temp_file_path = os.path.join(temp_dir, file.filename)
            texture_path = os.path.join(temp_dir, 'summary_texture.png')
            glb_save_path = os.path.join(models_dir, glb_filename)

            file.save(temp_file_path) 
            
            # Text Extraction
            full_text = ""
            if file_ext == '.pdf':
                doc = fitz.open(temp_file_path)
                full_text = "".join(page.get_text() for page in doc)
                doc.close()
            else:
                prs = Presentation(temp_file_path)
                text_runs = [shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")]
                full_text = "\n".join(text_runs)

            if not full_text.strip():
                flash(f"Could not extract text from {file.filename}.", 'error')
                continue

            # Process AI summary and GLB
            summary = summarize_text_with_bart(full_text)
            session['summary'] = summary
            create_text_texture(summary, texture_path)
            generate_3d_card(texture_path, glb_save_path)
            session['glb_path'] = f'models/{glb_filename}'

            # Drive Upload and DB Save
            pdf_drive_url, pdf_drive_id = upload_to_drive(temp_file_path, file.filename, "application/pdf")
            glb_drive_url, glb_drive_id = upload_to_drive(glb_save_path, glb_filename, "model/gltf-binary")

            mongo.db.assets.insert_one({
                "filename": file.filename,
                "pdf_url": pdf_drive_url, 
                "glb_url": glb_drive_url, 
                "pdf_id": pdf_drive_id,   
                "glb_id": glb_drive_id,   
                "coordinate": coordinate,
                "semester": semester,
                "branch": branch
            })

            flash(f"'{file.filename}' processed successfully!", 'success')

        except Exception as e:
            flash(f"An error occurred with {file.filename}: {e}", 'error')
        
        finally:
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if 'texture_path' in locals() and os.path.exists(texture_path):
                os.remove(texture_path)

    return redirect(url_for('admin.generator'))


@admin_bp.route('/serve_model/<file_id>')
def serve_model(file_id):
    """
    Proxy route: Fetches file from Drive and serves it to the browser
    so <model-viewer> doesn't face CORS/Auth issues.
    """
    try:
        file_stream = stream_file(file_id)
        
        if file_stream:
            return send_file(
                file_stream,
                mimetype='model/gltf-binary',
                as_attachment=False,
                download_name=f"{file_id}.glb"
            )
        else:
            return "File not found or Drive Error", 404
    except Exception as e:
        print(f"Proxy Error: {e}")
        return f"Error: {e}", 500