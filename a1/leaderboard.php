<!DOCTYPE html>
<html>
<head>
    <title>Funny</title>
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
    <table> 
        <tr> 
            <th>Ranking</th> 
            <th>UserName</th> 
            <th>Marks</th> 
        </tr>
        <?php
        $filePath = "record.txt"; // Path to your file
        $leaderboard = []; // Initialize an empty array for leaderboard

        if (file_exists($filePath)) {
            $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
            foreach ($lines as $line) {
                list($username, $score) = explode(", ", $line); // Split each line into username and score
                $leaderboard[] = ['username' => $username, 'score' => (int)$score]; // Add to leaderboard array
            }

            // Sort the leaderboard by score in descending order
            usort($leaderboard, function($a, $b) {
                return $b['score'] - $a['score'];
            });

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
</body>
</html>