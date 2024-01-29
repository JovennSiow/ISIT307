<!DOCTYPE html>
<html>
<head>
    <title>Funny </title>
    <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 8px;
            text-align: left;
        }
    </style>
</head>
<body>
    <h1>Welcome to Funny facts</h1>

    <form action="" method="get">
        <label for="sort">Sort by:</label>
        <select name="sort" id="sort">
            <option value="nickname_asc" <?php echo (isset($_GET['sort']) && $_GET['sort'] == 'nickname_asc') ? 'selected' : ''; ?>>Nickname ASC order</option>
            <option value="nickname_desc" <?php echo (isset($_GET['sort']) && $_GET['sort'] == 'nickname_desc') ? 'selected' : ''; ?>>Nickname DESC order</option>
            <option value="marks_asc" <?php echo (isset($_GET['sort']) && $_GET['sort'] == 'marks_asc') ? 'selected' : ''; ?>>Marks ASC</option>
            <option value="marks_desc" <?php echo (isset($_GET['sort']) && $_GET['sort'] == 'marks_desc') ? 'selected' : ''; ?>>Marks DESC</option>
        </select>
        &nbsp;<input type="submit" value="Sort"> 
    </form>

    <table> 
        <tr> 
            <th>Ranking</th> 
            <th>NickName</th> 
            <th>Marks</th> 
        </tr>
        <?php
        $filePath = "record.txt"; // Path to your file
        $leaderboard = []; // Initialize an empty array for leaderboard

        if (file_exists($filePath)) {
            $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
            foreach ($lines as $line) {
                list($username, $score) = explode(",", $line); // Split each line into username and score
                $leaderboard[] = ['username' => $username, 'score' => (int)$score]; // Add to leaderboard array
            }

           $sortOption = isset($_GET['sort']) ? $_GET['sort'] : 'marks_desc'; // Default sort option
            function sortLeaderboard(&$leaderboard, $sortOption) {
                usort($leaderboard, function($a, $b) use ($sortOption) {
                    switch ($sortOption) {
                        case 'nickname_asc':
                            return strcmp($a['username'], $b['username']);
                        case 'nickname_desc':
                            return strcmp($b['username'], $a['username']);
                        case 'marks_asc':
                            return $a['score'] - $b['score'];
                        case 'marks_desc':
                            return $b['score'] - $a['score'];
                    }
                });
            }

            sortLeaderboard($leaderboard, $sortOption);

            // Display the leaderboard
            $ranking = 1;
            foreach ($leaderboard as $entry) {
                echo "<tr>";
                echo "<td>" . $ranking++ . "</td>";
                echo "<td>" . htmlspecialchars($entry['username']) . "</td>"; // Prevent XSS
                echo "<td>" . $entry['score'] . "</td>";
                echo "</tr>";
            }
        } else {
            echo "<tr><td colspan='3'>File not found.</td></tr>";
        }
        ?>
    </table>
    <?php 
    if (isset($_POST['Exit'])) {
        header("Location: Exit.php");
        exit();
    }
    if (isset($_POST['Back'])) {
        header("Location: score.php");
        exit();
    }
    ?>
    <form name="QuizForm" action="leaderboard.php" method="post">
        &nbsp;<p>&nbsp;<input type="submit" name="Back" value="Back">&nbsp;<input type="submit" name="Exit" value="Exit"/></p>
    </form>
</body>
</html>