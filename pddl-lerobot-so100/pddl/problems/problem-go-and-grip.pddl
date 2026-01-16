(define (problem go-and-grip)
  (:domain lerobot-so100)
  (:objects
    so100 - robot
    main-gripper - gripper
    home pregrasp pickup - pose
  )
  (:init
    (enabled so100)
    (at so100 home)
    (gripper-open main-gripper)
    (adjacent home pregrasp)
    (adjacent pregrasp home)
    (adjacent pregrasp pickup)
    (adjacent pickup pregrasp)
    (= (x home) 0.0)
    (= (y home) 0.20)
    (= (z home) 0.12)
    (= (x pregrasp) 0.03)
    (= (y pregrasp) 0.22)
    (= (z pregrasp) 0.11)
    (= (x pickup) 0.06)
    (= (y pickup) 0.20)
    (= (z pickup) 0.07)
  )
  (:goal (and (at so100 pickup) (gripper-closed main-gripper)))
)
