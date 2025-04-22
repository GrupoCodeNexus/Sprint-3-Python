import json
from datetime import datetime, timedelta
from collections import Counter
import os

from flask import Flask, render_template, request, redirect, url_for

# Nome dos arquivos JSON locais
CADASTROS_FILE = "Data/cadastros.json"
LOGIN_FILE = "Data/login.json"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'  # Para funcionalidades como sessões (se adicionar login web)

# Lista para armazenar os tratamentos cadastrados (agora populada via arquivo JSON)
tratamentos_cadastrados = []

# Função para ler dados de um arquivo JSON local
def ler_dados_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar JSON do arquivo '{filename}'.")
        return None

# Função para escrever dados em um arquivo JSON local
def escrever_dados_json(filename, dados):
    try:
        with open(filename, 'w') as f:
            json.dump(dados, f, indent=4)
        return True
    except IOError:
        print(f"Erro: Falha ao escrever no arquivo '{filename}'.")
        return False

# Função para obter os dados de tratamento do arquivo cadastros.json
def obter_dados_cadastros():
    cadastros_data = ler_dados_json(CADASTROS_FILE)
    if cadastros_data and isinstance(cadastros_data, list):
        return cadastros_data
    return []

# Função para cadastrar um novo tratamento (adiciona ao arquivo cadastros.json)
def cadastrar_tratamento(nome, idade, medicamento, responsavel):
    medicamento_normalizado = medicamento.strip().capitalize() # Remove espaços e converte para a primeira letra ser maiuscula
    novo_tratamento = {
        'nome': nome.strip().title(),
        'idade': idade,
        'medicamento': medicamento_normalizado,
        'responsavel': responsavel.strip().title(),
        'data_cadastro': datetime.now().isoformat()
    }

    tratamentos = obter_dados_cadastros()
    tratamentos.append(novo_tratamento)
    if escrever_dados_json(CADASTROS_FILE, tratamentos):
        global tratamentos_cadastrados
        tratamentos_cadastrados = tratamentos # Atualiza a lista em memória
        return True
    else:
        return False

# Função para remover um tratamento (atualiza o arquivo cadastros.json)
def remover_tratamento(indice):
    global tratamentos_cadastrados
    if not tratamentos_cadastrados:
        return False

    if 1 <= indice <= len(tratamentos_cadastrados):
        tratamento_removido = tratamentos_cadastrados.pop(indice - 1)
        if escrever_dados_json(CADASTROS_FILE, tratamentos_cadastrados):
            return tratamento_removido['nome']
        else:
            tratamentos_cadastrados.insert(indice - 1, tratamento_removido) # Reverte a remoção em caso de erro
            return None
    else:
        return False

# Função para listar todos os tratamentos (da lista em memória)
def listar_tratamentos():
    return tratamentos_cadastrados

# --- Funções para Geração de Relatórios ---

def gerar_relatorio_cadastros_data():
    agora = datetime.now()
    ultimas_24_horas = agora - timedelta(hours=24)
    ultima_semana = agora - timedelta(weeks=1)
    ultimo_mes = agora - timedelta(days=30) # Aproximação de um mês

    cadastrados_24h = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimas_24_horas)
    cadastrados_semana = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultima_semana)
    cadastrados_mes = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimo_mes)

    return {
        'cadastrados_24h': cadastrados_24h,
        'cadastrados_semana': cadastrados_semana,
        'cadastrados_mes': cadastrados_mes
    }

def gerar_relatorio_frequencia_medicamentos_data():
    medicamentos = [tratamento['medicamento'] for tratamento in tratamentos_cadastrados]
    frequencia = Counter(medicamentos)

    mais_frequente = frequencia.most_common(1)[0] if frequencia else None
    menos_frequente = frequencia.most_common()[:-2:-1][0] if len(frequencia) > 1 else (frequencia.most_common(1)[0] if len(frequencia) == 1 else None)

    return {
        'mais_frequente': mais_frequente,
        'menos_frequente': menos_frequente,
        'total_medicamentos': len(frequencia)
    }

# --- Rotas Flask ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/realizar_login', methods=['POST'])
def realizar_login_web():
    user = request.form['usuario']
    password = request.form['senha']

    usuarios_data = ler_dados_json(LOGIN_FILE)
    if usuarios_data:
        for login_usuario in usuarios_data:
            if login_usuario['usuario'] == user and login_usuario['senha'] == password:
                global tratamentos_cadastrados
                tratamentos_cadastrados = obter_dados_cadastros() or []
                return redirect(url_for('listar'))
        return render_template('login.html', erro_login=True)
    else:
        return render_template('login.html', erro_login=True)

@app.route('/listar')
def listar():
    tratamentos = listar_tratamentos()
    return render_template('listar_tratamentos.html', tratamentos=tratamentos)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = request.form['idade']
        medicamento = request.form['medicamento']
        responsavel = request.form['responsavel']  # Novo campo do formulário
        if cadastrar_tratamento(nome, idade, medicamento, responsavel):
            return redirect(url_for('listar'))
        else:
            return render_template('cadastrar_tratamento.html', erro_cadastro=True)
    return render_template('cadastrar_tratamento.html')

@app.route('/remover/<int:indice>')
def remover(indice):
    nome_removido = remover_tratamento(indice)
    if nome_removido:
        return redirect(url_for('listar'))
    else:
        return render_template('listar_tratamentos.html', tratamentos=listar_tratamentos(), erro_remover=True)

@app.route('/relatorio_cadastros')
def relatorio_cadastros():
    relatorio = gerar_relatorio_cadastros_data()
    return render_template('relatorio_cadastros.html', relatorio=relatorio)

@app.route('/relatorio_medicamentos')
def relatorio_medicamentos():
    relatorio = gerar_relatorio_frequencia_medicamentos_data()
    return render_template('relatorio_medicamentos.html', relatorio=relatorio)

@app.route('/dashboard')
def dashboard():
    try:
        import matplotlib.pyplot as plt
        from io import BytesIO
        import base64
        from collections import Counter

        # Gráfico de Cadastros por Período
        agora = datetime.now()
        ultimas_24_horas = agora - timedelta(hours=24)
        ultima_semana = agora - timedelta(weeks=1)
        ultimo_mes = agora - timedelta(days=30)

        cadastros_periodo = {
            "Últimas 24h": sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimas_24_horas),
            "Última Semana": sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultima_semana),
            "Último Mês": sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimo_mes)
        }

        labels_cadastros = list(cadastros_periodo.keys())
        values_cadastros = list(cadastros_periodo.values())

        plt.figure(figsize=(8, 6))
        plt.bar(labels_cadastros, values_cadastros, color=['blue', 'green', 'orange'])
        plt.title("Novos Cadastros por Período")
        plt.ylabel("Número de Pacientes")
        plt.xlabel("Período")
        plt.tight_layout()

        buffer_cadastros = BytesIO()
        plt.savefig(buffer_cadastros, format='png')
        buffer_cadastros.seek(0)
        image_cadastros_base64 = base64.b64encode(buffer_cadastros.read()).decode('utf-8')
        plt.close()

        # Gráfico de Frequência de Medicamentos
        medicamentos = [tratamento['medicamento'] for tratamento in tratamentos_cadastrados]
        frequencia_medicamentos = Counter(medicamentos)
        mais_comuns = frequencia_medicamentos.most_common(5)

        if mais_comuns:
            medicamentos_labels = [item[0] for item in mais_comuns]
            frequencia_valores = [item[1] for item in mais_comuns]

            plt.figure(figsize=(8, 6))
            plt.bar(medicamentos_labels, frequencia_valores, color='skyblue')
            plt.title("Frequência dos Medicamentos Mais Utilizados")
            plt.xlabel("Medicamento")
            plt.ylabel("Número de Vezes Utilizado")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            buffer_medicamentos = BytesIO()
            plt.savefig(buffer_medicamentos, format='png')
            buffer_medicamentos.seek(0)
            image_medicamentos_base64 = base64.b64encode(buffer_medicamentos.read()).decode('utf-8')
            plt.close()
        else:
            image_medicamentos_base64 = None

        return render_template('dashboard.html', grafico_cadastros=image_cadastros_base64, grafico_medicamentos=image_medicamentos_base64)

    except ImportError:
        return render_template('dashboard_erro.html')

if __name__ == '__main__':
    # Carrega os tratamentos ao iniciar a aplicação web
    tratamentos_cadastrados = obter_dados_cadastros() or []
    app.run(debug=True)