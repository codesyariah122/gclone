# gclone

Lightweight GitHub private repository clone CLI for macOS.

`gclone` is a simple command-line tool built with Python that makes cloning private GitHub repositories easier without manually putting a Personal Access Token (PAT) into the Git URL.

## Features

* Clone private GitHub repositories
* Store GitHub credentials securely in macOS Keychain
* No GitHub CLI required
* No PAT in Git remote URLs
* No plaintext credential file
* Simple `owner/repository` syntax
* Automatically clone repositories into `~/Projects`
* Automatically open the cloned project in VS Code
* Built using Python standard library and native macOS tools

## Requirements

* macOS
* Python 3
* Git
* GitHub account with access to the repository
* GitHub Personal Access Token (PAT)

## Installation

Clone this repository:

```bash
git clone https://github.com/YOUR_USERNAME/gclone.git
cd gclone
```

Make the installer executable:

```bash
chmod +x install.sh
```

Run the installer:

```bash
./install.sh
```

Reload your shell:

```bash
source ~/.zshrc
```

Verify the installation:

```bash
which gclone
```

Expected:

```text
/Users/YOUR_USERNAME/.local/bin/gclone
```

Then:

```bash
gclone help
```

## Authentication

Before cloning a private repository, configure your GitHub credential:

```bash
gclone auth
```

You will be asked for:

```text
GitHub username:
GitHub Personal Access Token:
```

The PAT is entered securely and is not displayed in the terminal.

The credential is stored in the macOS Keychain.

Check authentication status:

```bash
gclone auth --status
```

Example:

```text
✓ GitHub credential ditemukan.
  Username : your-github-username
  Token    : ********
```

## Clone a Repository

The simplest way to clone a repository:

```bash
gclone owner/repository
```

Example:

```bash
gclone wanguntechno/fe-wangun-compro
```

The repository will be cloned into:

```text
~/Projects/fe-wangun-compro
```

After cloning, `gclone` displays:

* Repository location
* Current branch
* Git remote URL

It also offers to open the project automatically in VS Code.

## Explicit Clone Command

You can also use:

```bash
gclone clone owner/repository
```

Example:

```bash
gclone clone wanguntechno/fe-wangun-compro
```

## Custom Clone Directory

Specify a custom directory:

```bash
gclone clone owner/repository --dir ~/Work
```

Example:

```bash
gclone clone wanguntechno/fe-wangun-compro --dir ~/Work
```

## Open in VS Code

After cloning, `gclone` can automatically open the project using the `code` command.

Example:

```text
Buka project di VS Code? [Y/n]: Y
✓ VS Code dibuka.
```

Make sure the VS Code `code` command is available in your PATH.

Check:

```bash
which code
```

## Logout

Remove the stored GitHub credential from macOS Keychain:

```bash
gclone logout
```

Example:

```text
✓ Credential 'your-github-username' berhasil dihapus.
```

## Security

`gclone` is designed to avoid putting the GitHub PAT directly into the repository URL.

### Recommended

```text
https://github.com/owner/repository.git
```

### Not recommended

```text
https://<PERSONAL_ACCESS_TOKEN>@github.com/owner/repository.git
```

The Git remote created by `gclone` does not contain the PAT.

For example:

```bash
git remote -v
```

returns:

```text
origin  https://github.com/wanguntechno/fe-wangun-compro.git (fetch)
origin  https://github.com/wanguntechno/fe-wangun-compro.git (push)
```

The PAT is stored separately using macOS Keychain.

## Available Commands

```text
gclone owner/repository
gclone clone owner/repository
gclone clone owner/repository --dir ~/Projects
gclone auth
gclone auth --status
gclone logout
gclone help
```

## Project Structure

```text
gclone/
├── gclone.py
├── install.sh
└── README.md
```

### gclone.py

Main CLI application.

Responsible for:

* CLI commands
* Git clone
* GitHub credential handling
* macOS Keychain integration
* VS Code integration

### install.sh

Installation script that:

* Creates the local executable directory
* Installs `gclone`
* Creates the CLI launcher
* Adds `~/.local/bin` to the shell PATH

### README.md

Project documentation.

## How It Works

The basic workflow is:

```text
gclone owner/repository
          │
          ▼
   Read credential
   from Keychain
          │
          ▼
      Git clone
          │
          ▼
   Private GitHub
    repository
          │
          ▼
    ~/Projects/repo
          │
          ▼
      VS Code
```

The Git remote remains clean and does not contain the PAT.

## Roadmap

Planned improvements:

* GitHub credential verification
* Support GitHub repository URLs
* Clone specific branches
* `--no-code` option
* Repository access checking
* Recent repositories
* Open previously cloned repositories
* Git repository status
* Improved interactive CLI
* Modular project architecture

## License

MIT License.
