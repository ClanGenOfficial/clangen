# Contributing
Thank you for your interest in contributing to Clangen!

If you would like to contribute writing, art, or a major gameplay feature, please apply for a developer role on our [Discord](https://discord.gg/rnFQqyPZ7K). This is so that we can better coordinate the style and overall direction of the game.

For quality-of-life changes, bug fixes, minor enhancements (such as balance and customization), or any open issues, feel free to make a Pull Request. You do not have to be on the Discord or have a developer role on the Discord to submit a Pull Request.

**IF YOU ARE DOING A BUG FIX**: Before fixing the bug, please check if it also exists in the latest release branch. If it does, please branch off the release branch and target the release branch in your PR. You do not have to make another PR of the same bugfix to the development branch; the release branch is periodically merged back into development.

## Installation
> [!WARNING]
> Running the game via poetry is no longer supported. Please use uv instead.

> [!NOTE] 
> You no longer need to install Python on your system. uv will automatically install the correct version for you.

ClanGen now utilises a new tool called "uv" for Python dependency management and packaging. uv will automatically set up and manage your virtual environment for you. Installation instructions for uv can be found [here](https://docs.astral.sh/uv/getting-started/installation/).

To install requirements using uv:
```sh
uv sync
```

Then run using:
```sh
uv run main.py
```

For your convenience, a helper script has been included for the major platforms which automatically installs the dependencies and then executes the main script.
You can find it in the root directory as `run.bat` for Windows or `run.sh` for macOS, Linux and other compatible *nix systems.

## Issues
### Creating an issue
If you find a bug, please report it on our [issues page](https://github.com/ClanGenOfficial/clangen/issues).

### Solving an Issue
When solving an issue, please link it in your Pull Request.

If you do not know where to get started, check the [good first issue tag](https://github.com/ClanGenOfficial/clangen/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22). These issues have been marked as “good first issues” because they are non-urgent improvements that do not require a great familiarity with the larger codebase. Solving these issues is a great way to better understand the codebase.
