import json
from datetime import datetime, timedelta
from collections import Counter
import os

# Estilização para o terminal
import rich

from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

console = Console()

# Nome dos arquivos JSON locais
CADASTROS_FILE = "Data/cadastros.json"
LOGIN_FILE = "Data/login.json"

# Lista para armazenar os tratamentos cadastrados (agora populada via arquivo JSON)
tratamentos_cadastrados = []


# Função para ler dados de um arquivo JSON local
def ler_dados_json(cadastros):
    try:
        with open(cadastros, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Erro:[/bold red] Arquivo '{cadastros}' não encontrado.")
        return None
    except json.JSONDecodeError:
        console.print(f"[bold red]Erro:[/bold red] Falha ao decodificar JSON do arquivo '{cadastros}'.")
        return None

# Função para escrever dados em um arquivo JSON local
def escrever_dados_json(cadastros, dados):
    try:
        with open(cadastros, 'w') as f:
            json.dump(dados, f, indent=4)
        return True
    except IOError:
        console.print(f"[bold red]Erro:[/bold red] Falha ao escrever no arquivo '{cadastros}'.")
        return False

# Função para obter os dados de tratamento do arquivo cadastros.json
def obter_dados_cadastros():
    cadastros_data = ler_dados_json(CADASTROS_FILE)
    if cadastros_data and isinstance(cadastros_data, list):
        return cadastros_data
    return []

# Função para cadastrar um novo tratamento (adiciona ao arquivo cadastros.json)
def cadastrar_tratamento():
    console.print("[bold green]\n--- Cadastrar Novo Tratamento ---[/bold green]")
    nome = Prompt.ask("[cyan]Digite o nome do paciente[/cyan]")
    idade = Prompt.ask("[cyan]Digite a idade do paciente[/cyan]")
    medicamento = Prompt.ask("[cyan]Digite o medicamento[/cyan]")

    novo_tratamento = {
        'nome': nome,
        'idade': idade,
        'medicamento': medicamento,
        'data_cadastro': datetime.now().isoformat()
    }

    tratamentos = obter_dados_cadastros()
    tratamentos.append(novo_tratamento)
    if escrever_dados_json(CADASTROS_FILE, tratamentos):
        console.print("[bold green]Tratamento cadastrado com sucesso![/bold green]")
        global tratamentos_cadastrados
        tratamentos_cadastrados = tratamentos # Atualiza a lista em memória
    else:
        console.print("[bold red]Erro ao salvar o tratamento.[/bold red]")

# Função para remover um tratamento (atualiza o arquivo cadastros.json)
def remover_tratamento():
    global tratamentos_cadastrados
    if not tratamentos_cadastrados:
        console.print("[yellow]Nenhum tratamento cadastrado.[/yellow]")
        return

    console.print(Panel("[bold blue]--- Tratamentos Cadastrados ---[/bold blue]", expand=False))
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Nome", style="cyan")
    table.add_column("Idade", style="green")
    table.add_column("Medicamento", style="yellow")

    for i, tratamento in enumerate(tratamentos_cadastrados, start=1):
        table.add_row(str(i), tratamento["nome"], str(tratamento["idade"]), tratamento["medicamento"])
    console.print(table)

    try:
        indice_str = Prompt.ask("[red]Digite o número do tratamento que deseja remover[/red]")
        indice = int(indice_str)
        if 1 <= indice <= len(tratamentos_cadastrados):
            tratamento_removido = tratamentos_cadastrados.pop(indice - 1)
            if escrever_dados_json(CADASTROS_FILE, tratamentos_cadastrados):
                console.print(f"[bold green]Tratamento de {tratamento_removido['nome']} removido com sucesso.[/bold green]")
            else:
                console.print("[bold red]Erro ao atualizar o arquivo de cadastros.[/bold red]")
        else:
            console.print("[bold red]Número do tratamento inexistente ou inválido.[/bold red]")
    except ValueError:
        console.print("[bold red]Por favor, digite um número válido.[/bold red]")

# Função para listar todos os tratamentos (da lista em memória)
def listar_tratamentos():
    if tratamentos_cadastrados:
        console.print(Panel("[bold blue]--- Tratamentos Cadastrados ---[/bold blue]", expand=False))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Nome", style="cyan")
        table.add_column("Idade", style="green")
        table.add_column("Medicamento", style="yellow")

        for i, tratamento in enumerate(tratamentos_cadastrados, start=1):
            table.add_row(str(i), tratamento["nome"], str(tratamento["idade"]), tratamento["medicamento"])
        console.print(table)
    else:
        console.print("[yellow]Nenhum tratamento cadastrado.[/yellow]")

# --- Funções para Geração de Relatórios e Dashboards ---

def gerar_relatorio_cadastros():
    agora = datetime.now()
    ultimas_24_horas = agora - timedelta(hours=24)
    ultima_semana = agora - timedelta(weeks=1)
    ultimo_mes = agora - timedelta(days=30) # Aproximação de um mês

    cadastrados_24h = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimas_24_horas)
    cadastrados_semana = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultima_semana)
    cadastrados_mes = sum(1 for t in tratamentos_cadastrados if datetime.fromisoformat(t.get('data_cadastro', '1970-01-01T00:00:00')) >= ultimo_mes)

    console.print(Panel("[bold green]--- Relatório de Cadastros ---[/bold green]", expand=False))
    console.print(f"[blue]Pacientes cadastrados nas últimas 24 horas:[/blue] [bold]{cadastrados_24h}[/bold]")
    console.print(f"[blue]Pacientes cadastrados na última semana:[/blue] [bold]{cadastrados_semana}[/bold]")
    console.print(f"[blue]Pacientes cadastrados no último mês:[/blue] [bold]{cadastrados_mes}[/bold]")

def gerar_relatorio_frequencia_medicamentos():
    medicamentos = [tratamento['medicamento'] for tratamento in tratamentos_cadastrados]
    frequencia = Counter(medicamentos)

    console.print(Panel("[bold green]--- Relatório de Frequência de Medicamentos ---[/bold green]", expand=False))
    if frequencia:
        mais_frequente = frequencia.most_common(1)[0]
        console.print(f"[blue]Medicamento mais frequente:[/blue] [bold]{mais_frequente[0]}[/bold] ([green]{mais_frequente[1]}[/green] vezes)")
        if len(frequencia) > 1:
            menos_frequentes = frequencia.most_common()[:-2:-1] # Pega o último elemento
            console.print(f"[blue]Medicamento menos frequente:[/blue] [bold]{menos_frequentes[0][0]}[/bold] ([green]{menos_frequentes[0][1]}[/green] vez)")
        elif len(frequencia) > 0:
            console.print("[yellow]Apenas um medicamento cadastrado.[/yellow]")
        else:
            console.print("[yellow]Nenhum medicamento cadastrado.[/yellow]")
    else:
        console.print("[yellow]Nenhum tratamento cadastrado para analisar a frequência de medicamentos.[/yellow]")

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
            console.print("[yellow]\nNenhum medicamento cadastrado para exibir no dashboard.[/yellow]")

    except ImportError:
        console.print("[bold red]A biblioteca 'matplotlib' não está instalada.[/bold red] Instale-a com '[italic]pip install matplotlib[/italic]' para exibir o dashboard.")

# Menu principal
def menu():
    while True:
        menu_table = Table(title="[bold magenta]\n--- Menu ---[/bold magenta]", show_lines=True)
        menu_table.add_column("[bold]Opção[/bold]", style="cyan", justify="right")
        menu_table.add_column("[bold]Ação[/bold]", style="green")
        menu_table.add_row("1", "Cadastrar tratamento")
        menu_table.add_row("2", "Remover tratamento")
        menu_table.add_row("3", "[dim]Editar tratamento (em construção)[/dim]")
        menu_table.add_row("4", "Ver tratamentos")
        menu_table.add_row("5", "Gerar relatório de cadastros")
        menu_table.add_row("6", "Gerar relatório de frequência de medicamentos")
        menu_table.add_row("7", "Exibir Dashboard")
        menu_table.add_row("8", "Sair")
        console.print(menu_table)

        opcao = Prompt.ask("[yellow]Escolha uma opção[/yellow]", choices=["1", "2", "3", "4", "5", "6", "7", "8"])

        if opcao == "1":
            cadastrar_tratamento()
        elif opcao == "2":
            remover_tratamento()
        elif opcao == "3":
            console.print("[italic yellow]Editar tratamento ainda em construção[/italic yellow]")
        elif opcao == "4":
            listar_tratamentos()
        elif opcao == "5":
            gerar_relatorio_cadastros()
        elif opcao == "6":
            gerar_relatorio_frequencia_medicamentos()
        elif opcao == "7":
            exibir_dashboard()
        elif opcao == "8":
            console.print("[bold red]Encerrando o sistema...[/bold red]")
            break
        else:
            console.print("[bold red]Opção inválida.[/bold red]")

# Função de Login para acessar o sistema
def realizar_login ():
    try:
        with open(LOGIN_FILE, 'r') as arquivo:
            usuario = json.load(arquivo)
    # Verifica se o arquivo json existe
    except FileNotFoundError:
        print("-----Arquivo de usuário não encontrado-----")
        return False

    console.print(Panel("[bold blue]--- Login ---[/bold blue]", expand=False))
    user = Prompt.ask("[cyan]Digite o seu usuário[/cyan]")
    password = Prompt.ask("[cyan]Digite a sua senha[/cyan]", password=True)

    for login_usario in usuario:
        if login_usario['usuario'] == user and login_usario['senha'] == password:
            console.print(f"[bold green]Bem vindo {login_usario['usuario']}![/bold green]")
            # global para carregar os cadastros que estão dentro da API
            global tratamentos_cadastrados
            tratamentos_cadastrados = ler_dados_json(CADASTROS_FILE) or [] # Carrega os dados aqui
            menu()
            return True

    print("\nUsuário ou senha incorretos, tentar novamente?")
    print("\n----Menu----\n1.Tentar novamente\n2.Sair\n---------")
    opcao_login_str = Prompt.ask("[yellow]Digite a opção[/yellow]", choices=["1", "2"])
    opcao_login = int(opcao_login_str)
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