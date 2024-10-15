# Importando bibliotecas
import os
import datetime
import oracledb
import pandas as pd
import sys
import json

# Subalgoritmos

def adicionar_solo():
    try:
        print("-------Registrar Solo-------")
        # Recebendo os inputs
        ph = float(input("Digite o PH do solo: "))
        nitrogenio = float(input("Digite a concentração de Nitrogênio: "))
        potassio = float(input("Digite a concentração de Potássio: "))
        fosforo = float(input("Digite a concentração de Fósforo: "))
        data_registro = input("Digite a data de registro (dd/mm/yyyy): ")
        # Convertendo data
        data = datetime.datetime.strptime(data_registro, "%d/%m/%Y").date()
        data_str = data.strftime("%Y-%m-%d")
        # Instrução banco de dados
        cadastro = "INSERT INTO tb_solo (ph, nitrogenio, potassio, fosforo, data_registro) VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'))"
        var_cadastro.execute(cadastro, [ph, nitrogenio, potassio, fosforo, data_str])
        conn.commit()
    except ValueError:
        print("Digite um número válido!")
    except:
        print("Algo deu errado...")
    else:
        print("DADOS ARMAZENADOS")
        # Adiciona ao arquivo json os valores
        adicionar_dados_json(ph, nitrogenio, potassio, fosforo, data_str)
        #Regista a ação feita pelo usuário
        arq = open("arquivos.txt", "a+")
        arq.write("Registro efetuado\n")
        arq.close()

def listar_solos():
    print("-------Listar Solo-------")
    lista_dados = []

    try:
        # Consulta banco de dados
        consulta = "SELECT id, ph, nitrogenio, potassio, fosforo, data_registro FROM tb_solo"
        var_consulta.execute(consulta)
        # recuperando todas as linhas da consulta
        data = var_consulta.fetchall()
        # Adicionando os dado na lista
        for dt in data:
            lista_dados.append(dt)

        # Ordenando a lista
        lista_dados.sort()
        # Data Frame para visualização dos dados
        data_frame_dados = pd.DataFrame.from_records(lista_dados, columns=['id', 'ph', 'nitrogenio', 'potassio', 'fosforo', 'data_registro'], index= 'id')

        if data_frame_dados.empty:
            print(f"Não hà solos registrados!")
        else:
            print(data_frame_dados)
            # Regista a ação feita pelo usuário
            arq = open("arquivos.txt", "a+")
            arq.write("Consulta efetuada\n")
            arq.close()
    except Exception as e:
        print("Algo deu errado!", e)
    print()

def atualizar_solo():
    try:
        print("-------Atualizar Solo-------")

        lista_dados = []
        solo_id = int(input("Escolha um ID: "))

        consulta = f"""select * from tb_solo where id = {solo_id}"""
        var_consulta.execute(consulta)
        data = var_consulta.fetchall()

        for dt in data:
            lista_dados.append(dt)

        if len(lista_dados) == 0:
            print(f"Não existe solo com o ID = {solo_id}")
        else:
            novo_ph = float(input("Digite um novo valor para o PH: "))
            novo_nitrogenio = float(input("Digite um novo valor para o nitrogenio: "))
            novo_potassio = float(input("Digite um novo valor para o potassio: "))
            novo_fosforo = float(input("Digite um novo valor para o fosforo: "))
            data_atual = input("Digite a data de registro (dd/mm/yyyy): ")

            data = datetime.datetime.strptime(data_atual, "%d/%m/%Y").strftime('%d/%m/%Y')

            atualizar = f"""
                   UPDATE tb_solo
                   SET ph = {novo_ph}, nitrogenio = {novo_nitrogenio}, potassio = {novo_potassio}, fosforo = {novo_fosforo}, data_registro = TO_DATE('{data}', 'DD/MM/YYYY')
                   WHERE id = {solo_id}
                   """

            var_atualizacao.execute(atualizar)
            conn.commit()
            print("Dados atualizados!")
            adicionar_dados_json(novo_ph,novo_nitrogenio, novo_potassio, novo_fosforo, data)
            # Regista a ação feita pelo usuário
            arq = open("arquivos.txt", "a+")
            arq.write("Update efetuado\n")
            arq.close()
    except Exception as e:
        print("Algo deu errado!")

def deletar_solo():
    print("-------Deletar Solo-------")

    lista_dados = []
    solo_id = input("Escolha um ID: ")

    if solo_id.isdigit():
        solo_id = int(solo_id)
        consulta = f"""select * from tb_solo"""
        var_consulta.execute(consulta)
        dado = var_consulta.fetchall()

        for dt in dado:
            lista_dados.append(dt)
        if len(lista_dados) == 0:
            print(f"Não há um solo com o ID = {solo_id}")
        else:
            deletar = f"""delete from tb_solo where id = {solo_id}"""
            var_delecao.execute(deletar)
            conn.commit()
            print("Solo Deletado!")
            #Regista a ação feita pelo usuário
            arq = open("arquivos.txt", "a+")
            arq.write("Delete efetuado\n")
            arq.close()

def excluir_todos():
    try:
        print("-------Excluir todos os Solos-------")
        confirmar = input("Deseja excluir todos os solos? [S]im ou [N]ão: ")
        if confirmar.upper() == 'S':
            exclusao = f"""delete from tb_solo"""
            var_delecao.execute(exclusao)
            conn.commit()

            print("Todos os solos foram excluidos!")
            # Regista a ação feita pelo usuário
            arq = open("arquivos.txt", "a+")
            arq.write("Excluiu todos os dados\n")
            arq.close()
        else:
            print("Exclusão cancelada")
    except Exception as e:
        print("Algo deu errado!", e)

def analisar_solo():
    # A análise do solo pega valores referentes ao solo ideal para plantações de SOJA e MILHO
    print("-------Analisar Solo-------")
    try:
        solo_id = int(input("Digite o ID do solo que deseja analisar: "))
        consulta = f"SELECT ph, nitrogenio, potassio, fosforo FROM tb_solo WHERE id = {solo_id}"
        var_consulta.execute(consulta)
        dados_solos = var_consulta.fetchall()

        if dados_solos:
            for dados_solo in dados_solos:
                ph, nitrogenio, potassio, fosforo = dados_solo
                # Intervalos ideais para o cultivo de plantas
                pH_ideal = (6.0, 7.5)
                nitrogenio_ideal = (20, 50)  # em mg/kg
                fosforo_ideal = (15, 40)     # em mg/kg
                potassio_ideal = (120, 200)  # em mg/kg

                # Verificação de cada parâmetro
                print(f"\nAnalisando solo com ID {solo_id}:")
                if not (pH_ideal[0] <= ph <= pH_ideal[1]):
                    print(f"PH fora do ideal!\n Valor atual: {ph}, intervalo ideal: {pH_ideal}")
                else:
                    print(f"PH adequado: {ph}")

                if not (nitrogenio_ideal[0] <= nitrogenio <= nitrogenio_ideal[1]):
                    print(f"Teor de nitrogênio fora do ideal!\n Valor atual: {nitrogenio} mg/kg, intervalo ideal: {nitrogenio_ideal} mg/kg")
                else:
                    print(f"Teor de nitrogênio adequado: {nitrogenio} mg/kg")

                if not (fosforo_ideal[0] <= fosforo <= fosforo_ideal[1]):
                    print(f"Teor de fósforo fora do ideal!\n Valor atual: {fosforo} mg/kg, intervalo ideal: {fosforo_ideal} mg/kg")
                else:
                    print(f"Teor de fósforo adequado: {fosforo} mg/kg")

                if not (potassio_ideal[0] <= potassio <= potassio_ideal[1]):
                    print(f"Teor de potássio fora do ideal!\n Valor atual: {potassio} mg/kg, intervalo ideal: {potassio_ideal} mg/kg")
                else:
                    print(f"Teor de potássio adequado: {potassio} mg/kg")
            # Regista a ação feita pelo usuário
            arq = open("arquivos.txt", "a+")
            arq.write("Analise efetuada\n")
            arq.close()
        else:
            print(f"Nenhum solo encontrado com o ID {solo_id}.")
    except ValueError:
        print("Por favor, digite um número válido.")
    except Exception as e:
        print("Ocorreu um erro: ", e)

def sair():
    try:
        confirmar = input("Deseja mesmo sair? [S]im ou [N]ão: ")
        if confirmar.upper() == 'S':
            print("Programa encerrado")
            # Regista a ação feita pelo usuário
            arq = open("arquivos.txt", "a+")
            arq.write("Saiu do programa\n")
            arq.close()
            sys.exit()  # Encerra a execução do programa
        elif confirmar.upper() == 'N':
            print("Continuando o programa...")
        else:
            print("Opção inválida. Tente novamente.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def adicionar_dados_json(ph, nitrogenio, potassio, fosforo, data_str):
    # Cria um dicionário com os novos dados
    dicionario = {
        "ph": str(ph),
        "nitrogenio": str(nitrogenio),
        "potassio": str(potassio),
        "fosforo": str(fosforo),
        "data": str(data_str)
    }

    # Caminho para o arquivo JSON
    filename = "agro.json"

    try:
        # Tenta abrir o arquivo existente para leitura
        with open(filename, 'r') as file:
            # Carrega os dados existentes
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se não existir ou houver erro na leitura, inicia uma nova lista
        data = []

    # Adiciona o novo dicionário à lista de dados
    data.append(dicionario)

    # Abre o arquivo para escrita e atualiza com a nova lista de dados
    with open(filename, 'w') as file:
        json.dump(data, file, indent=6)



# Conectando Banco de dados
try:
    conn = oracledb.connect(user='rm559290', password="161000", dsn='oracle.fiap.com.br:1521/ORCL')
    #Criando instruções do CRUD
    var_cadastro = conn.cursor()
    var_consulta = conn.cursor()
    var_atualizacao = conn.cursor()
    var_delecao = conn.cursor()

except Exception as e:
    print("Erro: ", e)
    conexao = False
else:
    conexao = True

margem = ' ' * 4

# Criando o laço

while conexao:
    os.system('cls')

    # Menu
    print("-------------MENU-------------")
    print(""""
    1 - Registrar solo
    2 - Listar solo(s)
    3 - Atualizar solo
    4 - Deletar solo
    5 - Excluir todos os solos
    6 - Análise do solo
    7 - Sair
    """)
    # input
    escolha = input(margem + "Escolha um número: ")

    if escolha.isdigit():
        escolha = int(escolha)
    else:
        print(margem + "Digite um número!")
        continue

    match escolha:
        case 1:
            adicionar_solo()
        case 2:
            listar_solos()
        case 3:
            atualizar_solo()
        case 4:
            deletar_solo()
        case 5:
            excluir_todos()
        case 6:
            analisar_solo()
        case 7:
            sair()