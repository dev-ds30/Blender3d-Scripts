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


def mandelbulb_distance(pos, power=8, iterations=15, bailout=2.0):
    """
    Calculate distance estimation for Mandelbulb fractal
    
    Args:
        pos: 3D position Vector
        power: Mandelbulb power (8 is classic, try 6-12 for variations)
        iterations: More iterations = more detail (10-20 typical)
        bailout: Escape radius
    
    Returns:
        distance estimate (used for vertex displacement)
    """
    z = pos.copy()
    dr = 1.0
    r = 0.0
    
    for i in range(iterations):
        r = z.length
        
        if r > bailout:
            break
        
        if r < 0.0001:  # Avoid division by zero
            return 0
        
        # Convert to spherical coordinates
        theta = math.acos(max(-1.0, min(1.0, z.z / r)))  # Clamp to valid range
        phi = math.atan2(z.y, z.x)
        
        # Scale and rotate the point
        zr = r ** power
        theta = theta * power
        phi = phi * power
        
        # Convert back to cartesian coordinates
        z = zr * Vector((
            math.sin(theta) * math.cos(phi),
            math.sin(theta) * math.sin(phi),
            math.cos(theta)
        ))
        z += pos
        
        # Derivative for distance estimation
        dr = (r ** (power - 1.0)) * power * dr + 1.0
    
    # Distance estimation with safety checks
    if r > 0.0001 and dr > 0:
        return 0.5 * math.log(max(r, 0.0001)) * r / dr
    else:
        return 0


def create_mandelbulb(resolution=64, power=8, scale=2.0, threshold=1.5):
    """
    Create Mandelbulb fractal using marching cubes approach
    
    Args:
        resolution: Grid resolution (32-128, higher = more detail but slower)
        power: Mandelbulb power parameter
        scale: Overall size scaling
        threshold: Surface threshold (adjust to capture more/less detail)
    """
    print(f"Generating Mandelbulb (power={power}, resolution={resolution})...")
    
    # Create initial icosphere for deformation
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=scale)
    obj = bpy.context.active_object
    obj.name = f"Mandelbulb_P{power}"
    mesh = obj.data
    
    # Apply subdivision for high detail
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    bpy.ops.object.modifier_apply(modifier="Subdivision")
    
    # Deform vertices based on Mandelbulb distance field
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(mesh)
    
    for vert in bm.verts:
        # Sample position in fractal space
        pos = vert.co.copy() / scale
        
        # Get distance estimate from Mandelbulb
        dist = mandelbulb_distance(pos, power=power, iterations=12)
        
        # Displace vertex inward/outward based on distance
        # Vertices inside fractal pull in, outside push out
        displacement = -dist * scale * 0.3
        vert.co += vert.normal * displacement
    
    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Smooth shading
    bpy.ops.object.shade_smooth()
    
    # Add final smoothing subdivision
    subsurf2 = obj.modifiers.new(name="Smooth", type='SUBSURF')
    subsurf2.levels = 2
    subsurf2.render_levels = 3
    
    return obj


def create_fractal_material(obj, color_scheme='alien'):
    """
    Create material with fractal-like coloring
    
    Args:
        color_scheme: 'alien', 'gold', 'ice', 'void'
    """
    mat = bpy.data.materials.new(name=f"Fractal_{color_scheme}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    colorramp = nodes.new('ShaderNodeValToRGB')
    
    # Position nodes
    output.location = (400, 0)
    principled.location = (200, 0)
    colorramp.location = (0, 0)
    noise.location = (-200, 0)
    coord.location = (-400, 0)
    
    # Configure noise
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 15.0
    
    # Color schemes
    if color_scheme == 'alien':
        # Purple to green gradient
        colorramp.color_ramp.elements[0].color = (0.3, 0.1, 0.5, 1.0)
        colorramp.color_ramp.elements[1].color = (0.1, 0.8, 0.4, 1.0)
        principled.inputs['Metallic'].default_value = 0.6
        principled.inputs['Roughness'].default_value = 0.3
    elif color_scheme == 'gold':
        # Dark gold to bright gold
        colorramp.color_ramp.elements[0].color = (0.3, 0.2, 0.05, 1.0)
        colorramp.color_ramp.elements[1].color = (1.0, 0.8, 0.3, 1.0)
        principled.inputs['Metallic'].default_value = 0.9
        principled.inputs['Roughness'].default_value = 0.2
    elif color_scheme == 'ice':
        # White to cyan
        colorramp.color_ramp.elements[0].color = (0.8, 0.9, 1.0, 1.0)
        colorramp.color_ramp.elements[1].color = (0.4, 0.8, 1.0, 1.0)
        principled.inputs['Metallic'].default_value = 0.1
        principled.inputs['Roughness'].default_value = 0.1
        principled.inputs['Transmission'].default_value = 0.3
    else:  # void
        # Black to deep purple
        colorramp.color_ramp.elements[0].color = (0.05, 0.0, 0.1, 1.0)
        colorramp.color_ramp.elements[1].color = (0.2, 0.1, 0.3, 1.0)
        principled.inputs['Metallic'].default_value = 0.8
        principled.inputs['Roughness'].default_value = 0.4
        principled.inputs['Emission Strength'].default_value = 0.2
    
    # Link nodes
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], colorramp.inputs['Fac'])
    links.new(colorramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    obj.data.materials.append(mat)


def setup_scene():
    """Setup camera and lighting for fractal showcase"""
    # Camera
    bpy.ops.object.camera_add(location=(6, -6, 4))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(70), 0, math.radians(45))
    bpy.context.scene.camera = camera
    camera.data.lens = 50
    
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.data.angle = math.radians(5)
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Rim light
    bpy.ops.object.light_add(type='AREA', location=(-4, 4, 3))
    rim = bpy.context.active_object
    rim.data.energy = 200
    rim.data.color = (0.4, 0.6, 1.0)
    rim.data.size = 5
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(2, 2, -2))
    fill = bpy.context.active_object
    fill.data.energy = 50
    fill.data.color = (1.0, 0.8, 0.6)
    fill.data.size = 3


# Generate multiple Mandelbulbs with different powers
fractal_configs = [
    {'power': 8, 'scale': 1.5, 'x_offset': -4, 'color': 'alien'},    # Classic
    {'power': 9, 'scale': 1.5, 'x_offset': 0, 'color': 'gold'},      # Spikier
    {'power': 6, 'scale': 1.5, 'x_offset': 4, 'color': 'ice'},       # Smoother
]

print("=" * 60)
print("MANDELBULB FRACTAL GENERATOR")
print("=" * 60)

for i, config in enumerate(fractal_configs):
    print(f"\nGenerating fractal {i+1}/{len(fractal_configs)}...")
    
    obj = create_mandelbulb(
        resolution=64,
        power=config['power'],
        scale=config['scale']
    )
    
    # Position
    obj.location.x = config['x_offset']
    
    # Material
    create_fractal_material(obj, config['color'])
    
    print(f"✓ Completed: Power-{config['power']} Mandelbulb")

setup_scene()

print("\n" + "=" * 60)
print("• Increase resolution (64→96) for more detail (slower)")
print("• Try powers 4-12 for different fractal shapes")
print("• Powers 7-9 are most Mandelbulb-like")
print("• Power 6 = smoother, Power 10+ = extremely spiky")
print("=" * 60)
