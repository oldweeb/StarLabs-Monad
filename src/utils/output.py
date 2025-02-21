from termcolor import cprint
from pyfiglet import figlet_format
from colorama import init
import sys
import os


def show_logo():
    """Clears the console and displays the STAR LABS logo"""
    os.system("cls" if os.name == "nt" else "clear")
    init(strip=not sys.stdout.isatty())

    logo = figlet_format(
        "STARLABS", font="slant"
    )  # Using slant as it's closer to ANSI Shadow

    # Create a gradient-like effect with multiple blue shades
    gradient_lines = logo.split("\n")
    blue_shades = [
        "\033[38;2;65;105;225m",  # RoyalBlue
        "\033[38;2;30;144;255m",  # DodgerBlue
        "\033[38;2;0;191;255m",  # DeepSkyBlue
        "\033[38;2;135;206;235m",
    ]  # SkyBlue
    
    print()
    for i, line in enumerate(gradient_lines):
        shade = blue_shades[min(i % len(blue_shades), len(blue_shades) - 1)]
        print(f"{shade}{line}\033[0m")


def show_dev_info():
    """Displays development and version information"""
    info_box = [
        "╔════════════════════════════════════════╗",
        "║         StarLabs Monad 1.2             ║",
        "║----------------------------------------║",
        "║                                        ║",
        "║  GitHub: https://github.com/StarLabs   ║",
        "║                                        ║",
        "║  Developer: https://t.me/StarLabsTech  ║",
        "║  Chat: https://t.me/StarLabsChat       ║",
        "║                                        ║",
        "╚════════════════════════════════════════╝",
    ]

    # Light blue color for the info box
    blue_color = "\033[38;2;0;191;255m"  # DeepSkyBlue

    for line in info_box:
        print(f"{blue_color}{line}\033[0m")
    print()

