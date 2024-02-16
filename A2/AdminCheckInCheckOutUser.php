<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="userhome.css">
</head>
<body>
<?php

require_once "database.php";
class ParkingUserManager {
    private $conn;

    public function __construct($conn) {
        $this->conn = $conn;
    }

    public function getParkingLocations($filter = '') {
        if (!empty($filter)) {
            $filtervalues = $this->conn->real_escape_string($filter);
            $query = $this->conn->prepare("SELECT * FROM user WHERE CONCAT(firstname, surname, email) LIKE CONCAT('%', ?, '%')");
            $query->bind_param("s", $filtervalues);
            $query->execute();
            return $query->get_result(); 
        } else {
            return $this->conn->query("SELECT * FROM user");
        }
    }

    public function renderSearchForm() {
        echo '<form name="search" action="searchlocation.php" method="POST">
                <input type="text" name="search" value="" class="form-control" placeholder="Search">
                <input type="submit" name="Form" value="Submit" />
              </form>';
    }

    public function renderUserTable($qRes) {
        echo "<table width='100%' border='1'>\n";
        echo "<tr><th>ID</th><th>Types</th><th>Firstname</th>" .
             "<th>Surname</th><th>Phone Number</th><th>Email</th><th>Status</th></tr>\n";

        if ($qRes->num_rows > 0) {
            while (($Row = $qRes->fetch_row())) {
                    echo "<tr><td>{$Row[0]}</td>";
                    echo "<td>{$Row[1]}</td>";
                    echo "<td>{$Row[2]}</td>";
                    echo "<td>{$Row[3]}</td>";
                    echo "<td>{$Row[4]}</td>";
                    echo "<td>{$Row[5]}</td>";
                    if($Row[7] == 'Check-In')
                        echo "<td class='btn'><a href='Admincheckout.php?id={$Row[0]}' class='btn btn-primary'>Check-Out</a></td></tr>\n";
                    else
                        echo "<td class='btn'><a href='Adminsearchlocation.php?id={$Row[0]}' class='btn btn-primary'>Check-In</a></td></tr>\n";
            }
        } else {
            echo "<tr><td colspan='7'>No Record Found</td></tr>";
        }
        echo "</table>\n";
    }
}

// Usage example
try {
    $parkingManager = new ParkingUserManager($conn);

    // If a search term has been posted, filter the parking locations
    $searchTerm = isset($_POST['search']) ? $_POST['search'] : '';
    $qRes = $parkingManager->getParkingLocations($searchTerm);

    $parkingManager->renderSearchForm();
    $parkingManager->renderUserTable($qRes);

} catch (mysqli_sql_exception $e) {
    die($e->getCode(). ": " . $e->getMessage());
} finally {
    $conn->close();
}

?>
</form>
</body>
</html>

