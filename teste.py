import json
from datetime import datetime, timedelta
from collections import Counter
import os

# Nome dos arquivos JSON locais
USUARIOS_FILE = "usuarios.json"
CADASTROS_FILE = "cadastros.json"

# Lista para armazenar os tratamentos cadastrados (agora populada via arquivo JSON)
tratamentos_cadastrados = []


# Função para ler dados de um arquivo JSON local
def ler_dados_json(cadastros):
    try:
        with open(cadastros, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{cadastros}' não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar JSON do arquivo '{cadastros}'.")
        return None

# Função para escrever dados em um arquivo JSON local
def escrever_dados_json(cadastros, dados):
    try:
        with open(cadastros, 'w') as f:
            json.dump(dados, f, indent=4)
        return True
    except IOError:
        print(f"Erro: Falha ao escrever no arquivo '{cadastros}'.")
        return False

# Função para obter os dados de tratamento do arquivo cadastros.json
def obter_dados_cadastros():
    cadastros_data = ler_dados_json(CADASTROS_FILE)
    if cadastros_data and isinstance(cadastros_data, list):
        return cadastros_data
    return []

# Função para cadastrar um novo tratamento (adiciona ao arquivo cadastros.json)
def cadastrar_tratamento():
    nome = str(input("Digite o nome do paciente: "))
    idade = int(input("Digite a idade do paciente: "))
    medicamento = input("Digite o medicamento: ")

    novo_tratamento = {
        'nome': nome,
        'idade': idade,
        'medicamento': medicamento,
        'data_cadastro': datetime.now().isoformat()
    }

    tratamentos = obter_dados_cadastros()
    tratamentos.append(novo_tratamento)
    if escrever_dados_json(CADASTROS_FILE, tratamentos):
        print("Tratamento cadastrado com sucesso!")
        global tratamentos_cadastrados
        tratamentos_cadastrados = tratamentos # Atualiza a lista em memória
    else:
        print("Erro ao salvar o tratamento.")

# Função para remover um tratamento (atualiza o arquivo cadastros.json)
def remover_tratamento():
    global tratamentos_cadastrados
    if not tratamentos_cadastrados:
        print('Nenhum tratamento cadastrado.')
        return

    print('\n--- Tratamentos Cadastrados ---')
    for i, tratamento in enumerate(tratamentos_cadastrados, start=1):
        print(f'{i}. Nome: {tratamento["nome"]}, Idade: {tratamento["idade"]}, Medicamento: {tratamento["medicamento"]}')

    try:
        indice = int(input('Digite o número do tratamento que deseja remover: '))
        if 1 <= indice <= len(tratamentos_cadastrados):
            tratamento_removido = tratamentos_cadastrados.pop(indice - 1)
            if escrever_dados_json(CADASTROS_FILE, tratamentos_cadastrados):
                print(f'Tratamento de {tratamento_removido["nome"]} removido com sucesso.')
            else:
                print("Erro ao atualizar o arquivo de cadastros.")
        else:
            print('Número do tratamento inexistente ou inválido.')
    except ValueError:
        print('Por favor, digite um número válido.')

# Função para listar todos os tratamentos (da lista em memória)
def listar_tratamentos():
    if tratamentos_cadastrados:
        print('\n--- Tratamentos Cadastrados ---')
        for i, tratamento in enumerate(tratamentos_cadastrados, start=1):
            print(f'{i}. Nome: {tratamento["nome"]}, Idade: {tratamento["idade"]}, Medicamento: {tratamento["medicamento"]}')
    else:
        print('Nenhum tratamento cadastrado.')

# --- Funções para Geração de Relatórios e Dashboards ---

def gerar_relatorio_cadastros():
    agora = datetime.now()
    ultimas_24_horas = agora - timedelta(hours=24)
    ultima_semana = agora - timedelta(weeks=1)
    ultimo_mes = agora - timedelta(days=30) # Aproximação de um mês

    cadastrados_24h = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimas_24_horas)
    cadastrados_semana = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultima_semana)
    cadastrados_mes = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimo_mes)

    print("\n--- Relatório de Cadastros ---")
    print(f"Pacientes cadastrados nas últimas 24 horas: {cadastrados_24h}")
    print(f"Pacientes cadastrados na última semana: {cadastrados_semana}")
    print(f"Pacientes cadastrados no último mês: {cadastrados_mes}")

def gerar_relatorio_frequencia_medicamentos():
    medicamentos = [tratamento['medicamento'] for tratamento in tratamentos_cadastrados]
    frequencia = Counter(medicamentos)

    if frequencia:
        mais_frequente = frequencia.most_common(1)[0]
        menos_frequentes = frequencia.most_common()[:-2:-1] # Pega o último elemento

        print("\n--- Relatório de Frequência de Medicamentos ---")
        print(f"Medicamento mais frequente: {mais_frequente[0]} ({mais_frequente[1]} vezes)")
        if menos_frequentes:
            print(f"Medicamento menos frequente: {menos_frequentes[0][0]} ({menos_frequentes[0][1]} vez)")
        elif len(frequencia) > 0:
            print("Apenas um medicamento cadastrado.")
        else:
            print("Nenhum medicamento cadastrado.")
    else:
        print("Nenhum tratamento cadastrado para analisar a frequência de medicamentos.")

def exibir_dashboard():
    try:
        import matplotlib.pyplot as plt
        from collections import Counter

        # Dados para o gráfico de cadastros por período
        agora = datetime.now()
        ultimas_24_horas = agora - timedelta(hours=24)
        ultima_semana = agora - timedelta(weeks=1)
        ultimo_mes = agora - timedelta(days=30)

        cadastros_periodo = {
            "Últimas 24h": sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimas_24_horas),
            "Última Semana": sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultima_semana),
            "Último Mês": sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimo_mes)
        }

        labels = list(cadastros_periodo.keys())
        values = list(cadastros_periodo.values())

        plt.figure(figsize=(8, 6))
        plt.bar(labels, values, color=['blue', 'green', 'orange'])
        plt.title("Novos Cadastros por Período")
        plt.ylabel("Número de Pacientes")
        plt.xlabel("Período")
        plt.tight_layout()
        plt.show()

        # Dados para o gráfico de frequência de medicamentos
        medicamentos = [tratamento['medicamento'] for tratamento in tratamentos_cadastrados]
        frequencia_medicamentos = Counter(medicamentos)
        mais_comuns = frequencia_medicamentos.most_common(5) # Top 5 medicamentos

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
            plt.show()
        else:
            print("\nNenhum medicamento cadastrado para exibir no dashboard.")

    except ImportError:
        print("A biblioteca 'matplotlib' não está instalada. Instale-a com 'pip install matplotlib' para exibir o dashboard.")

# Menu principal
def menu():
    while True:
        print("\n--- Menu ---")
        print("1. Cadastrar tratamento")
        print("2. Remover tratamento")
        print("3. Editar tratamento (em construção)")
        print("4. Ver tratamentos")
        print("5. Gerar relatório de cadastros")
        print("6. Gerar relatório de frequência de medicamentos")
        print("7. Exibir Dashboard")
        print("8. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_tratamento()
        elif opcao == "2":
            remover_tratamento()
        elif opcao == "3":
            print('Editar tratamento ainda em construção')
        elif opcao == "4":
            listar_tratamentos()
        elif opcao == "5":
            gerar_relatorio_cadastros()
        elif opcao == "6":
            gerar_relatorio_frequencia_medicamentos()
        elif opcao == "7":
            exibir_dashboard()
        elif opcao == "8":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida.")

# Função de Login para acessar o sistema
def realizar_login ():
    try:
        with open('login.json', 'r') as arquivo:
            usuario = json.load(arquivo)
    # Verifica se o arquivo json existe
    except FileNotFoundError:
        print("-----Arquivo de usuário não encontrado-----")
        return False

    user = str(input('Digite o seu usuário: '))
    password = input('Digite a sua senha: ')
    

    for login_usario in usuario:
        if login_usario['usuario'] == user and login_usario['senha'] ==password:
            print(f"Bem vindo {login_usario['usuario']}")
            # global para carregar os cadastros que estão dentro da API
            global tratamentos_cadastrados
            tratamentos_cadastrados = ler_dados_json(CADASTROS_FILE) or [] # Carrega os dados aqui
            menu()
            return True
    
    print("\nUsuário ou senha incorretos, tentar novamente?")
    print("\n----Menu----\n1.Tentar novamente\n2.Sair\n---------")
    opcao_login = int(input("Digite a opção 1 ou 2: "))
    match opcao_login:
        case 1:
            realizar_login()
        case 2:
            print("Fechando sistema...")
            return False
        case _:
            print(f"Opção invalida")
    return False

realizar_login()