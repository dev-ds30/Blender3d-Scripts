import bpy
import bmesh
from mathutils import Vector
import math

# Clear scene
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    obj.select_set(True)
bpy.ops.object.delete()

# Clear materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)


def create_klein_bottle_mesh(u_steps=200, v_steps=100):
    """
    Create Klein bottle using classic figure-8 immersion
    Optimized for upright glass sculpture appearance
    """
    mesh = bpy.data.meshes.new("KleinBottle")
    obj = bpy.data.objects.new("KleinBottle", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    verts = []
    
    for i in range(u_steps):
        u = (i / u_steps) * 2 * math.pi
        row = []
        
        for j in range(v_steps):
            v = (j / v_steps) * 2 * math.pi
            
            # Figure-8 Klein bottle parametrization
            r = 4 * (1 - math.cos(u) / 2)
            
            if u < math.pi:
                x = 6 * math.cos(u) * (1 + math.sin(u)) + r * math.cos(v + math.pi)
                y = 16 * math.sin(u)
                z = r * math.sin(v + math.pi)
            else:
                x = 6 * math.cos(u) * (1 + math.sin(u)) + r * math.cos(u) * math.cos(v)
                y = 16 * math.sin(u)
                z = r * math.sin(u) * math.sin(v)
            
            # Scale to appropriate size
            scale = 0.08
            
            # Rotate 90 degrees to stand upright
            pos = Vector((x * scale, z * scale, -y * scale * 0.9))
            
            # Shift up so base sits on ground
            pos.z += 1.2
            
            vert = bm.verts.new(pos)
            row.append(vert)
        
        verts.append(row)
    
    # Create faces
    for i in range(u_steps):
        for j in range(v_steps):
            v1 = verts[i][j]
            v2 = verts[(i + 1) % u_steps][j]
            v3 = verts[(i + 1) % u_steps][(j + 1) % v_steps]
            v4 = verts[i][(j + 1) % v_steps]
            
            try:
                bm.faces.new([v1, v2, v3, v4])
            except:
                pass
    
    bm.to_mesh(mesh)
    bm.free()
    
    # Smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True
    
    # Subdivision for glass-smooth surface
    mod = obj.modifiers.new("Subsurf", 'SUBSURF')
    mod.levels = 3
    mod.render_levels = 4
    
    # Solidify for glass thickness
    solid = obj.modifiers.new("Solidify", 'SOLIDIFY')
    solid.thickness = 0.012
    solid.offset = 0
    
    return obj


def create_glass_material():
    """Pure glass material - crystal clear"""
    mat = bpy.data.materials.new("Glass")
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    glass = nodes.new('ShaderNodeBsdfGlass')
    
    output.location = (200, 0)
    glass.location = (0, 0)
    
    glass.inputs['IOR'].default_value = 1.45
    glass.inputs['Roughness'].default_value = 0.0
    
    links.new(glass.outputs['BSDF'], output.inputs['Surface'])
    
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'HASHED'
    
    return mat


def setup_scene():
    """White studio setup matching reference"""
    
    # Ground plane - white
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    
    mat_ground = bpy.data.materials.new("White")
    mat_ground.use_nodes = True
    bsdf = mat_ground.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    bsdf.inputs['Roughness'].default_value = 0.7
    
    ground.data.materials.append(mat_ground)
    
    # Lights - soft studio lighting
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    key = bpy.context.active_object
    key.data.energy = 500
    key.data.size = 8
    key.rotation_euler = (0.8, 0, 0.5)
    
    bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
    fill = bpy.context.active_object
    fill.data.energy = 200
    fill.data.size = 6
    
    bpy.ops.object.light_add(type='AREA', location=(0, 3, 3))
    rim = bpy.context.active_object
    rim.data.energy = 300
    rim.data.size = 5
    
    # Camera
    bpy.ops.object.camera_add(location=(3, -3, 2))
    cam = bpy.context.active_object
    
    direction = Vector((0, 0, 0.8)) - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    
    bpy.context.scene.camera = cam
    cam.data.lens = 85
    
    # World - light gray background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.92, 0.92, 0.92, 1)
    bg.inputs['Strength'].default_value = 1.0
    
    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256
    scene.cycles.max_bounces = 12
    scene.cycles.transmission_bounces = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1920


# Generate
print("Creating Klein bottle glass sculpture...")
klein = create_klein_bottle_mesh(u_steps=200, v_steps=100)

print("Applying glass material...")
glass_mat = create_glass_material()
klein.data.materials.append(glass_mat)

print("Setting up studio scene...")
setup_scene()

print("\n✓ Complete! Glass Klein bottle sculpture ready to render.")
print("Cycles: 256 samples, 12 bounces for realistic glass")
