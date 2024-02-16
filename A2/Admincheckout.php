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
        <?php
            class ParkingSystem {
                private $conn;
            
                public function __construct($conn) {
                    $this->conn = $conn;
                }
            
                public function redirectToAdmin() {
                    header("Location: AdminCheckInCheckOutUser.php");
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

                public function updateRecord($userid){
                    $sql = "UPDATE user SET status='Check-Out' WHERE id = ?";
                    $stmt = mysqli_stmt_init($this->conn);
                    if (!mysqli_stmt_prepare($stmt, $sql)) {
                        throw new Exception("Something went wrong with updating: " . mysqli_error($this->conn));
                    }
                    mysqli_stmt_bind_param($stmt, "i", $userid);
                    mysqli_stmt_execute($stmt);
                }
            }
            
            // Usage
            require_once "database.php";
            $parkingSystem = new ParkingSystem($conn);
            
            $tableName = $_SESSION["user"];
            $parkingSystem->createTableIfNeeded($tableName);
            $parkingSystem->insertRecord($tableName, $_SESSION["Location"], $_SESSION["Description"], $_SESSION['starttime']);
            $parkingSystem->redirectToAdmin();
            $userid = $_GET['id'];
            $parkingSystem->updateRecord($userid);
        ?>
    </div>
</body>
</html>
