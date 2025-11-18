'''
conftest.py is a configuration file automatically accessed by pytest
any @pytest.fixture created here is available to any other test file
if they reference it as a parameter.
'''
# =======
# IMPORTS
# =======

import pytest, re, sys, os, json, traceback, pickle, inspect, multiprocessing, \
       ast, importlib, difflib, copy, builtins, sqlite3, csv,  types, site, sysconfig
from io import StringIO
from collections.abc import Iterable
from datetime import date, timedelta

# ====================
# LOCAL MODULE IMPORTS
# ====================

# makes sure the root of the directory is added to the path for when running tests
# through GitHub Actions.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Get the absolute path of the directory containing this script
current_dir = os.path.dirname(__file__)

# Construct the path to 'test_cases' and add it to sys.path
test_cases_path = os.path.join(current_dir, "test_cases")
sys.path.append(test_cases_path)

from class_test_cases import test_cases_classes_dict # type: ignore
from function_test_cases import test_cases_functions_dict # type: ignore

def load_env_file(path):
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            # skip comments and blank lines
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")  # remove wrapping quotes if present
            os.environ.setdefault(key, value)  # don't overwrite existing env

# ================
# GLOBAL VARIABLES
# ================
load_env_file(os.path.join(current_dir, ".env"))
# Enter the name of the file to be tested here, but leave out the .py file extention.
solution_module = os.getenv("SOLUTION_FILE")
student_module = os.getenv("STUDENT_FILE")
solution_module_2 = os.getenv("SOLUTION_FILE_2", "no file 2 found")
student_module_2  = os.getenv("STUDENT_FILE_2",  "no file 2 found")


def detect_module(solution_module, student_module):
    if os.path.exists(f"{solution_module}.py"):
        return solution_module
    elif os.path.exists(f"{student_module}.py"):
        return student_module
    else:
        return "PATH NOT FOUND"

default_module_to_test = detect_module(solution_module, student_module)
default_module_to_test_2 = detect_module(solution_module_2, student_module_2)

# default per-test-case timeout amount in seconds:
default_timeout_seconds = 10

# default decimal place to round to for regex comparisons
# helpful for accounting for different rounding methods students could use.
global_decimal_places = 2

# global that keeps track of exceptions raised within a subprocess.
raised_exceptions = []

# Path to the directory containing this file
CURRENT_DIR = os.path.dirname(__file__)

expected_database_name = r"movies.db"


# =============
# VERSION CHECK
# =============

# ANSI escape codes for colors
YELLOW_BOLD = "\033[1;33m"
RESET = "\033[0m"

def pytest_sessionstart(session):
    """Print a warning if Python version is below 3.9."""
    if sys.version_info < (3, 9):
        print(
            f"{YELLOW_BOLD}\n"
            "⚠️ WARNING: You are running a version of Python < 3.9. These tests have only been tested with Python 3.9 and up, so some tests may not behave as expected!\n"
            f"{RESET}"
        )

# ========
# FIXTURES
# ========

@pytest.fixture
def input_test_cases():
    # Path to the final captured test cases JSON file
    captured_test_cases_file = os.path.join(CURRENT_DIR, 'test_cases', 'input_test_cases_final.json')
    
    # Load the test cases
    with open(captured_test_cases_file, 'r') as f:
        test_cases = json.load(f)
    
    return test_cases

@pytest.fixture
def function_test_cases():
    return test_cases_functions_dict

@pytest.fixture
def class_test_cases(): 
    return test_cases_classes_dict

@pytest.fixture
def current_test_name(request):
    return request.node.name

# =====
# HOOKS
# =====

# Global set to track which tests have been run
_run_tests = set()

# Hook that runs before each test is executed
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    """
    I sometimes use this in testing to make sure tests work regardless of the order
    they are run in. Currently not called
    """
    test_name = item.nodeid  # Get the test's identifier (e.g., file path + test name)
    
    if test_name not in _run_tests:
        print(f"First time running {test_name}")
        _run_tests.add(test_name)
    else:
        print(f"{test_name} has already been run in this session")


def pytest_sessionfinish(session, exitstatus=None):
    """
    After all tests finish, emit:
      - TEST_RESULTS_SUMMARY.md (summary table + per-test collapsible details; error-first layout)
      - test_scores.csv (rows per test + TOTAL row)
    """
    if not PC_RESULTS:
        return

    # -------- Load input test cases for rich MD details (with path fallbacks) --------
    input_cases_by_id = {}
    candidates = [
        os.path.join(CURRENT_DIR, 'test_cases', 'input_test_cases_final.json'),
        os.path.join(CURRENT_DIR, 'input_test_cases_final.json'),
        'test_cases/input_test_cases_final.json',
        'input_test_cases_final.json',
    ]
    for fp in candidates:
        try:
            if os.path.exists(fp):
                with open(fp, 'r', encoding='utf-8') as f:
                    cases = json.load(f)
                input_cases_by_id = {c.get("id_input_test_case"): c for c in cases if "id_input_test_case" in c}
                break
        except Exception:
            # If a path fails, try the next one; we'll just omit case metadata if none work
            pass

    # -------- Aggregate per-test results --------
    total_possible = sum(rec.max_score for rec in PC_RESULTS.values())
    total_points = 0.0

    per_test_rows = []
    for test_id, rec in PC_RESULTS.items():
        res = rec.results()
        total_points += res["points"]
        per_test_rows.append({
            "test_id": test_id,
            "passed": res["passed"],
            "total": res["total"],
            "points": res["points"],
            "max_score": rec.max_score,
            "per_case": round(res["per_case"], 4),
            "cases": rec.cases,
        })

    # -------- Build Markdown --------
    md = []
    md.append("# Test Results Summary\n")

    # Summary table (HTML so we can colspan the Total row)
    md.append("<table>")
    md.append("<thead><tr><th>Test</th><th>Cases Passed</th><th style='text-align:right'>Points</th></tr></thead>")
    md.append("<tbody>")
    for row in per_test_rows:
        cases_cell = f"{row['passed']}/{row['total']}" if row["total"] > 1 else "-"
        points_cell = f"{row['points']}/{row['max_score']}"
        md.append(f"<tr><td>{row['test_id']}</td><td>{cases_cell}</td><td style='text-align:right'>{points_cell}</td></tr>")
    md.append(f"<tr><td colspan='2'><strong>Total Score</strong></td><td style='text-align:right'><strong>{round(total_points, 2)}/{total_possible}</strong></td></tr>")
    md.append("</tbody></table>\n")

    # Per-test details (each test is its own H1 + its own <details>)
    for row in per_test_rows:
        failed = [c for c in row["cases"] if not c["passed"]]
        if not failed:
            continue

        # Test heading and collapsible
        md.append(f"# {row['test_id']}\n")
        md.append("_Click the arrow below to see details for each failed test case._\n")
        md.append(f"<details><summary>Details for {row['test_id']}</summary>\n")
        md.append("<br>\n")

        if row["total"] <= 1:
            # -------- Binary/Non-case test (e.g., comments test): single collapsible, only custom_message --------
            # Prefer the first failed record's custom message if present
            first_failed = failed[0] if failed else None
            if first_failed and first_failed.get('id'):
                this_input_case = input_cases_by_id.get(first_failed.get('id'))
                if this_input_case:
                    desc = this_input_case.get("input_test_case_description")
                    if desc:
                        md.append("### What this test case is testing:")
                        md.append(desc)
            if first_failed and first_failed.get("custom_message"):
                md.append(first_failed["custom_message"])
            else:
                md.append("_No formatted error message available._")
        else:
            # -------- Multi-case test: each failed case gets its own collapsible + guidance sections --------
            for case in failed:
                case_id = case["id"]
                case_type = case.get("case_type", "input")
                label = case.get("label")

                if case_type == "function":
                    # Function-test rendering: title and custom message only
                    case_title = label or f"Function test {case_id}"
                    md.append(f"<details><summary>{case_title}</summary>\n")
                    md.append(f"## {case_title}\n")
                    if case.get("custom_message"):
                        md.append(case["custom_message"])
                    else:
                        md.append("_No formatted error message available._")
                    md.append("</details>\n")
                    continue

                if case_type == "class":
                    # class-test rendering: title and custom message only
                    case_title = label or f"Class test {case_id}"
                    md.append(f"<details><summary>{case_title}</summary>\n")
                    md.append(f"## {case_title}\n")
                    if case.get("custom_message"):
                        md.append(case["custom_message"])
                    else:
                        md.append("_No formatted error message available._")
                    md.append("</details>\n")
                    continue

                if case_type == "method":
                    # class-test rendering: title and custom message only
                    case_title = label or f"Method test {case_id}"
                    md.append(f"<details><summary>{case_title}</summary>\n")
                    md.append(f"## {case_title}\n")
                    if case.get("custom_message"):
                        md.append(case["custom_message"])
                    else:
                        md.append("_No formatted error message available._")
                    md.append("</details>\n")
                    continue

                if case_id == "runtime_error":
                    md.append(f"## Runtime Error\n")
                    md.append(case.get("custom_message") or "_No formatted error message available._")
                    continue
                cmeta = input_cases_by_id.get(case_id, {})
                desc = cmeta.get("input_test_case_description", "N/A")
                inputs = cmeta.get("inputs", [])
                example_output = cmeta.get("example_output", "N/A")

                case_title = f"Test Case {case_id}"
                case_summary = f"{case_title} — {desc}" if desc else case_title

                md.append(f"<details><summary>{case_summary}</summary>\n")
                md.append("")
                md.append(f"## {case_summary}")

                # Error-first (the exact custom_message captured during the test)
                if case.get("custom_message"):
                    md.append(case["custom_message"])
                else:
                    md.append("_No formatted error message available._")

                # Then metadata and guidance
                md.append("\n### Having trouble fixing the error messages above?")
                md.append("This test case is entering the inputs listed below with the expectation to get the *exact* same example output shown below. "
                          "Try running your code using the inputs given below and if your code doesn't match the example output, alter your code until it does. "
                          "\n\nRemember, you can always reach out to the TAs, professor, or AI if you need help. If you use AI, it will be better at helping you if "
                          "you paste in the assignment instructions, your code, and the error message from above.")

                md.append("\n#### Inputs")
                md.append("The inputs below (without the quotes) will be entered one by one each time an `input()` function is found in your code.")
                md.append("```")
                for idx, val in enumerate(inputs, start=1):
                    md.append(f'{idx}: "{val}"')
                md.append("```")

                md.append("\n#### Example Output")
                md.append("This is what your terminal should look like if you use the inputs above when running your code.")
                md.append("```")
                md.append(example_output)
                md.append("```")

                md.append("</details>\n")  # end per-case collapsible

        md.append("</details>\n")  # end test-level collapsible
        md.append("<br>\n")  # spacer between tests

    # VS Code occasionally doesn't reload the preview when writing the test results file.
    # Rewriting the file from a temp file seems to fix that issue.
    tmp = "TEST_RESULTS_SUMMARY.tmp.md"
    final = "TEST_RESULTS_SUMMARY.md"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    os.replace(tmp, final)

    # -------- CSV (unchanged except filenames) --------
    csv_out_path = os.path.join("tests", "test_scores.csv")
    os.makedirs(os.path.dirname(csv_out_path), exist_ok=True)
    with open(csv_out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test_id", "passed_cases", "total_cases", "points_awarded", "max_score", "points_per_case"])
        for row in per_test_rows:
            writer.writerow([row["test_id"], row["passed"], row["total"], row["points"], row["max_score"], row["per_case"]])
        writer.writerow(["TOTAL", "", "", round(total_points, 2), total_possible, ""])

    # One-line terminal total
    print(f"\n==> TOTAL SCORE: {round(total_points, 2)}/{total_possible} points\n")




# ====================
# PARTIAL CREDIT INFRA
# ====================

class PartialCreditRecorder:
    def __init__(self, test_id, max_score = None):
        self.test_id = test_id
        self.max_score = (float(max_score) if max_score is not None else None)
        self.cases = []  # list of dicts: {id, passed: bool, reason: str|None, custom_message: str|None}

    def pass_case(self, case_id, note=None, *, case_type="input", label=None):
            self.cases.append({
                "id": case_id, "passed": True, "reason": note,
                "custom_message": None, "case_type": case_type, "label": label
            })

    def fail_case(self, case_id, reason=None, custom_message=None, *, case_type="input", label=None):
            self.cases.append({
                "id": case_id, "passed": False, "reason": reason,
                "custom_message": custom_message, "case_type": case_type, "label": label
            })

    def results(self):
        total = max(1, len(self.cases))
        passed = sum(1 for c in self.cases if c["passed"])
        ms = self.max_score if self.max_score is not None else 0.0  # until test sets real score
        per_case = (ms / total) if total else 0.0
        points = round(passed * per_case, 2)
        return {"total": total, "passed": passed, "per_case": per_case, "points": points}


PC_RESULTS = {}

def pc_get_or_create(test_id, max_score = None) -> PartialCreditRecorder:
    rec = PC_RESULTS.get(test_id)
    if rec is None:
        rec = PartialCreditRecorder(test_id, max_score)
        PC_RESULTS[test_id] = rec
    else:
        # If the caller provides a concrete score, set/upgrade it.
        if max_score is not None:
            try:
                ms_new = float(max_score)
                if rec.max_score is None or ms_new > rec.max_score:
                    rec.max_score = ms_new
            except Exception:
                pass
    return rec


def pc_finalize_and_maybe_fail(rec: PartialCreditRecorder):
    r = rec.results()
    summary_line = f"{rec.test_id}: passed {r['passed']}/{r['total']} → {r['points']}/{rec.max_score} points"

    failed = [c for c in rec.cases if not c["passed"]]
    if failed:
        failed_ids = ", ".join(str(c["id"]) for c in failed)
        print(summary_line)
        # concise, informative failure for the FAILURES section
        raise AssertionError(
            f"{summary_line}\nFailed case(s): {failed_ids}\nOpen TEST_RESULTS_SUMMARY.md (Preview) for full details."
        )
    else:
        print(summary_line)

def record_failure(current_test_name, *, formatted_message, input_test_case=None, case_id = None, reason = "exception"):
    """
    Unified failure logger:
      - Records a failure into PartialCreditRecorder.
      - Never raises (so test loops can continue).
      - Does NOT set/alter max_score; tests set it explicitly.
    """
    try:
        rec = pc_get_or_create(current_test_name, max_score=None)  # <-- do not set a score here
        if case_id is None:
            case_id = (input_test_case or {}).get("id_input_test_case", "runtime_error")
        rec.fail_case(case_id, reason=reason, custom_message=formatted_message)
    except Exception:
        pass
    return


# =================================
# RUNNING STUDENT CODE SUBPROCESSES
# =================================

_ALLOWED_PRIMITIVES = (str, int, float, bool, type(None))
_CONTAINER_TYPES = (list, tuple, set, dict)

def _is_from_student_module(value, student_module_name: str) -> bool:
    mod = getattr(value, "__module__", None)
    return (mod == student_module_name) or (mod is None)

def _looks_like_harness(value) -> bool:
    mod = getattr(value, "__module__", "") or ""
    # exclude anything clearly from your harness/helpers
    return (
        "conftest" in mod
        or "mock_input" in mod
        or "pytest" in mod
        or "importlib" in mod
    )

def _keep_symbol(name: str, value, student_module_name: str) -> bool:
    # name-level filters
    if not name:
        return False
    if name.startswith("_"):        # drop dunders and privates
        return False
    if "[" in name or "]" in name:  # safety against weird injected keys
        return False

    # type-level filters
    if isinstance(value, type):
        # keep classes, but only if they're defined by the student's file
        return _is_from_student_module(value, student_module_name) and not _looks_like_harness(value)

    # drop callables (functions, lambdas, bound methods, etc.)
    if callable(value):
        return False

    # drop modules
    import types as _types
    if isinstance(value, _types.ModuleType):
        return False

    # drop obvious harness artifacts
    if _looks_like_harness(value):
        return False

    # keep primitives and common containers
    if isinstance(value, _ALLOWED_PRIMITIVES):
        return True

    if isinstance(value, _CONTAINER_TYPES):
        return True

    # for other objects: keep *only* if created in the student's module (e.g., instances of their classes)
    return _is_from_student_module(value, student_module_name)

def _clean_value(value, *, depth=0, max_depth=3, max_items=50):
    if depth >= max_depth:
        # stop recursion; give a tiny summary
        return repr(value)[:200]

    # primitives pass through
    if isinstance(value, _ALLOWED_PRIMITIVES):
        return value

    # containers (recurse)
    if isinstance(value, (list, tuple, set)):
        out = []
        for i, item in enumerate(value):
            if i >= max_items:
                out.append("... (truncated)")
                break
            out.append(_clean_value(item, depth=depth+1, max_depth=max_depth, max_items=max_items))
        return out  # normalize to list for JSON-friendliness

    if isinstance(value, dict):
        out = {}
        for i, (k, v) in enumerate(value.items()):
            if i >= max_items:
                out["..."] = "(truncated)"
                break
            # keys: keep as stringy repr to be safe
            try:
                clean_k = k if isinstance(k, (str, int, float, bool)) else repr(k)
            except Exception:
                clean_k = repr(k)
            out[str(clean_k)] = _clean_value(v, depth=depth+1, max_depth=max_depth, max_items=max_items)
        return out

    # instances of student-defined classes: show their __dict__ (sanitized), plus class name
    try:
        cls = value.__class__
        cls_name = getattr(cls, "__name__", type(value).__name__)
        d = getattr(value, "__dict__", None)
        if isinstance(d, dict):
            return {
                "__class__": cls_name,
                "__data__": _clean_value(d, depth=depth+1, max_depth=max_depth, max_items=max_items),
            }
    except Exception:
        pass

    # fallback: short repr
    return repr(value)[:200]


def load_student_code(current_test_name, inputs, input_test_case=None, module_to_test=default_module_to_test,
                      function_tests=None, class_tests=None):
    """
    Loads the student's code in a subprocess with mocked inputs to prevent hanging the main test process.

    If code is successfully executed, will return:
    captured_input_prompts, captured_output, module_globals, function_results, class_results, raised_exceptions
    """
    try:
        # Create a Manager object and dictionary to communicate with the subprocess
        manager = multiprocessing.Manager()
        shared_data = manager.dict()

        # Start the subprocess
        p = multiprocessing.Process(target=_load_student_code_subprocess,
                                    args=(shared_data, current_test_name, inputs, input_test_case, module_to_test, function_tests, class_tests))
        p.start()

        # Wait for the subprocess to finish, or continue if the timeout limit is reached
        p.join(default_timeout_seconds)

        if p.is_alive():
            # Subprocess is still running; terminate it
            p.terminate()
            p.join()  # Ensure the main program waits for the subprocess to fully terminate

            # Handle timeout
            timeout_message = timeout_message_for_students(input_test_case, current_test_name)
            record_failure(current_test_name, formatted_message=timeout_message, input_test_case=input_test_case, reason="timeout error")

        else:
            # Subprocess finished; get the result
            if 'status' in shared_data:
                status = shared_data['status']
                if status == 'success':
                    return shared_data['payload']
                elif status == 'exception':
                    exception_data = shared_data['payload']  # Exception data dictionary
                    exception_message_for_students(exception_data, input_test_case, current_test_name)
                else:
                    record_failure(current_test_name, formatted_message="Unexpected status from subprocess. Contact your professor.", input_test_case=input_test_case, reason="unexpected status")
            else:
                record_failure(current_test_name, formatted_message="Subprocess finished without returning any data. Contact your professor.", input_test_case=input_test_case, reason="unexpected status") 
    except Exception as e:
        exception_message_for_students(e, input_test_case, current_test_name)

def _load_student_code_subprocess(shared_data, current_test_name, inputs, input_test_case, module_to_test, function_tests, class_tests, pre_imports = None):
    """
    Executes the student's code in a subprocess, capturing inputs, outputs, exceptions, and testing functions/classes.
    """
    # Define a custom exception for exit handling
    class ExitCalled(Exception):
        pass

    try:
        # Prepare the mocked input function and capture variables
        manager_payload = {}
        captured_input_prompts = []
        input_iter = iter(inputs)

        def mock_input(prompt=''):
            if prompt == '':
                return ''
            elif normalize_text(prompt) == normalize_text("Press enter to continue..."):
                captured_input_prompts.append(prompt)
                return ''
            else:
                captured_input_prompts.append(prompt)
            try:
                return next(input_iter)
            except StopIteration:
                # Handle the case where there are more input() calls than provided inputs
                raise

        # Prepare the global namespace for exec()
        globals_dict = {
            '__name__': '__main__',  # Ensures that the if __name__ == '__main__' block runs
            'input': mock_input,     # Overrides input() in the student's code
        }

        # Override exit, quit, and sys.exit to prevent termination
        def override_exit_functions(*args):
            raise ExitCalled("sys.exit, exit, or quit was called.")

        builtins.exit = override_exit_functions
        sys.exit = override_exit_functions
        builtins.quit = override_exit_functions

        # Read the student's code from the file
        module_file_path = module_to_test + '.py'
        with open(module_file_path, 'r', encoding='utf-8', errors='replace') as f:
            code = f.read()

        # set up storage for tracking variables, raised exceptions, and exception handlers
        scoped_locals = {}           
        raised_exceptions = []       
        exception_handlers = get_exception_handlers_from_source(code)

        student_root = os.path.abspath(os.path.dirname(module_file_path))

        # where Python lives
        stdlib_dir = os.path.abspath(sysconfig.get_paths()["stdlib"])
        # all site-packages dirs
        site_dirs = set(map(os.path.abspath, site.getsitepackages() + [site.getusersitepackages()]))

        blocked_prefixes = {stdlib_dir, *site_dirs}

        def _is_blocked(path):
            ap = os.path.abspath(path)
            return any(ap.startswith(p + os.sep) or ap == p for p in blocked_prefixes)

        def _is_student(path):
            ap = os.path.abspath(path)
            return ap.startswith(student_root + os.sep) or ap == student_root

        inner_trace = create_trace_function(raised_exceptions, exception_handlers, scoped_locals,
                                            student_filename=os.path.abspath(module_file_path))

        def gate(frame, event, arg):
            fn = frame.f_code.co_filename
            if _is_blocked(fn):
                return None                # don’t trace stdlib/site-packages
            if _is_student(fn):
                return inner_trace(frame, event, arg)  # trace all student files in their folder
            return None                    # ignore everything else

        sys.settrace(gate)

        # Redirect sys.stdout to capture print statements
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Execute the student's code within the controlled namespace
        try:
            code_obj = compile(code, module_file_path, "exec")
            exec(code_obj, globals_dict)
        except ExitCalled as e:
            print(f"Exit call intercepted: {e}")  # Log or handle exit calls

        # Remove the trace function
        sys.settrace(None)

        # Capture the output printed by the student's code
        captured_output = sys.stdout.getvalue()

        # Reset sys.stdout
        sys.stdout = old_stdout

        # Test functions if provided
        if function_tests:
            function_results = test_functions(function_tests, globals_dict)
        else:
            function_results = {"No functions tested": "No functions tested"}

        # Test classes if provided
        if class_tests:
            class_results = test_classes(class_tests, globals_dict)
        else:
            class_results = {"No classes tested": "No classes tested"}

        # ---- Build a single map of ALL variables (filtered & sanitized) ----

        # 0) Student module name (exec ran as __main__)
        student_module_name = "__main__"

        # 1) Start from globals from the exec namespace, excluding builtins
        raw_globals = {k: v for k, v in globals_dict.items() if k != "__builtins__"}

        # 2) Merge in traced locals (these are what your tracer recorded during execution)
        merged = {**raw_globals, **dict(scoped_locals)}

        # 3) Filter and sanitize
        filtered = {
            name: _clean_value(val)
            for name, val in merged.items()
            if _keep_symbol(name, val, student_module_name)
        }

        # 4) Save
        all_variables = filtered


        # add each payload into a dictionary:
        manager_payload['captured_input_prompts'] = captured_input_prompts
        manager_payload['captured_output'] = captured_output
        manager_payload['all_variables'] = all_variables
        manager_payload['function_results'] = function_results
        manager_payload['class_results'] = class_results
        manager_payload['raised_exceptions'] = raised_exceptions

        # Send back the results
        shared_data['status'] = 'success'
        shared_data['payload'] = manager_payload

    except StopIteration as e:
        sys.settrace(None)
        # Send the exception back as a dictionary
        exc_type, exc_value, exc_tb = sys.exc_info()
        input_with_quotes = [f'{index}: "{input}"' for index, input in enumerate(input_test_case["inputs"], start=1)]
        test_case_inputs = '\n'.join(input_with_quotes)
        exception_data = {
            'type': type(e).__name__,
            'message': (f"### How to fix it:\n"
                        f"This error was very likely caused by your code asking for more input() calls than the input test case expected. "
                        f"To see where this is happening in your code, run your code and input THESE EXACT INPUTS IN THIS ORDER (without the quotations):\n"
                        f"```\n{test_case_inputs}\n```\n"
                        f"Your code should end after all of those inputs have been entered. If, after entering those exact inputs in that order, your code asks for another input, THAT is the cause of this error. "
                        f"You likely wrote an if statement or loop in a way that it is asking for inputs again. Make it so your code doesn't ask for any more inputs after the last input entered. "
                        f"If you believe that is a mistake, please "
                        f"reach out to your professor."),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
        }
        shared_data['status'] = 'exception'
        shared_data['payload'] = exception_data

    except EOFError as e:
        sys.settrace(None)
        # Send the exception back as a dictionary
        exc_type, exc_value, exc_tb = sys.exc_info()
        exception_data = {
            'type': type(e).__name__,
            'message': (f"{str(e)}\n\nThis was most likely caused by an input() function being present "
                        f"in a .py module that you imported. Please only use the input() function in the main assignment .py file. Contact your professor if you have issues fixing this."),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
        }
        shared_data['status'] = 'exception'
        shared_data['payload'] = exception_data

    except Exception as e:
        sys.settrace(None)
        # Send the exception back as a dictionary

        exc_type, exc_value, exc_tb = sys.exc_info()
        exception_data = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
        }
        shared_data['status'] = 'exception'
        shared_data['payload'] = exception_data
        


    finally:
        sys.settrace(None)
        if 'old_stdout' in globals() or 'old_stdout' in locals():
            sys.stdout = old_stdout

def is_picklable(obj):
    """
    Each test case is run in a subprocess, with relevant info/variables
    Sent back to the main process through a Queue. Because that requires
    pickling the data, this is used to check if something I'm trying to send
    is actually able to be pickled before I actually send it.
    """

    try:
        pickle.dumps(obj)
    except Exception:
        return False
    else:
        return True

# ===================================================
# TRACE FUNCTIONS
# (for tracking exceptions variables in student code)
# ===================================================
def _good_var_name(name: str) -> bool:
    if not isinstance(name, str) or not name:
        return False
    if name.startswith("_"):                 # drop dunders/privates
        return False
    if "." in name or "<" in name or ">" in name or "[" in name or "]" in name:
        return False
    return name.isidentifier()

def create_trace_function(raised_exceptions, exception_handlers, scoped_locals,
                          *, student_filename: str):
    """
    Collect locals from student frames only (by filename) and track exceptions.
    Locals are flattened as 'outer.inner.var' but only when names are clean.
    """
    pending_exception = {'type': None, 'frame': None}
    call_stack = []  # only for frames from the student's file

    def _in_student_file(frame) -> bool:
        try:
            fn = os.path.abspath(frame.f_code.co_filename)
            # accept compiled-from-string as a fallback (optional)
            if fn == "<string>":
                return True
            return fn == os.path.abspath(student_filename)
        except Exception:
            return False


    def _add_scoped_locals(frame):
        if not _in_student_file(frame):
            return
        prefix = ".".join(call_stack)
        for k, v in frame.f_locals.items():
            if k == "__builtins__" or not _good_var_name(k):
                continue
            fq_key = f"{prefix}.{k}" if prefix else k
            serialized = serialize_object(v)
            # accumulate if same var name appears multiple times
            if fq_key in scoped_locals:
                prev = scoped_locals[fq_key]
                scoped_locals[fq_key] = prev + [serialized] if isinstance(prev, list) else [prev, serialized]
            else:
                scoped_locals[fq_key] = serialized

    def trace_function(frame, event, arg):
        nonlocal pending_exception, call_stack

        if event == 'call':
            if _in_student_file(frame):
                call_stack.append(frame.f_code.co_name)
            return trace_function

        elif event == 'return':
            if _in_student_file(frame):
                _add_scoped_locals(frame)
                if call_stack:
                    call_stack.pop()

        elif event == 'exception':
            # Only record exceptions that originate in the student's file
            if _in_student_file(frame):
                exc_type, exc_value, exc_traceback = arg
                exception_name = exc_type.__name__
                raised_exceptions.append({'exception': exception_name, 'handled_by': None})
                pending_exception['type'] = exception_name
                pending_exception['frame'] = frame
                _add_scoped_locals(frame)
            # If not student frame, ignore and don't modify pending_exception
            return trace_function

        elif event == 'line':
            # Only attempt to mark handled_by inside the student's file
            if pending_exception['type'] and _in_student_file(frame):
                lineno = frame.f_lineno
                for handler in exception_handlers:
                    if handler['start_lineno'] <= lineno <= handler['end_lineno']:
                        # Only claim a handler if it actually matches the pending exception
                        pen = pending_exception['type']
                        if handler.get('is_general') or (pen in handler.get('types', [])):
                            if raised_exceptions:
                                # record the handler type that caught it (e.g., "KeyError" or "(ValueError, KeyError)" or "Exception")
                                raised_exceptions[-1]['handled_by'] = handler['type']
                            pending_exception['type'] = None
                            pending_exception['frame'] = None
                            break
            return trace_function

        return trace_function

    return trace_function



def get_exception_handlers_from_source(source):
    exception_handlers = []
    tree = ast.parse(source)

    class ExceptionHandlerVisitor(ast.NodeVisitor):
        def visit_Try(self, node):
            for handler in node.handlers:
                # Determine the *display* label and the normalized list of types
                if handler.type is None:
                    display_type = 'Exception'   # bare except
                    types_list = []              # empty list means "any"
                    is_general = True
                elif isinstance(handler.type, ast.Name):
                    display_type = handler.type.id
                    types_list = [handler.type.id]
                    is_general = (display_type == 'Exception')
                elif isinstance(handler.type, ast.Tuple):
                    # except (ValueError, KeyError) as e:
                    names = []
                    for elt in handler.type.elts:
                        if isinstance(elt, ast.Name):
                            names.append(elt.id)
                        else:
                            # fallback to unparse for unusual nodes
                            names.append(ast.unparse(elt))
                    display_type = "(" + ", ".join(names) + ")"
                    types_list = names
                    is_general = ('Exception' in names)
                else:
                    # other complex expressions; keep a readable display and try to derive names
                    display_type = ast.unparse(handler.type)
                    # a conservative attempt to extract bare names
                    names = []
                    try:
                        for n in ast.walk(handler.type):
                            if isinstance(n, ast.Name):
                                names.append(n.id)
                    except Exception:
                        pass
                    types_list = names or [display_type]
                    is_general = ('Exception' in types_list)

                start_lineno = handler.lineno
                end_lineno = handler.body[-1].lineno if handler.body else start_lineno

                exception_handlers.append({
                    'type': display_type,      # e.g., "KeyError", "(ValueError, KeyError)", or "Exception"
                    'types': types_list,       # normalized list of names, [] means "any"
                    'start_lineno': start_lineno,
                    'end_lineno': end_lineno,
                    'is_general': is_general,
                })

            self.generic_visit(node)

    ExceptionHandlerVisitor().visit(tree)
    return exception_handlers


def exception_profiler(frame, event, arg):
    """Profile function to track exceptions raised."""
    if event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        raised_exceptions.append(exc_type.__name__)

# ======================================================
# ACCOUNTING FOR DIFFERENT NAMING CONVENTIONS IN CLASSES
# ======================================================

def _name_variants_from_class_name(cls_name: str):
    parts = re.findall(r'[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z])', cls_name.replace('_', ' '))
    words = [w.lower() for w in parts if w.strip()]
    if not words:
        words = [cls_name.lower()]
    pascal = ''.join(w.capitalize() for w in words)
    camel = (words[0] + ''.join(w.capitalize() for w in words[1:])) if words else cls_name
    snake = '_'.join(words)
    seen, out = set(), []
    for v in (pascal, camel, snake):
        if v not in seen:
            out.append(v)
            seen.add(v)
    return out

def _attr_case_variants(core: str):
    # produce lower, Capitalized, UPPER
    v = [core.lower(), core.capitalize(), core.upper()]
    seen, out = set(), []
    for x in v:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def _try_set_attr_by_candidates(obj, candidates, value, *, create_if_missing: bool = False):
    """
    Try to set obj.<candidate> = value for the first candidate that ALREADY EXISTS.
    If none exist and create_if_missing=True, create the first candidate.
    Return the name actually used (or None if not set).
    """
    for name in candidates:
        if hasattr(obj, name) or (hasattr(obj, "__dict__") and name in getattr(obj, "__dict__", {})):
            setattr(obj, name, value)
            return name

    if create_if_missing and candidates:
        try:
            setattr(obj, candidates[0], value)
            return candidates[0]
        except Exception:
            pass
    return None


def set_attr_flexible(obj, logical_attr_name, value, *, create_if_missing: bool = False):
    """
    STRICT by default:
      - Update an existing attribute that matches (including mangled + case variants).
      - If nothing matches and create_if_missing=False, return None (DO NOT create).
      - If create_if_missing=True, create a sensible candidate (useful in some non-strict tests).
    """
    # 0) exact
    if hasattr(obj, logical_attr_name):
        setattr(obj, logical_attr_name, value)
        return logical_attr_name

    candidates = []

    # Already-mangled provided?
    m = _MANGLED_RE.match(logical_attr_name)
    if m:
        tail_variants = _attr_case_variants(m.group(2))
        existing = _find_existing_mangled_key(obj, tail_variants)
        if existing:
            setattr(obj, existing, value)
            return existing

        # Build base-first MRO candidate list
        for class_variants in _mro_class_variants_base_first(obj):
            for cv in class_variants:
                for tv in tail_variants:
                    candidates.append(f"_{cv}__{tv}")

        used = _try_set_attr_by_candidates(obj, candidates, value, create_if_missing=create_if_missing)
        if used:
            return used

        # Last-chance casefold match
        d = getattr(obj, "__dict__", {})
        cand_cf = {c.casefold(): c for c in candidates}
        for name in d.keys():
            if name.casefold() in cand_cf:
                setattr(obj, name, value)
                return name
        return None

    # Logical private (“__wins”)
    if logical_attr_name.startswith("__") and not logical_attr_name.startswith("___"):
        tail_core = logical_attr_name[2:]
        tail_variants = _attr_case_variants(tail_core)

        existing = _find_existing_mangled_key(obj, tail_variants)
        if existing:
            setattr(obj, existing, value)
            return existing

        for class_variants in _mro_class_variants_base_first(obj):
            for cv in class_variants:
                for tv in tail_variants:
                    candidates.append(f"_{cv}__{tv}")

        used = _try_set_attr_by_candidates(obj, candidates, value, create_if_missing=create_if_missing)
        if used:
            return used

        d = getattr(obj, "__dict__", {})
        cand_cf = {c.casefold(): c for c in candidates}
        for name in d.keys():
            if name.casefold() in cand_cf:
                setattr(obj, name, value)
                return name
        return None

    # Protected/public (“_wins”, “wins”)
    base = logical_attr_name.lstrip("_") or logical_attr_name
    tail_variants = _attr_case_variants(base)
    # Prefer existing
    for tv in tail_variants:
        if hasattr(obj, f"_{tv}") or (hasattr(obj, "__dict__") and f"_{tv}" in obj.__dict__):
            setattr(obj, f"_{tv}", value)
            return f"_{tv}"
        if hasattr(obj, tv) or (hasattr(obj, "__dict__") and tv in obj.__dict__):
            setattr(obj, tv, value)
            return tv

    # Else candidates; only create if allowed
    candidates = [f"_{tv}" for tv in tail_variants] + tail_variants
    return _try_set_attr_by_candidates(obj, candidates, value, create_if_missing=create_if_missing)


def apply_set_var_values(obj, mapping: dict, *, create_if_missing: bool = False):
    """
    Apply mapping of logical names to values.
    If create_if_missing=False (default), we DO NOT create new attrs. Missing ones are reported.
    Returns (used_map, missing_list)
    """
    used = {}
    missing = []
    for logical_name, val in (mapping or {}).items():
        actual = set_attr_flexible(obj, logical_name, val, create_if_missing=create_if_missing)
        used[logical_name] = actual
        if actual is None:
            missing.append(logical_name)
    return used, missing




# ==================================
# TESTING CUSTOM FUNCTIONS & CLASSES
# ==================================

def get_function(module_name, func_name):
    """
    Try to import the function from a module with various naming conventions.
    """
    function_variations = [
    func_name,  # snake_case
        func_name.title().replace("_", ""), # PascalCase
        (func_name[0].lower() + func_name.title()[1:]).replace("_", ""),    # camelCase
    ]

    module = importlib.import_module(module_name)
    
    for variation in function_variations:
        if hasattr(module, variation):
            return getattr(module, variation)
    
    raise AttributeError(f"Function '{func_name}' not found in {module_name}.")

def get_custom_functions_from_module(module):
    """
    Given a module object, return a dictionary of all custom functions defined in the module.
    """
    return {name: obj for name, obj in vars(module).items() if inspect.isfunction(obj)}

def is_user_defined_module(module):
    """
    Determines if a module is user-defined by checking if it resides in the student's directory.
    Excludes standard library and external packages.
    """
    module_path = getattr(module, '__file__', '')
    if module_path:  # Only proceed if the module has a __file__ attribute
        base_dir = os.path.dirname(os.path.realpath(module_path))  # Get the directory of the module
        # Compare to standard library or third-party package paths
        return not base_dir.startswith(sys.prefix)  # Exclude standard library and packages
    return False

def get_all_custom_functions(globals_dict):
    """
    Retrieve all custom functions defined within the student's code and any user-defined modules
    they import. Excludes functions from external libraries like random, numpy, etc.
    """
    custom_functions = {}
    
    # First, collect all custom functions defined in the main file
    for name, obj in globals_dict.items():
        if inspect.isfunction(obj):
            # Only include functions defined in the student's main file (__main__) or other files
            if obj.__module__ == '__main__' or is_user_defined_module(sys.modules[obj.__module__]):
                if name != 'input':  # this just exlcudes the mocked input function run during the tests.
                    custom_functions[name] = obj

    # Now, check for any imported modules in the globals_dict
    for name, obj in globals_dict.items():
        if inspect.ismodule(obj) and is_user_defined_module(obj):
            # Add custom functions from this imported module
            custom_functions.update(get_custom_functions_from_module(obj))

    return custom_functions

def test_functions(function_tests, globals_dict, instance=None):
    """
    Tests functions or methods based on the provided test cases.
    If 'instance' is provided, tests methods of the instance.
    """
    class MissingVarError(AssertionError):
        pass
    function_results = {}
    is_method_test = False

    if not function_tests:
        exception_data = {
            'type': 'Missing function tests',
            'message': (f"No function tests were provided to test_functions function in conftest.py. Contact your professor."),
            'custom_location': f'test_functions in conftest.py',
            'detail': 'FUNCTION ERROR'
        }
        function_results["FUNCTION ERROR"] = exception_data
        return function_results

    if instance is not None:
        is_method_test = True
        # Testing methods of the instance
        all_functions = {name: getattr(instance, name) for name in dir(instance)
                         if callable(getattr(instance, name)) and not name.startswith('__')}
        context = f"object of class {instance.__class__.__name__}"
    else:
        # Testing functions in the globals_dict
        all_functions = get_all_custom_functions(globals_dict)
        context = "your code"

    all_functions_names = '\n'.join(all_functions.keys())

    for test_case in function_tests:
        # Handle function name variations
        func_name_original = test_case.get('function_name')
        function_variations = [
            func_name_original,  # original name
            func_name_original.lower(),
            func_name_original.title().replace("_", ""),
            (func_name_original[0].lower() + func_name_original.title()[1:]).replace("_", ""),
        ]

        func_found = False
        for func_variation in function_variations:
            if func_variation in all_functions:
                func_found = True
                func = all_functions[func_variation]
                break

        if not func_found:
            newline = '\n' # this is just to make it compatible with older python versions.
            exception_data = {
                    'type': 'Function not found',
                    'message': (f"This test is looking specifically for the function or method\n"
                                f"```\n{func_name_original}\n```\n"
                                f"in {context}, but it couldn't find it, nor any of its accepted variations:\n"
                                f"```\n{newline.join(function_variations[1:])}\n```\n"
                                f"Make sure you are spelling the function/method name correctly, and that you didn't name any other variables "
                                f"in your code the exact same name as the function. Below are all of "
                                f"the functions/methods that the test could find in {context}:\n"
                                f"```\n{all_functions_names}\n```\n"),
                    'custom_location': f'test_classes in conftest.py',
                    'detail': 'CLASS ERROR'
            }
            function_results['FUNCTION ERROR'] = exception_data
            return function_results


        # Run the function with the provided arguments
        if callable(func):
            args = test_case.get("args", [])
            
            num_calls = test_case.get('num_calls', 1)

            try:
                for _ in range(num_calls): # usually just called once, but some tests require several calls
                    if is_method_test:
                    # first store the initial state of the object:
                        values_to_set = test_case.get('set_var_values')
                        if values_to_set:
                            # use the flexible setter that tolerates class name and capitalization variations
                            used_map, missing = apply_set_var_values(instance, values_to_set, create_if_missing=False)  # STRICT
                            test_case.setdefault("attr_set_map", used_map)

                            if missing:
                                def grab_from_double_underscore(s: str) -> str:
                                    idx = s.find("__")
                                    if idx != -1:
                                        return s[idx:]
                                    else:
                                        return s
                                    
                                # build a clear error so the case fails fast
                                available = list(getattr(instance, "__dict__", {}).keys())
                                available_str = '\n'.join([grab_from_double_underscore(var) for var in available])
                                missing_str = '\n'.join(missing)

                                raise MissingVarError(
                                    f"### Missing variable(s):\n"
                                    f"The test could not find the following expected instance variable(s) in the object:\n"
                                    f"```\n{missing_str}\n```\n"
                                    f"### Your object's variables:\n"
                                    f"These are the instance variables that exist in the object:\n\n"
                                    f"```\n{available_str}\n```\n"
                                    "Hint: the tests accept Pascal/camel/snake class names "
                                    "but they will fail if the variable name itself is misspelled (e.g., '__Winz' instead of '__Wins', etc.)."
                                )


                        object_state = get_object_state(instance)
                        test_case.setdefault('initial_obj_state', []).append(object_state)

                    actual_return_value = func(*args)
                    test_case.setdefault('actual_return_value', []).append(actual_return_value)

                    if is_method_test:
                    # first store the initial state of the object:
                        object_state = get_object_state(instance)
                        test_case.setdefault('final_obj_state', []).append(object_state)
            except MissingVarError as e:
                exception_data = {
                    'type': type(e).__name__,
                    'message': (f"Your {func_name_original} function couldn't run because the object was missing a needed variable\n```\n"
                                f"{e}\n```\n"
),
                    'custom_location': f'Your {func_name_original} function',
                    'detail': 'FUNCTION ERROR'
                }
                test_case["FUNCTION ERROR"] = exception_data
                function_results["FUNCTION ERROR"] = exception_data
                return function_results

            except Exception as e:
                if len(args) > 0:
                    init_args_str = '\n'.join([f"{index}: {argument}" for index, argument in enumerate(args, start=1)])
                elif instance:
                    init_args_str = 'None besides "self"'
                else:
                    init_args_str = "No arguments"
                exception_data = {
                    'type': type(e).__name__,
                    'message': (f"Your code gave the following error while trying to run the function {func_name_original}:\n\n"
                                f"{e}\n\n"
                                f"{func_name_original} was using these arguments when it ran into the error:\n\n"
                                f"{func_name_original.upper()} ARGUMENTS:\n"
                                f"{'-'*len(f'{func_name_original.upper()} ARGUMENTS:')}\n"
                                f"{init_args_str}\n\n"
                                f"Make sure your function is accepting the correct number of arguments, you may have written the function with "
                                f"more or fewer parameters than the test is expecting. Also double check that your function doesn't run into a "
                                f"runtime error when providing it with the exact arguments shown above."),
                    'custom_location': f'Your {func_name_original} function',
                    'detail': 'FUNCTION ERROR'
                }
                test_case["FUNCTION ERROR"] = exception_data
                function_results["FUNCTION ERROR"] = exception_data
                return function_results
        else:
            exception_data = {
                    'type': 'Function name isn\'t callable',
                    'message': (f"{func_name_original} was found in {context}, but it isn't callable as a function. Make sure you defined it correctly, "
                                f"and that you aren't using the exact name of the function as a variable name somewhere else in your code."),
                    'custom_location': f'test_classes in conftest.py',
                    'detail': 'FUNCTION ERROR'
                }
            test_case["FUNCTION ERROR"] = exception_data
            function_results["FUNCTION ERROR"] = exception_data
            return function_results
        
    # If no errors occured while trying to run the function and store its results, store those here
    function_results['function_results'] = function_tests
    return function_results


def get_all_custom_classes(globals_dict):
    """
    Retrieves all custom classes defined within the student's code and any user-defined modules
    they import. Excludes classes from external libraries.
    """
    custom_classes = {}

    # First, collect all custom classes defined in the main file
    for name, obj in globals_dict.items():
        if inspect.isclass(obj):
            # Only include classes defined in the student's main file (__main__) or user-defined modules
            if obj.__module__ == '__main__' or is_user_defined_module(sys.modules[obj.__module__]):
                custom_classes[name] = obj

    # Now, check for any imported modules in the globals_dict
    for name, obj in globals_dict.items():
        if inspect.ismodule(obj) and is_user_defined_module(obj):
            # Add custom classes from this imported module
            custom_classes.update({name: cls for name, cls in vars(obj).items() if inspect.isclass(cls)})

    return custom_classes

def _resolve_class_by_variations(requested_name: str, all_custom_classes: dict):
    """
    Try to resolve a class name allowing PascalCase, camelCase, and snake_case
    using the existing convert_pascal_case helper.
    """
    # convert_pascal_case returns [PascalCase, camelCase, snake_case]
    # We de-dup while preserving order.
    variations = list(dict.fromkeys(convert_pascal_case(requested_name)))
    for variation in variations:
        if variation in all_custom_classes:
            return all_custom_classes[variation], variations
    return None, variations

def process_init_args(init_args, all_custom_classes):
    processed_args = []
    for arg in init_args:
        if isinstance(arg, dict) and 'class_name' in arg:
            requested_class_name = arg['class_name']
            init_args_nested = arg.get('init_args', [])
            # Try to resolve by Pascal/camel/snake variants
            nested_cls, tried_variations = _resolve_class_by_variations(requested_class_name, all_custom_classes)
            if nested_cls is None:
                # Build a helpful message listing what's available and what we tried
                available = "\n".join(all_custom_classes.keys())
                tried = "\n".join(tried_variations[1:]) if len(tried_variations) > 1 else "(no alternatives)"
                raise Exception(
                    "Class not found in student's code.\n\n"
                    f"Requested class name:\n```\n{requested_class_name}\n```\n"
                    "Accepted naming variations (PascalCase / camelCase / snake_case):\n"
                    f"```\n{tried}\n```\n"
                    "Below are all classes the test could see in your code:\n"
                    f"```\n{available}\n```\n"
                )
            # Recurse to process nested init args
            nested_init_args_processed = process_init_args(init_args_nested, all_custom_classes)
            nested_obj = nested_cls(*nested_init_args_processed)
            # Keep a reference for later comparisons, just like your original
            arg['actual_object'] = nested_obj
            processed_args.append(nested_obj)
        else:
            processed_args.append(arg)
    return processed_args


def serialize_object(obj, *, _seen=None, _depth=0, _max_depth=10):
    """Serialize arbitrarily nested objects to JSON-friendly structures,
    avoiding cycles and skipping non-data runtime objects.
    """
    if _seen is None:
        _seen = set()

    # Fast path: primitives (and a few primitives you already allow)
    if isinstance(obj, (int, float, str, bool, type(None), date, timedelta)):
        return obj

    # Stop on cycles
    oid = id(obj)
    if oid in _seen:
        return "<cycle>"

    # Depth guard
    if _depth >= _max_depth:
        return repr(obj)

    # Containers
    if isinstance(obj, dict):
        _seen.add(oid)
        return {str(k): serialize_object(v, _seen=_seen, _depth=_depth+1, _max_depth=_max_depth)
                for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        _seen.add(oid)
        seq = [serialize_object(v, _seen=_seen, _depth=_depth+1, _max_depth=_max_depth) for v in obj]
        return seq if isinstance(obj, list) else tuple(seq) if isinstance(obj, tuple) else set(seq)

    # Skip/short-circuit noisy runtime objects that cause deep graphs
    if isinstance(obj, (types.ModuleType,
                        types.FunctionType, types.BuiltinFunctionType, types.MethodType,
                        types.CodeType, types.FrameType, types.GeneratorType, types.CoroutineType)):
        # Keep a short, harmless representation
        name = getattr(obj, "__name__", obj.__class__.__name__)
        return f"<{obj.__class__.__name__}:{name}>"

    # Generic objects with __dict__
    if hasattr(obj, "__dict__"):
        _seen.add(oid)
        try:
            data = vars(obj)
        except Exception:
            return repr(obj)
        return {
            "__class__": obj.__class__.__name__,
            "__data__": serialize_object(data, _seen=_seen, _depth=_depth+1, _max_depth=_max_depth),
        }

    # Fallback
    return repr(obj)

def test_classes(class_tests, globals_dict):
    """
    Tests the classes defined by the student according to the specifications in class_tests.
    """

    if not class_tests:
        exception_data = {
                    'type': 'Missing class tests',
                    'message': (f"No class tests were provided to test_classes function in conftest.py. Contact your professor."),
                    'custom_location': f'test_classes in conftest.py',
                    'detail': 'CLASS ERROR'
                }
        class_tests['CLASS ERROR'] = exception_data
        return class_tests

    all_custom_classes = get_all_custom_classes(globals_dict)
    all_custom_classes_names = '\n'.join(all_custom_classes.keys())

    # returns pascal, camel, and snake
    class_name_original = class_tests.get('class_name')
    class_variations = list(dict.fromkeys(convert_pascal_case(class_name_original)).keys()) # if snake or camel are identical, it gets rid of duplicates.

    # Before running any of the tests, check if the class is even in the students' code

    class_found = False
    for class_variation in class_variations:
        if class_variation in all_custom_classes:
            cls = all_custom_classes[class_variation]
            class_found = True
            break

    if not class_found:
        newline = '\n' # this is just to make it compatible with older python versions.
        exception_data = {
                    'type': 'Can\'t find required class',
                    'message': (f"This test is looking specifically for the class:\n"
                                f"```\n{class_name_original}\n```\n"
                                f"But it couldn't find it, nor any of its accepted variations:\n"
                                f"```\n{newline.join(class_variations[1:])}\n```\n"
                                f"Make sure you are spelling the class name correctly. Below are all of "
                                f"the classes you made in your code that the test could find:\n"
                                f"```\n{all_custom_classes_names}\n```\n"),
                    'custom_location': f'your .py file',
                    'detail': 'CLASS ERROR'
                }
        class_tests['CLASS ERROR'] = exception_data
        return class_tests

    for class_test in class_tests.get('class_test_cases'):
        init_args = copy.deepcopy(class_test.get("init_args", {}))
        try:
            # Process init_args to create nested class instances if necessary
            init_args_processed = process_init_args(list(init_args.values()), all_custom_classes)
            try:
                obj = cls(*init_args_processed)
            except Exception as e:
                init_args_str = '\n'.join([f"{parameter_name}: {argument}" for parameter_name, argument in class_test.get("init_args", {}).items()])
                exception_data = {
                    'type': type(e).__name__,
                    'message': (f"{str(e)}\n\n\n"
                                f"### How to fix it:\n"
                                f"This was most likely caused by the {class_name_original} constructor requiring more (or fewer) arguments than the test case "
                                f"was expecting. If so, change your {class_name_original} constructor to where it can work with the arguments shown below. "
                                f"This test is calling the constructor of {class_name_original} with the following arguments:\n\n"
                                f"### Expected {class_name_original} init arguments:\n"
                                f"```\n{init_args_str}\n```\n"),
                    'custom_location': f'The __init__ method of your {class_name_original} class',
                    'detail': 'CLASS ERROR'
                }
                class_tests['CLASS ERROR'] = exception_data
                return class_tests
            # Serialize the object
            serialized_obj = serialize_object(obj)

            # Collect method names
            actual_method_names = [name for name, value in inspect.getmembers(obj, predicate=inspect.isfunction)
                       if not name.startswith('__')]

            class_test['actual_object'] = serialized_obj
            class_test['actual_method_names'] = actual_method_names
            
            # if the test is for a specific method, call that method:
            if class_tests.get('test_type', '') == 'method_test':
                method_to_test = class_tests.get('method_to_test')
                method_test_cases = [method_test_case for method_test_case in class_test.get('method_test_cases') if method_test_case.get('function_name') == method_to_test]

                function_results = test_functions(method_test_cases, globals_dict, instance=obj)
                if function_results.get("FUNCTION ERROR"):
                    class_tests["FUNCTION ERROR"] = function_results
                pass
                    
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            exception_data = {
                'type': type(e).__name__,
                'message': (f"{str(e)}\n\n\n### How to fix it:\n"
                            f"Something went wrong during the class test. Contact your professor."),
                'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
            }
            class_tests['CLASS ERROR'] = exception_data
            return class_tests
        
    return class_tests

def get_object_state(obj):
    """
    Returns a dictionary representing the object's state,
    including class name, instance variables, and methods.
    Recursively serializes any nested objects stored as instance variables.
    """
    def serialize(value):
        # 1) Always normalize custom objects (student classes) to a dict shape
        if hasattr(value, '__dict__'):
            return get_object_state(value)

        # 2) Then handle containers
        if isinstance(value, list):
            return [serialize(item) for item in value]
        if isinstance(value, dict):
            return {k: serialize(v) for k, v in value.items()}
        if isinstance(value, tuple):
            return tuple(serialize(item) for item in value)

        # 3) Finally, primitives/other values: keep if picklable, else string fallback
        if is_picklable(value):
            return value
        return str(value)

    # Get instance variables and recursively serialize them
    instance_variables = {name: serialize(value) for name, value in vars(obj).items()}

    # Get methods
    methods = [name for name, value in inspect.getmembers(obj, predicate=inspect.ismethod)
               if not name.startswith('__')]

    return {
        'class_name': obj.__class__.__name__,
        'instance_variables': instance_variables,
        'methods': methods,
    }

# ========================
# ERROR MESSAGE FORMATTING
# ========================

def format_error_message(custom_message: str = None,
                         current_test_name: str = None,
                         input_test_case: dict = None,
                         display_inputs: bool = False,
                         display_input_prompts: bool = False,
                         display_invalid_input_prompts: bool = False,
                         display_printed_messages: bool = False,
                         display_invalid_printed_messages: bool = False,
                         line_length: int = 74) -> str:
    """
    Constructs the main error students will see in the Test Results window.
    The main purpose in the error message is to communicate which test case
    a test failed on, and then optionally include extra details that might
    help out the student

    Keep line_length at 74, that is where pytest splits lines in its error
    reporting
    """
    
    # some starting strings. All messages will be appended to error_message
    error_message = ''
    divider = f"\n{'-'*line_length}\n"

    if custom_message:
        error_message += f"### Error Message (what went wrong):\n"
        error_message += custom_message
    
    return error_message


def exception_message_for_students(exception_data, input_test_case, current_test_name):
    """
    Gets called when a test fails because of an exception occuring, rather than
    the test failing because it didn't produce the right output, etc.

    If an exception occurs during the subprocess of the code running, it gets
    returned as a dictionary (since you can't pickle Exception objects and send them
    to a higher process). Otherwise, this function just expects an exception object.
    """

    if isinstance(exception_data, dict):
        # Exception data from the subprocess
        error_type = exception_data.get('type')
        error_message_str = exception_data.get('message')
        traceback_list = exception_data.get('traceback')
        custom_location = exception_data.get('custom_location')
        error_detail = exception_data.get('detail')
        # Attempt to get the last traceback entry for the error location
        if traceback_list:
            error_location = ''.join(traceback_list[-2:]) if len(traceback_list) >= 2 else ''.join(traceback_list)
        elif custom_location:
            error_location = custom_location
        else:
            error_location = "No location available."
    else:
        # Exception object with traceback
        e = exception_data
        tb_list = traceback.extract_tb(e.__traceback__)
        if tb_list:
            last_traceback = [tb_list[-1]]
            error_location = ''.join(traceback.format_list(last_traceback))
        else:
            error_location = "No location available."
        error_type = type(e).__name__
        error_message_str = str(e)
        error_detail = None

    # Because the student's code is run by exec in a subprocess, it just shows up as <string>
    # These just puts back their python file name in that case, as well as improves
    # some of the messaging to make it easier for students to understand
    # at a glance by clearly separating the location of the error and the error itself.
    error_location = error_location.replace('File "<string>"', f"{default_module_to_test}.py" )
    error_location = error_location.replace(', in <module>', '' )
    error_message = f"\n{error_type}: {error_message_str}" if error_type != "StopIteration" else error_message_str
    error_message = error_message.strip()
    error_location = error_location.replace(error_message, '').strip()
    
    display_inputs_option = False
    if input_test_case:
        # Check if 'inputs' is in test_case and set display_inputs_option accordingly
        if input_test_case.get("inputs", None):
            display_inputs_option = True
    else:
        input_test_case = {'id_input_test_case': None}
        input_test_case['input_test_case_description'] =  "No input test case for this test."

    if error_type == "StopIteration":
        custom_message = (f"While trying to run {current_test_name}, the automated test couldn't complete because your code "
            f"called an input() function more times than it should have.\n\n"
            f"{error_message}\n\n")

        formatted_message = format_error_message( 
                                custom_message=custom_message,
                                current_test_name=current_test_name,
                                input_test_case=input_test_case)

        record_failure(current_test_name, formatted_message=formatted_message, input_test_case=input_test_case, reason="student exception")
        return  # keep running other cases


    elif error_detail in ["CLASS ERROR", "FUNCTION ERROR"]:

        if error_type == "Function not found":
            custom_message = (f"While trying to run {current_test_name}, python ran into an error.\n\n"
                f"### Error type:\n"
                f"```\n{error_type}\n```\n"
                f"{error_message}")
        else:
            custom_message = (f"While trying to run {current_test_name}, python ran into an error.\n\n"
                f"### Location of the error:\n"
                f"```\n{error_location}\n```\n"
                f"### Error message:\n"
                f"```\n{error_message}\n```\n")
        
        formatted_message = format_error_message(
                                custom_message=custom_message,
                                current_test_name=current_test_name,
                                input_test_case=input_test_case)

        record_failure(current_test_name, formatted_message=formatted_message, input_test_case=input_test_case, reason="student exception")
        return  # keep running other cases

    else:
        custom_message = (f"While trying to run {current_test_name}, python ran into an error.\n\n"
            f"### Location of the error:\n"
            f"```\n{error_location}\n```\n"
            f"### Error message:\n"
            f"```\n{error_message}\n```\n"
            f"### How to fix it:\n"
            f"If the error occurred in {default_module_to_test}.py or another .py file that you wrote, set a breakpoint at the location in that file where "
            f"the error occurred and see if you can repeat the error by running your code using the inputs for Test Case {input_test_case['id_input_test_case']}. "
            f"That should help you see what went wrong.\n\n"
            f"If the error occurred in a different file (for example, a file like \"test_01_\" or \"conftest\", etc.), reach out to your professor ASAP. The error might be with the test, not your code.\n\n")
        
        formatted_message = format_error_message(
            custom_message=custom_message,
            current_test_name=current_test_name,
            input_test_case=input_test_case,
            display_inputs=True)
        
        record_failure(current_test_name, formatted_message=formatted_message, input_test_case=input_test_case, reason="student exception")
        return  # keep running other cases


def timeout_message_for_students(input_test_case, current_test_name):
    """
    Just returns a message for timeout errors.
    I put this in a function just so there is one central place
    to edit the message if I change it in the future.
    """
    if isinstance(input_test_case, dict):
        test_case_inputs = input_test_case.get("inputs", "No inputs")
        test_case_inputs = [f'{index}: "{input}"' for index, input in enumerate(test_case_inputs, start=1)]
        test_case_inputs = '\n'.join(test_case_inputs)

        return format_error_message(
                    custom_message=(f"TimeoutError\n\n"
                                    f"### How to fix it:\n"
                                    f"--------------\n"
                                    f"You got a Timeout Error, meaning this Input Test Case didn't complete after {default_timeout_seconds} seconds. "
                                    f"The test timed out during Input Test Case {input_test_case.get('id_input_test_case')}. To try and identify the problem, run your code like normal, but enter these EXACT inputs "
                                    f"in this order (without the quotes):\n"
                                    f"```\n{test_case_inputs}\n```\n"
                                    f"Most likely, "
                                    f"when your code uses these inputs your code never exits properly. This could be due to you asking for more inputs() than the test is expecting, or due to an infinite loop.\n\n"),
                    input_test_case=input_test_case,
                    current_test_name=current_test_name,
                    )
    else:
        return format_error_message(
                    custom_message=(f"TimeoutError\n\n"
                                    f"### How to fix it:\n"
                                    f"--------------\n"
                                    f"You got a Timeout Error, meaning the test couldn't run your code after {default_timeout_seconds} seconds. "
                                    f"Reach out to your professor."),
                    current_test_name=current_test_name,
                    )

# =========================
# ASSORTED HELPER FUNCTIONS
# =========================

def normalize_text(text):
    """
    Used by tests that look for specific output or input prompts.
    Makes all text lowercase, reduces all spacing to just one space
    and removes any extra symbols, except for negative signs and decimals
    associated with numbers. Handles recursion for iterables and dictionaries.
    """
    
    if isinstance(text, str):
        # Lowercase the input
        text = text.lower()
        
        # Replace newlines with a single space
        text = text.replace('\n', ' ')
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove periods not between digits
        text = re.sub(r'(?<!\d)\.(?!\d)', '', text)
        
        # If there is any character followed by a colon : other than a space, add a space
        text = re.sub(r'(:)(\S)', r'\1 \2', text)
    
        # Remove all other punctuation and symbols
        text = re.sub(r'[!"#$%&\'()*+,/:;<=>?@\[\]^_`{|}~]', '', text)
        
        # Temporarily replace negative signs with a placeholder
        text = re.sub(r'((?<=^)|(?<=\s))-(?=\d)', 'NEG_SIGN_PLACEHOLDER', text)
        
        # Replace remaining hyphens (e.g., between numbers) with a space
        text = text.replace('-', ' ')
        
        # Replace multiple spaces again in case punctuation removal created extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Restore negative signs
        text = text.replace('NEG_SIGN_PLACEHOLDER', '-')
        
        # Strip leading and trailing spaces
        return text.strip()
    
    elif isinstance(text, dict):
        # Apply normalize_text to both keys and values in the dictionary
        return {normalize_text(k): normalize_text(v) for k, v in text.items()}
    
    elif isinstance(text, Iterable) and not isinstance(text, (str, bytes)):
        # Apply normalize_text recursively for each item in the iterable (excluding strings/bytes)
        return type(text)(normalize_text(item) for item in text)
    
    else:
        # If the text is not a string, iterable, or dictionary, return as is
        return text

def insert_newline_at_last_space(s, width=74):
    """
    Because pytest fail messages have a specific width they are printed at,
    if I don't format my own error messages at that same width, they
    look much worse. This just adds in a new line before the width limit
    is hit for any string that you pass to it.
    """

    lines = []
    current_line = ""
    
    for char in s:
        current_line += char
        
        # If we hit a newline, append the current line and reset the line
        if char == '\n':
            lines.append(current_line.strip())  # Add the line and strip any extra spaces
            current_line = ""
            continue
        
        # If the current line exceeds the width, break at the last space
        if len(current_line) > width:
            # Find the last space before the width limit
            break_index = current_line.rfind(' ', 0, width)
            
            # If no space is found, break at the width limit
            if break_index == -1:
                break_index = width
            
            # Append the part of the line before the break
            lines.append(current_line[:break_index].strip())
            
            # Reset current_line to the remaining unprocessed part of the string
            current_line = current_line[break_index:].lstrip()  # Remove leading spaces in the next line
            
    # Append the last part of the string (if any)
    if current_line:
        lines.append(current_line.strip())
    
    return '\n'.join(lines)

def round_match(match):
    number = match.group()
    # Check if the number is a float (contains a decimal point)
    if '.' in number:
        # Convert to float and round to 2 decimal places
        # it uses the global_decimal_places that is defined at the top of this module.
        rounded_number = round(float(number), global_decimal_places)
        return f"{rounded_number}"
    else:
        # If it's an integer, just return it as is
        return number
    

def convert_pascal_case(pascal_str):
    # Convert to camelCase
    camel_case = pascal_str[0].lower() + pascal_str[1:]

    # Convert to snake_case
    snake_case = re.sub(r'([A-Z])', r'_\1', pascal_str).lower().lstrip('_')

    return [pascal_str, camel_case, snake_case]

# def prettify_dictionary(dictionary):
#     if not isinstance(dictionary, dict):
#         return dictionary
    
#     formatted_dict_str = ''
#     for key, value in dictionary.items():
#         formatted_dict_str += f'{key}: {value}\n'
    
#     # return it without the last newline
#     return formatted_dict_str[:-1]

def prettify_dictionary(dictionary, indent_level=0):
    if not isinstance(dictionary, dict):
        return str(dictionary)
    
    formatted_dict_str = ''
    indent = '-    ' * indent_level  # 4 spaces per indentation level
    
    for key, value in dictionary.items():
        formatted_dict_str += f'{indent}{key}: '
        if isinstance(value, dict):
            # Recursively format nested dictionaries with increased indentation
            formatted_dict_str += '\n' + prettify_dictionary(value, indent_level + 1) + '\n'
        else:
            formatted_dict_str += f'{value}\n'
    
    # Return without the last newline
    return formatted_dict_str.rstrip()

def get_similarity_feedback(normalized_expected_phrase, normalized_captured_strings_list, similarity_threshold=0.7):
    """
    Checks for similarity between a normalized expected phrase and a list of normalized captured strings.
    For close matches, shows side-by-side differences with markers for mismatches.
    
    Parameters:
        normalized_expected_phrase (str): The normalized phrase to match or find similarity to.
        normalized_captured_strings_list (list): A list of normalized strings to check against.
        similarity_threshold (float): The minimum similarity ratio to consider a close match.
        
    Returns:
        str: A feedback message with close matches sorted by similarity or a message indicating no similar strings were found.
    """
    # Check for an exact match
    if normalized_expected_phrase in normalized_captured_strings_list:
        return f"Exact match found for expected phrase: \"{normalized_expected_phrase}\""
    
    # Calculate similarity ratios for close matches
    similar_strings = []
    
    for captured_string in normalized_captured_strings_list:
        similarity = difflib.SequenceMatcher(None, normalized_expected_phrase, captured_string).ratio()
        
        if similarity >= similarity_threshold:
            # 1) Materialize the iterator into a list
            diff_lines = list(difflib.ndiff([normalized_expected_phrase], [captured_string]))

            # 2) Build a labeled copy instead of assigning into the iterator
            labeled = []
            for line in diff_lines:
                if line.startswith('- '):
                    labeled.append("Expected:".ljust(12) + line)
                elif line.startswith('+ '):
                    labeled.append("Yours:".ljust(12) + line)
                elif line.startswith('? '):
                    labeled.append("".ljust(12) + line)  # keep alignment
                else:
                    labeled.append("".ljust(12) + line)

            diff_string = '\n'.join(labeled)
            similar_strings.append(
                (similarity, f"Similarity: {similarity:.2f}\n{diff_string}")
            )
    # Sort similar strings by similarity score in descending order
    similar_strings.sort(reverse=True, key=lambda x: x[0])
    
    # Construct feedback message
    if similar_strings:
        feedback_message = (
            "Here are the closest matches to the expected phrase (sorted by similarity):\n\n"
            + "\n\n".join(item[1] for item in similar_strings)
        )
    else:
        feedback_message = (
            f"No strings in your code were found that were very similar to the expected phrase, so it likely wasn't due to a spelling error. Check whether you included the expected phrase at all, or whether your logic prevents the expected phrase from appearing."
        )
    
    return feedback_message

def sqlite_db_exists(expected_db_name = expected_database_name):
    return os.path.exists(expected_db_name)

def delete_sqlite_db():
    # Check if the database file exists
    if sqlite_db_exists():
        try:
            os.remove(expected_database_name)
            print(f"Database '{expected_database_name}' has been deleted.")
        except Exception as e:
            print(f"An error occurred while deleting the database: {e}")
    else:
        print(f"Database '{expected_database_name}' does not exist.")

def df_error_message_formatting(df):
    dtype_mapping = {
        'int64': 'int',
        'float64': 'float',
        'object': 'str'
    }
    rows = [
        f"{col} ({dtype_mapping.get(str(dtype), dtype)}): {list(df[col])}"
        for col, dtype in zip(df.columns, df.dtypes)
    ]
    return "\n".join(rows)

def normalize_dataframe(df):
    # Normalize column labels
    df.columns = [normalize_text(col) for col in df.columns]
    # Normalize every value in the DataFrame
    df = df.map(normalize_text)
    return df

def clear_database(table_name):
    try:
        assert sqlite_db_exists(expected_database_name)
        conn = sqlite3.connect(expected_database_name)
        cursor = conn.cursor()
        # Drop all tables (or specify which ones to drop)
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        # Alternatively, delete rows from a specific table
        # cursor.execute("DELETE FROM your_table_name")
        conn.commit()
        conn.close()
        return True
    except AssertionError:
        return False
    except Exception as e:
        print(f"Error clearing the database: {e}")
        return False

def check_forbidden_statements(code, forbidden_types):
    """
    Parses the given code and checks if any of the forbidden statement types are used.

    :param code: The source code as a string.
    :param forbidden_types: A tuple of AST node types that should not appear in the code.
    :return: A list of forbidden statements found.
    """
    tree = ast.parse(code)
    forbidden_statements = []

    class ForbiddenStatementVisitor(ast.NodeVisitor):
        def visit(self, node):
            if isinstance(node, forbidden_types):  # Now actually using forbidden_types
                forbidden_statements.append(f"Line {node.lineno}: {type(node).__name__} statement detected")
            self.generic_visit(node)  # Continue traversal

    visitor = ForbiddenStatementVisitor()
    visitor.visit(tree)

    return forbidden_statements

_MANGLE_PREFIX = re.compile(r"^_+[A-Za-z_][A-Za-z0-9_]*__")

def unmangle_name(name: str) -> str:
    """Turn '_SoccerTeam__wins' / '_soccerTeam__Wins' / '_soccer_team__wins' into '__wins' (logical)."""
    return _MANGLE_PREFIX.sub("__", str(name))

def unmangle_keys(obj):
    """
    Recursively unmangle dict keys in a structure (dict/list/tuple/scalars).
    Dict keys that are strings get unmangled via unmangle_name.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            nk = unmangle_name(k) if isinstance(k, str) else k
            out[nk] = unmangle_keys(v)
        return out
    elif isinstance(obj, list):
        return [unmangle_keys(x) for x in obj]
    elif isinstance(obj, tuple):
        return tuple(unmangle_keys(x) for x in obj)
    return obj

_MANGLED_RE = re.compile(r"^_+([A-Za-z_][A-Za-z0-9_]*)__([A-Za-z0-9_]+)$")

def _class_variants(name: str):
    # reuse your existing class-name variant logic if available; otherwise do a simple set
    try:
        return set(_name_variants_from_class_name(name))
    except Exception:
        return {name, name.lower(), name.replace("_", "").lower()}

def unmangle_and_collapse_keys(d, preferred_class = None):
    """
    Return a new dict where mangled keys like '_SoccerTeam__wins' and '_SponsoredTeam__wins'
    are both mapped to the logical '__wins' key. If multiple sources map to the same logical key,
    prefer the entry originating from `preferred_class` (if provided). Otherwise keep the first seen.
    """
    if not isinstance(d, dict):
        return d

    preferred_set = _class_variants(preferred_class) if preferred_class else set()
    out = {}
    winners = {}  # logical_key -> ("origin_class", original_key)

    for k, v in d.items():
        if isinstance(v, dict):
            v = unmangle_and_collapse_keys(v, preferred_class)
        elif isinstance(v, list):
            v = [unmangle_and_collapse_keys(x, preferred_class) for x in v]

        logical_key = k
        origin_class = None
        m = _MANGLED_RE.match(k) if isinstance(k, str) else None
        if m:
            origin_class = m.group(1)  # class part of the mangled name
            logical_key = "__" + m.group(2)  # '__wins' etc.

        if logical_key not in out:
            out[logical_key] = v
            winners[logical_key] = (origin_class, k)
        else:
            # decide whether to replace current winner
            prev_origin, _ = winners[logical_key]
            # Replace if this one matches the preferred class (by variant) and previous did not
            if preferred_set and origin_class:
                if origin_class in _class_variants(next(iter(preferred_set))) and (not prev_origin or prev_origin not in preferred_set):
                    out[logical_key] = v
                    winners[logical_key] = (origin_class, k)
            # else keep the first one seen

    return out

def _mro_class_variants_base_first(obj):
    """Return a list of lists of class-name variants for each class in MRO, base-first (exclude object)."""
    chain = []
    for C in obj.__class__.__mro__:
        if C is object:
            continue
        # base-first -> reverse later
        chain.append(C)
    chain.reverse()  # now base first
    out = []
    for C in chain:
        out.append(_name_variants_from_class_name(C.__name__))  # you already have this helper
    return out  # e.g. [["soccer_team","soccerTeam","SoccerTeam"], ["SponsoredTeam","sponsoredTeam","sponsored_team"]]

def _norm(s: str) -> str:
    return s.replace("_", "").casefold()

def _find_existing_mangled_key(obj, tail_variants):
    """
    Scan obj.__dict__ for any key that looks like _Class__Tail, where Tail matches one of tail_variants (case-insensitive).
    If multiple match, prefer the one whose class part is the *base-most* class by MRO.
    """
    d = getattr(obj, "__dict__", {})
    matches = []  # (origin_class_name, key)
    for key in d.keys():
        m = _MANGLED_RE.match(key)
        if not m:
            continue
        origin = m.group(1)
        tail = m.group(2)
        for tv in tail_variants:
            if tail.casefold() == tv.casefold():
                matches.append((origin, key))
                break
    if not matches:
        return None
    # Rank by base-first MRO
    mro_classes = [C.__name__ for C in obj.__class__.__mro__ if C is not object]
    rank = { _norm(C.__name__): i for i, C in enumerate(reversed(obj.__class__.__mro__)) }  # base has lowest i
    # Choose the one with smallest rank (closest to base)
    def keyfn(pair):
        origin = _norm(pair[0])
        return rank.get(origin, 10**9)
    matches.sort(key=keyfn)
    return matches[0][1]  # return the attribute key string like "_soccer_team__Wins"
