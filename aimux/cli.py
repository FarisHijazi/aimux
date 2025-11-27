"""Main CLI entry point for aimux."""

import argparse
import re
import sys

from .cmd import (
    auto,
    broadcast,
    checkpoint,
    kill,
    ls,
    prompt,
    reset,
    run,
)

# Command aliases matching Go implementation
COMMAND_ALIASES = {
    "prompt": re.compile(r"^p(ro(mpt)?)?$"),
    "ls": re.compile(r"^l(s)?$"),
    "kill": re.compile(r"^k(ill)?$"),
    "reset": re.compile(r"^re(set)?$"),
    "checkpoint": re.compile(r"^c(heckpoint)?$"),
    "run": re.compile(r"^r(un)?$"),
    "auto": re.compile(r"^a(uto)?$"),
    "broadcast": re.compile(r"^b(roadcast)?$"),
}


def resolve_alias(cmd: str) -> str:
    """Resolve command aliases to full command names."""
    for real_cmd, pattern in COMMAND_ALIASES.items():
        if pattern.match(cmd):
            return real_cmd
    return cmd


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="aimux",
        description="AI coding agent orchestration tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Prompt command
    prompt_parser = subparsers.add_parser(
        "prompt", aliases=["p"], help="Create new agent sessions"
    )
    prompt_parser.add_argument(
        "--agents", default="claude:1", help="Agents to run (e.g., claude:2,codex:1)"
    )
    prompt_parser.add_argument("--config", default=None, help="Path to config file")
    prompt_parser.add_argument(
        "-m",
        "--init-method",
        choices=["worktree", "copy", "clone"],
        default=None,
        help="Project initialization method: 'worktree' (git worktree), 'copy' (hard copy), or 'clone' (from URL)",
    )
    prompt_parser.add_argument(
        "-u",
        "--url",
        default=None,
        help="Repository URL (implies --init-method=clone if not specified)",
    )
    # Legacy flags for backward compatibility
    prompt_parser.add_argument(
        "--no-worktree",
        action="store_true",
        help="[DEPRECATED] Use --init-method=copy instead",
    )
    prompt_parser.add_argument(
        "--clone",
        dest="clone_url",
        default=None,
        help="[DEPRECATED] Use --init-method=clone --url=URL instead",
    )
    prompt_parser.add_argument("prompt", nargs="+", help="Prompt text")

    # Ls command
    ls_parser = subparsers.add_parser(
        "ls", aliases=["l"], help="List active agent sessions"
    )
    ls_parser.add_argument(
        "-w", "--watch", action="store_true", help="Watch mode - refresh every second"
    )
    ls_parser.add_argument(
        "-a", "--all", action="store_true", help="Show all sessions including inactive"
    )

    # Kill command
    kill_parser = subparsers.add_parser(
        "kill", aliases=["k"], help="Kill agent sessions"
    )
    kill_parser.add_argument("agent", help='Agent name or "all"')

    # Auto command
    auto_parser = subparsers.add_parser(
        "auto", aliases=["a"], help="Auto-manage agent sessions"
    )

    # Broadcast command
    broadcast_parser = subparsers.add_parser(
        "broadcast", aliases=["b"], help="Broadcast message to all agents"
    )
    broadcast_parser.add_argument("message", nargs="+", help="Message to broadcast")

    # Checkpoint command
    checkpoint_parser = subparsers.add_parser(
        "checkpoint", aliases=["c"], help="Checkpoint agent changes"
    )
    checkpoint_parser.add_argument("agent", help="Agent name")
    checkpoint_parser.add_argument("message", help="Commit message")

    # Run command
    run_parser = subparsers.add_parser(
        "run", aliases=["r"], help="Run command in all sessions"
    )
    run_parser.add_argument(
        "--delete", action="store_true", help="Delete window after running"
    )
    run_parser.add_argument("run_command", nargs="+", help="Command to run")

    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Delete all aimux data")

    # Handle alias resolution manually for compatibility
    if len(sys.argv) > 1:
        resolved_cmd = resolve_alias(sys.argv[1])
        if resolved_cmd != sys.argv[1]:
            sys.argv[1] = resolved_cmd

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Route to appropriate command
        if args.command in ["prompt", "p"]:
            prompt_text = " ".join(args.prompt)
            prompt.execute_prompt(
                prompt_text,
                args.agents,
                args.config,
                init_method=args.init_method,
                url=args.url,
                no_worktree=args.no_worktree,
                clone_url=args.clone_url,
            )

        elif args.command in ["ls", "l"]:
            ls.execute_ls(watch=args.watch)

        elif args.command in ["kill", "k"]:
            kill.execute_kill(args.agent)

        elif args.command in ["auto", "a"]:
            auto.execute_auto()

        elif args.command in ["broadcast", "b"]:
            message = " ".join(args.message)
            broadcast.execute_broadcast(message)

        elif args.command in ["checkpoint", "c"]:
            checkpoint.execute_checkpoint(args.agent, args.message)

        elif args.command in ["run", "r"]:
            command_text = " ".join(args.run_command)
            run.execute_run(command_text, delete=args.delete)

        elif args.command == "reset":
            reset.execute_reset()

        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    except Exception as e:
        print(f"aimux: error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
