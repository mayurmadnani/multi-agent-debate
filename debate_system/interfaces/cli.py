"""Command-line interface for the debate system."""
from __future__ import annotations

import argparse
from typing import Dict

from colorama import Fore, Style, init

from ..core import build_orchestrator, ConfigManager
from ..utils.logger import setup_logging

init(autoreset=True)


def _display_result(result: Dict[str, object]) -> None:
    if result.get("error"):
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return

    print(f"\n{Fore.BLUE}=== Debate ==={Style.RESET_ALL}\n")
    for entry in result.get("history", []):
        speaker = entry.get("speaker", "Agent")
        content = entry.get("content", "")
        color = Fore.CYAN
        if str(speaker).lower() == "plato":
            color = Fore.GREEN
        elif str(speaker).lower() == "aristotle":
            color = Fore.YELLOW
        elif str(speaker).lower() == "summary":
            color = Fore.MAGENTA
        print(f"{color}[{speaker}]{Style.RESET_ALL}\n{content}\n")

    summary = result.get("summary")
    if summary:
        print(f"{Fore.MAGENTA}=== Summary ==={Style.RESET_ALL}\n{summary}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent philosophical debate")
    parser.add_argument("question", nargs="?", help="Question to debate")
    parser.add_argument("-r", "--rounds", type=int, default=None, help="Number of rounds")
    parser.add_argument("-c", "--config", default="configs/settings.yaml", help="Settings file path")
    parser.add_argument("-p", "--personas", default="configs/personas.yaml", help="Personas file path")
    parser.add_argument("-t", "--tools", default="configs/tools.yaml", help="Tools file path")
    args = parser.parse_args()

    config_manager = ConfigManager(
        settings_path=args.config,
        personas_path=args.personas,
        tools_path=args.tools,
    )
    setup_logging(config_manager.get_logging_config())
    orchestrator = build_orchestrator(config_manager=config_manager)

    if args.question:
        result = orchestrator.run_debate(args.question, rounds=args.rounds)
        _display_result(result)
    else:
        print("Enter a question to start. Type 'quit' to exit.\n")
        while True:
            try:
                prompt = input("Question: ").strip()
                if prompt.lower() in {"quit", "exit"}:
                    break
                if not prompt:
                    continue
                result = orchestrator.run_debate(prompt, rounds=args.rounds)
                _display_result(result)
            except KeyboardInterrupt:
                print("\nExiting...")
                break


if __name__ == "__main__":  # pragma: no cover
    main()
