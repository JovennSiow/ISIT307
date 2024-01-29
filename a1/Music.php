<?php session_start(); ?>
<!DOCTYPE html>
<html>

<head>
    <title>Funny Quiz</title>
    <h1>Music</h1>
</head>

<body>
    <?php
    if (isset($_POST['Form'])) {
        $score = 0;
        $numofcorrect = 0;
        $numofwrong = 0;
        $userAnswers = $_POST['ans']; // This should be an array of answers indexed by question
        if (isset($_POST['ans'])) {
            $userAnswers = $_POST['ans'];
            $index = 0; // Initialize a counter for the questions

            foreach ($_SESSION['questions_answers'] as $question => $correctAnswer) {
                // Check if an answer was provided for the question index
                if (isset($userAnswers[$index])) {
                    // Compare the provided answer with the correct answer
                    if ($userAnswers[$index] === $correctAnswer) {
                        // The user's answer is correct
                        $score += 4;
                        $numofcorrect++;
                    } else {
                        // The user's answer is incorrect
                        $score -= 2;
                        $numofwrong++;
                    }
                } else {
                    // No answer was provided for this question
                    $score -= 2;
                    $numofwrong++;
                }
                $index++; // Increment the index for the next question
            }
        } else {
            $numofwrong += count($_SESSION['questions_answers']);
        }
        header("Location: score.php?score=$score&numofcorrect=$numofcorrect&numofwrong=$numofwrong");
        exit();
    
    }
    $filename = 'Musicqns.txt';

    if (file_exists($filename)) {
        $lines = file($filename, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        // Initialize an associative array to hold questions and answers
        $qaArray = [];
        $imagearray = [];

        $question = "";
        foreach ($lines as $line) {
            if (strpos($line, "Ans:") === false && strpos($line, "Image:") === false) {
                // It's a question
                $question = $line;
            }
            else if(strpos($line, "Ans:") === false && strpos($line, "Description:") === false)
            {
                $image = trim(str_replace('Image:', '', $line));
                $imagearray[$question] = $image;
            }
            else {
                // It's an answer, associate with the question
                $answer = trim(str_replace('Ans:', '', $line));
                $qaArray[$question] = $answer;
            }
        }
        
        // Get three random keys (questions)
        $randomQuestions = array_rand($qaArray, 3);

        // Store questions and answers in the session
        $_SESSION['questions_answers'] = [];
        foreach ($randomQuestions as $question) {
            $_SESSION['questions_answers'][$question] = $qaArray[$question];
        }
        ?>
        <form name="AnsForm" action="country.php" method="post">
            <?php
                $index = 0; // Initialize a counter for the questions
                foreach ($_SESSION['questions_answers'] as $question => $correctAnswer) {
                    // Display the question
                    echo "<p>$question</p>";
                    echo '<img src="' . htmlspecialchars($imagearray[$question]) . '" alt="Image" style="max-width: 15%; height: auto;"><br>';
                    echo "Ans: "."<input type='Text' name='ans[$index]'/>";
                    $index++; // Increment the index for the next question
            }
            ?>
            <p><input type="submit" name="Form" value="Send Form" /></p>
        </form>
        <?php
        //display the qns and ans to check
        echo "<h3>Session Data:</h3>";
        echo "<pre>"; // Preformatted text tag for readability
        foreach ($_SESSION as $key => $value) {
            echo htmlspecialchars($key) . ' => ' . htmlspecialchars(print_r($value, true)) . "<br>";
        }
        echo "</pre>";
        ?>

    <?php
    } else {
        echo "File does not exist.";
    }
    ?>
</body>

</html>
