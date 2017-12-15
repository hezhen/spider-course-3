<!DOCTYPE html>
<html>

<head>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>

<body>
  <div class='login-input-block'>

    <img src="chlogo.png" alt="">
    <?php

$redirectToLogin = FALSE;

session_start();

if (isset($_COOKIE['session'])) {
    $sessionId = $_SESSION[$_COOKIE['session']['name']];
    $cookieId = $_COOKIE['session']['id'];
    echo "<li>user:" . $_SESSION['user'] . "</li>";
    // echo 'sessionid: ' . $sessionId . '<br>cookieid: ' . $cookieId;
    if ( $cookieId == $sessionId ){
        foreach ($_COOKIE['session'] as $name => $value) {
            $name = htmlspecialchars($name);
            $value = htmlspecialchars($value);
            echo "<li>$name : $value</li>";
        }
        
        if ( isset($_GET['logout']) ){
            // echo 'session name is :' . $_SESSION[$_COOKIE['session']['name']];
            unset($_SESSION[$_COOKIE['session']['name']]);
            foreach ($_COOKIE as $ck => $cv) {
                if ( is_array($cv) ){
                    foreach ($cv as $name => $value) {
                        // echo "cookie key is $ck, sub key is $name, value is $value <br>";
                        $name = htmlspecialchars($name);
                        $value = htmlspecialchars($value);
                        setcookie( $ck.'['. $name.']', $value, time() );
                    }
                } else {
                    // echo "cookie key is $ck, value is $cv <br>";
                    setcookie( "$ck", $cv, 1 );
                }
            }
            $redirectToLogin = True;
        }
    } else {
        $redirectToLogin = True;
    }
} else {
    echo 'session not found!';
    $redirectToLogin = TRUE;
}

if ( $redirectToLogin ){
    header('Location: login.php', true, 302);
    session_unset();
    session_destroy();
}

?>
      <form action="main.php" method="get">
        <div style="display: none;">
          <input type="text" name="logout">
        </div>
        <div class="ed-login">
          <input type="submit" value="Logout">
        </div>
      </form>
  </div>
</body>

</html>