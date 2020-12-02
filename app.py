from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import pymongo
from pymongo import MongoClient
import re, string, requests, json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sedecti'

def conecta_banco():
    credenciais = json.load(open('static/credenciais_banco.json'))
    cliente = MongoClient("mongodb+srv://hiago:" + credenciais['password'] + "@cluster0.sn5zy.mongodb.net/" + credenciais['database'] + "?retryWrites=true&w=majority")

    banco = cliente['sedecti']

    return banco['usuarios'], banco['enderecos']

def valida_digitos_cpf(cpf):

    # verificando se o cpf está no padrão 111.222.333-44 ou 11122233344
    if not re.search('\d{3}.\d{3}.\d{3}-\d{2}|\d{11}', cpf):
        return False

    # removendo possíveis pontuações
    cpf = cpf.replace('.', '').replace('-','')

    # cálculo dos digitos verificadores

    """
    multiplicador 10 9  8   7  6  5    4  3  2
    digito        1  1  1 . 2  2  2  . 3  3  3 - primeiro digito

    multiplicador 11 10 9  8   7  6  5    4  3   2
    digito        1  1  1 . 2  2  2  . 3  3  3 - 4 segundo digito
    """

    # somando a multiplicação dos digitos pelos valores posicionais em ordem decrescente
    primeiro_digito = 0
    segundo_digito = int(cpf[0])*11

    for i in range(10,1,-1):
        primeiro_digito += int(cpf[10-i])*i
        segundo_digito += int(cpf[(10-i)+1])*i

    primeiro = (11 - (primeiro_digito%11))
    segundo = (11 - (segundo_digito%11))

    # verificando se os dígitos estão corretos
    if str(primeiro) == cpf[-2] and str(segundo) == cpf[-1]:
        return True

    return False

def busca_endereco(cep):
    # validando endereco pelo cep
    url = 'https://viacep.com.br/ws/' + cep + '/json/unicode/'
    response = requests.get(url)

    return response.json()

def limpa_string(nome):
    # removendo caracteres indesejados
    nome = re.sub('[0-9]|[^A-Za-z ]', '', nome)

    # removendo o excesso de espaços
    nome = ' '.join(nome.split())

    # retornando a string com as letras iniciais de cada palavra em maiúsculo
    return nome.title()

# carregando o template de menu (CREATE, READ, UPDATE, DELETE)
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

# validando os dados formulário CREATE
@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if request.method == 'POST':

        # formatando o nome inserido com possíveis caracteres inapropriados
        nome = limpa_string(request.form['nome'])
        cpf = request.form['cpf']

        idade = request.form['idade']
        sexo = request.form['sexo']

        cep = request.form['cep']
        endereco = busca_endereco(cep)

        logradouro = endereco['logradouro']
        numero = request.form['numero']
        bairro = endereco['bairro']
        cidade = endereco['localidade']
        estado = endereco['uf']

        # validando os digitos verificadores do cpf
        if not valida_digitos_cpf(cpf):
            return render_template('create.html', nome=nome, cpf_invalido=True, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado)

        else:
            return redirect(url_for('create', nome=nome, cpf=cpf, idade=idade, sexo=sexo, cep=cep, logradouro=logradouro, numero=numero, bairro=bairro, cidade=cidade, estado=estado))

    return render_template('create.html')

# salvando os dados do formulário CREATE
@app.route('/create', methods=['GET','POST'])
def create():

    # conectando as tabelas do banco de dados
    tabela_usuario, tabela_endereco = conecta_banco()

    usuario = {
        'nome': request.args.get('nome'),
        'cpf': request.args.get('cpf'),
        'idade': request.args.get('idade'),
        'sexo': request.args.get('sexo')
    }

    endereco = {
        'id_usuario': request.args.get('cpf'),
        'cep': request.args.get('cep'),
        'logradouro': request.args.get('logradouro'),
        'numero': request.args.get('numero'),
        'bairro': request.args.get('bairro'),
        'cidade': request.args.get('cidade'),
        'estado': request.args.get('estado')
    }

    id_usuario = tabela_usuario.find_one(usuario)

    # verificando os dados de usuário já foram cadastrados anteriormente
    # salvando os dados do formulário na nuvem
    if not id_usuario:
        tabela_usuario.insert_one(usuario)
        id_usuario = tabela_usuario.find_one(usuario)
        tabela_endereco.insert_one(endereco)

    return render_template('create.html', mensagem='Registro inserido no banco de dados!')


@app.route('/form_read', methods=['GET', 'POST'])
def form_read():
    if request.method == 'POST':
        cpf = request.form['cpf']
        cpf_validado = valida_digitos_cpf(cpf)

        if not cpf_validado:
            return render_template('read.html', cpf_invalido=True, cpf=cpf)
        else:
            return redirect(url_for('read', cpf=cpf))

    return render_template('read.html')

@app.route('/read', methods=['GET', 'POST'])
def read():
    cpf = request.args.get('cpf')

    # conectando as tabelas do banco de dados
    tabela_usuario, tabela_endereco = conecta_banco()

    usuario = tabela_usuario.find_one({'cpf':cpf})

    if not usuario:
        return 'NOT FOUND CPF!'
    else:
        endereco = tabela_endereco.find_one({'id_usuario':cpf})
        return render_template('read.html', usuario=usuario, endereco=endereco)

@app.route('/form_update', methods=['GET', 'POST'])
def form_update():
    if request.method == 'POST':
        cpf = request.form['cpf']
        cpf_validado = valida_digitos_cpf(cpf)

        if not cpf_validado:
            return render_template('update.html', cpf_invalido=True, cpf=cpf)
        else:
            return redirect(url_for('update', cpf=cpf))

    return render_template('update.html')

@app.route('/update', methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)

