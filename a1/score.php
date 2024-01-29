<?php session_start();?>
<!DOCTYPE html>
<html>

<head>
    <title>Funny Quiz</title>
</head>

<body>
    <h1>Result</h1>
    <?php
    if (isset($_GET['numofcorrect'])) {
        $_SESSION['numofcorrect'] = $_GET['numofcorrect'];
    }
    if (isset($_GET['numofwrong'])) {
        $_SESSION['numofwrong'] = $_GET['numofwrong'];
    }
    if (isset($_GET['score'])) {
        $_SESSION['score'] = $_GET['score'];
    }
    if (isset($_POST['Exit'])) {
        header("Location: Exit.php");
        exit();
    }
    if (isset($_POST['LeaderBoard'])) {
        header("Location: leaderboard.php");
        exit();
    }
    if (isset($_POST['countries'])) {
        header("Location: country.php");
        exit();
    }
    if (isset($_POST['Music'])) {
        header("Location: Music.php");
        exit();
    }
    $filePath = 'record.txt';
    $nameToUpdate = isset($_SESSION['name']) ? $_SESSION['name'] : ''; // Check if the session exist if exist return _session[name] else return ''
    $newScore = $_SESSION['score']; // The additional score to add to the existing score

    // Read the file into an array of lines
    $lines = file($filePath, FILE_IGNORE_NEW_LINES);

    // Array to hold updated lines
    $updatedLines = [];

    // Loop through each line to find and update the score for the given name
    foreach ($lines as $line) {
        // Check if the line contains the name we're looking for
        if (strpos($line, $nameToUpdate) !== false) {
            // Separate the name and the score
            list($currentName, $currentScore) = explode(',', $line, 2);
            // Update the score if the current name matches the name we're updating
            if (trim($currentName) === $nameToUpdate) {
                // Convert the current score to an integer and add the additional score
                $currentScore = (int)$currentScore + $newScore;
                // Reconstruct the line with the new score
                $line = $currentName . ',' . $currentScore;
            }
        }
        $updatedLines[] = $line;
    }
    echo "<p>Number of correct: ". $_SESSION['numofcorrect'];
    echo "<p>Number of wrong: ". $_SESSION['numofwrong'];
    echo "<p>Your current point: ". $_SESSION['score'];
    echo "<p>Your overall point: $currentScore</p>";
    // Write the updated lines back to the file
    file_put_contents($filePath, implode("\n", $updatedLines));
    echo "---------------------------------------------------------------------------------------------------------"
    ?>
    <h2>New Quiz</h2>
    <?php

    ?>
    <form name="QuizForm" action="score.php" method="post">
            &nbsp;<input type="submit" name="countries" value="Countries" style="margin-right: 30px;"/><input type="submit" name="Music" value="Music"/></p>
            &nbsp;<p>&nbsp;<input type="submit" name="LeaderBoard" value="LeaderBoard">&nbsp;<input type="submit" name="Exit" value="Exit"/></p>
    </form>
</body>
</html>
