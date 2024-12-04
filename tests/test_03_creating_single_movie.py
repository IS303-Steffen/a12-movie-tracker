max_score = 10  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import (normalize_text, load_student_code, format_error_message, exception_message_for_students, round_match, df_error_message_formatting,
    normalize_dataframe, get_similarity_feedback, sqlite_db_exists, delete_sqlite_db, expected_database_name
)
import re, subprocess, sys, sqlite3, pytest

# Checks if the expected printed messages actually appear, but doesn't check for specific inputs or correct calculations.
def test_03_creating_single_movie(current_test_name, input_test_cases):
    try:
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            input_test_case = {"id_input_test_case": None}
            exception_message_for_students(ValueError("input_test_cases should be a list of dictionaries. Contact your professor."), input_test_case, current_test_name) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        input_test_case = input_test_cases[0]        
        delete_sqlite_db()

        inputs = input_test_case["inputs"]

        # Load in the student's code and capture output
        load_student_code(current_test_name, inputs, input_test_case)

        # Ensure the expected database is here
        assert sqlite_db_exists(), format_error_message(
            custom_message=(f"The tests are expecting a database named:\n\n"
                            f"\"{expected_database_name}\"\n\n"
                            f"But couldn't find a database with that exact name. Make sure your code creates a SQLite database using that name.\n\n"),
            current_test_name=current_test_name,
            input_test_case=input_test_case,
            display_inputs=True,
        )

        try:
            import pandas as pd
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
            import pandas as pd

        # Expected data
        expected_data = pd.DataFrame({
            "id": [1],
            "name": ["Inception"],
            "year_released": [2010],
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
            pytest.fail(format_error_message(
            custom_message=(f"Your {expected_database_name} is expected didn't have the expected table name:\n\n"
                            f"EXPECTED TABLE NAME:\n"
                            f"--------------------\n"
                            f"movie\n\n"
                             f"YOUR TABLE NAME(S):\n"
                            f"--------------------\n"
                            f"{db_tables_str}\n\n"
                            f"HOW TO FIX IT:\n"
                            f"--------------\n"
                            f"You likely are making a spelling error in the name of your tables when creating your database. "
                            f"Try deleting and recreating your database and make sure the class name matches the name of the expected table name.\n"
                            f"\n\n"),
            current_test_name=current_test_name,
            input_test_case=input_test_case,
            display_inputs=True,
        ))

        actual_data = normalize_dataframe(actual_data)
        actual_data_str = df_error_message_formatting(actual_data)

        try:
            pd.testing.assert_frame_equal(actual_data, expected_data, check_column_type=False, check_dtype=False, atol=.2)
        except AssertionError as e:
            pytest.fail(format_error_message(
            custom_message=(f"Your {expected_database_name} database didn't contain the expected values.\n\n"
                            f"EXPECTED VALUES:\n"
                            f"----------------\n"
                            f"{expected_data_str}\n\n"
                             f"YOUR VALUES:\n"
                            f"-------------\n"
                            f"{actual_data_str}\n\n"
                            f"HOW TO FIX IT:\n"
                            f"--------------\n"
                            f"Make sure you are calling the columns (fields) the exact same thing as the expected "
                            f"values in the class where you are defining the column names. Also double check that "
                            f"the datatypes of each of the columns is the same as the expected values\n"
                            f"\n\n"),
            current_test_name=current_test_name,
            input_test_case=input_test_case,
            display_inputs=True,
        ))

            
    # assert raises an AssertionError, but I don't want to actually catch it
    # this is just so I can have another Exception catch below it in case
    # anything else goes wrong.
    except AssertionError:
        raise
    
    except Exception as e:
        # Handle other exceptions
        exception_message_for_students(e, input_test_case, current_test_name)

            