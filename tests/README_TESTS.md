### A Quick Note to Students:
If you are student and found this, you might be looking for the README file, not this README_TESTS file. However, feel free to look at the files in this folder if you are curious about how automated testing works. But don't alter any of the files in the tests folder. GitHub will flag it and you may not get graded correctly.

# Structure of Tests
- Each test is run using pytest
    - `pip install pytest`
- Each test is contained in the tests folder and will automatically be discovered by pytest as long as it begins with `test` as a prefix.
- Any fixtures (special pytest functions that are reset each time they are referenced) contained in `conftest.py` are automatically discovered by pytest and made available as function parameters in each of the test files.
- Individual test cases are pulled in from the `test_cases_final.json` file.

# Generating Test Cases
> Rather than manually typing out individual test cases, you can use `capture_test_cases.py` to generate test case data for you based on a working solution that you provide it.
1.  Update `capture_test_cases.py` with the filename of solution file for the assignment
2. Run `capture_test_cases.py`. You will notice it will automatically start whatever solution file you reference in it. Run the solution code using specific test case prompts for a specific case you'd like the students' code to be able to handle
3. When `capture_test_cases.py` finishes running, it outputs the inputs, input prompts, printed messages, and all variables captured during the run to a .json file called `test_cases_drafts.json`. It will ask you to give a description to the test case when you finish running through your solution script. Each additional test case run will append an additional test case to the .json file.
4. When you are finished generating test cases, you should copy `test_cases_drafts.json` to `test_cases_final.json`, which is referenced by conftest.py in a fixture called `test_cases`. The `test_cases` fixture can be called by any pytest.
5. Once the `test_cases_final.json` is set up, you can also run `generate_markdown_test_cases.py`, which helps generate tables for each test case for use in the `README.md` instructions. That saves hours of time writing instructions.

# Setting Up Tests for GitHub Classroom
- This repository needs to be a set as a public template in the GitHub settings after it has been pushed to GitHub.
- GitHub Classroom uses GitHub Actions to run an autograding workflow every time a student pushes up their code. This is what will run the pytests.
- GitHub Actions are reliant on a .yml configuration file located in .github/workflows. To automatically create this file based on the `test_*.py` files in the tests/ folder, just run the `yml_generator.py` script before pushing the repository to GitHub and referencing.
    - Make sure you install ruamel.yaml for this to work
        - `pip install ruamel.yaml`
    - IMPORTANT: Do not create any tests in GitHub Classroom when making the assignment. If you do, it will overwrite the .yml configuration. It is far quicker to just run the script here and not worry about setting any tests up through their GUI.
    - The classroom.yml configuration currently created uses these GitHub actions after setting up an ubuntu machine and installing python:
        - [classroom-resources/autograding-command-grader@v1](https://github.com/classroom-resources/autograding-command-grader)
            - This just allows you to run a task and if it succeeds, assign points to successful execution
        - [classroom-resources/autograding-grading-reporter@v1](https://github.com/classroom-resources/autograding-grading-reporter)
            - This collects the points from the autograding command grader (or other graders that GitHub provides) and then reports the points back to GitHub Classroom. It also displays them for the student if they go into the Actions section of their repository.
        - You could also use the python autograder [classroom-resources/autograding-python-grader@v1](https://github.com/classroom-resources/autograding-python-grader) but I moved away from this because it didn't allow specifying a specific version of python. 

# Checklist For Submitting to GitHub
1. Ensure all tests pass using the solution file
2. In conftest.py:
    1. default_module_to_test in conftest.py has the proper file name for the student file name
    2. The timeout time is set to 6 seconds
3. Ensure each of the test files has the correct max_score set at the top of the file, and that it matches the README.md.
4. Run the generate_yml.py
5. Ensure .gitignore includes:
    - \*solution\*.py
    - ~$*.xlsx
    - .vscode*
    - student_test_module.py
    - test_cases_table_output.html
    - test_cases_drafts.json
6. Push all changes to GitHub
7. In GitHub Classroom use the following settings:
    - Private repository visibility
    - Don't grant admin status
    - Copy the default branch only
    - Don't use an online IDE
    - Use YAML (DO NOT ADD ANY GITHUB PRESET TESTS)
    - Run Autograding every time a a student submits an assignment
    - add the following as protected filepaths:
        - github/**/*
        - tests/\*test\*
    - Enable feedback pull requests
8. After publishing, use another GitHub account to ensure that the link to the assignment works and that when code is pushed the automated grading works.

