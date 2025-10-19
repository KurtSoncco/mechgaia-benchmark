# utils/safe_runner.py
import traceback
import numpy as np
import math

def execute_code(code_string: str, controlled_scope: dict = None) -> dict:
    """
    Executes a string of Python code in a restricted scope and captures the output.

    Args:
        code_string: The Python code to execute.
        controlled_scope: An optional dictionary to serve as the global scope.

    Returns:
        A dictionary containing the execution status, the result, and any errors.
    """
    if controlled_scope is None:
        # Provide a controlled global scope with common math libraries
        controlled_scope = {
            "__builtins__": {
                "print": print, "range": range, "abs": abs, "round": round,
                "len": len, "min": min, "max": max, "sum": sum,
                "float": float, "int": int, "str": str, "list": list, "dict": dict,
                "open": None, "file": None  # Block file operations but allow __import__
            },
            # Safe libraries for engineering calculations
            "np": np,
            "numpy": np,
            "math": math,
            "pi": math.pi,
            "e": math.e
        }

    try:
        # Create a dictionary to capture local variables created by the exec'd code
        local_scope = {}
        exec(code_string, controlled_scope, local_scope)

        # Assume the agent assigns the final answer to a variable named 'result'
        result = local_scope.get("result", None)

        if result is None:
            return {
                "success": False,
                "result": None,
                "error": "Execution succeeded, but no 'result' variable was found."
            }

        return {"success": True, "result": result, "error": None}

    except Exception:
        # Capture the full traceback as a string for debugging
        error_message = traceback.format_exc()
        return {"success": False, "result": None, "error": error_message}