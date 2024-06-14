from flask import Flask, request, jsonify, render_template, redirect, url_for
from banco_sqlite import Banco

app = Flask(__name__)
banco = Banco()

@app.route('/')
def login():
    return render_template('login.html')

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

@app.route('/pagina_usuario')
def pagina_usuario():
    return render_template('pagina_usuario.html')

@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']
        banco.adicionar_cliente(nome, cpf, senha)
        return redirect(url_for('index'))
    return render_template('adicionar_cliente.html')

@app.route('/depositar', methods=['GET', 'POST'])
def depositar():
    if request.method == 'POST':
        cpf = request.form['cpf']
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_deposito(cpf, valor, senha)
        return redirect(url_for('login'))
    return render_template('depositar.html')

@app.route('/sacar', methods=['GET', 'POST'])
def sacar():
    if request.method == 'POST':
        cpf = request.form['cpf']
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_saque(cpf, valor, senha)
        return redirect(url_for('login'))
    return render_template('sacar.html')

@app.route('/transferir', methods=['GET', 'POST'])
def transferir():
    if request.method == 'POST':
        cpf_origem = request.form['cpf_origem']
        cpf_destino = request.form['cpf_destino']
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_transferencia(cpf_origem, cpf_destino, valor, senha)
        return redirect(url_for('login'))
    return render_template('transferir.html')

@app.route('/visualizar_extrato', methods=['GET', 'POST'])
def visualizar_extrato():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        extrato = banco.visualizar_extrato(cpf, senha)
        if extrato:
            return render_template('extrato.html', extrato=extrato)  
        else:
            return render_template('visualizar_extrato.html', erro="Cliente não encontrado ou senha incorreta!")
    return render_template('visualizar_extrato.html')

@app.route('/visualizar_saldo', methods=['GET', 'POST'])
def visualizar_saldo():
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        saldo = banco.visualizar_saldo(cpf, senha)
        if saldo is not None:
            return render_template('saldo.html', saldo=saldo)
        else:
            return render_template('visualizar_saldo.html', erro="Cliente não encontrado ou senha incorreta!")
    return render_template('visualizar_saldo.html')

if __name__ == '__main__':
    app.run(debug=True)
