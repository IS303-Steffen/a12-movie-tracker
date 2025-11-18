max_score = 13  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import (
    normalize_text,
    load_student_code,
    format_error_message,
    exception_message_for_students,
    round_match,
    df_error_message_formatting,
    normalize_dataframe,
    get_similarity_feedback,
    sqlite_db_exists,
    clear_database,
    expected_database_name,
    pc_get_or_create,
    pc_finalize_and_maybe_fail,
    record_failure,
    default_module_to_test
)
import ast

def test_09_create_method_overridden(current_test_name):
    try:
        rec = pc_get_or_create(current_test_name, max_score)
        with open(f"{default_module_to_test}.py", "r") as file:
            tree = ast.parse(file.read())

        # Find the Movie class in the AST, case-insensitive
        class_node = next(
            (
                node
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name.lower() == "movie"
            ),
            None,
        )

        if class_node is None:
            formatted = format_error_message(
                custom_message=f"A class named \"Movie\" or \"movie\" wasn't found in your {default_module_to_test}.py file.",
                current_test_name=current_test_name,
                input_test_case= None)
            record_failure(current_test_name, formatted_message=formatted)
            return

        # Check if 'create' method is defined in the Movie class
        create_method = next(
            (
                node
                for node in class_node.body
                if isinstance(node, ast.FunctionDef) and node.name == "create"
            ),
            None,
        )

        if create_method is None:
            formatted = format_error_message(
                custom_message=f"A method named \"create\" wasn't found in the Movie class.",
                current_test_name=current_test_name,
                input_test_case= None)
            record_failure(current_test_name, formatted_message=formatted)
            return
        
        if not any(
            decorator.id == "classmethod"
            for decorator in create_method.decorator_list
            if isinstance(decorator, ast.Name)
        ):
            formatted = format_error_message(
                custom_message=f"The \"create\" method isn't a class method (meaning it doesn't have @classmethod above the definition)",
                current_test_name=current_test_name,
                input_test_case= None)
            record_failure(current_test_name, formatted_message=formatted)
            return
        
        rec.pass_case('ok')
    
    except AssertionError:
        raise
    except Exception as e:
        input_test_case = None
        exception_message_for_students(e, input_test_case, current_test_name)
    finally:
        pc_finalize_and_maybe_fail(rec)