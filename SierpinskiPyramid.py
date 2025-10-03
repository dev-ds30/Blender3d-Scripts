import bpy
import bmesh
from mathutils import Vector
import math

# Clear existing mesh objects
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
if bpy.context.selected_objects:
    bpy.ops.object.delete()

# Clear materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)


def tetrahedron_vertices(center, scale):
    """
    Calculate vertices of a regular tetrahedron (triangular pyramid)
    
    A tetrahedron is the 3D simplex - 4 vertices, 4 faces, 6 edges
    Perfect for 3D fractals due to its symmetry
    """
    # Height of tetrahedron from base to apex
    h = scale * math.sqrt(2.0/3.0)
    
    # Radius of circle containing base vertices
    r = scale * math.sqrt(3.0) / 3.0
    
    # One vertex at top
    v0 = center + Vector((0, 0, h))
    
    # Three vertices forming equilateral triangle base
    # Positioned 120 degrees apart
    v1 = center + Vector((r * math.cos(0), r * math.sin(0), 0))
    v2 = center + Vector((r * math.cos(2*math.pi/3), r * math.sin(2*math.pi/3), 0))
    v3 = center + Vector((r * math.cos(4*math.pi/3), r * math.sin(4*math.pi/3), 0))
    
    return [v0, v1, v2, v3]


def create_single_tetrahedron(center, scale, name="Tetrahedron"):
    """Create a single tetrahedron mesh"""
    verts = tetrahedron_vertices(center, scale)
    
    # Create mesh
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Build mesh using bmesh
    bm = bmesh.new()
    bm_verts = [bm.verts.new(v) for v in verts]
    
    # Create 4 triangular faces
    # Each face connects 3 vertices
    bm.faces.new([bm_verts[0], bm_verts[1], bm_verts[2]])  # Top-front face
    bm.faces.new([bm_verts[0], bm_verts[2], bm_verts[3]])  # Top-left face
    bm.faces.new([bm_verts[0], bm_verts[3], bm_verts[1]])  # Top-right face
    bm.faces.new([bm_verts[1], bm_verts[3], bm_verts[2]])  # Base face
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj


def create_sierpinski_pyramid(base_center, size=4.0, iterations=5, hollow=False):
    """
    Create a Sierpinski tetrahedron (3D Sierpinski gasket)
    
    The Sierpinski tetrahedron is created by:
    1. Start with a tetrahedron
    2. Subdivide into 4 smaller tetrahedra at each vertex
    3. Remove the center (or keep for "solid" version)
    4. Repeat recursively
    
    Args:
        base_center: Center position of base
        size: Size of the initial tetrahedron
        iterations: Recursion depth (1-6 recommended, 7+ is very heavy!)
        hollow: If True, only creates outermost layer (more intricate look)
    
    Returns:
        List of all tetrahedron objects created
    """
    all_objects = []
    total_count = 0
    
    def sierpinski_recursive(center, scale, depth, max_depth):
        nonlocal total_count
        
        # Base case: create actual tetrahedron
        if depth >= max_depth:
            obj = create_single_tetrahedron(
                center, 
                scale, 
                f"Tetra_L{depth}_N{total_count}"
            )
            total_count += 1
            return [obj]
        
        # For hollow mode, skip intermediate levels
        if hollow and depth < max_depth - 1:
            verts = tetrahedron_vertices(center, scale)
            new_scale = scale / 2.0
            
            objects = []
            for vert in verts:
                objects.extend(sierpinski_recursive(vert, new_scale, depth + 1, max_depth))
            return objects
        
        # Recursive case: create 4 smaller pyramids at each vertex
        verts = tetrahedron_vertices(center, scale)
        new_scale = scale / 2.0
        
        objects = []
        for vert in verts:
            objects.extend(sierpinski_recursive(vert, new_scale, depth + 1, max_depth))
        
        return objects
    
    print(f"Generating Sierpinski Pyramid with {iterations} iterations...")
    print(f"Expected tetrahedra: {4**iterations}")
    
    all_objects = sierpinski_recursive(base_center, size, 0, iterations)
    
    print(f"✓ Created {len(all_objects)} tetrahedra")
    
    return all_objects


def create_gradient_materials(count, color_start, color_end):
    """Create gradient materials from start to end color"""
    materials = []
    
    for i in range(count):
        t = i / max(count - 1, 1)  # Interpolation factor
        
        # Interpolate between colors
        color = tuple(
            color_start[j] * (1 - t) + color_end[j] * t
            for j in range(3)
        )
        
        mat = bpy.data.materials.new(name=f"Sierpinski_Mat_{i}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        bsdf = nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.6
        bsdf.inputs['Roughness'].default_value = 0.3
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
        
        materials.append(mat)
    
    return materials


def assign_materials_by_depth(objects, materials):
    """Assign materials based on recursion depth for visual interest"""
    # Sort objects by Z position to create gradient effect
    sorted_objs = sorted(objects, key=lambda o: o.location.z)
    
    for i, obj in enumerate(sorted_objs):
        mat_index = int((i / len(sorted_objs)) * len(materials))
        mat_index = min(mat_index, len(materials) - 1)
        
        if not obj.data.materials:
            obj.data.materials.append(materials[mat_index])
        else:
            obj.data.materials[0] = materials[mat_index]


def join_and_smooth(objects, name):
    """Join all objects and apply smooth subdivision"""
    if not objects:
        return None
    
    # Select all
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    
    # Join
    bpy.ops.object.join()
    combined = bpy.context.active_object
    combined.name = name
    
    # Smooth shading
    bpy.ops.object.shade_smooth()
    
    # Add subdivision modifier for ultra-smooth result
    subsurf = combined.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Optional: Add bevel modifier for crisp edges
    bevel = combined.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 2
    
    return combined


def setup_camera_and_lighting():
    """Setup cinematic view of the fractal"""
    # Camera - orbiting view to see 3D structure
    cam_distance = 12
    cam_angle = math.radians(30)
    
    bpy.ops.object.camera_add(
        location=(
            cam_distance * math.cos(cam_angle),
            -cam_distance * math.sin(cam_angle),
            8
        )
    )
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(65), 0, math.radians(30))
    bpy.context.scene.camera = camera
    camera.data.lens = 50
    
    # Three-point lighting for dramatic effect
    
    # Key light - main illumination
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
    key_light = bpy.context.active_object
    key_light.data.energy = 3.0
    key_light.data.angle = math.radians(5)
    key_light.rotation_euler = (math.radians(45), 0, math.radians(45))
    key_light.name = "Key_Light"
    
    # Fill light - soften shadows
    bpy.ops.object.light_add(type='AREA', location=(-8, 8, 10))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 300
    fill_light.data.color = (0.8, 0.9, 1.0)  # Cool tone
    fill_light.data.size = 10
    fill_light.name = "Fill_Light"
    
    # Rim light - highlight edges
    bpy.ops.object.light_add(type='AREA', location=(5, 10, 5))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 400
    rim_light.data.color = (1.0, 0.7, 0.4)  # Warm tone
    rim_light.data.size = 8
    rim_light.name = "Rim_Light"
    
    # Set world background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)


# ============================================================================
# MAIN GENERATION
# ============================================================================

print("=" * 70)
print("SIERPINSKI PYRAMID (TETRAHEDRON) FRACTAL GENERATOR")
print("=" * 70)

# Configuration
ITERATIONS = 5  # 3=64 tetras, 4=256, 5=1024, 6=4096
SIZE = 4.0
HOLLOW_MODE = False  # Set True for hollow (more intricate) version

print(f"\nConfiguration:")
print(f"  Iterations: {ITERATIONS}")
print(f"  Base Size: {SIZE}")
print(f"  Mode: {'Hollow (Intricate)' if HOLLOW_MODE else 'Solid (Full)'}")
print(f"  Expected Tetrahedra: {4**ITERATIONS}")
print()

# Generate the fractal
objects = create_sierpinski_pyramid(
    base_center=Vector((0, 0, 0)),
    size=SIZE,
    iterations=ITERATIONS,
    hollow=HOLLOW_MODE
)

# Create beautiful gradient materials
print("\nCreating gradient materials...")
materials = create_gradient_materials(
    count=20,
    color_start=(0.1, 0.3, 0.9),  # Deep blue
    color_end=(0.9, 0.2, 0.5)     # Pink/magenta
)

# Assign materials for depth visualization
assign_materials_by_depth(objects, materials)

# Join and smooth everything
print("Joining and smoothing geometry...")
final_object = join_and_smooth(objects, "Sierpinski_Pyramid_Fractal")

# Setup scene
print("Setting up camera and lighting...")
setup_camera_and_lighting()


print(f"\nFractal Statistics:")
print(f"  Total Tetrahedra: {4**ITERATIONS}")
print(f"  Recursion Depth: {ITERATIONS} levels")
print(f"  Self-Similarity: Each level is 1/2 scale of previous")
print(f"  Fractal Dimension: ~2 (between 2D and 3D)")
print()
print("Customization Tips:")
print("  • Change ITERATIONS (3-6 recommended, 7+ very heavy)")
print("  • Set HOLLOW_MODE = True for intricate outer shell only")
print("  • Adjust SIZE for different scales")
print("  • Modify color_start/color_end for different gradients")
print()
print("Mathematical Properties:")
print("  • 4^n tetrahedra at iteration n")
print("  • Volume = (1/2)^n of original at each level")
print("  • Surface area increases while volume approaches zero!")
print("=" * 70)
