# Sprint 3 | Hospital Infantil Sabará | Code Nexus
# Sistema de Cadastro de tratamentos

# Importes de bibliotecas
import json

# Lista para armazenar os tratamentos cadastrados
tratamentos_cadastrados = []


# Função para cadastrar um novo tratamento
def cadastrar_tratamento():
    nome = str(input("Digite o nome do paciente: "))
    idade = int(input("Digite a idade do paciente: "))
    medicamento = input("Digite o medicamento: ")

    novo_tratamento = {
        'nome': nome,
        'idade': idade,
        'medicamento': medicamento
    }

    tratamentos_cadastrados.append(novo_tratamento)
    print("Tratamento cadastrado com sucesso!")


# Função para remover um tratamento
def remover_tratamento():
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
            print(f'Tratamento de {tratamento_removido["nome"]} removido com sucesso.')
        else:
            print('Número do tratamento inexistente ou inválido.')
    except ValueError:
        print('Por favor, digite um número válido.')


# Função para listar todos os tratamentos
def listar_tratamentos():
    if tratamentos_cadastrados:
        print('\n--- Tratamentos Cadastrados ---')
        for i, tratamento in enumerate(tratamentos_cadastrados, start=1):
            print(f'{i}. Nome: {tratamento["nome"]}, Idade: {tratamento["idade"]}, Medicamento: {tratamento["medicamento"]}')
    else:
        print('Nenhum tratamento cadastrado.')


# Menu principal
def menu():
    while True:
        print("\n--- Menu ---")
        print("1. Cadastrar tratamento")
        print("2. Remover tratamento")
        print("3. Editar tratamento (em construção)")
        print("4. Ver tratamentos")
        print("5. Sair")

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


