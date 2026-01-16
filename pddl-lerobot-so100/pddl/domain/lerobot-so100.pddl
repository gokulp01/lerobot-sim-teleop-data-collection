(define (domain lerobot-so100)
  (:requirements :typing :strips :fluents)
  (:types robot gripper pose)

  (:predicates
    (at ?r - robot ?p - pose)
    (adjacent ?from - pose ?to - pose)
    (gripper-open ?g - gripper)
    (gripper-closed ?g - gripper)
    (enabled ?r - robot)
  )

  (:functions
    (x ?p - pose)
    (y ?p - pose)
    (z ?p - pose)
  )

  (:action open-gripper
    :parameters (?g - gripper)
    :precondition (gripper-closed ?g)
    :effect (and (gripper-open ?g) (not (gripper-closed ?g)))
  )

  (:action close-gripper
    :parameters (?g - gripper)
    :precondition (gripper-open ?g)
    :effect (and (gripper-closed ?g) (not (gripper-open ?g)))
  )

  (:action go-to
    :parameters (?r - robot ?from - pose ?to - pose)
    :precondition (and (enabled ?r) (at ?r ?from) (adjacent ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )
)
