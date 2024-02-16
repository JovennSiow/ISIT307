<?php
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Form</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
    <h1>Check-In</h1><br>
    <?php
    require_once "database.php";
    class ParkingManager {
        private $conn;
    
        public function __construct($conn) {
            $this->conn = $conn;
        }
    
        public function redirectToCheckout() {
            $sql = "UPDATE user SET status='Check-Out' WHERE email = ?";
            $stmt = mysqli_prepare($this->conn, $sql);
            mysqli_stmt_bind_param($stmt, "s", $_SESSION['email']);
            mysqli_stmt_execute($stmt);
            header("Location: checkout.php");
            exit();
        }
    
        public function getParkingDetails() {
            $sql = "SELECT * FROM parkinglocation WHERE ParkingID = ?";
            $stmt = mysqli_prepare($this->conn, $sql);
            mysqli_stmt_bind_param($stmt, "i", $_SESSION['id']);
            mysqli_stmt_execute($stmt);
            return mysqli_stmt_get_result($stmt);
        }
    
        public function displayParkingDetails() {
            $result = $this->getParkingDetails();
    
            if ($row = mysqli_fetch_array($result, MYSQLI_ASSOC)) {
                $_SESSION['Location'] = $row['Location'];
                $_SESSION['Description'] = $row['Description'];
                $costPerHour = htmlspecialchars($row['CostperHour']);
                $costForLate = htmlspecialchars($row['CostforLate']);
    
                echo "<p style=\"font-size:1.65em;\">End Date and Time: " . $_SESSION['datetime'] . "</p>";
                echo "<p style=\"font-size:1.65em;\">Cost per hour: " . $costPerHour . "</p>";
                echo "<p style=\"font-size:1.65em;\">Cost for late: " . $costForLate . "</p>";
            } else {
                echo "<p>No parking details found.</p>";
            }
        }
    }
    

    $parkingManager = new ParkingManager($conn);
    
    if (isset($_POST['submit'])) {
        $parkingManager->redirectToCheckout();
    }
    
    $parkingManager->displayParkingDetails();
    
    ?>
    <form action="usercheckin.php" method="post">
            <input type="submit" value="Check-Out" name="submit" class="btn btn-primary" style="padding: 10px 10px; font-size: 1.25em;">
    </form>
    </div>
</body>
</html>