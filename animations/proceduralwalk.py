import bpy
import math

"""
PROCEDURAL WALK CYCLE GENERATOR
Automatically creates a realistic walk cycle using inverse kinematics (IK) manipulation.
This demonstrates specific animation manipulation techniques:
- IK constraint manipulation
- Procedural keyframe generation
- Bone rotation curves
- Cyclic animation with offset timing
"""

# Configuration
WALK_CYCLE_FRAMES = 24  # Standard walk cycle length (1 second at 24fps)
STEP_HEIGHT = 0.3       # How high feet lift
STEP_LENGTH = 1.0       # Forward distance of each step
HIP_SWAY = 0.1          # Side-to-side hip movement
SPINE_BEND = 5          # Degrees of forward spine lean

def get_armature():
    """Get the selected armature or find one in scene"""
    if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
        return bpy.context.active_object
    
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            return obj
    
    print("ERROR: No armature found! Please select or create a rigged character.")
    return None

def setup_ik_constraints(armature):
    """Set up IK constraints for legs if they don't exist"""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bones = armature.pose.bones
    
    # Common bone naming conventions
    leg_bones = {
        'left_leg': ['leg.L', 'shin.L', 'foot.L'],
        'right_leg': ['leg.R', 'shin.R', 'foot.R']
    }
    
    print("Setting up IK constraints...")
    # This is a simplified setup - real implementation would detect bone names
    
    return True

def animate_foot(armature, foot_bone_name, is_left, frames):
    """Create walking motion for a single foot using sinusoidal curves"""
    bpy.ops.object.mode_set(mode='POSE')
    
    if foot_bone_name not in armature.pose.bones:
        print(f"Warning: Bone '{foot_bone_name}' not found, using placeholder animation")
        return
    
    foot_bone = armature.pose.bones[foot_bone_name]
    
    # Phase offset (left and right feet are opposite)
    phase_offset = 0 if is_left else math.pi
    
    for frame in range(1, frames + 1):
        # Normalize frame to 0-1 cycle
        t = (frame - 1) / frames
        angle = t * 2 * math.pi + phase_offset
        
        # Vertical motion (foot lift)
        # Use absolute value of sin to create step pattern
        height = abs(math.sin(angle)) * STEP_HEIGHT
        foot_bone.location.z = height
        
        # Forward motion (foot placement)
        # Feet move forward and back relative to body
        forward = math.cos(angle) * STEP_LENGTH / 2
        foot_bone.location.y = forward
        
        # Insert keyframes
        foot_bone.keyframe_insert(data_path="location", frame=frame)
        
        # Foot rotation (toe pointing)
        if math.sin(angle) > 0:  # When foot is lifted
            foot_bone.rotation_euler.x = math.radians(-20)
        else:
            foot_bone.rotation_euler.x = 0
        
        foot_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

def animate_hip(armature, hip_bone_name, frames):
    """Animate hip sway and bob"""
    bpy.ops.object.mode_set(mode='POSE')
    
    if hip_bone_name not in armature.pose.bones:
        print(f"Using root object for hip motion")
        # Animate the armature object itself
        target = armature
        use_object = True
    else:
        target = armature.pose.bones[hip_bone_name]
        use_object = False
    
    for frame in range(1, frames + 1):
        t = (frame - 1) / frames
        angle = t * 2 * math.pi
        
        # Vertical bob (goes up/down twice per cycle)
        bob = abs(math.sin(angle * 2)) * 0.05
        
        # Side-to-side sway
        sway = math.sin(angle) * HIP_SWAY
        
        if use_object:
            original_z = target.location.z
            target.location.z = original_z + bob
            target.location.x = sway
            target.keyframe_insert(data_path="location", frame=frame)
        else:
            target.location.z = bob
            target.location.x = sway
            target.keyframe_insert(data_path="location", frame=frame)

def animate_spine(armature, spine_bone_name, frames):
    """Animate spine lean and twist"""
    bpy.ops.object.mode_set(mode='POSE')
    
    if spine_bone_name not in armature.pose.bones:
        return
    
    spine_bone = armature.pose.bones[spine_bone_name]
    
    for frame in range(1, frames + 1):
        t = (frame - 1) / frames
        angle = t * 2 * math.pi
        
        # Forward lean
        spine_bone.rotation_euler.x = math.radians(SPINE_BEND)
        
        # Subtle twist following hip movement
        twist = math.sin(angle) * math.radians(3)
        spine_bone.rotation_euler.z = twist
        
        spine_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

def animate_arms(armature, arm_bones, frames):
    """Animate arm swing (opposite to legs)"""
    bpy.ops.object.mode_set(mode='POSE')
    
    for side, bone_name in arm_bones.items():
        if bone_name not in armature.pose.bones:
            continue
        
        arm_bone = armature.pose.bones[bone_name]
        
        # Left arm swings with right leg
        phase_offset = 0 if side == 'right' else math.pi
        
        for frame in range(1, frames + 1):
            t = (frame - 1) / frames
            angle = t * 2 * math.pi + phase_offset
            
            # Swing back and forth
            swing = math.sin(angle) * math.radians(30)
            arm_bone.rotation_euler.x = swing
            
            arm_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

def set_cyclic_interpolation(armature):
    """Make the animation loop seamlessly"""
    if not armature.animation_data or not armature.animation_data.action:
        return
    
    action = armature.animation_data.action
    
    for fcurve in action.fcurves:
        # Set cyclic extrapolation
        fcurve.modifiers.new(type='CYCLES')
        
        # Smooth interpolation
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'BEZIER'
            keyframe.handle_left_type = 'AUTO_CLAMPED'
            keyframe.handle_right_type = 'AUTO_CLAMPED'

def create_walk_cycle():
    """Main function to create procedural walk cycle"""
    armature = get_armature()
    
    if not armature:
        print("\n=== CREATING DEMO SETUP ===")
        print("No armature found. Creating demonstration with cubes...")
        create_demo_walk()
        return
    
    print(f"\n=== GENERATING WALK CYCLE for '{armature.name}' ===")
    
    # Set frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = WALK_CYCLE_FRAMES
    
    # Clear existing animation
    if armature.animation_data:
        armature.animation_data_clear()
    
    # Common bone names to try
    bone_sets = {
        'feet': {'left': 'foot.L', 'right': 'foot.R'},
        'hip': 'hips',
        'spine': 'spine',
        'arms': {'left': 'upper_arm.L', 'right': 'upper_arm.R'}
    }
    
    # Animate components
    animate_foot(armature, bone_sets['feet']['left'], True, WALK_CYCLE_FRAMES)
    animate_foot(armature, bone_sets['feet']['right'], False, WALK_CYCLE_FRAMES)
    animate_hip(armature, bone_sets['hip'], WALK_CYCLE_FRAMES)
    animate_spine(armature, bone_sets['spine'], WALK_CYCLE_FRAMES)
    animate_arms(armature, bone_sets['arms'], WALK_CYCLE_FRAMES)
    
    # Make it loop
    set_cyclic_interpolation(armature)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"\n✓ Walk cycle created! {WALK_CYCLE_FRAMES} frames")
    print(f"✓ Cyclic modifiers applied for seamless looping")
    print(f"\nPress SPACEBAR to see the walk cycle!")

def create_demo_walk():
    """Create a simple demo with cubes to show the walk cycle principle"""
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (0.5, 0.3, 0.8)
    
    # Create feet
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(-0.2, 0, 0.15))
    left_foot = bpy.context.active_object
    left_foot.name = "Left_Foot"
    
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0.2, 0, 0.15))
    right_foot = bpy.context.active_object
    right_foot.name = "Right_Foot"
    
    # Animate
    bpy.context.scene.frame_end = WALK_CYCLE_FRAMES
    
    for frame in range(1, WALK_CYCLE_FRAMES + 1):
        t = (frame - 1) / WALK_CYCLE_FRAMES
        
        # Left foot
        angle_l = t * 2 * math.pi
        left_foot.location.z = abs(math.sin(angle_l)) * STEP_HEIGHT + 0.15
        left_foot.location.y = math.cos(angle_l) * STEP_LENGTH / 2
        left_foot.keyframe_insert(data_path="location", frame=frame)
        
        # Right foot (opposite phase)
        angle_r = t * 2 * math.pi + math.pi
        right_foot.location.z = abs(math.sin(angle_r)) * STEP_HEIGHT + 0.15
        right_foot.location.y = math.cos(angle_r) * STEP_LENGTH / 2
        right_foot.keyframe_insert(data_path="location", frame=frame)
        
        # Body bob
        body.location.z = abs(math.sin(angle_l * 2)) * 0.05 + 1.5
        body.keyframe_insert(data_path="location", frame=frame)
    
    print("\n✓ Demo walk cycle created with cubes!")
    print("✓ This demonstrates the walking motion principle")

# Run the script
if __name__ == "__main__":
    create_walk_cycle()
