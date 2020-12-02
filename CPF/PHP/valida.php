// código executado no xampp

<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>CPF-PHP</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
</head>
<body>
<form method="POST" action="valida.php">
    <div class="form-group col-sm-5">
        <label for="cpf">CPF</label>
        <input type="text" class="form-control form-control-sm" id="cpf" name="cpf" pattern="\d{3}\.\d{3}\.\d{3}-\d{2}" title="Digite no formato 000.000.000-00" mame="cpf" required>
    </div>
    <button type="submit" name="submit" class="btn btn-primary ml-3">Validar</button>
</form>
</body>
</html>

<?php
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $cpf = $_POST["cpf"];

        $cpf = str_replace('.','',$cpf);

        $cpf = str_replace('-','',$cpf);

        $primeiro = 0;
        $segundo = (11 * $cpf[0]);

        for ($i = 10; $i > 1; $i--) {
            $digito1 = $cpf[10 - $i];
            $digito2 = $cpf[(10 -$i) + 1];

            $primeiro += ($i * $digito1);
            $segundo += ($i * $digito2);
        }

        $primeiro = (11 - ($primeiro % 11));
        $segundo = (11 - ($segundo % 11));

        $primeiro_digito = $cpf[9];
        $segundo_digito = $cpf[10];

        if (($primeiro == $primeiro_digito) && ($segundo == $segundo_digito)) {
            echo "<div class='alert alert-primary col-sm-5' role='alert'>";
            echo "CPF válido";
        }else{
            echo "<div class='alert alert-danger col-sm-5' role='alert'>";
            echo "CPF inválido";
        }

        echo "</div>";
    }
?>