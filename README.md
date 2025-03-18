# clangen

### [Discord Server](https://discord.gg/clangen) || [Official website](https://clangen.io) || [Itch.io Page](https://sablesteel.itch.io/clan-gen-fan-edit) 

## Description
Fan-edit of the warrior cat clangen game built using Python and Pygame.

## Credits
Original creator: just-some-cat.tumblr.com

Fan-edit creator: SableSteel, and many others

## Downloads
### Stable
Stable versions can be downloaded directly from the [official ClanGen website](https://clangen.io/download)

### Development
**Note**: Development versions are automatic snapshots of current development efforts. They are _not_ stable, can crash and even corrupt your save files.
Additionally, we do not provide tech support for development versions.

Download at your own risk here: [ClanGen development download](https://clangen.io/download-development)

## Running from source
ClanGen uses poetry to manage virtual environments. Therefore it is required to install the dependencies and run the game from source without manual tweaking.

### Installing python
ClanGen currently supports python versions >=3.8 and <3.13.

Download from the official python website here: https://www.python.org/downloads

Check if python is installed correctly by running `python3 --version`


### Installing poetry
Follow the instructions for installing poetry from the official website: https://python-poetry.org/docs/#installing-with-pipx

#### Linux, macOS, Windows (WSL)
Open a terminal and paste this:
```
python3 -m pip install pipx --user
python3 -m pipx install poetry
python3 -m pipx ensurepath
```
Then restart your terminal and check if poetry is installed by running `poetry --version`

#### Windows (Powershell)
Open a PowerShell window (Windows key and then enter `PowerShell`) and paste this:
```
py -m pip install pipx --user
py -m pipx install poetry
py -m pipx ensurepath
```
or in case you installed Python from the Windows Store:
```
python -m pip install pipx --user
python -m pipx install poetry
python -m pipx ensurepath
```
Then restart your terminal and check if poetry is installed by running `poetry --version`

### Running the game via the helper scripts
#### Linux, macOS
Double click the `run.sh` script or open it in the terminal via `./run.sh` with the current working directory set to the game's root directory.

#### Windows
Double click the `run.bat` script.

### Running the game via Visual Studio Code
To configure poetry to run with Visual Studio Code, open the ClanGen folder and run the following code snippet in the Visual Studio Code integrated terminal (Ctrl + ` to open the integrated terminal):
```
poetry config virtualenvs.in-project true
```

Now run the following command to create a virtual environment:
```
poetry install --no-root
```

It should have created a `.venv` folder in the root directory of the game.
If you don't see it, remove existing poetry virtual environments by running `poetry env remove python` and try again.

After that, ensure that you have the Python extension installed in Visual Studio Code. You can install it from the Extensions tab on the left sidebar. [(or click here)
](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

Then, open the Command Palette (Ctrl+Shift+P) and search for `Python: Select Interpreter`. Select the virtual environment created by poetry (it should mention a `.venv` somewhere).

Finally, open the `main.py` file and click the play button in the top right corner to run the game.


## Bug Reporting
We have migrated to GitHub Issues for bug reporting and tracking. We no longer review bug reports from the retired Google Form.

## Contributing
If you'd like to contribute to Clangen, please read our [Contributing guide](https://github.com/ClanGenOfficial/clangen/blob/development/CONTRIBUTING.md).
