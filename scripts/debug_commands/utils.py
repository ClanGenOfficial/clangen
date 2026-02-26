_debugClass = None


def set_debug_class(debug_class):
    global _debugClass  # pylint: disable=global-statement
    _debugClass = debug_class


def add_multiple_lines_to_log(lines: str):
    """Function to add multiple lines from a mutliline string to the log.
    Automatically trims whitespace.

    Args:
        lines (str)
    """
    for line in lines.split("\n"):
        _debugClass.push_line(line.strip())


def add_output_line_to_log(line: str):
    """Function to add a line to the log.

    Args:
        line (str)
    """
    _debugClass.push_line(line)
