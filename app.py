# bibliotecas do Flask
from flask import Flask, redirect, url_for, render_template, request, jsonify, session

# bibliotecas de manipulação de strings
import re, string, json

# biblioteca de requisição HTTP
import requests

# bibliotecas de manipulação do banco do banco de dados via Python
import pymongo
from pymongo import MongoClient

# instanciando a aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sedecti'

# método utilizado para conexão ao MongoDB Cloud
def conecta_banco():
    # carregando as credenciais de acesso ao banco de dados
    credenciais = json.load(open('static/credenciais_banco.json'))

    # conectando ao banco de dados na nuvem
    cliente = MongoClient("mongodb+srv://hiago:" + credenciais['password'] + "@cluster0.sn5zy.mongodb.net/" + credenciais['database'] + "?retryWrites=true&w=majority")

    # selecionando o banco de dados da aplicação
    banco = cliente['sedecti']

    # retornando as duas tabelas do banco
    # usuarios: (nome, cpf, idade, sexo)
    # endereco: (cep, logradouro, numero, bairro, cidade, estado)
    return banco['usuarios'], banco['enderecos']

# método utilizado para validação dos dígitos do CPF
def valida_digitos_cpf(cpf):

    # verificando se o cpf está no padrão 111.222.333-44 ou 11122233344
    if not re.search('\d{3}.\d{3}.\d{3}-\d{2}|\d{11}', cpf):
        return False

    # removendo possíveis pontuações
    cpf = cpf.replace('.', '').replace('-','')

    """
    cálculo dos digitos verificadores

    10 9  8   7  6  5    4  3  2
  x
    1  1  1 . 2  2  2  . 3  3  3 - (?) 4

    11 10 9  8   7  6  5    4  3   2
  x
    1  1  1 . 2  2  2  . 3  3  3 - 4 (?)
    """

    # somando a multiplicação dos digitos pelos valores posicionais em ordem decrescente
    primeiro_digito = 0
    segundo_digito = int(cpf[0])*11

    for i in range(10,1,-1):
        primeiro_digito += int(cpf[10-i])*i
        segundo_digito += int(cpf[(10-i)+1])*i

    # calculando os dígitos verificadores do cpf
    primeiro = (11 - (primeiro_digito%11))
    segundo = (11 - (segundo_digito%11))

    # verificando se os dígitos estão corretos
    if str(primeiro) == cpf[-2] and str(segundo) == cpf[-1]:
        return True

    return False

# método utilizado na busca pelo endereco a partir do CEP
def busca_endereco(cep):
    # definindo a url de busca do cep
    url = 'https://viacep.com.br/ws/' + cep + '/json/unicode/'

    # executando uma requisição para obter o endereco
    response = requests.get(url)

    # retornando o resultado da requisição
    return response.json()

# método utilizado para remoção de caracteres do nome de usuario
def limpa_string(nome):
    # removendo os dígitos e os caracteres diferentes de letras maiúsculas, minúsculas e espaço
    nome = re.sub('[0-9]|[^A-Za-z ]', '', nome)

    # removendo o excesso de espaços
    nome = ' '.join(nome.split())

    # retornando a string com as letras iniciais de cada palavra em maiúsculo
    return nome.title()

# rota que exibe o menu (CREATE, READ, UPDATE, DELETE)
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

# rota que captura os dados do formulário CREATE
@app.route('/form_create', methods=['GET', 'POST'])
def form_create():

    # verificando se foi feita uma requisição HTTP
    if request.method == 'POST':

        # capturando as informações preenchidas no formulário
        nome = limpa_string(request.form['nome'])
        cpf = request.form['cpf']
        idade = request.form['idade']
        sexo = request.form['sexo']

        # buscando o endereço através do cep informado
        cep = request.form['cep']
        endereco = busca_endereco(cep)
        logradouro = endereco['logradouro']
        numero = request.form['numero']
        bairro = endereco['bairro']
        cidade = endereco['localidade']
        estado = endereco['uf']

        # validando os digitos verificadores do cpf
        cpf_validado = valida_digitos_cpf(cpf)

        # se os dígitos verificadores forem inválidos, retorna os dados do formulário e uma mensagem (CPF Inválido!)
        if not cpf_validado:
            return render_template('create.html', nome=nome, cpf_invalido=True, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado)

        # caso contrário, os dados são repassados para a rota responsável pelo métoto CREATE
        else:
            return redirect(url_for('create', nome=nome, cpf=cpf, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado))

    return render_template('create.html')

# rota que salva os dados do formulário CREATE
@app.route('/create', methods=['GET','POST'])
def create():

    # conectando ao banco de dados e obtendo as tabelas
    tabela_usuario, tabela_endereco = conecta_banco()

    # dados pessoais
    usuario = {
        'nome': request.args.get('nome'),
        'cpf': request.args.get('cpf'),
        'idade': request.args.get('idade'),
        'sexo': request.args.get('sexo')
    }

    # dados de endereço
    endereco = {
        'id_usuario': request.args.get('cpf'), # chave estrangeira que identifica para a tabela usuario
        'cep': request.args.get('cep'),
        'logradouro': request.args.get('logradouro'),
        'numero': request.args.get('numero'),
        'bairro': request.args.get('bairro'),
        'cidade': request.args.get('cidade'),
        'estado': request.args.get('estado')
    }

    id = request.args.get('cpf')
    id_usuario = tabela_usuario.find_one({'cpf':id})
    id_endereco = tabela_endereco.find_one({'id_usuario':id})

    # verificando os dados para um determinado CPF não foram cadastrados anteriormente
    if not id_usuario and not id_endereco:
        # salvando os dados pessoais na tabela de usuario
        tabela_usuario.insert_one(usuario)

        # salvando os dados de endereço na tabela de endereco
        tabela_endereco.insert_one(endereco)

        return render_template('create.html', mensagem='Os dados foram cadastrados!')

    return render_template('create.html', mensagem='O CPF informado já foi cadastrado!')

# rota que captura os dados do formulário READ
@app.route('/form_read', methods=['GET', 'POST'])
def form_read():

    # verificando se foi feita uma requisição HTTP
    if request.method == 'POST':

        # capturando o cpf informado
        cpf = request.form['cpf']

        # validando os digitos verificadores do cpf
        cpf_validado = valida_digitos_cpf(cpf)

        # se os dígitos verificadores forem inválidos, retorna o CPF informado e uma mensagem (CPF Inválido!)
        if not cpf_validado:
            return render_template('read.html', cpf_invalido=True, cpf=cpf)

        # caso contrário, o CPF a ser consultado é repassado para a rota responsável pelo métoto READ
        else:
            return redirect(url_for('read', cpf=cpf))

    return render_template('read.html')

# rota que busca os dados de CPF cadastrado
@app.route('/read', methods=['GET', 'POST'])
def read():
    # capturando o CPF desejado
    cpf = request.args.get('cpf')

    # conectando ao banco de dados e obtendo as tabelas
    tabela_usuario, tabela_endereco = conecta_banco()

    # buscando os possíveis dados do CPF desejado
    usuario = tabela_usuario.find_one({'cpf':cpf})
    endereco = tabela_endereco.find_one({'id_usuario':cpf})

    # se não existem informações para o CPF, retorna uma mensagem (O CPF não foi cadastrado!)
    if not usuario and not endereco:
        return render_template('read.html', mensagem=True)

    #caso contrário, retorna as informações encontradas no banco de dados para o CPF informado
    else:
        return render_template('read.html', usuario=usuario, endereco=endereco)

# rota que captura o CPF a ser atualizado os dados de cadastro
@app.route('/form_busca_update', methods=['GET', 'POST'])
def form_busca_update():
    # verificando se foi feita uma requisição HTTP
    if request.method == 'POST':
        # capturando o CPF desejado
        cpf = request.form['cpf']

        # validando os digitos verificadores do cpf
        cpf_validado = valida_digitos_cpf(cpf)

        # se os dígitos verificadores forem inválidos, retorna o CPF informado e uma mensagem (CPF Inválido!)
        if not cpf_validado:
            return render_template('update.html', cpf_invalido=True, cpf=cpf)

        # caso contrário, o CPF a ser consultado é repassado para a rota responsável pela captura dos dados de cadastro
        else:
            return redirect(url_for('form_update', cpf=cpf))

    return render_template('update.html')

# rota que captura os dados de cadastro a serem atualizados
@app.route('/form_update', methods=['GET', 'POST'])
def form_update():
    # capturando o CPF desejado
    cpf = request.args.get('cpf')

    # conectando ao banco de dados e obtendo as tabelas
    tabela_usuario, tabela_endereco = conecta_banco()

    # buscando os possíveis dados do CPF desejado
    usuario = tabela_usuario.find_one({'cpf':cpf})
    endereco = tabela_endereco.find_one({'id_usuario':cpf})

    # se não existem informações para o CPF, retorna uma mensagem (O CPF informado não foi cadastrado!)
    if not usuario and not endereco:
        return render_template('update.html', mensagem='O CPF informado não foi cadastrado!')

    #caso contrário, retorna as informações encontradas no banco de dados para o CPF informado
    else:
        nome = usuario['nome']
        id =  cpf = usuario['cpf']
        idade = usuario['idade']
        sexo = usuario['sexo']

        cep = endereco['cep']
        logradouro = endereco['logradouro']
        numero = endereco['numero']
        bairro = endereco['bairro']
        cidade = endereco['cidade']
        estado = endereco['estado']

        return render_template('update.html', usuario=True, id=id, nome=nome, cpf=cpf, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado)

# rota que atualiza os dados de cadastro
@app.route('/update', methods=['GET', 'POST'])
def update():
    # verificando se foi feita uma requisição HTTP
    if request.method == 'POST':

        # capturando as informações a serem atualizadas
        id = cpf = request.form['id']
        nome = limpa_string(request.form['nome'])
        idade = request.form['idade']
        sexo = request.form['sexo']

        # buscando o endereço através do cep informado
        cep = request.form['cep']
        endereco = busca_endereco(cep)
        logradouro = endereco['logradouro']
        numero = request.form['numero']
        bairro = endereco['bairro']
        cidade = endereco['localidade']
        estado = endereco['uf']

        # validando os digitos verificadores do cpf
        cpf_validado = valida_digitos_cpf(cpf)

        # se os dígitos verificadores forem inválidos, retorna o CPF informado e uma mensagem (CPF Inválido!)
        if not cpf_validado:
            return render_template('update.html', usuario=True, cpf_invalido=True, nome=nome, cpf=cpf, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado)

        # caso contrário, os dados de cadastro são atualizados no banco de dados
        else:

            # conectando ao banco de dados e obtendo as tabelas
            tabela_usuario, tabela_endereco = conecta_banco()

            # buscando os possíveis dados do CPF desejado
            usuario = tabela_usuario.find_one({'cpf':id})
            endereco = tabela_endereco.find_one({'cpf':id})

            # dados de usuario a serem atualizados
            tabela_usuario.update_one(usuario, {"$set": {
                    'nome': nome,
                    'cpf': cpf,
                    'idade': idade,
                    'sexo': sexo
                  }
               }
            )

            # dados de endereco a serem atualizados
            tabela_endereco.update_one({'id_usuario':usuario['cpf']}, {"$set": {
                        'id_usuario': cpf,
                        'cep': cep,
                        'logradouro': logradouro,
                        'numero': numero,
                        'bairro': bairro,
                        'cidade': cidade,
                        'estado': estado
                    }
                }
            )

            return render_template('update.html', mensagem='Os dados foram atualizados!')

# rota que captura o CPF a ser deletado no banco de dados
@app.route('/form_busca_delete', methods=['GET', 'POST'])
def form_busca_delete():
    # verificando se foi feita uma requisição HTTP
    if request.method == 'POST':
        # capturando o CPF a ser deletado os dados de cadastro
        cpf = request.form['cpf']

        # validando os digitos verificadores do cpf
        cpf_validado = valida_digitos_cpf(cpf)

        # se os dígitos verificadores forem inválidos, retorna o CPF informado e uma mensagem (CPF Inválido!)
        if not cpf_validado:
            return render_template('delete.html', cpf_invalido=True, cpf=cpf)
        # caso contrário, o CPF a ser deletado é repassado para a rota responsável pela captura dos dados de cadastro
        else:
            return redirect(url_for('form_delete', cpf=cpf))

    return render_template('delete.html')

# rota que captura os dados de cadastro a serem deletados do banco de dados
@app.route('/form_delete', methods=['GET', 'POST'])
def form_delete():
    # capturando o CPF a ser deletado as informações
    cpf = request.args.get('cpf')

    # conectando ao banco de dados e obtendo as tabelas
    tabela_usuario, tabela_endereco = conecta_banco()

    # buscando os possíveis dados do CPF desejado
    usuario = tabela_usuario.find_one({'cpf':cpf})
    endereco = tabela_endereco.find_one({'id_usuario':cpf})

    # se não existem informações para o CPF, retorna uma mensagem (O CPF informado não foi cadastrado!)
    if not usuario and not endereco:
        return render_template('delete.html', mensagem='O CPF informado não foi cadastrado!')

    #caso contrário, retorna as informações encontradas no banco de dados para o CPF informado
    else:
        nome = usuario['nome']
        id =  cpf = usuario['cpf']
        idade = usuario['idade']
        sexo = usuario['sexo']

        cep = endereco['cep']
        logradouro = endereco['logradouro']
        numero = endereco['numero']
        bairro = endereco['bairro']
        cidade = endereco['cidade']
        estado = endereco['estado']

        return render_template('delete.html', usuario=True, id=id, nome=nome, cpf=cpf, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado)

# rota que deleta os dados de cadastro do banco de dados
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    # verificando se foi feita uma requisição HTTP
    if request.method == 'POST':
        # capturando o CPF a ser deletado as informações
        cpf = request.form['id']

        # conectando ao banco de dados e obtendo as tabelas
        tabela_usuario, tabela_endereco = conecta_banco()

        # deletando os dados de cadastro do CPF desejado
        x = tabela_usuario.delete_many({'cpf':cpf})
        tabela_endereco.delete_many({'id_usuario':cpf})

        return render_template('delete.html', mensagem=str(x.deleted_count)+' registro(s) deletado(s)!')

# iniciando a aplicação
if __name__ == '__main__':
    app.run(debug=True)

