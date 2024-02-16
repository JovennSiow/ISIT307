<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="userhome.css">
</head>
<body>
<?php

require_once "database.php";
class ParkingLocationManager {
    private $conn;

    public function __construct($conn) {
        $this->conn = $conn;
    }

    public function getParkingLocations($filter = '') {
        if (!empty($filter)) {
            $filtervalues = $this->conn->real_escape_string($filter);
            $query = $this->conn->prepare("SELECT * FROM parkinglocation WHERE CONCAT(ParkingID, Location, Description) LIKE CONCAT('%', ?, '%')");
            $query->bind_param("s", $filtervalues);
            $query->execute();
            return $query->get_result(); 
        } else {
            return $this->conn->query("SELECT * FROM parkinglocation");
        }
    }

    public function renderSearchForm() {
        echo '<form name="search" action="Adminsearchlocation.php" method="POST">
                <input type="text" name="search" value="" class="form-control" placeholder="Search">
                <input type="submit" name="Form" value="Submit" />
              </form>';
    }

    public function renderParkingLocationsTable($qRes) {
        echo "<table width='100%' border='1'>\n";
        echo "<tr><th>ParkingID</th><th>Location</th><th>Description</th>" .
             "<th>Parking Spaces</th><th>Cost Per Hour</th><th>Cost For Late</th><th>Check-In</th></tr>\n";

        if ($qRes->num_rows > 0) {
            while (($Row = $qRes->fetch_row())) {
                if ($Row[3] > 0) {
                    echo "<tr><td>{$Row[0]}</td>";
                    echo "<td>{$Row[1]}</td>";
                    echo "<td>{$Row[2]}</td>";
                    echo "<td>{$Row[3]}</td>";
                    echo "<td>{$Row[4]}</td>";
                    echo "<td>{$Row[5]}</td>";
                    echo "<td class='btn'><a href='Admincheckinduration.php?id={$Row[0]}' class='btn btn-primary'>Check-in</a></td></tr>\n";
                }
            }
        } else {
            echo "<tr><td colspan='7'>No Record Found</td></tr>";
        }
        echo "</table>\n";
    }

    public function getUser(){
        $id = $_GET['id'];
        $_SESSION["userid"] = $id;
        $sql = "SELECT * FROM user WHERE id = ?";
        $stmt = mysqli_prepare($this->conn, $sql);
        mysqli_stmt_bind_param($stmt, "i", $id);
        mysqli_stmt_execute($stmt);
        $result = mysqli_stmt_get_result($stmt);
        $user = mysqli_fetch_array($result, MYSQLI_ASSOC);
        $_SESSION["user"] = $user['firstname'].$user['surname'];
    }
}

// Usage example
try {
    session_start();
    $parkingManager = new ParkingLocationManager($conn);

    // If a search term has been posted, filter the parking locations
    $searchTerm = isset($_POST['search']) ? $_POST['search'] : '';
    $qRes = $parkingManager->getParkingLocations($searchTerm);

    $parkingManager->renderSearchForm();
    $parkingManager->renderParkingLocationsTable($qRes);
    $parkingManager->getUser();

} catch (mysqli_sql_exception $e) {
    die($e->getCode(). ": " . $e->getMessage());
} finally {
    $conn->close();
}

?>
</form>
</body>
</html>

