import bpy
import math

# Configuration
ANIMATION_LENGTH = 240  # frames (10 seconds at 24fps)
FPS = 24

# Set scene frame rate and range
bpy.context.scene.render.fps = FPS
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = ANIMATION_LENGTH

# Get the active object
char = bpy.context.active_object

if char is None:
    print("No object selected! Please select your character.")
else:
    # Clear existing animation data
    if char.animation_data:
        char.animation_data_clear()
    
    # Store starting position
    start_x = char.location.x
    start_y = char.location.y
    start_z = char.location.z
    
    # === ENERGETIC DANCE/SPIN SEQUENCE ===
    
    # Frame 1: Starting pose
    bpy.context.scene.frame_set(1)
    char.location = (start_x, start_y, start_z)
    char.rotation_euler = (0, 0, 0)
    char.scale = (1, 1, 1)
    char.keyframe_insert(data_path="location", frame=1)
    char.keyframe_insert(data_path="rotation_euler", frame=1)
    char.keyframe_insert(data_path="scale", frame=1)
    
    # Frame 20: Jump up and start spinning
    char.location.z = start_z + 0.8
    char.rotation_euler.z = math.radians(90)
    char.scale = (1.05, 0.95, 1.1)  # Squash and stretch
    char.keyframe_insert(data_path="location", frame=20)
    char.keyframe_insert(data_path="rotation_euler", frame=20)
    char.keyframe_insert(data_path="scale", frame=20)
    
    # Frame 35: Mid-air spin
    char.location.z = start_z + 1.2
    char.rotation_euler.z = math.radians(270)
    char.rotation_euler.x = math.radians(15)
    char.scale = (1, 1, 1)
    char.keyframe_insert(data_path="location", frame=35)
    char.keyframe_insert(data_path="rotation_euler", frame=35)
    char.keyframe_insert(data_path="scale", frame=35)
    
    # Frame 50: Complete spin, land with bounce
    char.location.z = start_z - 0.2
    char.rotation_euler.z = math.radians(360)
    char.rotation_euler.x = 0
    char.scale = (1.1, 1.1, 0.8)  # Landing squash
    char.keyframe_insert(data_path="location", frame=50)
    char.keyframe_insert(data_path="rotation_euler", frame=50)
    char.keyframe_insert(data_path="scale", frame=50)
    
    # Frame 60: Bounce back up
    char.location.z = start_z + 0.3
    char.scale = (0.95, 0.95, 1.05)
    char.keyframe_insert(data_path="location", frame=60)
    char.keyframe_insert(data_path="scale", frame=60)
    
    # Frame 70: Settle
    char.location.z = start_z
    char.scale = (1, 1, 1)
    char.keyframe_insert(data_path="location", frame=70)
    char.keyframe_insert(data_path="scale", frame=70)
    
    # === PLAYFUL WOBBLE SECTION ===
    
    # Frame 90: Lean left with rotation
    char.rotation_euler.z = math.radians(375)
    char.rotation_euler.y = math.radians(-20)
    char.location.x = start_x - 0.5
    char.keyframe_insert(data_path="rotation_euler", frame=90)
    char.keyframe_insert(data_path="location", frame=90)
    
    # Frame 110: Lean right
    char.rotation_euler.z = math.radians(390)
    char.rotation_euler.y = math.radians(20)
    char.location.x = start_x + 0.5
    char.keyframe_insert(data_path="rotation_euler", frame=110)
    char.keyframe_insert(data_path="location", frame=110)
    
    # Frame 130: Center with bounce
    char.rotation_euler.z = math.radians(360)
    char.rotation_euler.y = 0
    char.location.x = start_x
    char.location.z = start_z + 0.4
    char.keyframe_insert(data_path="rotation_euler", frame=130)
    char.keyframe_insert(data_path="location", frame=130)
    
    # === DOUBLE SPIN FINALE ===
    
    # Frame 150: Launch into double spin
    char.location.z = start_z + 1.5
    char.rotation_euler.z = math.radians(450)
    char.rotation_euler.x = math.radians(-30)
    char.scale = (0.95, 0.95, 1.1)
    char.keyframe_insert(data_path="location", frame=150)
    char.keyframe_insert(data_path="rotation_euler", frame=150)
    char.keyframe_insert(data_path="scale", frame=150)
    
    # Frame 170: Continue spinning
    char.location.z = start_z + 1.8
    char.rotation_euler.z = math.radians(630)
    char.rotation_euler.x = 0
    char.keyframe_insert(data_path="location", frame=170)
    char.keyframe_insert(data_path="rotation_euler", frame=170)
    
    # Frame 190: Finish spin at peak
    char.location.z = start_z + 1.5
    char.rotation_euler.z = math.radians(720)
    char.rotation_euler.x = math.radians(20)
    char.keyframe_insert(data_path="location", frame=190)
    char.keyframe_insert(data_path="rotation_euler", frame=190)
    
    # Frame 210: Dramatic landing
    char.location.z = start_z - 0.3
    char.rotation_euler.x = 0
    char.scale = (1.15, 1.15, 0.7)  # Big squash
    char.keyframe_insert(data_path="location", frame=210)
    char.keyframe_insert(data_path="rotation_euler", frame=210)
    char.keyframe_insert(data_path="scale", frame=210)
    
    # Frame 225: Final bounce
    char.location.z = start_z + 0.2
    char.scale = (0.95, 0.95, 1.05)
    char.keyframe_insert(data_path="location", frame=225)
    char.keyframe_insert(data_path="scale", frame=225)
    
    # Frame 240: Return to rest pose
    char.location = (start_x, start_y, start_z)
    char.rotation_euler = (0, 0, math.radians(720))
    char.scale = (1, 1, 1)
    char.keyframe_insert(data_path="location", frame=240)
    char.keyframe_insert(data_path="rotation_euler", frame=240)
    char.keyframe_insert(data_path="scale", frame=240)
    
    # Set interpolation for smooth, energetic movement
    if char.animation_data and char.animation_data.action:
        for fcurve in char.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'
                keyframe.handle_left_type = 'AUTO_CLAMPED'
                keyframe.handle_right_type = 'AUTO_CLAMPED'
    
    print(f"✨ Energetic dance animation created for {char.name}!")
    print(f"Duration: {ANIMATION_LENGTH} frames ({ANIMATION_LENGTH/FPS:.1f} seconds)")
    print("\nAnimation includes:")
    print("- Jump spin with mid-air rotation")
    print("- Squash and stretch dynamics")
    print("- Playful side-to-side wobble")
    print("- Epic double-spin finale")
    print("\n Press SPACEBAR to watch the magic! ✨")

# === CAMERA ANIMATION (OPTIONAL) ===
# Uncomment to add dynamic camera movement
"""
if "Camera" in bpy.data.objects:
    cam = bpy.data.objects["Camera"]
    
    if cam.animation_data:
        cam.animation_data_clear()
    
    # Camera circles around character
    radius = 8
    for frame in range(1, ANIMATION_LENGTH + 1, 20):
        angle = (frame / ANIMATION_LENGTH) * 2 * math.pi
        cam.location.x = start_x + radius * math.cos(angle)
        cam.location.y = start_y + radius * math.sin(angle)
        cam.location.z = start_z + 2
        cam.keyframe_insert(data_path="location", frame=frame)
        
        # Point camera at character
        direction = char.location - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        cam.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    print("Camera animation added!")
"""
