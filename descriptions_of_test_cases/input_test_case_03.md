# Test Case 3

## Description
Creating 2 movies and viewing them

## Inputs
```
1: "1"
2: "Inception"
3: "2010"
4: "1"
5: "Pride & Prejudice"
6: "2006"
7: "2"
8: "6"
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
9: "Movie 'Pride & Prejudice' added to the watchlist."
11: "ID: 1 | Name: Inception | Year: 2010 | Status: Want to watch | Rating: None"
12: "ID: 2 | Name: Pride & Prejudice | Year: 2006 | Status: Want to watch | Rating: None"
13: "Goodbye!"
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
Enter the year released: 2006

Movie 'Pride & Prejudice' added to the watchlist.

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
