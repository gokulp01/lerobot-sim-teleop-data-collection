(define (problem open-gripper)
  (:domain lerobot-so100)
  (:objects
    so100 - robot
    main-gripper - gripper
    home - pose
  )
  (:init
    (enabled so100)
    (at so100 home)
    (gripper-closed main-gripper)
    (= (x home) 0.0)
    (= (y home) 0.20)
    (= (z home) 0.12)
  )
  (:goal (gripper-open main-gripper))
)
