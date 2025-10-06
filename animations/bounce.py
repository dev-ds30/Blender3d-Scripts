import bpy
import math

# Configuration
ANIMATION_LENGTH = 120  # frames
FPS = 24

# Set scene frame rate and range
bpy.context.scene.render.fps = FPS
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = ANIMATION_LENGTH

# Get the active object (make sure your character is selected)
char = bpy.context.active_object

if char is None:
    print("No object selected! Please select your character.")
else:
    # Clear existing animation data
    if char.animation_data:
        char.animation_data_clear()
    
    # Go to frame 1
    bpy.context.scene.frame_set(1)
    
    # === MAIN BODY BOUNCE ANIMATION ===
    # Starting position
    start_z = char.location.z
    char.location.z = start_z
    char.keyframe_insert(data_path="location", index=2, frame=1)
    
    # Bounce up
    char.location.z = start_z + 0.3
    char.keyframe_insert(data_path="location", index=2, frame=15)
    
    # Bounce down
    char.location.z = start_z - 0.1
    char.keyframe_insert(data_path="location", index=2, frame=30)
    
    # Return to start
    char.location.z = start_z
    char.keyframe_insert(data_path="location", index=2, frame=45)
    
    # Second bounce cycle
    char.location.z = start_z + 0.3
    char.keyframe_insert(data_path="location", index=2, frame=60)
    
    char.location.z = start_z - 0.1
    char.keyframe_insert(data_path="location", index=2, frame=75)
    
    char.location.z = start_z
    char.keyframe_insert(data_path="location", index=2, frame=90)
    
    # Final bounce
    char.location.z = start_z + 0.2
    char.keyframe_insert(data_path="location", index=2, frame=105)
    
    char.location.z = start_z
    char.keyframe_insert(data_path="location", index=2, frame=120)
    
    # === ROTATION ANIMATION ===
    # Full 360 rotation over the animation
    char.rotation_euler.z = 0
    char.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
    
    char.rotation_euler.z = math.radians(360)
    char.keyframe_insert(data_path="rotation_euler", index=2, frame=120)
    
    # === SLIGHT TILT ANIMATION ===
    # Subtle X-axis tilt for more life
    char.rotation_euler.x = 0
    char.keyframe_insert(data_path="rotation_euler", index=0, frame=1)
    
    char.rotation_euler.x = math.radians(5)
    char.keyframe_insert(data_path="rotation_euler", index=0, frame=30)
    
    char.rotation_euler.x = math.radians(-5)
    char.keyframe_insert(data_path="rotation_euler", index=0, frame=60)
    
    char.rotation_euler.x = math.radians(5)
    char.keyframe_insert(data_path="rotation_euler", index=0, frame=90)
    
    char.rotation_euler.x = 0
    char.keyframe_insert(data_path="rotation_euler", index=0, frame=120)
    
    # Set interpolation to bezier for smooth animation
    if char.animation_data and char.animation_data.action:
        for fcurve in char.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'
                # Make bounces more elastic
                if fcurve.data_path == "location":
                    keyframe.handle_left_type = 'AUTO_CLAMPED'
                    keyframe.handle_right_type = 'AUTO_CLAMPED'
    
    print(f"Animation created for {char.name}!")
    print(f"Duration: {ANIMATION_LENGTH} frames at {FPS} FPS")

# === OPTIONAL: HAIR BOUNCE ANIMATION ===
# If your hair pieces are separate objects, uncomment and modify this section
"""
hair_objects = ["Hair.L", "Hair.R"]  # Replace with your hair object names

for hair_name in hair_objects:
    if hair_name in bpy.data.objects:
        hair = bpy.data.objects[hair_name]
        
        # Clear existing animation
        if hair.animation_data:
            hair.animation_data_clear()
        
        bpy.context.scene.frame_set(1)
        
        # Hair lags behind main body movement
        hair.rotation_euler.y = 0
        hair.keyframe_insert(data_path="rotation_euler", index=1, frame=1)
        
        hair.rotation_euler.y = math.radians(-15)
        hair.keyframe_insert(data_path="rotation_euler", index=1, frame=20)
        
        hair.rotation_euler.y = math.radians(10)
        hair.keyframe_insert(data_path="rotation_euler", index=1, frame=40)
        
        hair.rotation_euler.y = math.radians(-15)
        hair.keyframe_insert(data_path="rotation_euler", index=1, frame=65)
        
        hair.rotation_euler.y = math.radians(10)
        hair.keyframe_insert(data_path="rotation_euler", index=1, frame=85)
        
        hair.rotation_euler.y = 0
        hair.keyframe_insert(data_path="rotation_euler", index=1, frame=120)
        
        # Set interpolation
        if hair.animation_data and hair.animation_data.action:
            for fcurve in hair.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'BEZIER'
                    keyframe.handle_left_type = 'AUTO_CLAMPED'
                    keyframe.handle_right_type = 'AUTO_CLAMPED'
        
        print(f"Hair animation created for {hair_name}!")
"""

print("\n=== Animation Setup Complete! ===")
print("Press SPACEBAR to preview the animation")
print("Adjust timing by scaling keyframes in the Graph Editor")
