max_score = 13 # This value is pulled by yml_generator.py to assign a score to this test.
import re, ast
from conftest import default_module_to_test, format_error_message, exception_message_for_students

def test_09_create_method_overridden(current_test_name):
    try:

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

        assert class_node is not None, format_error_message(
            custom_message=f"A class named \"Movie\" or \"movie\" wasn't found in your {default_module_to_test}.py file.",
            current_test_name=current_test_name,
            input_test_case= None)

        # Check if 'create' method is defined in the Movie class
        create_method = next(
            (
                node
                for node in class_node.body
                if isinstance(node, ast.FunctionDef) and node.name == "create"
            ),
            None,
        )

        assert create_method is not None, format_error_message(
            custom_message=f"A method named \"create\" wasn't found in the Movie class.",
            current_test_name=current_test_name,
            input_test_case= None)
        
        assert any(
            decorator.id == "classmethod"
            for decorator in create_method.decorator_list
            if isinstance(decorator, ast.Name)
        ), format_error_message(
            custom_message=f"The \"create\" method isn't a class method (meaning it doesn't have @classmethod above the definition)",
            current_test_name=current_test_name,
            input_test_case= None)
    
    except AssertionError:
        raise
    
    except Exception as e:
        input_test_case = None
        exception_message_for_students(e, input_test_case, current_test_name)