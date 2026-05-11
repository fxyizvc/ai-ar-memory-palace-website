import os
import trimesh
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_text_texture(text, output_path, image_size=(1024, 614), bg_color='black', text_color='white'):
    """
    Creates a PNG texture image with robust text wrapping.
    """
    img = Image.new('RGB', image_size, color=bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=45)
    except IOError:
        font = ImageFont.load_default()
    wrapper = textwrap.TextWrapper(width=40, break_long_words=True)
    wrapped_text = "\n".join(wrapper.wrap(text))
    _, _, text_width, text_height = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=10)
    text_x = (image_size[0] - text_width) / 2
    text_y = (image_size[1] - text_height) / 2
    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=font,
        fill=text_color,
        align="center",
        spacing=10
    )
    img.save(output_path)
    print(f"Texture image saved to {output_path}")

# --- START OF THE FINAL generate_3d_card FUNCTION ---
def generate_3d_card(texture_path, output_glb_path):
    """
    Final, robust function to generate a 3D card with text on the front face.
    This version uses explicit orientation and detailed logging.
    """
    print("\n--- Running FINAL, ROBUST generate_3d_card function ---")
    if not os.path.exists(texture_path):
        print(f"Error: Texture file not found at {texture_path}")
        return

    # 1. Create a box with specific dimensions (X=width, Y=height, Z=thickness)
    card_extents = [8.56, 5.4, 0.076]
    card_mesh = trimesh.creation.box(extents=card_extents)
    print(f"Step 1: Created box with {len(card_mesh.vertices)} vertices and {len(card_mesh.faces)} faces.")

    # 2. Load the texture
    texture_img = Image.open(texture_path).convert("RGBA")

    # 3. Initialize UV coordinates for all vertices to a safe default (a single point)
    uv = np.zeros((len(card_mesh.vertices), 2))

    # 4. Identify the front face. With our extents, the large flat faces are on the Z-axis.
    # The "front" face will have a normal vector of [0, 0, 1] (pointing along +Z).
    front_normal = np.array([0, 0, 1])
    face_indices = np.where(np.all(np.abs(card_mesh.face_normals - front_normal) < 1e-6, axis=1))[0]

    if not face_indices.size:
        print("FATAL: Could not identify the front face (+Z) of the card. Aborting UV mapping.")
        return

    print(f"Step 2: Identified front face (normal ~{front_normal}) with face indices: {face_indices}")

    # 5. Get the 4 unique vertices that make up this face
    vert_indices = np.unique(card_mesh.faces[face_indices])
    print(f"Step 3: Found {len(vert_indices)} unique vertices for this face: {vert_indices}")

    # 6. Calculate the bounding box and ranges for the front face vertices
    active_vertices = card_mesh.vertices[vert_indices]
    min_x, max_x = active_vertices[:, 0].min(), active_vertices[:, 0].max()
    min_y, max_y = active_vertices[:, 1].min(), active_vertices[:, 1].max()
    range_x = max_x - min_x
    range_y = max_y - min_y
    print(f"Step 4: Calculated bounding box for face: X range={range_x}, Y range={range_y}")

    if range_x < 1e-6 or range_y < 1e-6:
        print("FATAL: Front face has zero area. Cannot map texture.")
        return

    # 7. Calculate and assign the correct UV coordinate for each vertex on the front face
    print("Step 5: Calculating UV coordinates for each front-face vertex...")
    for v_idx in vert_indices:
        pt = card_mesh.vertices[v_idx]
        # U coordinate is the horizontal position (based on X)
        u = (pt[0] - min_x) / range_x
        # V coordinate is the vertical position (based on Y)
        v = (pt[1] - min_y) / range_y
        uv[v_idx] = [u, v]
        print(f"  - Vertex {v_idx}: pt=({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f}) -> uv=({u:.2f}, {v:.2f})")

    # 8. Apply the texture using the calculated UVs
    card_mesh.visual = trimesh.visual.texture.TextureVisuals(uv=uv, image=texture_img)
    print("Step 6: Applied texture visual to the mesh.")

    # 9. Export the final model
    scene = trimesh.Scene([card_mesh])
    scene.export(output_glb_path)
    print(f"✅ 3D card model saved to {output_glb_path}")