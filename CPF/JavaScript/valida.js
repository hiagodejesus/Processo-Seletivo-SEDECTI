// código executado no node.js

const readline = require('readline');

const input = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

input.question("Digite o CPF a ser validado:\n", (cpf) => {

    let formato = cpf.match(/^\d{3}\.\d{3}\.\d{3}\-\d{2}$/);

    if(formato){

        cpf = cpf.replace(/\./g,"");
        cpf = cpf.replace(/\-/g,"");

        var primeiro = 0;
        var segundo = (11 * (cpf.charAt(0)))

        for(let i=10; i>1; i--){
            var digito1 = (cpf.charAt(10-i));
            var digito2 = (cpf.charAt((10-i)+1));

            primeiro += (i * digito1);
            segundo += (i * digito2);
        }

        primeiro = (11 - (primeiro%11));
        segundo = (11 - (segundo%11));

        if ((primeiro == cpf.charAt(9)) && (segundo == cpf.charAt(10))){
            console.log('CPF válido');
        }else{
            console.log('CPF inválido');
        }

    }else{
        console.log('CPF inválido');
    }
});