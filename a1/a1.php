<!DOCTYPE html>
<html>

<head>
    <title>Funny facts</title>
</head>

<body>
    <?php
    $DisplayForm = TRUE;
    $Name = "";
    if (isset($_POST['Countries'])) {
        $Name = $_POST['nickname'];
        if ($Name != '') {
            $DisplayForm = FALSE;
        } else {
            echo "<p>You need to enter a NickName.</p>\n";
            $DisplayForm = TRUE;
        }
    }
    if ($DisplayForm) {//if dipslayform is true
    ?>
        <form name="QuizForm" action="a1.php" method="post">
            <p>NickName: <input type="text" name="nickname" value="<?php echo $Name; ?>" /></p>
            &nbsp;<input type="submit" name="Countries" value="Countries" style="margin-right: 30px;"/><input type="submit" name="Music" value="Music" /></p>
        </form>
    <?php
    } else {
        file_put_contents("record.txt", $Name, FILE_APPEND);
        $filename = 'C:\Users\Jovenn\Documents\PHP programming\a1\countryqns.txt';
        if (file_exists($filename)) {
            // Read the file into an array. Each element of the array represents a line.
            $lines = file($filename, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        
            // Filter out lines that contain "Ans"
            $filteredLines = array_filter($lines, function($line) {
                return strpos($line, "Ans") === false;
            });
        
            // Shuffle the array to randomize the order of lines
            shuffle($filteredLines);
        
            // Get the first three elements of the shuffled array
            $randomLines = array_slice($filteredLines, 0, 3);
        
            // Output the three random lines
            foreach ($randomLines as $line) {
                echo "<p>$line</p>";
            ?>
                <form name="AnsForm" action="a1.php" method="post">
                    True<input type="radio" name="ans" value="true" />
                    False<input type="radio" name="ans" value="false" />
                </form>
            <?php
            }
            ?>
            <form name="SubmitForm" action="a1.php" method="post">
            </br>
                &nbsp;<input type="submit" name="Submit" value="Send Form" /></p>
            </form>
        <?php
        } else {
            echo "File does not exist.";
        }
    }
    ?>
</body>

</html>