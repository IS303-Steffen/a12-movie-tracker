#### Assignment
# Movie Tracker

The point of this assignment is to combine OOP with databases through object relational mapping (ORM) using the `peewee` library. You'll make a simple movie tracker app where the user can enter in movies that they want to watch. Once the movies are watched, they can mark a movie as watched and provide it with a rating.

You can see a video example of the program <a href="https://www.youtube.com/watch?v=YJ6HeOos5JU&ab_channel=ProfSteffen" target="_blank">here.</a>

Enter all your code in the `a12_movie_tracker.py` file. Don't edit any of the other files.

## Libraries Required
- `peewee`

## Classes Required

#### Movie
- Details described in the logical flow section. This needs to inherit from the `peewee` `Base` class.

## Logical Flow:
#### Set Up the Database and ORM Structure:
- Using the `peewee` library, create a SQLite database called `movies.db` and define a `Movie` class that inherits from the `peewee` `Model` class.
- Define the `Movie` model with the following fields:
    - `id`: Auto-incrementing integer (Primary Key)
    - `name`: Name of the movie (CharField)
    - `year_released`: Year the movie was released (IntegerField)
    - `status`: Current status of the movie in the watchlist (default is `"Want to watch"`) (CharField)
    - `rating`: Rating of the movie (optional on creation, meaning null=True) (IntegerField)
- Use proper `peewee` methods so that the database is created with the `Movie` table (or connected if it already exists) when your code is run.

#### Menu Options:
- Design a menu with the following options (instructions for each option will be given after):
    - ```
      Movie Tracker Menu:
      1. Add a movie to the watchlist
      2. View all movies
      3. Update movie status to 'Watched' and provide a rating
      4. View only watched movies with rating of 4 or above
      5. Delete a movie
      6. Exit
      Choose an option (1-6):
      ```
- The menu should repeatedly show after each option is chosen until option `6` is entered. If any other input is given, it should just display:
    - `Invalid choice. Please choose again.`
- And then display the menu again.

#### Option 1: Add a movie to the watchlist
- If the user enters `1`, it should prompt the user to enter a movie name, and then the year released:
    - `Enter the movie name: `
    - `Enter the year released: `
- Then, you should enter the movie into the database using the `Movie` class's `.create()` method. After you create a movie, it should print out:
    - `Movie '<movie name>' added to the watchlist.`
- Here's an example of inputting a movie:
    - ```
      Enter the movie name: Inception
      Enter the year released: 2010
      Movie 'Inception' added to the watchlist.
      ```
- One additional requirement is that you need to override the `.create()` method to add some validation for the `year_released` field.
    - Remember that the `.create()` method is given to us from the `peewee` library. You can override it by creating a method with the same name inside your `Movie` class. The basic structure is given below that you can just copy in.
        - ```
            @classmethod
            def create(cls, **query):
                # ENTER YOUR YEAR VALIDATION LOGIC HERE:
                # The 'query' variable is a dictionary that has each of the fields of your class,
                # including year_released. You can use query.get('year_released') or
                # query['year_released'] to get access.

                # If the year_released is valid, make sure to call the original .create():
                return super().create(**query)
          ```
    - For a new movie to be created in the database, the year must:
        - Be exactly 4 digits long
        - Be between 1888 and the current year
            - You can hardcode these values. For a small optional challenge (e.g. for no extra points), see if you can dynamically get the current year.
        - To simplify the assignment, you can assume that the user will always enter in digits for the year (e.g. they will never enter letters like `bla bla`. But if you want a little extra challenge, feel free to also handle non-digit inputs).
    - Example of valid year:
        - `1991`
    - Examples of invalid years:
        - `91`
        - `6007`
        - `1800`
    - If an invalid year is entered, the movie shouldn't be saved in the database (even though `.create()` is called) and it should print out:
        - `Movie not saved because of an invalid year. Please provide a valid 4-digit year.`
        - It should then just display the Movie Tracker Menu again. 

    

#### Option 2: View all movies
- If the user enters `2`, it should print out the movie information for every movie in your `movies.db` database.
- To do this, add a method called `get_info` to your `Movie` class. It should return a string like this:
    - `ID: <id> | Name: <movie name> | Year: <year released> | Status: <movie status> | Rating: <movie_rating>`
- Below is an example of what it would look like if option 2 was chosen when 2 movies were in the database, 1 that hasn't been watched yet, and one that has been watched and rated:

    - ```
      ID: 1 | Name: Inception | Year: 2010 | Status: Watched | Rating: 5
      ID: 2 | Name: Pride & Prejudice | Year: 2006 | Status: Want to watch | Rating: None
      ```
- To simplify the assignment, you can assume that option `2` will only be chosen when there are movies in the database. If you want to add logic for handling the case of no movies being present for extra practice, feel free.

#### Option 3: Update movie status to 'Watched' and rate
- If the user enters `3`, it should prompt the user for a movie ID:
    - `Enter the ID of the movie you've watched: `
- It should then prompt the user for a rating:
    - `Enter your rating (1-5): `
- Your program should then call a custom method called `rate_movie` on the `Movie` object corresponding to the ID entered. `rate_movie` should have a parameter for the rating. It should update the `Movie` object's `status` to "Watched" and the `rating` to whatever rating was entered, and then save the updated values to the database.
- To simplify the assignment, you can assume that the user will always enter in a valid, existing movie ID and a valid rating between 1 and 5. If you want to add logic for error handling those situations for extra practice, feel free.

#### Option 4: View watched movies with a rating of 4 or above.
- If the user enters `4`, it should do the exact same thing as option `2`, but only for movies that have a `rating` value of 4 or above.
- For example, if you had one movie rated at a 4 or more, it would just display that movie:
    - ```
      ID: 1 | Name: Inception | Year: 2010 | Status: Watched | Rating: 5
      ```
- To simplify the assignment, you can assume that option `4` will only be chosen when there is at least 1 movie with a rating of 4 or above. If you want to add logic for handling the case of no movies being present for extra practice, feel free.

#### Option 5: Delete a movie
- If the user enters `5` it should prompt the user:
    - `Enter the ID of the movie to delete: `
- After a movie ID is entered, it should delete the movie from the database and print out:
    `Movie '<movie name>' deleted successfully.`
- Here's an example:
    - ```
      Enter the ID of the movie to delete: 1
      Movie 'Inception' deleted successfully.
      ```
- To simplify the assignment, you can assume that the user always enter in a valid existing id when trying to delete. If you want to add logic for error handling those situations for extra practice, feel free.

#### Option 6: Exit
- If the user enters `6` then it should print:
    - `Goodbye!`
- Then the program should end.

Push your code up to your GitHub repository to receive credit. If you pass all the automated tests you will receive full credit.

## Grading Rubric
See `Rubric.md`

## Example Output
See a video example <a href="https://www.youtube.com/watch?v=YJ6HeOos5JU&ab_channel=ProfSteffen" target="_blank">here.</a>

This is an example of adding 3 movies, rating 2 of them, and then going through all the options.

```
Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 1

Enter the movie name: Inception
Enter the year released: 2010

Movie 'Inception' added to the watchlist.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 1

Enter the movie name: Pride & Prejudice
Enter the year released: 2006

Movie 'Pride & Prejudice' added to the watchlist.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 1

Enter the movie name: Dune
Enter the year released: 21

Movie not saved because of an invalid year. Please provide a valid 4-digit year.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 1

Enter the movie name: Dune
Enter the year released: 2021

Movie 'Dune' added to the watchlist.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 2

ID: 1 | Name: Inception | Year: 2010 | Status: Want to watch | Rating: None
ID: 2 | Name: Pride & Prejudice | Year: 2006 | Status: Want to watch | Rating: None
ID: 3 | Name: Dune | Year: 2021 | Status: Want to watch | Rating: None

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 3

Enter the ID of the movie you've watched: 1
Enter your rating (1-5): 5

Movie 'Inception' updated to 'Watched' with rating 5.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 3

Enter the ID of the movie you've watched: 2
Enter your rating (1-5): 2

Movie 'Pride & Prejudice' updated to 'Watched' with rating 2.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 2

ID: 1 | Name: Inception | Year: 2010 | Status: Watched | Rating: 5
ID: 2 | Name: Pride & Prejudice | Year: 2006 | Status: Watched | Rating: 2
ID: 3 | Name: Dune | Year: 2021 | Status: Want to watch | Rating: None

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 4

ID: 1 | Name: Inception | Year: 2010 | Status: Watched | Rating: 5

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 5

Enter the ID of the movie to delete: 1

Movie 'Inception' deleted successfully.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 2

ID: 2 | Name: Pride & Prejudice | Year: 2006 | Status: Watched | Rating: 2
ID: 3 | Name: Dune | Year: 2021 | Status: Want to watch | Rating: None

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 6

Goodbye!
```