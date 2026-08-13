#!/usr/bin/env python3

import argparse
import getpass
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "gclone"
KEYCHAIN_SERVICE = "gclone-github"
DEFAULT_CLONE_DIR = Path.home() / "Projects"


# ============================================================
# Terminal
# ============================================================

class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"


def info(message):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")


def success(message):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def error(message):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")


# ============================================================
# System
# ============================================================

def check_command(command):
    if shutil.which(command) is None:
        error(f"Command '{command}' tidak ditemukan.")
        sys.exit(1)


def run_command(command, capture_output=False, env=None):
    return subprocess.run(
        command,
        capture_output=capture_output,
        text=True,
        env=env,
    )


# ============================================================
# Keychain
# ============================================================

def keychain_get(account):
    result = run_command(
        [
            "security",
            "find-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
            "-w",
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def keychain_set(account, value):
    # Hapus credential lama
    run_command(
        [
            "security",
            "delete-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
        ],
        capture_output=True,
    )

    result = run_command(
        [
            "security",
            "add-generic-password",
            "-U",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
            "-w",
            value,
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        error("Gagal menyimpan credential ke macOS Keychain.")
        sys.exit(1)


def keychain_delete(account):
    run_command(
        [
            "security",
            "delete-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
        ],
        capture_output=True,
    )


# ============================================================
# Authentication
# ============================================================

def get_github_username():
    return keychain_get("username")


def get_github_token():
    return keychain_get("token")


def auth_status():
    username = get_github_username()
    token = get_github_token()

    print()

    if username and token:
        success("GitHub credential ditemukan.")
        print(f"  Username : {username}")
        print("  Token    : ********")
    else:
        warning("GitHub credential belum tersedia.")

    print()


def authenticate():
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}🔐 GitHub Authentication{Colors.RESET}")
    print("────────────────────────────────────")
    print()

    current_username = get_github_username()

    if current_username:
        info(f"Credential saat ini: {current_username}")
        print()

        replace = input("Replace credential? [y/N]: ").strip().lower()

        if replace != "y":
            info("Authentication dibatalkan.")
            return

        print()

    username = input("GitHub username: ").strip()

    if not username:
        error("Username tidak boleh kosong.")
        sys.exit(1)

    token = getpass.getpass("GitHub Personal Access Token: ").strip()

    if not token:
        error("Token tidak boleh kosong.")
        sys.exit(1)

    print()
    info("Menyimpan credential ke macOS Keychain...")

    keychain_set("username", username)
    keychain_set("token", token)

    print()
    success("GitHub credential berhasil disimpan.")
    info("Credential disimpan di macOS Keychain.")
    info("PAT tidak disimpan di URL atau file plaintext.")
    print()


def logout():
    username = get_github_username()

    if not username:
        info("Tidak ada credential GitHub yang tersimpan.")
        return

    keychain_delete("username")
    keychain_delete("token")

    success(f"Credential '{username}' berhasil dihapus.")


# ============================================================
# Repository
# ============================================================

def validate_repository(repository):
    pattern = r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"

    if not re.match(pattern, repository):
        error("Format repository tidak valid.")
        print()
        print("Gunakan:")
        print("  owner/repository")
        print()
        print("Contoh:")
        print("  wanguntechno/fe-wangun-compro")
        sys.exit(1)


def parse_repository(repository):
    validate_repository(repository)

    owner, repo = repository.split("/", 1)

    return owner, repo


# ============================================================
# Clone
# ============================================================

def clone_repository(repository, destination=None):
    check_command("git")
    check_command("security")

    owner, repo_name = parse_repository(repository)

    username = get_github_username()
    token = get_github_token()

    if not username or not token:
        warning("GitHub credential belum tersedia.")
        print()

        authenticate()

        username = get_github_username()
        token = get_github_token()

    if destination:
        clone_dir = Path(destination).expanduser().resolve()
    else:
        clone_dir = DEFAULT_CLONE_DIR

    clone_dir.mkdir(parents=True, exist_ok=True)

    target_dir = clone_dir / repo_name

    if target_dir.exists():
        error(f"Directory sudah ada:")
        print(f"  {target_dir}")
        sys.exit(1)

    print()
    print(f"{Colors.CYAN}{Colors.BOLD}📦 Clone Repository{Colors.RESET}")
    print("────────────────────────────────────")
    print(f"  Repository : {repository}")
    print(f"  Account    : {username}")
    print(f"  Location   : {target_dir}")
    print()

    # Git menggunakan GIT_ASKPASS untuk mengambil credential.
    askpass_script = target_dir.parent / f".gclone-askpass-{os.getpid()}.sh"

    try:
        askpass_script.write_text(
            f"""#!/bin/sh

case "$1" in
    *Username*)
        printf '%s\\n' "$GCLONE_USERNAME"
        ;;
    *Password*)
        printf '%s\\n' "$GCLONE_TOKEN"
        ;;
    *)
        printf '%s\\n' "$GCLONE_TOKEN"
        ;;
esac
"""
        )

        askpass_script.chmod(0o700)

        env = os.environ.copy()

        env["GCLONE_USERNAME"] = username
        env["GCLONE_TOKEN"] = token

        env["GIT_ASKPASS"] = str(askpass_script)
        env["GIT_TERMINAL_PROMPT"] = "0"

        git_url = f"https://github.com/{owner}/{repo_name}.git"

        print("🚀 Cloning...")
        print()

        result = subprocess.run(
            [
                "git",
                "clone",
                git_url,
                str(target_dir),
            ],
            env=env,
        )

        if result.returncode != 0:
            print()
            error("Clone gagal.")
            print()
            warning("Periksa:")
            print("  • Repository benar")
            print("  • Token masih aktif")
            print("  • Token mempunyai akses ke repository")
            print("  • Account mempunyai akses ke repository")
            sys.exit(result.returncode)

        print()
        success("Repository berhasil di-clone.")
        print()
        print(f"📁 Location:")
        print(f"   {target_dir}")

        print()
        print("🌿 Branch:")

        branch_result = run_command(
            ["git", "-C", str(target_dir), "branch", "--show-current"],
            capture_output=True,
        )

        print(f"   {branch_result.stdout.strip()}")

        print()
        print("🔗 Remote:")

        remote_result = run_command(
            ["git", "-C", str(target_dir), "remote", "get-url", "origin"],
            capture_output=True,
        )

        print(f"   {remote_result.stdout.strip()}")

        print()

        open_project = input("Buka project di VS Code? [Y/n]: ").strip().lower()

        if open_project != "n":
            if shutil.which("code"):
                subprocess.Popen(
                    ["code", str(target_dir)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                success("VS Code dibuka.")
            else:
                warning("Command 'code' tidak ditemukan.")

    finally:
        if askpass_script.exists():
            askpass_script.unlink()


# ============================================================
# Help
# ============================================================

def show_banner():
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}gclone{Colors.RESET}")
    print("Lightweight GitHub Clone CLI")
    print()


def show_help():
    show_banner()

    print("Usage:")
    print()
    print("  gclone <owner/repository>")
    print("  gclone clone <owner/repository>")
    print("  gclone auth")
    print("  gclone auth --status")
    print("  gclone logout")
    print("  gclone help")
    print()
    print("Examples:")
    print()
    print("  gclone wanguntechno/fe-wangun-compro")
    print("  gclone clone wanguntechno/backend-api")
    print("  gclone auth")
    print("  gclone auth --status")
    print("  gclone logout")
    print()


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        prog="gclone",
        description="Lightweight GitHub private repository clone CLI.",
        add_help=False,
    )

    parser.add_argument("command", nargs="?")
    parser.add_argument("repository", nargs="?")
    parser.add_argument("--dir", dest="directory")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.help:
        show_help()
        return

    command = args.command

    if not command:
        show_help()
        return

    if command == "auth":
        if args.status:
            auth_status()
        else:
            authenticate()
        return

    if command == "logout":
        logout()
        return

    if command == "help":
        show_help()
        return

    if command == "clone":
        if not args.repository:
            error("Repository belum diberikan.")
            print()
            print("Contoh:")
            print("  gclone clone wanguntechno/fe-wangun-compro")
            sys.exit(1)

        clone_repository(
            args.repository,
            args.directory,
        )

        return

    # Shortcut:
    # gclone owner/repository

    clone_repository(
        command,
        args.directory,
    )


if __name__ == "__main__":
    main()