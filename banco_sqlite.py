import sqlite3

class Cliente:
    def __init__(self, nome, cpf, senha, id=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.senha = senha
        self.conta = None

    def __str__(self):
        return f"Cliente: {self.nome}, CPF: {self.cpf}"

class Conta:
    def __init__(self, numero, cliente, saldo=0.0, extrato=None):
        self.numero = numero
        self.cliente = cliente
        self.saldo = saldo
        self.extrato = extrato if extrato else []

    def depositar(self, valor, senha):
        if senha == self.cliente.senha:
            valor = float(valor)
            self.saldo += valor
            self._atualizar_saldo()
            self._registrar_extrato(f"Depósito de R${valor}")
            print("Depósito realizado com sucesso!")
        else:
            print("Senha incorreta!")

    def sacar(self, valor, senha):
        if senha == self.cliente.senha:
            valor = float(valor)
            if valor <= self.saldo:
                self.saldo -= valor
                self._atualizar_saldo()
                self._registrar_extrato(f"Saque de R${valor}")
                print("Saque realizado com sucesso!")
            else:
                print("Saldo insuficiente!")
        else:
            print("Senha incorreta!")

    def transferir(self, valor, conta_destino, senha):
        if senha == self.cliente.senha:
            valor = float(valor)
            if valor <= self.saldo:
                self.saldo -= valor
                conta_destino.saldo += valor 
                self._atualizar_saldo() 
                conta_destino._atualizar_saldo()
                self._registrar_extrato(f"Transferência de R${valor} para conta {conta_destino.cliente.cpf}")
                conta_destino._registrar_extrato(f"Transferência de R${valor} recebida da conta {self.cliente.cpf}")
                print("Transferência realizada com sucesso!")
            else:
                print("Saldo insuficiente!")
        else:
            print("Senha incorreta!")

    def visualizar_saldo(self, senha):
        if senha == self.cliente.senha:
            return self.saldo
        else:
            print("Senha incorreta!")

    def visualizar_extrato(self, senha):
        if senha == self.cliente.senha:
            return self.extrato
        else:
            print("Senha incorreta!")

    def _atualizar_saldo(self):
        conn = sqlite3.connect("projeto_banco.db", check_same_thread=False)
        cur = conn.cursor()
        cur.execute("UPDATE contas SET saldo = ? WHERE numero = ?", (self.saldo, self.numero))
        conn.commit()
        cur.close()
        conn.close()



    def _registrar_extrato(self, mensagem):
        conn = sqlite3.connect("projeto_banco.db", check_same_thread=False)
        cur = conn.cursor()

        # Primeiro, recuperamos o extrato atual da conta
        cur.execute("SELECT extrato FROM contas WHERE numero = ?", (self.numero,))
        resultado = cur.fetchone()
        extrato_atual = resultado[0] if resultado else ""

        # Concatenamos o novo extrato com o extrato existente
        novo_extrato = extrato_atual + "\n" + mensagem

        # Atualizamos o campo extrato na tabela contas
        cur.execute("UPDATE contas SET extrato = ? WHERE numero = ?", (novo_extrato, self.numero))
        
        conn.commit()
        cur.close()
        conn.close()



class Banco:
    def __init__(self):
        self.conn = sqlite3.connect("projeto_banco.db", check_same_thread=False)
        self.cur = self.conn.cursor()

        # Criação da tabela clientes se não existir
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')

        # Criação da tabela contas se não existir
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS contas (
                numero INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER UNIQUE NOT NULL,
                saldo FLOAT NOT NULL DEFAULT 0.0,
                extrato TEXT DEFAULT '',
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')

        self.conn.commit()    

    def adicionar_cliente(self, nome, cpf, senha):
        self.cur.execute("INSERT INTO clientes (nome, cpf, senha) VALUES (?, ?, ?)", (nome, cpf, senha))
        cliente_id = self.cur.lastrowid
        self.cur.execute("INSERT INTO contas (cliente_id) VALUES (?)", (cliente_id,))
        numero_conta = self.cur.lastrowid
        self.conn.commit()
        cliente = Cliente(nome, cpf, senha, id=cliente_id)
        conta = Conta(numero_conta, cliente)
        cliente.conta = conta
        print(f"Cliente {nome} adicionado com sucesso!")

    def logar_cliente(self, cpf, senha):
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente != None and cliente.senha == senha:
            return True
        return False
            

    def buscar_cliente_por_cpf(self, cpf):
        self.cur.execute("SELECT id, nome, cpf, senha FROM clientes WHERE cpf = ?", (cpf,))
        row = self.cur.fetchone()
        if row:
            cliente_id, nome, cpf, senha = row
            self.cur.execute("SELECT numero, saldo, extrato FROM contas WHERE cliente_id = ?", (cliente_id,))
            conta_row = self.cur.fetchone()
            if conta_row:
                numero_conta, saldo, extrato = conta_row
                cliente = Cliente(nome, cpf, senha, id=cliente_id)
                conta = Conta(numero_conta, cliente, saldo, extrato)
                cliente.conta = conta
                return cliente
            else:
                print(f"Nenhuma conta encontrada para o cliente com CPF {cpf}")
                return None
        else:
            print(f"Cliente com CPF {cpf} não encontrado")
            return None

    def realizar_deposito(self, cpf, valor, senha):
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente:
            cliente.conta.depositar(valor, senha)
        else:
            print("Cliente não encontrado!")

    def realizar_saque(self, cpf, valor, senha):
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente:
            cliente.conta.sacar(valor, senha)
        else:
            print("Cliente não encontrado!")

    def realizar_transferencia(self, cpf_origem, cpf_destino, valor, senha):
        cliente_origem = self.buscar_cliente_por_cpf(cpf_origem)
        cliente_destino = self.buscar_cliente_por_cpf(cpf_destino)
        if cliente_origem and cliente_destino:
            cliente_origem.conta.transferir(valor, cliente_destino.conta, senha)
        else:
            print("Cliente de origem ou destino não encontrado!")

    def visualizar_extrato(self, cpf, senha):
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente:
            return cliente.conta.visualizar_extrato(senha)
        else:
            print("Cliente não encontrado!")

    def visualizar_saldo(self, cpf, senha):
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente:
            return cliente.conta.visualizar_saldo(senha)
        else:
            print("Cliente não encontrado!")

    def __del__(self):
        self.cur.close()
        self.conn.close()

# Exemplo de uso:
banco = Banco()
