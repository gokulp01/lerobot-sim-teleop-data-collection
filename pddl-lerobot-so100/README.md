# PDDL LeRobot SO-100

This folder contains a minimal, simulator-integrated PDDL setup for the SO-100 arm. It includes one domain, multiple problems, and a plan executor that drives the MuJoCo simulator using the `gym_lowcostrobot` assets copied into this repo.

## Layout
- `gym_lowcostrobot/`: simulator package and assets (MuJoCo XML + meshes).
- `pddl/domain/lerobot-so100.pddl`: domain with `open-gripper`, `close-gripper`, and `go-to`.
- `pddl/problems/`: multiple problem instances for the same domain.
- `plans/`: sample plans that match the problems.
- `scripts/execute_plan.py`: runs a plan in the simulator.

## PDDL Modeling Notes
- Poses are declared as objects of type `pose`.
- Each pose has numeric coordinates defined in `:init` using fluents:
  `= (x pose-name)`, `= (y pose-name)`, `= (z pose-name)`.
- `go-to` requires `(adjacent from to)` so problems can enforce waypoint sequences.
- The executor looks up pose coordinates from the PDDL problem file and moves the end-effector to that (x, y, z).

## Run a Plan in the Simulator
```bash
python scripts/execute_plan.py \
  --problem pddl/problems/problem-waypoint-tour.pddl \
  --plan plans/waypoint-tour.plan \
  --render
```

Defaults use `ReachCube-v0` with `action_mode=joint` plus a lightweight IK step in the executor. You can adjust motion and gripper tuning with:
- `--step-size` (IK step scale), `--tolerance`, `--max-steps`
- `--gripper-open`, `--gripper-close`, `--settle-steps`
- `--ee-link` if the environment uses a different end-effector body name
- `--step-delay` to slow down motion for easier viewing, plus `--hold` or `--hold-seconds` to keep Viser open

If it renders too quickly, just add the --step-delay flag to slow it down. For example:
```bash
python pddl-lerobot-so100/scripts/execute_plan.py \
    --problem pddl-lerobot-so100/pddl/problems/problem-waypoint-tour.pddl \
    --plan pddl-lerobot-so100/plans/waypoint-tour.plan \
    --render --step-delay 0.02 --hold
```

## Using an External Planner
Any PDDL planner that outputs action lines like `(go-to so100 home staging)` will work. Save the plan to a `.plan` file and pass it to `scripts/execute_plan.py`.
