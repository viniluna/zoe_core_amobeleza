import csv
import os
from datetime import datetime, timedelta
import glob

# Função para carregar perfumes a partir de um arquivo CSV
def carregar_perfumes(caminho_arquivo: str):
    perfumes = {}
    
    # Tentar diferentes codificações
    encodings = ['utf-8', 'ISO-8859-1', 'latin-1']

    for encoding in encodings:
        try:
            with open(caminho_arquivo, mode='r', encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    nome = row['nome']
                    marca = row['marca']
                    fragrancia = row['fragrancia']
                    descricao = row['descricao']
                    link = row['link']
                    perfumes[nome.lower()] = {
                        'nome': nome,
                        'marca': marca,
                        'fragrancia': fragrancia,
                        'descricao': descricao,
                        'link': link
                    }
            print(f"Arquivo lido com sucesso usando a codificação: {encoding}")
            break  # Se o arquivo foi lido corretamente, sair do loop
        except UnicodeDecodeError:
            print(f"Erro ao ler o arquivo com a codificação: {encoding}, tentando próxima...")
        except Exception as e:
            print(f"Outro erro ocorreu: {e}")
    
    if not perfumes:
        raise Exception("Nenhuma codificação conseguiu ler o arquivo.")
    
    return perfumes

# Função para carregar histórico de conversas (opcional, dependendo de como a aplicação lida com histórico)
def carregar_historico_conversas(caminho_base: str):
    try:
        with open(caminho_base, mode='r', encoding='utf-8') as file:
            historico = file.read()
            print("Histórico de conversas carregado com sucesso.")
            return historico
    except FileNotFoundError:
        print(f"Histórico de conversas não encontrado no caminho: {caminho_base}. Criando um novo.")
        return ""
    except Exception as e:
        print(f"Erro ao carregar histórico de conversas: {e}")
        return ""
