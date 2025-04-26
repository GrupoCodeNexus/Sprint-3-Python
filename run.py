# Instalando dependencias e rodando o projeto

import subprocess
import sys

def check_dependencies(dependencies):
    missing = []
    try:
        for dep in dependencies:
            __import__(dep)
    except ImportError as e:
        missing.append(e.name)
    return missing

def install_dependencies(dependencies):
    if dependencies:
        print("Instalando dependências...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)
            print("Dependências instaladas com sucesso!!!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar dependências: {e}")
            sys.exit(1)

def run_app():
    try:
        print("\nIniciando o projeto Flask...\n")
        process = subprocess.run([sys.executable, "app.py"], check=True)
        # Se o processo terminar
        print("O projeto Flask foi encerrado...")
    except FileNotFoundError:
        print("Erro: Arquivo 'app.py' não encontrado na raiz do projeto.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o projeto Flask: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nEncerrando o projeto (CTRL + C)...")
        sys.exit(0)

if __name__ == "__main__":
    dependencies = ["matplotlib", "flask"]
    missing_dependencies = check_dependencies(dependencies)

    if missing_dependencies:
        print("As seguintes dependências não foram encontradas:")
        for dep in missing_dependencies:
            print(f"- {dep}")
        install_prompt = input("Deseja tentar instalar as dependências agora? (s/n): ").lower()
        if install_prompt == 's':
            install_dependencies(dependencies)
        else:
            print("Por favor, instale as dependências manualmente para rodar o projeto.")
            print("Utilize:  pip install matplotlib Flask")
            sys.exit(1)
    else:
        print("\nTodas as dependências estão instaladas.")

    run_app()