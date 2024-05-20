from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuração do banco de dados SQLite
DATABASE = 'biblioteca.db'

# Função para criar a tabela se não existir
def criar_tabela(): 
 
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()

    # Tabela para clientes (chave primária auto-incremental. Esse é o identificador único para cada cliente)
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (  
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                nome TEXT, 
                email TEXT UNIQUE, 
                senha TEXT )''') 

    # Tabela para veículos 
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos ( 
              id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,  
              marca TEXT, 
              modelo TEXT, 
              categoria TEXT, 
              transmissao TEXT,
              tipo_veiculo TEXT,
              quantidade_pessoas TEXT, 
              max_pessoas INTEGER,  
              imagem TEXT, 
              valor_diaria REAL, 
              ultima_revisao TEXT,
              proxima_revisao TEXT,
              ultima_inspecao TEXT, 
              disponivel BOOLEAN )''')  
    
    #INTEGER (números inteiros) vs REAL (números decimais)
    #disponivel: Booleano, indica se o veículo está disponível para reserva (TRUE) ou já está reservado (FALSE)

    # Tabela para reservas 
    c.execute('''CREATE TABLE IF NOT EXISTS reservas ( 
              id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
              cliente_id INTEGER, 
              veiculo_id INTEGER, 
              data_inicio TEXT, 
              data_fim TEXT, 
              valor_total REAL, 
              FOREIGN KEY(cliente_id)  
              REFERENCES clientes(id), 
              FOREIGN KEY(veiculo_id) 
              REFERENCES veiculos(id) )''') 

    #Chave estrangeira: cliente_id garante que cada reserva esteja associada a um cliente existente na tabela clientes
    #Chave estrangeira: veiculo_id garante que cada reserva esteja associada a um veículo existente na tabela veiculos

    # Tabela para pagamentos 
    c.execute('''CREATE TABLE IF NOT EXISTS pagamentos ( 
              id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
              reserva_id INTEGER, 
              tipo_pagamento TEXT, 
              nome_cartao TEXT, 
              numero_cartao TEXT, 
              data_validade TEXT,
              cvv TEXT, 
              valor REAL, 
              status TEXT, 
              FOREIGN KEY(reserva_id) 
              REFERENCES reservas(id) )''') 

    #status: Texto, indica o status do pagamento (por exemplo, Aprovado, Pendente, Cancelado)
    #Chave estrangeira: reserva_id garante que cada pagamento esteja associado a uma reserva existente na tabela reservas

    # Guardar as alterações com commit e fechar a conexão
    conn.commit() 
    conn.close()

# Chamar a função para criar as tabelas
criar_tabela()

# Função para adicionar um cliente no banco de dados (Permite adicionar um novo cliente ao banco de dados, inserindo nome, email e senha na tabela clientes)
def adicionar_cliente(nome, email, senha):
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE email = ?", (email,))
    cliente = c.fetchone()
    if cliente:
        # Email já exite
        return False
    else:
        c.execute("INSERT INTO clientes (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        conn.close()
        return True
    
#Função para verificar login (Pesquisa na tabela clientes um registro com o email e senha informados. Retorna o registro do cliente caso encontrado, ou None se o login falhar)
def verificar_login(email, senha): 
    conn = sqlite3.connect('biblioteca.db') 
    c = conn.cursor() 
    c.execute("SELECT * FROM clientes WHERE email = ? AND senha = ?", (email, senha)) 
    cliente = c.fetchone() 
    conn.close() 
    return cliente

# Função para inserir veículos na Base de Dados
def inserir_veiculo(marca, modelo, categoria, transmissao, tipo_veiculo, quantidade_pessoas, max_pessoas, imagem, valor_diaria, ultima_revisao, proxima_revisao, ultima_inspecao, disponivel):
    # Convertendo as datas para objetos datetime
    ultima_revisao = datetime.strptime(ultima_revisao, '%Y-%m-%d')
    proxima_revisao = datetime.strptime(proxima_revisao, '%Y-%m-%d')
    ultima_inspecao = datetime.strptime(ultima_inspecao, '%Y-%m-%d')
    
    # Verificando se o veículo já existe na tabela
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()
    c.execute("SELECT * FROM veiculos WHERE marca = ? AND modelo = ?", (marca, modelo))
    veiculo = c.fetchone()
    
    if veiculo:
        # Veículo já existe na tabela
        print(f"Veículo {marca} {modelo} já está na base de dados.")
    else:
        # Verificando as condições de disponibilidade
        hoje = datetime.now()
        if (hoje - ultima_inspecao > timedelta(days=365)) or (proxima_revisao < hoje):
            disponivel = 0  # Indisponível
        else:
            disponivel = 1  # Disponível
        
        # Inserir o veículo na tabela
        c.execute("INSERT INTO veiculos (marca, modelo, categoria, transmissao, tipo_veiculo, quantidade_pessoas, max_pessoas, imagem, valor_diaria, ultima_revisao, proxima_revisao, ultima_inspecao, disponivel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (marca, modelo, categoria, transmissao, tipo_veiculo, quantidade_pessoas, max_pessoas, imagem, valor_diaria, ultima_revisao, proxima_revisao, ultima_inspecao, disponivel))
        conn.commit()
        print(f"Veículo {marca} {modelo} inserido com sucesso na base de dados.")
    
    conn.close()

# Chamar a função inserir_veiculo para adicionar veículos
inserir_veiculo('Fiat', 'Fiat Uno', 'Pequeno', 'Manual', 'Carro','1-4', 4, 'Fiat.jpg', 50.0, '2023-12-01', '2024-07-01', '2023-12-05', 1)
inserir_veiculo('Volkswagen', 'Volkswagen Gol', 'Pequeno', 'Automático', 'Carro','1-4', 4, 'Volkswagen.jpg', 60.0, '2021-05-01', '2022-07-01', '2022-12-01', 0)
inserir_veiculo('Ford', 'Ford Focus', 'Médio', 'Manual', 'Carro','1-4', 4, 'Ford.jpg', 55.0, '2024-04-20', '2024-10-20', '2023-11-20', 1)
inserir_veiculo('Jeep', 'Jeep Renegade', 'SUV', 'Automático', 'Carro','1-4', 4, 'Jeep.jpg', 75.0, '2024-04-20', '2024-10-20', '2023-11-20', 1)
inserir_veiculo('BMW', 'BMW X5', 'Luxo',  'Automático', 'Carro','mais_7', 8, 'BMW.jpg', 90.0, '2024-03-12', '2024-09-12', '2022-12-01', 0)
inserir_veiculo('Yamaha', 'Yamaha NMax 160', 'Pequeno', 'Automático', 'Moto','1-4', 2, 'Yamaha.jpg', 50.0, '2024-01-02', '2024-07-02', '2024-01-15', 1)
inserir_veiculo('Kawasaki', 'Kawasaki Ninja 650', 'Médio', 'Manual', 'Moto','1-4', 2, 'Kawasaki.jpg', 55.0, '2024-03-09', '2024-09-09', '2023-12-11', 1)
inserir_veiculo('Ducati', 'Ducati Diavel 1260', 'Médio', 'Manual', 'Moto','1-4', 2, 'Ducati.jpg', 60.0, '2024-03-08', '2024-09-08', '2023-12-10', 1)

def verificar_veiculos_disponiveis(categoria=None, transmissao=None, tipo_veiculo=None, quantidade_pessoas=None):
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()

    # Construir a consulta base
    query = "SELECT * FROM veiculos WHERE disponivel = 1"
    conditions = []
    params = {}

    # Adicionar cláusulas WHERE conforme necessário
    if categoria:
        conditions.append("categoria = :categoria")
        params['categoria'] = categoria
    if transmissao:
        conditions.append("transmissao = :transmissao")
        params['transmissao'] = transmissao
    if tipo_veiculo:
        conditions.append("tipo_veiculo = :tipo_veiculo")
        params['tipo_veiculo'] = tipo_veiculo
    if quantidade_pessoas:
        if quantidade_pessoas == '1-4':
            conditions.append("max_pessoas BETWEEN 1 AND 4")
        elif quantidade_pessoas == '5-6':
            conditions.append("max_pessoas BETWEEN 5 AND 6")
        elif quantidade_pessoas == 'mais_7':
            conditions.append("max_pessoas >= 7")

    # Construir a cláusula WHERE combinando todas as condições com OR
    if conditions:
        query += " AND (" + " OR ".join(conditions) + ")"
        
    print("Query SQL:", query)
    print("Parâmetros:", params)

    # Executar a consulta
    c.execute(query, params)
    result = c.fetchall()

    conn.close()
    return result

# Função para reservar veículos (Insere um registro na tabela reservas com as informações do cliente, veículo, datas de reserva e valor total)
def reservar_veiculo(cliente_id, veiculo_id, data_inicio, data_fim, valor_total):
     conn = sqlite3.connect('biblioteca.db') 
     c = conn.cursor() 
     c.execute("INSERT INTO reservas (cliente_id, veiculo_id, data_inicio, data_fim, valor_total) VALUES (?, ?, ?, ?, ?)", (cliente_id, veiculo_id, data_inicio, data_fim, valor_total)) 
     conn.commit() 
     conn.close()

# Função para fazer um pagamento (Insere um registro na tabela pagamentos com os detalhes do pagamento, incluindo tipo, dados do cartão, valor e status)
def fazer_pagamento(reserva_id, tipo_pagamento, nome_cartao, numero_cartao, data_validade, cvv, valor, status):
    conn = sqlite3.connect('biblioteca.db')
    c = conn.cursor()
    c.execute("INSERT INTO pagamentos (reserva_id, tipo_pagamento, nome_cartao, numero_cartao, data_validade, cvv, valor, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (reserva_id, tipo_pagamento, nome_cartao, numero_cartao, data_validade, cvv, valor, status))
    conn.commit()
    conn.close()

# Rota primeira página (/) 
@app.route("/")
def index():
    return render_template("index.html")

# Rota para a página de registo (/registo)
@app.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        if adicionar_cliente(nome, email, senha):
            return redirect(url_for("login"))
        else:
            return "Erro ao registar cliente!"
    return render_template("registo.html")

# Rota para a página de login (/login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        if verificar_login(email, senha):
            return redirect(url_for('veiculos'))
        else:
            return render_template("login.html", erro="Login inválido")
    else:
        return render_template("login.html")

# Rota para a página de veículos (/veiculos)
@app.route('/veiculos', methods=['GET', 'POST'])
def veiculos():
    if request.method == 'POST':
        categoria = request.form['categoria']
        transmissao = request.form['transmissao']
        tipo_veiculo = request.form['tipo_veiculo']
        quantidade_pessoas = request.form['quantidade_pessoas']
        
        # Consulta com base nos critérios
        veiculos_disponiveis = verificar_veiculos_disponiveis(categoria, transmissao, tipo_veiculo, quantidade_pessoas)

        # Renderizar a página veiculos.html com os resultados
        return render_template('veiculos.html', veiculos=veiculos_disponiveis)
    else:
        return render_template('veiculos.html')


# Rota para a página de reserva (/reserva)
@app.route("/reserva", methods=["GET", "POST"])
def reserva():
    if request.method == "POST":
        # Processar dados da reserva
        cliente_id = request.form["cliente_id"]  
        veiculo_id = request.form["veiculo_id"]
        data_inicio = request.form["data_inicio"]
        data_fim = request.form["data_fim"]

        # Chamar a função para adicionar a reserva
        reservar_veiculo(cliente_id, veiculo_id, data_inicio, data_fim)
        
        # Redirecionar para a página de pagamento
        return redirect(url_for("reserva_lista"))
    return render_template("reserva.html")

# Rota para a página de lista de reservas (/reserva_lista)
@app.route('/reserva_lista')
def confirmacao():
    return render_template('reserva_lista.html')

# Rota para a página de alteração de reserva (/reserva_alt)
@app.route('/reserva_alt', methods=['GET', 'POST'])
def reserva_alt():
    if request.method == 'POST':
        # Processar o formulário de alteração de reserva
        # Após processar, redirecionar para a página de lista de reservas
        return redirect(url_for('confirmacao'))

    # Se for uma requisição GET, apenas renderizar o template
    return render_template('reserva_alt.html')

# Rota para a página de pagamento (/pagamento)
@app.route("/pagamento", methods=["GET", "POST"])
def pagamento():
    if request.method == "POST":
        tipo_pagamento = request.form["tipo_pagamento"]
        nome_cartao = request.form["nome_cartao"]
        numero_cartao = request.form["numero_cartao"]
        data_validade = request.form["data_validade"]
        cvv = request.form["cvv"]
        # Processar o pagamento de acordo com os dados fornecidos
        fazer_pagamento(tipo_pagamento, nome_cartao, numero_cartao, data_validade, cvv)   
        return redirect(url_for("confirmacao"))
    return render_template("pagamento.html")

# Rota para a página de confirmação (/confirmacao)
@app.route('/confirmacao')
def confirmacao_reserva():
    return render_template('confirmacao.html')

# Colocar o site no ar
if __name__ == '__main__': 
    app.run(debug=True)  





    








