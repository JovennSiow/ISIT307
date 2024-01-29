<?php session_start();?>
<!DOCTYPE html>
<html>
<head>
    <title>Funny Quiz</title>
    <h1>Welcome to Funny facts</h1>
</head>

<body>
    <?php
    $Name = "";
    if (isset($_POST['countries'])) {
        $Name = $_POST['nickname'];
        if ($Name != '') {
            $_SESSION['name'] = $Name;
            $lines = file("record.txt",FILE_SKIP_EMPTY_LINES);
             // Initialize a variable to store the result
            $nameFound = false;

            // Loop through the lines to search for the name
            foreach ($lines as $line) {
                echo "$line";
                list($currentName, $currentScore) = explode(",", $line, 2);
                if (strcasecmp(trim($currentName), $Name) == 0) {
                    $nameFound = true;
                    break;
                }
            }
            echo "Name Found After Check: " . ($nameFound ? "true" : "false") . "<br>";
            if ($nameFound == false) {
                file_put_contents("record.txt", "\n".$Name.",0", FILE_APPEND);
            }
            header("Location: country.php");
            exit();
        } else {
            echo "<p>You need to enter a NickName.</p>\n";
        }
    }
    if (isset($_POST['Music'])) {
        $Name = $_POST['nickname'];
        if ($Name != '') {
            $_SESSION['name'] = $Name;
            $lines = file("record.txt",FILE_SKIP_EMPTY_LINES);
                // Initialize a variable to store the result
            $nameFound = false;

            // Loop through the lines to search for the name
            foreach ($lines as $line) {
                echo "$line";
                list($currentName, $currentScore) = explode(",", $line, 2);
                if (strcasecmp(trim($currentName), $Name) == 0) {
                    $nameFound = true;
                    break;
                }
            }
            echo "Name Found After Check: " . ($nameFound ? "true" : "false") . "<br>";
            if ($nameFound == false) {
                file_put_contents("record.txt", "\n".$Name.",0", FILE_APPEND);
            }
            header("Location: Music.php");
            exit();
        } else {
            echo "<p>You need to enter a NickName.</p>\n";
        }
    }
    ?>
        <form name="QuizForm" action="welcome.php" method="post">
            <p>NickName: <input type="text" name="nickname" value="<?php echo $Name; ?>" /></p>
            &nbsp;<input type="submit" name="countries" value="Countries" style="margin-right: 30px;"/><input type="submit" name="Music" value="Music" style="margin-right: 30px;"/></p>
        </form>
</body>

</html>