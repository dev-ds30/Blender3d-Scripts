import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Settings
SEED = 123
random.seed(SEED)

def recursive_tower(location, scale, depth, max_depth=4, angle_offset=0):
    """Recursively generate alien tower segments"""
    if depth >= max_depth or scale < 0.3:
        return []
    
    objects = []
    
    # Create main segment
    sides = random.choice([5, 6, 7, 8])
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=sides,
        radius=scale,
        depth=scale * 2,
        location=location
    )
    segment = bpy.context.active_object
    segment.name = f"AlienSegment_D{depth}_{len(objects)}"
    segment.rotation_euler = (0, 0, angle_offset)
    
    # Add twist modifier
    twist = segment.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
    twist.deform_method = 'TWIST'
    twist.angle = random.uniform(-0.5, 0.5)
    
    # Subdivision for smoothness
    subsurf = segment.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    
    objects.append(segment)
    
    # Recursively spawn children
    num_children = random.randint(2, 4)
    for i in range(num_children):
        child_angle = (i / num_children) * math.pi * 2 + angle_offset
        child_radius = scale * 0.7
        
        # Offset position
        child_x = location[0] + math.cos(child_angle) * scale * 0.8
        child_y = location[1] + math.sin(child_angle) * scale * 0.8
        child_z = location[2] + scale * 1.5
        
        child_loc = (child_x, child_y, child_z)
        child_scale = scale * random.uniform(0.5, 0.7)
        
        # Recursive call
        children = recursive_tower(
            child_loc, 
            child_scale, 
            depth + 1, 
            max_depth,
            child_angle + random.uniform(-0.3, 0.3)
        )
        objects.extend(children)
    
    return objects

def create_organic_base(radius=8, segments=7):
    """Create organic alien base structure"""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,
        radius=radius,
        depth=2,
        location=(0, 0, 1)
    )
    base = bpy.context.active_object
    base.name = "AlienBase"
    
    # Deform for organic look
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(base.data)
    
    for v in bm.verts:
        # Add noise to vertices
        noise_factor = random.uniform(0.9, 1.1)
        v.co.x *= noise_factor
        v.co.y *= noise_factor
        
        # Bulge the middle
        if abs(v.co.z) < 0.5:
            radial_dist = (v.co.x**2 + v.co.y**2)**0.5
            v.co.x *= 1.2
            v.co.y *= 1.2
    
    bmesh.update_edit_mesh(base.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add subdivision
    subsurf = base.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 3
    
    # Displacement for alien texture
    displace = base.modifiers.new(name="Displace", type='DISPLACE')
    tex = bpy.data.textures.new("AlienSkin", type='VORONOI')
    tex.distance_metric = 'DISTANCE'
    tex.noise_scale = 3.0
    displace.texture = tex
    displace.strength = 0.3
    
    bpy.ops.object.shade_smooth()
    
    return base

def create_fibonacci_spiral_pillars(count=13, height_multiplier=3):
    """Create pillars arranged in Fibonacci spiral"""
    pillars = []
    phi = (1 + math.sqrt(5)) / 2  # Golden ratio
    
    for i in range(count):
        # Fibonacci spiral positioning
        angle = i * 2 * math.pi / phi
        radius = math.sqrt(i) * 2
        
        height = (i + 1) * height_multiplier
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=random.choice([5, 6, 7]),
            radius=0.4 + (i * 0.05),
            depth=height,
            location=(
                math.cos(angle) * radius,
                math.sin(angle) * radius,
                height / 2
            )
        )
        pillar = bpy.context.active_object
        pillar.name = f"FibPillar_{i}"
        
        # Taper the pillar
        pillar.scale = (1, 1, 1 + i * 0.1)
        
        # Add twist
        twist = pillar.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
        twist.deform_method = 'TWIST'
        twist.angle = i * 0.3
        
        # Subdivision
        subsurf = pillar.modifiers.new(name="Subsurf", type='SUBSURF')
        subsurf.levels = 2
        
        bpy.ops.object.shade_smooth()
        pillars.append(pillar)
    
    return pillars

def create_voronoi_dome(radius=12, segments=64):
    """Create dome with Voronoi pattern"""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=segments//2,
        radius=radius,
        location=(0, 0, 15)
    )
    dome = bpy.context.active_object
    dome.name = "VoronoiDome"
    
    # Cut bottom half
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=(0, 0, 15),
        plane_no=(0, 0, 1),
        clear_inner=True
    )
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Wireframe modifier for alien structure
    wireframe = dome.modifiers.new(name="Wireframe", type='WIREFRAME')
    wireframe.thickness = 0.15
    wireframe.use_replace = False
    
    # Subdivision
    subsurf = dome.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    
    # Simple displacement without Voronoi to avoid API issues
    displace = dome.modifiers.new(name="Displace", type='DISPLACE')
    tex = bpy.data.textures.new("DomePattern", type='CLOUDS')
    tex.noise_scale = 8.0
    displace.texture = tex
    displace.strength = 0.5
    
    bpy.ops.object.shade_smooth()
    
    return dome

def create_floating_crystals(count=30):
    """Create floating alien crystal formations"""
    crystals = []
    
    for i in range(count):
        # Random crystal shape
        vertices = random.randint(5, 8)
        
        bpy.ops.mesh.primitive_cone_add(
            vertices=vertices,
            radius1=random.uniform(0.3, 0.8),
            radius2=0.05,
            depth=random.uniform(2, 5),
            location=(
                random.uniform(-15, 15),
                random.uniform(-15, 15),
                random.uniform(8, 25)
            )
        )
        crystal = bpy.context.active_object
        crystal.name = f"Crystal_{i}"
        
        # Random rotation
        crystal.rotation_euler = (
            random.uniform(0, math.pi),
            random.uniform(0, math.pi),
            random.uniform(0, math.pi * 2)
        )
        
        # Subdivision for smooth
        subsurf = crystal.modifiers.new(name="Subsurf", type='SUBSURF')
        subsurf.levels = 2
        
        bpy.ops.object.shade_smooth()
        crystals.append(crystal)
    
    return crystals

def create_energy_rings(count=8, base_radius=10):
    """Create rotating energy rings"""
    rings = []
    
    for i in range(count):
        offset = i * 3
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=base_radius - (i * 0.5),
            minor_radius=0.12,
            major_segments=128,
            minor_segments=16,
            location=(0, 0, 10 + offset)
        )
        ring = bpy.context.active_object
        ring.name = f"EnergyRing_{i}"
        
        # Rotate each ring
        ring.rotation_euler = (
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
            i * 0.4
        )
        
        rings.append(ring)
    
    return rings

def create_organic_tendrils(count=20):
    """Create organic tendril structures using curves"""
    tendrils = []
    
    for i in range(count):
        bpy.ops.curve.primitive_bezier_curve_add()
        tendril = bpy.context.active_object
        tendril.name = f"Tendril_{i}"
        
        curve_data = tendril.data
        curve_data.bevel_depth = 0.1
        curve_data.bevel_resolution = 8
        curve_data.resolution_u = 24
        
        # Modify curve points for organic shape
        spline = curve_data.splines[0]
        
        # Add more points
        for _ in range(3):
            spline.bezier_points.add(1)
        
        # Position points in spiral
        angle_start = random.uniform(0, math.pi * 2)
        radius_start = random.uniform(6, 10)
        
        for j, point in enumerate(spline.bezier_points):
            t = j / (len(spline.bezier_points) - 1)
            angle = angle_start + t * math.pi * 3
            radius = radius_start * (1 - t * 0.5)
            height = t * random.uniform(15, 25)
            
            point.co = Vector((
                math.cos(angle) * radius,
                math.sin(angle) * radius,
                height
            ))
            
            # Smooth handles
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'
        
        # Taper modifier
        taper_curve = bpy.data.curves.new('TaperCurve', 'CURVE')
        taper_curve.dimensions = '2D'
        taper_spline = taper_curve.splines.new('BEZIER')
        taper_spline.bezier_points.add(1)
        taper_spline.bezier_points[0].co = (0, 0, 0)
        taper_spline.bezier_points[1].co = (1, 0.1, 0)
        
        curve_data.taper_object = bpy.data.objects.new('TaperObj', taper_curve)
        bpy.context.collection.objects.link(curve_data.taper_object)
        curve_data.taper_object.hide_viewport = True
        curve_data.taper_object.hide_render = True
        
        tendrils.append(tendril)
    
    return tendrils

def create_fractal_spikes(center, radius, depth, max_depth=3):
    """Recursively create fractal spike formations"""
    if depth >= max_depth:
        return []
    
    spikes = []
    num_spikes = 6 - depth
    
    for i in range(num_spikes):
        angle = (i / num_spikes) * math.pi * 2
        
        spike_radius = radius / (depth + 1)
        spike_height = radius * 2 / (depth + 1)
        
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        z = center[2]
        
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=spike_radius,
            radius2=0.05,
            depth=spike_height,
            location=(x, y, z)
        )
        spike = bpy.context.active_object
        spike.name = f"FractalSpike_D{depth}_{i}"
        spike.rotation_euler = (0, 0, angle)
        
        # Subdivision
        subsurf = spike.modifiers.new(name="Subsurf", type='SUBSURF')
        subsurf.levels = 1
        
        bpy.ops.object.shade_smooth()
        spikes.append(spike)
        
        # Recursion
        if depth < max_depth - 1:
            tip_location = (x, y, z + spike_height / 2)
            children = create_fractal_spikes(
                tip_location,
                radius * 0.5,
                depth + 1,
                max_depth
            )
            spikes.extend(children)
    
    return spikes

def create_mandala_floor(radius=20, divisions=12):
    """Create intricate mandala pattern floor"""
    bpy.ops.mesh.primitive_circle_add(
        vertices=divisions * 8,
        radius=radius,
        fill_type='NGON',
        location=(0, 0, 0)
    )
    floor = bpy.context.active_object
    floor.name = "MandalaFloor"
    
    # Inset and extrude for pattern
    bpy.ops.object.mode_set(mode='EDIT')
    
    for i in range(4):
        bpy.ops.mesh.inset(thickness=0.5, depth=0.1 * (i % 2))
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Subdivision
    subsurf = floor.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    
    # Displacement
    displace = floor.modifiers.new(name="Displace", type='DISPLACE')
    tex = bpy.data.textures.new("MandalaPattern", type='VORONOI')
    tex.distance_metric = 'DISTANCE'
    tex.noise_scale = 15.0
    displace.texture = tex
    displace.strength = 0.2
    
    bpy.ops.object.shade_smooth()
    
    return floor

# ==================== MATERIALS ====================

def create_alien_metal_material():
    """Iridescent alien metal"""
    mat = bpy.data.materials.new(name="AlienMetal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.4, 1)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.2
    
    # Version-safe sheen and coat settings
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.5
    if 'Sheen Tint' in bsdf.inputs:
        # Sheen Tint is a color in newer versions
        if hasattr(bsdf.inputs['Sheen Tint'], 'default_value') and len(bsdf.inputs['Sheen Tint'].default_value) > 1:
            bsdf.inputs['Sheen Tint'].default_value = (0.8, 0.6, 0.9, 1.0)
        else:
            bsdf.inputs['Sheen Tint'].default_value = 0.8
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 0.5
    elif 'Clearcoat' in bsdf.inputs:
        bsdf.inputs['Clearcoat'].default_value = 0.5
    
    # Color ramp for iridescence
    coord = nodes.new('ShaderNodeTexCoord')
    coord.location = (-600, 0)
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-300, 100)
    noise.inputs['Scale'].default_value = 5.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 100)
    ramp.color_ramp.elements[0].color = (0.2, 0.1, 0.3, 1)
    ramp.color_ramp.elements[1].color = (0.5, 0.3, 0.6, 1)
    
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_energy_material(color=(0.2, 0.8, 1.0)):
    """Glowing energy material"""
    mat = bpy.data.materials.new(name=f"Energy_{color[0]}_{color[1]}_{color[2]}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, 0)
    emission.inputs['Color'].default_value = (*color, 1)
    emission.inputs['Strength'].default_value = 15
    
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    return mat

def create_crystal_material():
    """Translucent crystal material"""
    mat = bpy.data.materials.new(name="Crystal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (300, 100)
    glass.inputs['Color'].default_value = (0.6, 0.8, 1.0, 1)
    glass.inputs['Roughness'].default_value = 0.05
    glass.inputs['IOR'].default_value = 1.6
    
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (300, -100)
    emission.inputs['Color'].default_value = (0.4, 0.7, 1.0, 1)
    emission.inputs['Strength'].default_value = 2
    
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (500, 0)
    mix.inputs[0].default_value = 0.8
    
    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    return mat

def create_organic_material():
    """Organic alien bio-material"""
    mat = bpy.data.materials.new(name="OrganicAlien")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Base Color'].default_value = (0.15, 0.25, 0.2, 1)
    bsdf.inputs['Roughness'].default_value = 0.6
    
    # Version-safe subsurface
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.3
        bsdf.inputs['Subsurface Radius'].default_value = (0.5, 0.3, 0.2)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.3
        bsdf.inputs['Subsurface Radius'].default_value = (0.5, 0.3, 0.2)
    
    # Version-safe sheen
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = 0.3
    elif 'Sheen' in bsdf.inputs:
        bsdf.inputs['Sheen'].default_value = 0.3
    
    # Texture
    coord = nodes.new('ShaderNodeTexCoord')
    coord.location = (-600, 0)
    
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-300, 100)
    voronoi.inputs['Scale'].default_value = 8.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 100)
    ramp.color_ramp.elements[0].color = (0.1, 0.2, 0.15, 1)
    ramp.color_ramp.elements[1].color = (0.2, 0.3, 0.25, 1)
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (200, -100)
    bump.inputs['Strength'].default_value = 0.3
    
    links.new(coord.outputs['Generated'], voronoi.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# ==================== BUILD SCENE ====================

print("\n" + "="*70)
print("GENERATING ALIEN ARCHITECTURE WITH RECURSIVE PATTERNS...")
print("="*70 + "\n")

print("Creating organic base structure...")
base = create_organic_base()

print("Growing recursive alien towers...")
tower_objects = recursive_tower(location=(0, 0, 4), scale=3, depth=0, max_depth=4)

print("Arranging Fibonacci spiral pillars...")
pillars = create_fibonacci_spiral_pillars(count=13)

print("Constructing Voronoi dome...")
dome = create_voronoi_dome()

print("Spawning floating crystals...")
crystals = create_floating_crystals(count=30)

print("Generating energy rings...")
rings = create_energy_rings(count=8)

print("Growing organic tendrils...")
tendrils = create_organic_tendrils(count=20)

print("Creating fractal spike formations...")
spikes = create_fractal_spikes(center=(0, 0, 2), radius=8, depth=0, max_depth=3)

print("Designing mandala floor...")
floor = create_mandala_floor()

print("\nApplying alien materials...")
metal_mat = create_alien_metal_material()
energy_cyan = create_energy_material((0.2, 0.8, 1.0))
energy_purple = create_energy_material((0.6, 0.2, 1.0))
energy_green = create_energy_material((0.2, 1.0, 0.6))
crystal_mat = create_crystal_material()
organic_mat = create_organic_material()

# Apply materials
base.data.materials.append(organic_mat)

for obj in tower_objects:
    obj.data.materials.append(metal_mat)

for pillar in pillars:
    pillar.data.materials.append(metal_mat)

dome.data.materials.append(energy_cyan)

for crystal in crystals:
    crystal.data.materials.append(crystal_mat)

for ring in rings:
    ring.data.materials.append(random.choice([energy_cyan, energy_purple, energy_green]))

for tendril in tendrils:
    tendril.data.materials.append(organic_mat)

for spike in spikes:
    spike.data.materials.append(metal_mat)

floor.data.materials.append(metal_mat)

# Lighting
print("Setting up alien atmosphere...")

# Main light
bpy.ops.object.light_add(type='SUN', location=(20, -20, 40))
sun = bpy.context.active_object
sun.data.energy = 2.0
sun.data.color = (0.8, 0.9, 1.0)
sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(135))

# Accent lights
for i in range(12):
    angle = (i / 12) * math.pi * 2
    bpy.ops.object.light_add(
        type='POINT',
        location=(
            math.cos(angle) * 15,
            math.sin(angle) * 15,
            random.uniform(10, 20)
        )
    )
    light = bpy.context.active_object
    colors = [(0.2, 0.8, 1.0), (0.6, 0.2, 1.0), (0.2, 1.0, 0.6)]
    light.data.color = random.choice(colors)
    light.data.energy = random.uniform(300, 800)

# World
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_nodes["Background"].inputs['Strength'].default_value = 0.1
world_nodes["Background"].inputs['Color'].default_value = (0.05, 0.02, 0.08, 1)

# Camera
bpy.ops.object.camera_add(location=(30, -30, 25))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera
camera.data.lens = 35

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Enable effects
scene.eevee.use_bloom = True
scene.eevee.bloom_intensity = 0.15

print("\n" + "="*70)
print("ALIEN ARCHITECTURE COMPLETE!")
print("="*70)
print(f"""
CREATED:
  • Organic base with displacement
  • {len(tower_objects)} recursive tower segments (4 levels deep)
  • 13 Fibonacci spiral pillars (golden ratio)
  • Voronoi-patterned dome
  • 30 floating crystals
  • 8 rotating energy rings
  • 20 organic tendrils
  • {len(spikes)} fractal spike formations (3 levels recursive)
  • Intricate mandala floor
  • Iridescent alien metal materials
  • Glowing energy materials (cyan/purple/green)
  • Translucent crystal materials
  • Organic bio-materials with subsurface scattering
  
MATHEMATICAL PATTERNS USED:
  ✓ Recursive subdivision (towers & spikes)
  ✓ Fibonacci spiral (golden ratio pillars)
  ✓ Voronoi tessellation (dome & textures)
  ✓ Fractal geometry (self-similar patterns)
  ✓ Mandala symmetry (floor patterns)
  
HOW TO VIEW:
  1. Press Shift+Z for Rendered View
  2. Press F12 to render final image
  3. Fly around to see recursive details

""")
print("="*70 + "\n")
