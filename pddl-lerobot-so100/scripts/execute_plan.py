#!/usr/bin/env python
import argparse
import re
import sys
import time
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gymnasium as gym  # noqa: E402
import gym_lowcostrobot  # noqa: F401,E402


def tokenize_pddl(text):
    text = re.sub(r";.*", "", text)
    return re.findall(r"[()]|[^\s()]+", text.lower())


def parse_sexpr(tokens):
    if not tokens:
        raise ValueError("Unexpected end of tokens")
    token = tokens.pop(0)
    if token == "(":
        items = []
        while tokens:
            if tokens[0] == ")":
                tokens.pop(0)
                return items
            items.append(parse_sexpr(tokens))
        raise ValueError("Unclosed parenthesis in PDDL")
    return token


def parse_objects(tokens):
    objects = {}
    pending = []
    idx = 0
    while idx < len(tokens):
        tok = tokens[idx]
        if tok == "-":
            typ = tokens[idx + 1]
            for name in pending:
                objects[name] = typ
            pending = []
            idx += 2
        else:
            pending.append(tok)
            idx += 1
    for name in pending:
        objects[name] = "object"
    return objects


def parse_problem(path):
    text = Path(path).read_text()
    tokens = tokenize_pddl(text)
    tree = parse_sexpr(tokens)
    if not tree or tree[0] != "define":
        raise ValueError("Expected (define ...) in problem file")

    sections = {}
    for entry in tree[2:]:
        if isinstance(entry, list) and entry:
            sections[entry[0]] = entry[1:]

    objects = parse_objects(sections.get(":objects", []))
    init = sections.get(":init", [])

    pose_coords = {}
    initial_pose = None
    gripper_state = None

    for item in init:
        if not item:
            continue
        if item[0] == "=":
            func = item[1][0]
            pose = item[1][1]
            value = float(item[2])
            pose_coords.setdefault(pose, {})[func] = value
        elif item[0] == "at":
            initial_pose = item[2]
        elif item[0] == "gripper-open":
            gripper_state = "open"
        elif item[0] == "gripper-closed":
            gripper_state = "closed"

    return {
        "objects": objects,
        "pose_coords": pose_coords,
        "initial_pose": initial_pose,
        "gripper_state": gripper_state,
    }


def parse_plan(path):
    actions = []
    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue
        line = re.sub(r"^\s*\d+\s*:\s*", "", line)
        if "(" in line and ")" in line:
            line = line[line.find("(") : line.rfind(")") + 1]
        tokens = re.findall(r"[^\s()]+", line.lower())
        if not tokens:
            continue
        actions.append((tokens[0], tokens[1:]))
    return actions


def get_ee_pos(env, ee_link):
    ee_id = env.unwrapped.model.body(ee_link).id
    return env.unwrapped.data.xpos[ee_id].copy()


def ik_step(env, target, ee_link, step_size, regularization=1e-6, nullspace_weight=0.1):
    model = env.unwrapped.model
    data = env.unwrapped.data
    nb_dof = env.unwrapped.nb_dof
    arm_start = env.unwrapped.arm_dof_id

    body_id = model.body(ee_link).id
    ee_pos = data.xpos[body_id]

    jac = np.zeros((3, model.nv))
    mujoco.mj_jacBodyCom(model, data, jac, None, body_id)
    jac_arm = jac[:, arm_start : arm_start + nb_dof]

    delta_pos = target - ee_pos
    jac_reg = jac_arm.T @ jac_arm + regularization * np.eye(nb_dof)
    jac_pinv = np.linalg.inv(jac_reg) @ jac_arm.T
    qdot = jac_pinv @ delta_pos

    qpos = data.qpos[arm_start : arm_start + nb_dof]
    qdot += nullspace_weight * (-qpos)
    qdot_norm = np.linalg.norm(qdot)
    if qdot_norm > 1.0:
        qdot /= qdot_norm

    return qpos + qdot * step_size


def pose_xyz(pose_coords, pose_name):
    coords = pose_coords.get(pose_name)
    if not coords or any(axis not in coords for axis in ("x", "y", "z")):
        raise ValueError(f"Missing coordinates for pose '{pose_name}'")
    return np.array([coords["x"], coords["y"], coords["z"]], dtype=np.float32)


def move_to(env, target, gripper_value, step_size, tolerance, max_steps, ee_link, step_delay):
    for _ in range(max_steps):
        current = get_ee_pos(env, ee_link)
        dist = float(np.linalg.norm(target - current))
        if dist <= tolerance:
            return True
        qpos = ik_step(env, target, ee_link, step_size)
        qpos = qpos.copy()
        qpos[-1] = gripper_value
        env.step(qpos)
        if step_delay > 0.0:
            time.sleep(step_delay)
    return False


def set_gripper(env, gripper_value, settle_steps, step_delay):
    for _ in range(settle_steps):
        qpos = env.unwrapped.data.qpos[
            env.unwrapped.arm_dof_id : env.unwrapped.arm_dof_id + env.unwrapped.nb_dof
        ].copy()
        qpos[-1] = gripper_value
        env.step(qpos)
        if step_delay > 0.0:
            time.sleep(step_delay)


def execute_plan(env, plan, pose_coords, initial_pose, gripper_state, options):
    gripper_value = options.gripper_open if gripper_state != "closed" else options.gripper_close

    if initial_pose:
        target = pose_xyz(pose_coords, initial_pose)
        move_to(
            env,
            target,
            gripper_value,
            options.step_size,
            options.tolerance,
            options.max_steps,
            options.ee_link,
            options.step_delay,
        )

    for action, params in plan:
        if action == "open-gripper":
            gripper_state = "open"
            gripper_value = options.gripper_open
            set_gripper(env, gripper_value, options.settle_steps, options.step_delay)
        elif action == "close-gripper":
            gripper_state = "closed"
            gripper_value = options.gripper_close
            set_gripper(env, gripper_value, options.settle_steps, options.step_delay)
        elif action == "go-to":
            target_pose = params[-1]
            target = pose_xyz(pose_coords, target_pose)
            reached = move_to(
                env,
                target,
                gripper_value,
                options.step_size,
                options.tolerance,
                options.max_steps,
                options.ee_link,
                options.step_delay,
            )
            if not reached:
                raise RuntimeError(f"Failed to reach pose '{target_pose}' within max steps")
        else:
            raise ValueError(f"Unknown action '{action}' in plan")


def build_parser():
    parser = argparse.ArgumentParser(description="Execute a PDDL plan in the SO-100 simulator.")
    parser.add_argument("--problem", required=True, help="Path to PDDL problem file")
    parser.add_argument("--plan", required=True, help="Path to plan file")
    parser.add_argument("--env-id", default="ReachCube-v0", help="Gymnasium env id to run")
    parser.add_argument("--render", action="store_true", help="Render the MuJoCo viewer")
    parser.add_argument("--step-size", type=float, default=0.2, help="IK step size per simulator step")
    parser.add_argument("--tolerance", type=float, default=0.02, help="Goal tolerance in meters")
    parser.add_argument("--max-steps", type=int, default=200, help="Max simulator steps per go-to")
    parser.add_argument("--settle-steps", type=int, default=10, help="Steps to settle gripper open/close")
    parser.add_argument("--gripper-open", type=float, default=0.05, help="Command value for open gripper")
    parser.add_argument("--gripper-close", type=float, default=-1.0, help="Command value for close gripper")
    parser.add_argument("--ee-link", default="link_6", help="MuJoCo body name for the end effector")
    parser.add_argument("--step-delay", type=float, default=0.0, help="Seconds to sleep after each sim step")
    parser.add_argument("--hold", action="store_true", help="Keep the viewer open after plan completion")
    parser.add_argument(
        "--hold-seconds",
        type=float,
        default=0.0,
        help="Time to keep the viewer open after plan completion",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    problem = parse_problem(args.problem)
    plan = parse_plan(args.plan)

    render_mode = "human" if args.render else None
    env = gym.make(args.env_id, observation_mode="state", action_mode="joint", render_mode=render_mode)
    env.reset()

    try:
        execute_plan(
            env,
            plan,
            problem["pose_coords"],
            problem["initial_pose"],
            problem["gripper_state"],
            args,
        )
        if args.hold_seconds > 0:
            time.sleep(args.hold_seconds)
        elif args.hold:
            try:
                input("Plan complete. Press Enter to close the viewer...")
            except KeyboardInterrupt:
                pass
    finally:
        env.close()


if __name__ == "__main__":
    main()
