from pygame_gui.windows.ui_console_window import UIConsoleWindow

_debugClass: UIConsoleWindow = None


def setDebugClass(debugClass: UIConsoleWindow):
    global _debugClass  # pylint: disable=global-statement
    _debugClass = debugClass


def add_multiple_lines_to_log(lines: str):
    """Function to add multiple lines from a mutliline string to the log. 
    Automatically trims whitespace.

    Args:
        lines (str)
    """
    for line in lines.split("\n"):
        _debugClass.add_output_line_to_log(line.strip())


def add_output_line_to_log(line: str):
    """Function to add a line to the log.

    Args:
        line (str)
    """
    _debugClass.add_output_line_to_log(line)
