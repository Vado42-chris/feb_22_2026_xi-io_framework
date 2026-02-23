"""Terminal color + panel helpers."""

from __future__ import annotations


class Colors:
    RESET = "\033[0m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"


class TerminalUI:
    @staticmethod
    def clear() -> None:
        print("\033c", end="")

    @staticmethod
    def banner() -> None:
        print(f"{Colors.CYAN}XI-IO CLI{Colors.RESET}")

    @staticmethod
    def print_panel(text: str, title: str = "", color: str = Colors.CYAN) -> None:
        if title:
            print(f"{color}== {title} =={Colors.RESET}")
        print(text)

    @staticmethod
    def status(message: str, level: str = "OK") -> None:
        palette = {"OK": Colors.GREEN, "WARN": Colors.YELLOW, "ERR": Colors.RED}
        color = palette.get(level, Colors.CYAN)
        print(f"{color}[{level}] {message}{Colors.RESET}")
