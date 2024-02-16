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
        <h1>Edit parking locations</h1><br>
        <?php
        $id = $_GET['id'] ?? '';
        $Location = $_GET['Location'] ?? '';
        $Description = $_GET['Description'] ?? '';
        $ParkingSpaces = $_GET['ParkingSpaces'] ?? '';
        $CostPerHour = $_GET['CostPerHour'] ?? '';
        $CostForLate = $_GET['CostForLate'] ?? '';
        require_once "database.php";
        class UpdateLocation {
            private $conn;
        
            public function __construct($conn) {
                $this->conn = $conn;
            }
        
            public function UpdateLocation($id, $Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate) {
                 $sql = "UPDATE parkinglocation SET Location=?, Description=?, ParkingSpaces=?, CostPerHour=?, CostForLate=? WHERE ParkingID=?";
                $stmt = mysqli_prepare($this->conn, $sql);
                
                if (!$stmt) {
                    die("Something went wrong with prepare");
                }
                
                mysqli_stmt_bind_param($stmt, "sssssi", $Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate, $id);
                
                if (mysqli_stmt_execute($stmt)) {
                    header("Location: Admineditinsertsearchlocation.php");
                    exit();
                } else {
                    die("Something went wrong with execute");
                }
            }
        }
        
        if (isset($_POST["Update"])) {
            session_start();
            $id = $_POST["id"];
            $Location = $_POST["Location"];
            $Description = $_POST["Description"];
            $ParkingSpaces = $_POST["ParkingSpaces"];
            $CostPerHour = $_POST["CostPerHour"];
            $CostForLate = $_POST["CostForLate"];
            
            // Assuming $conn is your database connection
            $UpdateLocation = new UpdateLocation($conn);
            $UpdateLocation->UpdateLocation($id, $Location, $Description, $ParkingSpaces, $CostPerHour, $CostForLate);
        }
        ?>
        <form action="AdmineditLocation.php" method="post">
            <div class="form-group">
                <label for="Location" style="font-size: 1.5em;">Location:</label><input type="text" class="form-control" name="Location" value="<?php echo $Location; ?>">
            </div>
            <div class="form-group">
                <label for="Description" style="font-size: 1.5em;">Description:</label><input type="text" class="form-control" name="Description" value="<?php echo $Description; ?>">
            </div>
            <div class="form-group">
                <label for="ParkingSpaces" style="font-size: 1.5em;">Parking Spaces:</label><input type="text" class="form-control" name="ParkingSpaces" value="<?php echo $ParkingSpaces; ?>">
            </div>
            <div class="form-group">
                <label for="CostPerHour" style="font-size: 1.5em;">Cost Per Hour:</label><input type="text" class="form-control" name="CostPerHour" value="<?php echo $CostPerHour; ?>">
            </div>
            <div class="form-group">
                <label for="CostForLate" style="font-size: 1.5em;">Cost For Late:</label><input type="text" class="form-control" name="CostForLate" value="<?php echo $CostForLate; ?>">
            </div>
            <div class="form-group">
                <input type="submit" value="Update" name="Update" class="btn btn-primary">
            </div>
            <div class="form-group">
                <input type="hidden" name="id" value="<?php echo htmlspecialchars($id); ?>">
            </div>
        </form>
    </div>
</body>
</html>