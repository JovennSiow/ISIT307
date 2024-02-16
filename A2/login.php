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
    <h1>Login form</h1><br>
        <?php
        require_once "database.php";

        class UserAuthenticator {
            private $conn;
        
            public function __construct($conn) {
                $this->conn = $conn;
            }
        
            public function login($email, $password) {
                $sql = "SELECT * FROM user WHERE email = ?";
                $stmt = mysqli_prepare($this->conn, $sql);
                if (!$stmt) {
                    echo "<div class='alert alert-danger'>Database prepare error.</div>";
                    return false;
                }
        
                mysqli_stmt_bind_param($stmt, "s", $email);
                mysqli_stmt_execute($stmt);
                $result = mysqli_stmt_get_result($stmt);
                $user = mysqli_fetch_array($result, MYSQLI_ASSOC);
        
                if ($user && password_verify($password, $user["password"])) {
                    $_SESSION["user"] = $user['firstname'].$user['surname'];
                    $_SESSION["email"] = $user['email'];
                    header("Location: userhome.php");
                    exit();
                } else {
                    echo "<div class='alert alert-danger'>Invalid email or password.</div>";
                    return false;
                }
            }
        }
        
        // Usage
        if (isset($_POST["login"])) {
            session_start(); // Start the session if you haven't already done so
            $email = $_POST["email"];
            $password = $_POST["password"];
            
            $authenticator = new UserAuthenticator($conn); // $conn is your database connection
            $authenticator->login($email, $password);
        }
        ?>
      <form action="login.php" method="post">
        <div class="form-group">
            <input type="email" placeholder="Enter Email:" name="email" class="form-control">
        </div>
        <div class="form-group">
            <input type="password" placeholder="Enter Password:" name="password" class="form-control">
        </div>
        <div class="form-btn">
            <input type="submit" value="Login" name="login" class="btn btn-primary">
        </div>
      </form>
     <div><p>Not registered yet <a href="register.php">Register Here</a></p></div>
    </div>
</body>
</html>