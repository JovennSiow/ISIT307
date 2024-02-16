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
        <h1>User registration form</h1><br>
        <?php
        require_once "database.php";
        class UserRegistration {
            private $conn;
        
            public function __construct($conn) {
                $this->conn = $conn;
            }
        
            private function hasErrors($firstname, $surname, $email, $phone, $password, $passwordRepeat) {
                $errors = array();
                
                if (empty($firstname) || empty($surname) || empty($email) || empty($phone) || empty($password) || empty($passwordRepeat)) {
                    array_push($errors, "All fields are required");
                }
                
                if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
                    array_push($errors, "Email is not valid");
                }
                
                if ($password !== $passwordRepeat) {
                    array_push($errors, "Passwords do not match");
                }
                
                $sql = "SELECT * FROM user WHERE email = ?";
                $stmt = mysqli_prepare($this->conn, $sql);
                mysqli_stmt_bind_param($stmt, "s", $email);
                mysqli_stmt_execute($stmt);
                $result = mysqli_stmt_get_result($stmt);
                $rowCount = mysqli_num_rows($result);
                
                if ($rowCount > 0) {
                    array_push($errors, "Email already exists");
                }
                
                return $errors;
            }
        
            public function register($user, $firstname, $surname, $email, $phone, $password, $passwordRepeat, $status) {
                $errors = $this->hasErrors($firstname, $surname, $email, $phone, $password, $passwordRepeat);
        
                if (count($errors) > 0) {
                    foreach ($errors as $error) {
                        echo "<div class='alert alert-danger'>$error</div>";
                    }
                    return false;
                } else {
                    $passwordHash = password_hash($password, PASSWORD_DEFAULT);
                    $sql = "INSERT INTO user (types, firstname, surname, phone, email, password, status) VALUES (?, ?, ?, ?, ?, ?, ?)";
                    $stmt = mysqli_prepare($this->conn, $sql);
                    
                    if (!$stmt) {
                        die("Something went wrong with prepare");
                    }
                    
                    mysqli_stmt_bind_param($stmt, "sssssss", $user, $firstname, $surname, $phone, $email, $passwordHash, $status);
                    
                    if (mysqli_stmt_execute($stmt)) {
                        echo "<div class='alert alert-success'>You are registered successfully.</div>";
                        header("Location: login.php");
                        exit();
                    } else {
                        die("Something went wrong with execute");
                    }
                }
            }
        }
        
        if (isset($_POST["submit"])) {
            session_start();
            $user = "User";
            $firstname = $_POST["firstname"];
            $surname = $_POST["surname"];
            $email = $_POST["email"];
            $phone = $_POST["phone"];
            $password = $_POST["password"];
            $passwordRepeat = $_POST["repeat_password"];
            $status = "Check-Out";
            
            // Assuming $conn is your database connection
            $registration = new UserRegistration($conn);
            $registration->register($user, $firstname, $surname, $email, $phone, $password, $passwordRepeat, $status);
        }
        ?>
        <form action="register.php" method="post">
            <div class="form-group">
                <input type="text" class="form-control" name="firstname" placeholder="First Name:">
            </div>
            <div class="form-group">
                <input type="text" class="form-control" name="surname" placeholder="Surname:">
            </div>
            <div class="form-group">
                <input type="tel" class="form-control" name="phone" placeholder="Phone Number:" pattern="[8-9][0-9]{7}" required>
            </div>           
            <div class="form-group">
                <input type="email" class="form-control" name="email" placeholder="Email:">
            </div>
            
            <div class="form-group">
                <input type="password" class="form-control" name="password" placeholder="Password:">
            </div>
            <div class="form-group">
                <input type="password" class="form-control" name="repeat_password" placeholder="Comfirm Password:">
            </div>
            <div class="form-btn">
                <input type="submit" class="btn btn-primary" value="Register" name="submit">
            </div>
        </form>
        <div>
        <div><p>Already Registered <a href="login.php">Login Here</a></p></div>
      </div>
    </div>
</body>
</html>