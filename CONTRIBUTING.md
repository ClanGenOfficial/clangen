# Contributing
Thank you for your interest in contributing to Clangen!

If you would like to contribute writing, art, or a major gameplay feature, please apply for a developer role on our [Discord](https://discord.gg/rnFQqyPZ7K). This is so that we can better coordinate the style and overall direction of the game.

For quality-of-life changes, bug fixes, minor enhancements (such as balance and customization), or any open issues, feel free to make a Pull Request. You do not have to be on the Discord or have a developer role on the Discord to submit a Pull Request.

## Installation
The following instructions assume that you have already [installed Python](https://www.python.org/downloads/), and the working directory in your terminal is `clangen`.

### Python
When using Python, a virtual environment is recommended in order to increase reliability and more closely resemble our build environment. Instructions for setting up a virtual environment can be found [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

After you have set up and activated your virtual environment, run:
```sh
python3 pip install -r requirements.txt
```
You may have to replace `python3` in the above command with `python` or `py` depending on your environment.

### With Poetry
Poetry is a tool used for Python dependency management and packaging. Poetry will automatically set up and manage your virtual environment for you. Installation instructions for Poetry can be found [here](https://python-poetry.org/docs/#installation).

To install requirements using Poetry:
```sh
poetry install
```

Then run using:
```sh
poetry run python main.py
```

## Issues
### Creating an issue
If you find a bug, please report it on our [issues page](https://github.com/ClanGenOfficial/clangen/issues).

### Solving an Issue
When solving an issue, please link it in your Pull Request.

If you do not know where to get started, check the [good first issue tag](https://github.com/ClanGenOfficial/clangen/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22). These issues have been marked as “good first issues” because they are non-urgent improvements that do not require a great familiarity with the larger codebase. Solving these issues is a great way to better understand the codebase.
