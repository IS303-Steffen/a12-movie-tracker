# Test Case 2

## Description
Creating one movie successfully, then unsuccessfully creating another movie when using incorrectly formatted year data.

## Inputs
```
1: "1"
2: "Inception"
3: "2010"
4: "1"
5: "Pride & Prejudice"
6: "06"
7: "1"
8: "Pride & Prejudice"
9: "6007"
10: "1"
11: "Pride & Prejudice"
12: "1800"
13: "6"
```

## Expected Input Prompts
```
1: "Choose an option (1-6): "
2: "Enter the movie name: "
3: "Enter the year released: "
```

## Expected Printed Messages
```
1: "Movie Tracker Menu:"
2: "1. Add a movie to the watchlist"
3: "2. View all movies"
4: "3. Update movie status to 'Watched' and provide a rating"
5: "4. View only watched movies with rating of 4 or above"
6: "5. Delete a movie"
7: "6. Exit"
8: "Movie 'Inception' added to the watchlist."
9: "Movie not saved because of an invalid year. Please provide a valid 4-digit year."
10: "Goodbye!"
```

## Example Output **(combined Inputs, Input Prompts, and Printed Messages)**
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
Enter the year released: 06

Movie not saved because of an invalid year. Please provide a valid 4-digit year.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 1

Enter the movie name: Pride & Prejudice
Enter the year released: 6007

Movie not saved because of an invalid year. Please provide a valid 4-digit year.

Movie Tracker Menu:
1. Add a movie to the watchlist
2. View all movies
3. Update movie status to 'Watched' and provide a rating
4. View only watched movies with rating of 4 or above
5. Delete a movie
6. Exit
Choose an option (1-6): 1

Enter the movie name: Pride & Prejudice
Enter the year released: 1800

Movie not saved because of an invalid year. Please provide a valid 4-digit year.

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
