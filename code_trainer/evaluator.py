from typing import Any, Dict, List, Tuple


def get_starter_code(signature: str) -> str:
    return f"{signature}\n    # raksti savu kodu seit\n    pass\n"


def run_tests(user_code: str, tests: List[Tuple[Tuple[Any, ...], Any]]):
    safe_builtins = {
        "len": len,
        "max": max,
        "min": min,
        "sum": sum,
        "abs": abs,
        "range": range,
        "sorted": sorted,
        "all": all,
        "any": any,
        "bool": bool,
        "int": int,
        "float": float,
        "list": list,
    }
    safe_globals = {"__builtins__": safe_builtins}
    local_vars: Dict[str, Any] = {}

    try:
        exec(user_code, safe_globals, local_vars)
    except Exception as e:
        return False, f"koda kluda: {e}", []

    solution_fn = local_vars.get("solution") or safe_globals.get("solution")
    if not callable(solution_fn):
        return False, "funkcija solution nav atrasta vai nav callable.", []

    failed = []
    for test_input, expected in tests:
        try:
            got = solution_fn(*test_input)
            if got != expected:
                failed.append({"input": test_input, "expected": expected, "got": got})
        except Exception as e:
            failed.append({"input": test_input, "expected": expected, "got": f"iznemums: {e}"})

    if failed:
        return False, "ir kludas testos", failed

    return True, "visi random testi ir izieti", []
