import bpy
import math

# Configuration
ANIMATION_FRAMES = 300
SUN_SIZE = 3.0
PLANETS = [
    # (name, radius, orbit_distance, orbit_speed, color)
    ("Mercury", 0.3, 6, 4.0, (0.7, 0.7, 0.7, 1.0)),
    ("Venus", 0.5, 8, 3.5, (0.9, 0.7, 0.4, 1.0)),
    ("Earth", 0.55, 10, 3.0, (0.2, 0.4, 0.8, 1.0)),
    ("Mars", 0.4, 12, 2.5, (0.8, 0.3, 0.2, 1.0)),
    ("Jupiter", 1.5, 16, 1.5, (0.8, 0.6, 0.4, 1.0)),
    ("Saturn", 1.3, 20, 1.2, (0.9, 0.8, 0.6, 1.0)),
]

def clear_scene():
    """Remove all existing objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_material(name, color):
    """Create a material with emission"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create emission shader
    output = nodes.new(type='ShaderNodeOutputMaterial')
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Color'].default_value = color
    emission.inputs['Strength'].default_value = 2.0
    
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    return mat

def create_sun():
    """Create the sun at the center"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=SUN_SIZE, location=(0, 0, 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    
    # Create glowing sun material
    mat = create_material("Sun_Material", (1.0, 0.9, 0.3, 1.0))
    mat.node_tree.nodes['Emission'].inputs['Strength'].default_value = 5.0
    sun.data.materials.append(mat)
    
    return sun

def create_planet(name, radius, orbit_distance, color):
    """Create a planet"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(orbit_distance, 0, 0))
    planet = bpy.context.active_object
    planet.name = name
    
    # Create material
    mat = create_material(f"{name}_Material", color)
    mat.node_tree.nodes['Emission'].inputs['Strength'].default_value = 1.0
    planet.data.materials.append(mat)
    
    return planet

def animate_orbit(planet, orbit_distance, orbit_speed, frames):
    """Animate planet orbiting around origin"""
    for frame in range(1, frames + 1):
        angle = (frame / frames) * orbit_speed * 2 * math.pi
        x = math.cos(angle) * orbit_distance
        y = math.sin(angle) * orbit_distance
        
        planet.location = (x, y, 0)
        planet.keyframe_insert(data_path="location", frame=frame)
        
        # Add rotation
        planet.rotation_euler.z = angle
        planet.keyframe_insert(data_path="rotation_euler", frame=frame, index=2)

def create_orbit_path(orbit_distance, segments=64):
    """Create a visual orbit path (circle)"""
    curve = bpy.data.curves.new(name="OrbitPath", type='CURVE')
    curve.dimensions = '3D'
    
    spline = curve.splines.new(type='NURBS')
    spline.points.add(segments)
    
    for i, point in enumerate(spline.points):
        angle = (i / segments) * 2 * math.pi
        x = math.cos(angle) * orbit_distance
        y = math.sin(angle) * orbit_distance
        point.co = (x, y, 0, 1)
    
    spline.use_cyclic_u = True
    
    # Create object from curve
    obj = bpy.data.objects.new("OrbitPath", curve)
    bpy.context.collection.objects.link(obj)
    
    # Style the curve
    curve.bevel_depth = 0.02
    mat = bpy.data.materials.new(name="Orbit_Material")
    mat.diffuse_color = (0.3, 0.3, 0.3, 0.3)
    obj.data.materials.append(mat)
    
    return obj

def setup_camera():
    """Set up camera for good view"""
    bpy.ops.object.camera_add(location=(0, -35, 20))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(50), 0, 0)
    bpy.context.scene.camera = camera
    return camera

def setup_lighting():
    """Add ambient lighting"""
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    light = bpy.context.active_object
    light.data.energy = 0.5

def main():
    print("Creating Solar System Animation...")
    
    # Clear existing scene
    clear_scene()
    
    # Set frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = ANIMATION_FRAMES
    
    # Create sun
    sun = create_sun()
    print(f"Created {sun.name}")
    
    # Create planets and animate them
    for planet_data in PLANETS:
        name, radius, orbit_dist, orbit_speed, color = planet_data
        
        # Create orbit path
        create_orbit_path(orbit_dist)
        
        # Create planet
        planet = create_planet(name, radius, orbit_dist, color)
        
        # Animate orbit
        animate_orbit(planet, orbit_dist, orbit_speed, ANIMATION_FRAMES)
        
        print(f"Created and animated {name}")
    
    # Setup camera and lighting
    setup_camera()
    setup_lighting()
    
    # Set viewport shading to rendered for better preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
    
    print(f"\n✓ Solar System created successfully!")
    print(f"✓ {len(PLANETS)} planets orbiting the sun")
    print(f"✓ Animation: {ANIMATION_FRAMES} frames")
    print(f"\nPress SPACEBAR to play the animation!")

# Run the script
if __name__ == "__main__":
    main()
