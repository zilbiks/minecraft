import math
from collections import Counter
from typing import Any, Dict, List, Tuple


def is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def normalize_for_counter(v: Any) -> Any:
    if isinstance(v, (list, tuple)):
        return tuple(normalize_for_counter(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, normalize_for_counter(val)) for k, val in v.items()))
    if isinstance(v, set):
        return frozenset(normalize_for_counter(x) for x in v)
    return v


def values_equal(expected: Any, got: Any, unordered_output: bool) -> bool:
    if unordered_output and isinstance(expected, (list, tuple)) and isinstance(got, (list, tuple)):
        exp_counter = Counter(normalize_for_counter(x) for x in expected)
        got_counter = Counter(normalize_for_counter(x) for x in got)
        return exp_counter == got_counter

    if isinstance(expected, (list, tuple)) and isinstance(got, (list, tuple)):
        return list(expected) == list(got)

    if is_number(expected) and is_number(got):
        if math.isnan(expected) and math.isnan(got):
            return True
        if math.isfinite(expected) and math.isfinite(got):
            tol = 1e-9
            return abs(expected - got) <= tol * max(1.0, abs(expected), abs(got))

    return got == expected


def run_tests(
    user_code: str,
    tests: List[Tuple[Tuple[Any, ...], Any]],
    unordered_output: bool = False,
) -> Tuple[bool, str, List[Dict[str, Any]]]:
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
        "enumerate": enumerate,
        "zip": zip,
        "map": map,
        "filter": filter,
        "bool": bool,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "__build_class__": __build_class__,
        "object": object,
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
        "IndexError": IndexError,
        "KeyError": KeyError,
    }

    safe_globals: Dict[str, Any] = {"__builtins__": safe_builtins, "__name__": "__main__"}
    try:
        exec(user_code, safe_globals, safe_globals)
    except Exception as e:
        return False, f"kluda koda (exec): {e}", []

    solution_fn = safe_globals.get("solution")
    if not callable(solution_fn):
        return False, "netika atrasta funkcija `solution`", []

    failed: List[Dict[str, Any]] = []
    for test_input, expected in tests:
        try:
            got = solution_fn(*test_input)
        except Exception as e:
            failed.append(
                {
                    "input": test_input,
                    "expected": expected,
                    "got": None,
                    "error": f"Iznemums: {type(e).__name__}: {e}",
                }
            )
            continue

        if not values_equal(expected=expected, got=got, unordered_output=unordered_output):
            failed.append(
                {
                    "input": test_input,
                    "expected": expected,
                    "got": got,
                }
            )

    if failed:
        return False, "dazi testi neizdevas", failed
    return True, "visi testi ir izieti veiksmigi", []
