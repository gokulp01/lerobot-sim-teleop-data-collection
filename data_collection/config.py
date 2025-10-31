ENVIRONMENTS = {
    "1": ("LiftCube-v0", "Lift a cube above threshold height"),
    "2": ("ReachCube-v0", "Reach end-effector to cube position"),
    "3": ("PushCube-v0", "Push cube to target region"),
    "4": ("PushCubeLoop-v0", "Push cube between two target regions"),
    "5": ("PickPlaceCube-v0", "Pick cube and place at target"),
    "6": ("StackTwoCubes-v0", "Stack blue cube on top of red cube"),
}

JOINT_LIMITS_LOW = [-3.14159, -1.5708, -1.48353, -1.91986, -2.96706, -1.74533]
JOINT_LIMITS_HIGH = [3.14159, 1.22173, 1.74533, 1.91986, 2.96706, 0.0523599]

MAX_EPISODE_STEPS = 10000
CONTROL_RATE_HZ = 50
DEAD_ZONE_THRESHOLD = 0.15

