"""
Utility functions for scripts in this directory
"""

import subprocess


class commandOutput:
    def __init__(self, stdout: str, stderr: str, returncode: int):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


# Type hint the return type
def getCommandOutput(command: str) -> commandOutput:
    """
    Executes a command and returns the stdout
    """
    process = subprocess.run(command, shell=True, check=False, capture_output=True)
    return commandOutput(
        stdout=process.stdout.decode("utf-8"),
        stderr=process.stderr.decode("utf-8"),
        returncode=process.returncode,
    )
