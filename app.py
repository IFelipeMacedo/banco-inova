from flask import Flask, request, render_template, redirect, url_for
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

@app.route('/esqueceu_senha', methods=['GET', 'POST'])
def esqueceu_senha():
    if request.method == 'POST':
        cpf = request.form['cpf']
        cliente = banco.buscar_cliente_por_cpf(cpf)
        if cliente:
            return render_template('senha_recuperada.html', senha=cliente.senha)
        else:
            return render_template('esqueceu_senha.html', erro="CPF não encontrado")
    return render_template('esqueceu_senha.html')

@app.route('/senha_recuperada')
def senha_recuperada():
    return render_template('senha_recuperada.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']
        banco.adicionar_cliente(nome, cpf, senha)
        return redirect(url_for('login'))
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

@app.route('/alterar_nome', methods=['GET', 'POST'])
def alterar_nome():
    global cpf_cliente_log
    if request.method == 'POST':
        novo_nome = request.form['novo_nome']
        banco.alterar_nome(cpf_cliente_log, novo_nome)
        return redirect(url_for('perfil'))
    else:
        cliente = banco.buscar_cliente_por_cpf(cpf_cliente_log)
        nome_atual = cliente.nome if cliente else ''
        return render_template('alterar_nome.html', nome_atual=nome_atual)

@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    global cpf_cliente_log
    global senha_cliente_log
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmacao_senha = request.form['confirmacao_senha']
        
        if nova_senha != confirmacao_senha:
            return render_template('alterar_senha.html', erro="Nova senha e confirmação não coincidem!")
        
        cliente = banco.buscar_cliente_por_cpf(cpf_cliente_log)
        if cliente and cliente.senha == senha_atual:
            banco.atualizar_senha_cliente(cpf_cliente_log, nova_senha)
            senha_cliente_log = nova_senha
            return redirect(url_for('perfil'))
        else:
            return render_template('alterar_senha.html', erro="Senha atual incorreta!")
    
    return render_template('alterar_senha.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/depositar', methods=['GET', 'POST'])
def depositar():
    global cpf_cliente_log
    if request.method == 'POST':
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_deposito(cpf_cliente_log, valor, senha)
        return redirect(url_for('index'))
    return render_template('depositar.html')

@app.route('/sacar', methods=['GET', 'POST'])
def sacar():
    global cpf_cliente_log
    if request.method == 'POST':
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_saque(cpf_cliente_log, valor, senha)
        return redirect(url_for('index'))
    return render_template('sacar.html')

@app.route('/transferir', methods=['GET', 'POST'])
def transferir():
    global cpf_cliente_log
    if request.method == 'POST':
        cpf_destino = request.form['cpf_destino']
        valor = float(request.form['valor'])
        senha = request.form['senha']
        banco.realizar_transferencia(cpf_cliente_log, cpf_destino, valor, senha)
        return redirect(url_for('index'))
    return render_template('transferir.html')

@app.route('/visualizar_extrato', methods=['GET', 'POST'])
def visualizar_extrato():
    global cpf_cliente_log
    global senha_cliente_log
    extrato = banco.visualizar_extrato(cpf_cliente_log, senha_cliente_log)
    if extrato:
        extrato_list = extrato.split('\n')
        return render_template('extrato.html', extrato_list=extrato_list)
    else:
        return render_template('extrato.html', erro="Cliente não encontrado ou senha incorreta!")

@app.route('/saldo')
def saldo():
    global cpf_cliente_log
    global senha_cliente_log
    saldo = banco.visualizar_saldo(cpf_cliente_log, senha_cliente_log)
    if saldo is not None:
        return render_template('saldo.html', saldo=saldo)
    else:
        return render_template('saldo.html', erro="Cliente não encontrado ou senha incorreta!")

@app.route('/logout')
def logout():
    global cpf_cliente_log, senha_cliente_log
    cpf_cliente_log = ''
    senha_cliente_log = ''
    return redirect(url_for('login'))

@app.route('/excluir_conta', methods=['GET', 'POST'])
def excluir_conta():
    global cpf_cliente_log
    if request.method == 'POST':
        senha = request.form['senha']
        cliente = banco.buscar_cliente_por_cpf(cpf_cliente_log)
        if cliente and cliente.senha == senha:
            banco.excluir_cliente(cpf_cliente_log, senha)
            return redirect(url_for('login'))
        else:
            return render_template('excluir_conta.html', erro="Senha incorreta!")
    return render_template('excluir_conta.html')

if __name__ == '__main__':
    app.run(debug=True)
