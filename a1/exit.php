<?php session_start();?>
<!DOCTYPE html>
<html>

<head>
    <title>Funny Quiz</title>
</head>

<body>
    <h1>Exit</h1>
    <?php
    if (isset($_POST['Restart'])) {
        header("Location: welcome.php");
        exit();
    }
    $filePath = 'record.txt'; // Replace with your actual file path
    $nameToUpdate = isset($_SESSION['name']) ? $_SESSION['name'] : ''; // Check if the session exist if exist return _session[name] else return ''

    // Read the file into an array of lines
    $lines = file($filePath, FILE_IGNORE_NEW_LINES);

    // Loop through each line to find and update the score for the given name
    foreach ($lines as $line) {
        // Check if the line contains the name we're looking for
        if (strpos($line, $nameToUpdate) !== false) {
            // Separate the name and the score
            list($currentName, $currentScore) = explode(',', $line, 2);
            // Update the score if the current name matches the name we're updating
        }
    }
    if (isset($_POST['Restart'])) {
        header("Location: score.php");
        exit();
    }

    echo "<p>NickName: $currentName</p>";
    echo "<p>Overall Point: $currentScore</p>";
    
    ?>
    <form name="QuizForm" action="Exit.php" method="post">
            &nbsp;<input type="submit" name="Restart" value="Restart" />
    </form>
</body>
</html>
