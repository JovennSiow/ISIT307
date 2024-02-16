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
<div class="container d-flex flex-column justify-content-center align-items-center">
    <h1>Choose Option</h1><br>
        <?php
        if (isset($_POST["Check-In"])) {
            header("Location: usersearchlocation.php");
            exit();
        }
        if (isset($_POST["ViewHistory"])) {
            header("Location: userhistory.php");
            exit();
        }
        ?>
      <form action="userhome.php" method="post">
            <input type="submit" value="Check-In" name="Check-In" class="btn btn-primary">&nbsp;&nbsp;&nbsp;<input type="submit" value="View History" name="ViewHistory" class="btn btn-primary">
      </form>
</div>
</body>
</html>