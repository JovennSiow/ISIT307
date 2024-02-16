<?php
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registration Form</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Receipt</h1><br>
        <?php
            class ParkingSystem {
                private $conn;
                private $currentDateTime;
            
                public function __construct($conn) {
                    $this->conn = $conn;
                    date_default_timezone_set('Asia/Singapore');
                    $this->currentDateTime = new DateTime();
                }
            
                public function redirectToUserHome() {
                    header("Location: userhome.php");
                    exit();
                }
            
                public function createTableIfNeeded($tableName) {
                    $tableName = mysqli_real_escape_string($this->conn, $tableName);
                    $query = "SHOW TABLES LIKE '{$tableName}'";
                    $result = mysqli_query($this->conn, $query);
            
                    if (mysqli_num_rows($result) == 0) {
                        $sqlCreate = "CREATE TABLE $tableName (
                                        id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                        Location VARCHAR(255) NOT NULL,
                                        Description VARCHAR(255) NOT NULL,
                                        checkIn VARCHAR(50) NOT NULL,
                                        checkOut TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    )";
                        if (!mysqli_query($this->conn, $sqlCreate)) {
                            throw new Exception("Error creating table: " . mysqli_error($this->conn));
                        }
                    }
                }
            
                public function insertRecord($tableName, $location, $description, $checkIn) {
                    $sqlInsert = "INSERT INTO $tableName (Location, Description, checkIn) VALUES (?, ?, ?)";
                    $stmt = mysqli_stmt_init($this->conn);
                    if (!mysqli_stmt_prepare($stmt, $sqlInsert)) {
                        throw new Exception("Something went wrong with insert: " . mysqli_error($this->conn));
                    }
            
                    mysqli_stmt_bind_param($stmt, "sss", $location, $description, $checkIn);
                    mysqli_stmt_execute($stmt);
                }
            
                public function calculateCosts($parkingId, $duration, $datetime) {
                    $setDateTime = new DateTime($datetime); 
                    $interval = $this->currentDateTime->diff($setDateTime);
                    
                    $hours = (int)$interval->format('%h');
                    $days = (int)$interval->format('%a');
                    if ($days > 0) {
                        $hours += $days * 24;
                    }
            
                    $sql = "SELECT * FROM parkinglocation WHERE ParkingID = ?";
                    $stmt = mysqli_prepare($this->conn, $sql);
                    mysqli_stmt_bind_param($stmt, "i", $parkingId);
                    mysqli_stmt_execute($stmt);
                    $result = mysqli_stmt_get_result($stmt);
            
                    if ($row = mysqli_fetch_array($result, MYSQLI_ASSOC)) {
                        $costPerHour = (int)ltrim($row['CostperHour'], '$');
                        $costForLate = (int)ltrim($row['CostforLate'], '$');
                        $total = $duration * $costPerHour;
                        $addition = 0;
            
                        if ($hours > 0) {
                            $addition = $hours * $costForLate;
                        }
                        $total += $addition;
                        
                        $addition = '$'.$addition;
                        
                        return [
                            'hours' => $hours,
                            'days' => $days,
                            'additionCharge' => $addition,
                            'totalCost' => $total
                        ];
                    } else {
                        throw new Exception("No parking location found with ID: $parkingId");
                    }
                }
                
                // ... Other methods ...
            }
            
            // Usage
            require_once "database.php";
            $parkingSystem = new ParkingSystem($conn);
            
            if (isset($_POST['submit'])) {
                $parkingSystem->redirectToUserHome();
            }
            
            $tableName = $_SESSION["user"];
            $parkingSystem->createTableIfNeeded($tableName);
            $parkingSystem->insertRecord($tableName, $_SESSION["Location"], $_SESSION["Description"], $_SESSION['starttime']);
            
            $costs = $parkingSystem->calculateCosts($_SESSION['id'], $_SESSION['duration'], $_SESSION['datetime']);
            
            echo "Difference is: {$costs['days']} days, {$costs['hours']} hours";
            echo "<p style=\"font-size:1.65em;\">Addition Charge: {$costs['additionCharge']}</p>";
            echo "<p style=\"font-size:1.65em;\">Total Cost: $" . $costs['totalCost'] . "</p>";
        ?>
        <form action="usercheckout.php" method="post">
            <div class="form-btn">
                <input type="submit" class="btn btn-primary" value="Exit" name="submit">
            </div>
        </form>
    </div>
</body>
</html>
