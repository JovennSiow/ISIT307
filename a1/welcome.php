<?php session_start();?>
<!DOCTYPE html>
<html>
<head>
    <title>Funny</title>
    <h1>Welcome to Funny facts</h1>
</head>

<body>
    <?php
    $Name = "";
    if (isset($_POST['Enter'])) {
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
                file_put_contents("record.txt", $Name.",0\n", FILE_APPEND);
            }
            header("Location: topic.php");
            exit();
        } else {
            echo "<p>You need to enter a NickName.</p>\n";
        }
    }
    ?>
        <form name="QuizForm" action="welcome.php" method="post">
            <p>NickName: <input type="text" name="nickname" value="<?php echo $Name; ?>" /></p>
            &nbsp;<input type="submit" name="Enter" value="Enter Quiz"></p>
            <input type="hidden" name="Name" value="<?php echo isset($_GET['Name']) ? htmlspecialchars($_GET['Name']) : ''; ?>" />
        </form>
</body>

</html>