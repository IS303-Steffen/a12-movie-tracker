
## Rubric
Your grade is based on whether you pass the automated tests, listed below.

The tests will ignore spacing, capitalization, and punctuation, but you will fail the tests if you spell something wrong or calculate something incorrectly.


<table border="1" style="width: 100%; text-align: center;">
<thead style="text-align: center;">
    <tr>
        <th style="text-align: center;">Test</th>
        <th style="text-align: center;">Description</th>
        <th style="text-align: center;">Points</th>
    </tr>
</thead>
<tbody>
    <tr style="text-align: left">
        <td>1. Input Prompts</td>
        <td>
        <b>Input test cases used:</b> 1-7<br><br>
        Your input prompts must be the same as the expected input prompts of each input test case. 
        <br>
        <br>
        See the <code>descriptions_of_test_cases</code> folder for expected input prompts for each input test case.
        </td>
        <td style="text-align: center">5</td>
    </tr>
    <tr style="text-align: left">
        <td>2. Printed Messages</td>
        <td>
        <b>Input test cases used:</b> 1-7<br><br>
        Your printed output must be the same as the expected output of each input test case. 
        <br>
        <br>
        See the <code>descriptions_of_test_cases</code> folder for expected printed messages for each input test case.
        </td>
        <td style="text-align: center">15</td>
    </tr>
    <tr style="text-align: left">
        <td>3. Creating a single movie</td>
        <td>
        <b>Input test cases used:</b> 1<br><br>
        Your database must contain a movie.
        <td style="text-align: center">10</td>
    </tr>
    <tr style="text-align: left">
        <td>4. Year released validation</td>
        <td>
        <b>Input test cases used:</b> 2<br><br>
        Your database must contain a single movie, despite trying to enter a second movie with improper year_released data.
        <td style="text-align: center">12</td>
    </tr>
    <tr style="text-align: left">
        <td>5. Two movies no updates</td>
        <td>
        <b>Input test cases used:</b> 3<br><br>
        Your database must contain 2 movies.
        <td style="text-align: center">10</td>
    </tr>
    <tr style="text-align: left">
        <td>6. Two movies updated one</td>
        <td>
        <b>Input test cases used:</b> 4<br><br>
        Your database must contain 2 movies, with the status and rating updated for one of them.
        <td style="text-align: center">10</td>
    </tr>
    <tr style="text-align: left">
        <td>7. Two movies updated both</td>
        <td>
        <b>Input test cases used:</b> 5<br><br>
        Your database must contain 2 movies, with the status and rating updated for both of them.
        <td style="text-align: center">10</td>
    </tr>
    <tr style="text-align: left">
        <td>8. Two movies deleted one</td>
        <td>
        <b>Input test cases used:</b> 6<br><br>
        Your database must contain only 1 movie after entering 2 and deleting 1.
        <td style="text-align: center">10</td>
    </tr>
    <tr style="text-align: left">
        <td>9. Create method overridden</td>
        <td>
        <b>Input test cases used:</b> None<br><br>
        Your <code>Movie</code> class must contain an overridden version of the <code>create</code> method.
        <td style="text-align: center">13</td>
    </tr>
    <tr>
        <td style="text-align: left">10. Sufficient Comments</td>
        <td style="text-align: left">
        <b>Input test cases used:</b> None<br><br>
        Your code must include at least <code>10</code> comments. You can use any form of commenting:
        <ul>
          <li><code>#</code></li> 
          <li><code>''' '''</code></li>
          <li><code>""" """</code></li>
        </ul>
        </td>
        <td style="text-align: center">5</td>
    </tr>
    <tr>
        <td colspan="2">Total Points</td>
        <td>100</td>
  </tr>
</tbody>
</table>

## Test Cases
If you fail a test during a specific test case, see the `descriptions_of_test_cases` folder for the following:
<table border="1" style="width: 100%; text-align: left;">
  <tr>
    <th>Test Case</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>Input Test Case 01</td>
    <td>Creating a single movie and checking if it is stored in the database</td>
  </tr>
  <tr>
    <td>Input Test Case 02</td>
    <td>Creating one movie successfully, then unsuccessfully creating another movie when using incorrectly formatted year data.</td>
  </tr>
  <tr>
    <td>Input Test Case 03</td>
    <td>Creating 2 movies and viewing them</td>
  </tr>
  <tr>
    <td>Input Test Case 04</td>
    <td>Creating 2 movies, updating the status and rating of 1 of them, then viewing them.</td>
  </tr>
  <tr>
    <td>Input Test Case 05</td>
    <td>Creating 2 movies, updating the status and rating of both, but only 1 of them has a score over 4. Then checking that only 1 movie appears when choosing option 4.</td>
  </tr>
  <tr>
    <td>Input Test Case 06</td>
    <td>Creating 2 movies, deleting one and ensuring it doesn't show up when viewing all movies.</td>
  </tr>
  <tr>
    <td>Input Test Case 07</td>
    <td>Providing an incorrect input for the Movie Tracker Menu</td>
  </tr>
</table>
