import bpy
import math

# Configuration
ANIMATION_DURATION = 120  # frames
ANIMATION_TYPE = "rotate"  # Options: "rotate", "bounce", "scale_pulse", "wave", "orbit"

def clear_animation():
    """Remove all existing animations"""
    for obj in bpy.data.objects:
        obj.animation_data_clear()

def animate_rotation(obj, duration):
    """Rotate object 360 degrees"""
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.rotation_euler = (0, 0, math.radians(360))
    obj.keyframe_insert(data_path="rotation_euler", frame=duration)
    
    # Set interpolation to linear
    if obj.animation_data:
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'

def animate_bounce(obj, duration):
    """Bounce object up and down"""
    original_z = obj.location.z
    obj.keyframe_insert(data_path="location", frame=1, index=2)
    obj.location.z = original_z + 2
    obj.keyframe_insert(data_path="location", frame=duration // 2)
    obj.location.z = original_z
    obj.keyframe_insert(data_path="location", frame=duration)

def animate_scale_pulse(obj, duration):
    """Pulse object scale"""
    original_scale = obj.scale.copy()
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.scale = (original_scale.x * 1.5, original_scale.y * 1.5, original_scale.z * 1.5)
    obj.keyframe_insert(data_path="scale", frame=duration // 2)
    obj.scale = original_scale
    obj.keyframe_insert(data_path="scale", frame=duration)

def animate_wave(obj, duration, index):
    """Wave motion with offset based on object index"""
    original_z = obj.location.z
    offset = index * 10  # Stagger the animation
    
    for frame in range(1, duration + 1, 5):
        phase = (frame + offset) / duration * math.pi * 4
        obj.location.z = original_z + math.sin(phase) * 1.5
        obj.keyframe_insert(data_path="location", frame=frame, index=2)

def animate_orbit(obj, duration, index):
    """Orbit around origin"""
    original_loc = obj.location.copy()
    radius = math.sqrt(original_loc.x**2 + original_loc.y**2)
    
    if radius < 0.1:
        radius = 3  # Default radius if at origin
    
    offset = (index * 60) % 360  # Offset each object's starting position
    
    for frame in range(1, duration + 1, 2):
        angle = (frame / duration * 360 + offset) * math.pi / 180
        obj.location.x = math.cos(angle) * radius
        obj.location.y = math.sin(angle) * radius
        obj.keyframe_insert(data_path="location", frame=frame, index=0)
        obj.keyframe_insert(data_path="location", frame=frame, index=1)

def main():
    # Clear existing animations
    clear_animation()
    
    # Set frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = ANIMATION_DURATION
    
    # Get all mesh objects (you can modify this to include other types)
    objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    
    if not objects:
        print("No mesh objects found in the scene!")
        return
    
    print(f"Animating {len(objects)} objects with '{ANIMATION_TYPE}' animation")
    
    # Apply animation to each object
    for i, obj in enumerate(objects):
        if ANIMATION_TYPE == "rotate":
            animate_rotation(obj, ANIMATION_DURATION)
        elif ANIMATION_TYPE == "bounce":
            animate_bounce(obj, ANIMATION_DURATION)
        elif ANIMATION_TYPE == "scale_pulse":
            animate_scale_pulse(obj, ANIMATION_DURATION)
        elif ANIMATION_TYPE == "wave":
            animate_wave(obj, ANIMATION_DURATION, i)
        elif ANIMATION_TYPE == "orbit":
            animate_orbit(obj, ANIMATION_DURATION, i)
    
    print(f"Animation complete! {len(objects)} objects animated.")
    print(f"Frame range: 1 to {ANIMATION_DURATION}")

# Run the script
if __name__ == "__main__":
    main()
