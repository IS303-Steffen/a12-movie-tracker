max_score = 10  # This value is pulled by yml_generator.py to assign a score to this test.
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
import re, subprocess, sys, sqlite3

# Checks if the expected printed messages actually appear, but doesn't check for specific inputs or correct calculations.
def test_08_two_movies_deleted_one(current_test_name, input_test_cases):
    try:
        rec = pc_get_or_create(current_test_name, max_score)
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            input_test_case = {"id_input_test_case": None}
            exception_message_for_students(ValueError("input_test_cases should be a list of dictionaries. Contact your professor."), input_test_case, current_test_name) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        input_test_case = input_test_cases[5]
        case_id = input_test_case["id_input_test_case"]   
        inputs = input_test_case["inputs"]

        clear_database('movie')

        # Load in the student's code and capture output
        load_student_code(current_test_name, inputs, input_test_case, default_module_to_test)

        # Ensure the expected database is here
        if not sqlite_db_exists(expected_database_name):
            formatted = format_error_message(
                custom_message=(f"The tests are expecting a database named:\n"
                                f"```\n{expected_database_name}\n```\n"
                                f"But couldn't find a database with that exact name. Make sure your code creates a SQLite database using that name.\n\n"),
                current_test_name=current_test_name,
                input_test_case=input_test_case,
                display_inputs=True,
            )
            rec.fail_case(case_id=case_id, custom_message=formatted, case_type='input')
            return

        try:
            import pandas as pd
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
            import pandas as pd

        # Expected data
        expected_data = pd.DataFrame({
            "id": [2],
            "name": ["Pride & Prejudice"],
            "year_released": [2006],
            "status": ["Want to watch"],
            "rating": [None]
        })

        expected_data = normalize_dataframe(expected_data)

        expected_data_str = df_error_message_formatting(expected_data)
    
        db = sqlite3.connect(expected_database_name)

        db_tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        db_tables_str = '\n'.join([row[0] for row in db_tables])
        try:
            actual_data = pd.read_sql('select * from movie;', db)
        except Exception as e:
            formatted = format_error_message(
                custom_message=(f"Your {expected_database_name} database didn't have the expected table name:\n\n"
                                f"### Expected table name:\n"
                                f"```\nmovie\n```\n"
                                f"### Your table name(s):\n"
                                f"```\n{db_tables_str}\n```\n"
                                f"### How to fix it:\n"
                                f"You likely are making a spelling error in the name of your tables when creating your database. "
                                f"Try deleting and recreating your database and make sure the class name matches the name of the expected table name.\n"
                                f"\n\n"),
                current_test_name=current_test_name,
                input_test_case=input_test_case,
                display_inputs=True,
                )
            rec.fail_case(case_id=case_id, custom_message=formatted, case_type='input')
            return

        actual_data = normalize_dataframe(actual_data)
        actual_data_str = df_error_message_formatting(actual_data)

        try:
            pd.testing.assert_frame_equal(actual_data, expected_data, check_column_type=False, check_dtype=False, atol=.2)
        except AssertionError as e:
            formatted = format_error_message(
                custom_message=(f"Your {expected_database_name} database didn't contain the expected values.\n\n"
                                f"### Expected values:\n"
                                f"```\n{expected_data_str}\n```\n"
                                f"### Your values:\n"
                                f"```\n{actual_data_str}\n```\n"
                                f"### How to fix it:\n"
                                f"Make sure you are calling the columns (fields) the exact same thing as the expected "
                                f"values in the class where you are defining the column names. Also double check that "
                                f"the datatypes of each of the columns is the same as the expected values.\n\n"
                                f"This test is specifically checking if you can store 2 movies in the database, then delete one of them."
                                f"\n\n"),
                current_test_name=current_test_name,
                input_test_case=input_test_case,
                display_inputs=True,
                )
            rec.fail_case(case_id=case_id, custom_message=formatted, case_type='input')
            return
        
        rec.pass_case("ok")

    # assert raises an AssertionError, but I don't want to actually catch it
    # this is just so I can have another Exception catch below it in case
    # anything else goes wrong.
    except AssertionError:
        raise
    
    except Exception as e:
        # Handle other exceptions
        exception_message_for_students(e, input_test_case, current_test_name)
    finally:
        pc_finalize_and_maybe_fail(rec)
            