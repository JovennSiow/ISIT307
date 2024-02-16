<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="userhome.css">
</head>
<body>
<?php

require_once "database.php";
class UserHistory {
    private $conn;

    public function __construct($conn) {
        $this->conn = $conn;
    }

    public function getUser($user) {
            return $this->conn->query("SELECT * FROM $user");
    }


    public function displayHistory($qRes) {
        echo "<table width='100%' border='1'>\n";
        echo "<tr><th>ID</th><th>Location</th><th>Description</th>" .
             "<th>checkIn</th><th>checkOut</th></tr>\n";

        if ($qRes->num_rows > 0) {
            while (($Row = $qRes->fetch_row())) {

                    echo "<tr><td>{$Row[0]}</td>";
                    echo "<td>{$Row[1]}</td>";
                    echo "<td>{$Row[2]}</td>";
                    echo "<td>{$Row[3]}</td>";
                    echo "<td>{$Row[4]}</td>";
            }
        } else {
            echo "<tr><td colspan='7'>No Record Found</td></tr>";
        }
        echo "</table>\n";
    }
}

// Usage example
try {
    session_start();
    $user = $_SESSION['user'];
    $UserHistory = new UserHistory($conn);
    $qRes = $UserHistory->getUser($user);

    $UserHistory->displayHistory($qRes);

} catch (mysqli_sql_exception $e) {
    die($e->getCode(). ": " . $e->getMessage());
} finally {
    $conn->close();
}

?>
</form>
</body>
</html>

