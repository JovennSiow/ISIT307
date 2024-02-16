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
        <h1> Insert parking locations</h1><br>
        <?php
        require_once "database.php";
        class insertLocation {
            private $conn;
        
            public function __construct($conn) {
                $this->conn = $conn;
            }
        
            private function hasErrors($Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate) {
                $errors = array();
                
                if (empty($Location) || empty($Description) || empty($ParkingSpaces) || empty($CostPerHour) || empty($CostForLate)) {
                    array_push($errors, "All fields are required");
                }
                
                return $errors;
            }
        
            public function insertLocation($Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate) {
                $errors = $this->hasErrors($Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate);
        
                if (count($errors) > 0) {
                    foreach ($errors as $error) {
                        echo "<div class='alert alert-danger'>$error</div>";
                    }
                    return false;
                } else {
                    $sql = "INSERT INTO parkinglocation (Location, Description, ParkingSpaces, CostPerHour, CostForLate) VALUES (?, ?, ?, ?, ?)";
                    $stmt = mysqli_prepare($this->conn, $sql);
                    
                    if (!$stmt) {
                        die("Something went wrong with prepare");
                    }
                    
                    mysqli_stmt_bind_param($stmt, "sssss", $Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate);
                    
                    if (mysqli_stmt_execute($stmt)) {
                        header("Location: Admineditinsertsearchlocation.php");
                        exit();
                    } else {
                        die("Something went wrong with execute");
                    }
                }
            }
        }
        
        if (isset($_POST["Insert"])) {
            session_start();
            $Location = $_POST["Location"];
            $Description = $_POST["Description"];
            $ParkingSpaces = $_POST["ParkingSpaces"];
            $CostPerHour = $_POST["CostPerHour"];
            $CostForLate = $_POST["CostForLate"];
            
            // Assuming $conn is your database connection
            $insertLocation = new insertLocation($conn);
            $insertLocation->insertLocation($Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate);
        }
        ?>
        <form action="AdmininsertLocation.php" method="post">
            <div class="form-group">
                <input type="text" class="form-control" name="Location" placeholder="Location:">
            </div>
            <div class="form-group">
                <input type="text" class="form-control" name="Description" placeholder="Description:">
            </div>
            <div class="form-group">
                <input type="number" class="form-control" name="ParkingSpaces" placeholder="Parking Spaces:">
            </div>           
            <div class="form-group">
                <input type="text" class="form-control" name="CostPerHour" placeholder="Cost Per Hour:">
            </div>
            <div class="form-group">
                <input type="text" class="form-control" name="CostForLate" placeholder="Cost For Late:">
            </div>
            <div class="form-btn">
                <input type="submit" class="btn btn-primary" value="Insert" name="Insert">
            </div>
        </form>
    </div>
</body>
</html>