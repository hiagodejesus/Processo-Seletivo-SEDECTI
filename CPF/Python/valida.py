import re

def valida(cpf):
    if not re.search('\d{3}.\d{3}.\d{3}-\d{2}|\d{11}', cpf):
        return False

    cpf = cpf.replace('.', '').replace('-','')

    primeiro_digito = 0
    segundo_digito = int(cpf[0])*11

    for i in range(10,1,-1):
        primeiro_digito += int(cpf[10-i])*i
        segundo_digito += int(cpf[(10-i)+1])*i

    primeiro = (11 - (primeiro_digito%11))
    segundo = (11 - (segundo_digito%11))

    return True if str(primeiro) == cpf[-2] and str(segundo) == cpf[-1] else False

if __name__ == '__main__':
    while True:
        cpf = input("Digite o CPF a ser validado:\n")
        print("CPF", 'válido' if valida(cpf) else 'inválido')