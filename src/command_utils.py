import subprocess
from typing import Optional

def run_command(command: str, verbose: bool = False) -> str:
    """
    Execute a shell command and return its output as a string.

    Args:
        command (str): The shell command to execute.
        verbose (bool): If True, print the command before execution.

    Returns:
        str: The command's output.

    Raises:
        subprocess.CalledProcessError: If the command execution fails.
    """
    try:
        if verbose:
            print(command)
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running command: {e}")
    return result.stdout
