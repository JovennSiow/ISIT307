<?php session_start();?>
<!DOCTYPE html>
<html>

<head>
    <title>Funny Quiz</title>
</head>

<body>
    <?php
    if (isset($_GET['numofcorrect'])) {
        $numofcorrect = $_GET['numofcorrect'];
        echo "<p>Number of correct: $numofcorrect</p>";
    }
    if (isset($_GET['numofwrong'])) {
        $numofwrong = $_GET['numofwrong'];
        echo "<p>Number of wrong: $numofwrong</p>";
    }
    if (isset($_GET['score'])) {
        $score = $_GET['score'];
        echo "<p>Your current point is: $score</p>";
    }
    if (isset($_POST['Back'])) {
        header("Location: topic.php");
        exit();
    }
    if (isset($_POST['Exit'])) {
        header("Location: welcome.php");
    }
    if (isset($_POST['LeaderBoard'])) {
        header("Location: leaderboard.php");
    }
    $filePath = 'record.txt'; // Replace with your actual file path
    $nameToUpdate = isset($_SESSION['name']) ? $_SESSION['name'] : ''; // Check if the session exist if exist return _session[name] else return ''
    $newScore = $score; // The additional score to add to the existing score

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
                $line = $currentName . ', ' . $currentScore;
            }
        }
        $updatedLines[] = $line;
    }
    echo "<p>Your overall point: $currentScore</p>";
    // Write the updated lines back to the file
    file_put_contents($filePath, implode("\n", $updatedLines));

    ?>
    <form name="QuizForm" action="score.php" method="post">
            &nbsp;<input type="submit" name="Back" value="Back"></p>&nbsp;<input type="submit" name="Exit" value="Exit"></p>&nbsp;<input type="submit" name="LeaderBoard" value="LeaderBoard"></p>
    </form>
</body>
</html>
