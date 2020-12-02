import java.nio.file.FileAlreadyExistsException;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class valida {

    static boolean validaFormato(String cpf){
        Pattern padrao = Pattern.compile("\\d{3}.\\d{3}.\\d{3}-\\d{2}");
        Matcher match = padrao.matcher(cpf);

        if (match.find()){
            return true;
        }
        return false;
    }

    static boolean validaDigitos(String cpf){
        cpf = cpf.replace(".","").replace("-","");

        int primeiro = 0;
        int segundo = (11 * (Integer.valueOf(cpf.charAt(0)) - 48));

        for (int i = 10; i > 1; i--) {
            int digito1 = (Integer.valueOf(cpf.charAt(10-i)) - 48);
            int digito2 = (Integer.valueOf(cpf.charAt((10-i)+1)) - 48);

            primeiro += (i * digito1);
            segundo += (i * digito2);
        }

        primeiro = (11 - (primeiro % 11));
        segundo = (11 - (segundo % 11));

        int primeiro_digito = (Integer.valueOf(cpf.charAt(9)) - 48);
        int segundo_digito = (Integer.valueOf(cpf.charAt(10)) - 48);

        if ((primeiro == primeiro_digito) && (segundo == segundo_digito)) {
            return true;
        }
        return false;
    }

    public static void main(String[] args) {
        while (true){

            System.out.println("Digite o CPF a ser validado:");

            Scanner input = new Scanner(System.in);
            String cpf = input.nextLine();

            if (validaFormato(cpf) && validaDigitos(cpf)){
                System.out.println("CPF válido");
            }else {
                System.out.println("CPF inválido");

            }
        }
    }
}
