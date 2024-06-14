from flask import Flask, request, jsonify, render_template, redirect, url_for
from banco_sqlite import Banco

app = Flask(__name__)
banco = Banco()
cpf_cliente_log = ''
senha_cliente_log = ''

@app.route('/')
def login_redirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global cpf_cliente_log
        global senha_cliente_log
        cpf_cliente_log = request.form['cpf']
        senha_cliente_log = request.form['senha']
        retorno = banco.logar_cliente(cpf_cliente_log, senha_cliente_log)
        if retorno:
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']
        banco.adicionar_cliente(nome, cpf, senha)
        return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/pagina_admin', methods=['GET', 'POST'])
def pagina_admin():
    if request.method == 'POST':
        senha_admin = request.form.get('senha_admin')
        if senha_admin == 'senha_correta':
            return redirect(url_for('index'))
        else:
            return render_template('pagina_admin.html', erro="Senha de admin incorreta!")
    else:
        return render_template('pagina_admin.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('configuracao_conta', methods=['GET', 'POST'])
def configuracao_conta():
    if request.method == 'POST':
        senha = request.form['senha']
        banco.atualizar_cliente(senha, cpf_cliente_log)
        return redirect(url_for('pagina_usuario'))
    return render_template('configuracao_conta.html')

@app.route('/pagina_usuario')
def pagina_usuario():
    return render_template('pagina_usuario.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']
        banco.adicionar_cliente(nome, cpf, senha)
        return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/depositar', methods=['GET', 'POST'])
def depositar():
    if request.method == 'POST':
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_deposito(cpf_cliente_log, valor, senha)
        return redirect(url_for('pagina_usuario'))
    return render_template('depositar.html')

@app.route('/sacar', methods=['GET', 'POST'])
def sacar():
    if request.method == 'POST':
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_saque(cpf_cliente_log, valor, senha)
        return redirect(url_for('pagina_usuario'))
    return render_template('sacar.html')

@app.route('/transferir', methods=['GET', 'POST'])
def transferir():
    if request.method == 'POST':
        cpf_destino = request.form['cpf_destino']
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_transferencia(cpf_cliente_log, cpf_destino, valor, senha)
        return redirect(url_for('pagina_usuario'))
    return render_template('transferir.html')

@app.route('/visualizar_extrato', methods=['GET', 'POST'])
def visualizar_extrato():
    extrato = banco.visualizar_extrato(cpf_cliente_log, senha_cliente_log)
    if extrato:
        return render_template('extrato.html', extrato=extrato)  
    else:
        return render_template('extrato.html', erro="Cliente não encontrado ou senha incorreta!")

@app.route('/visualizar_saldo', methods=['GET', 'POST'])
def visualizar_saldo():
    saldo = banco.visualizar_saldo(cpf_cliente_log, senha_cliente_log)
    if saldo is not None:
        return render_template('saldo.html', saldo=saldo)
    else:
        return render_template('saldo.html', erro="Cliente não encontrado ou senha incorreta!")

if __name__ == '__main__':
    app.run(debug=True)
