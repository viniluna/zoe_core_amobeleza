import streamlit as st
from data_loader import carregar_perfumes
from user_interaction import processar_resposta_com_intencao  # Importa apenas as funções de interação
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import glob
#teste
# Definição de mensagens
@dataclass
class Mensagem:
    ator: str
    conteudo: str

USUARIO = "usuario"
ASSISTENTE = "Zoe"
MENSAGENS = "mensagens"

# Função para obter o modelo LLM (GPT-3.5)
def obter_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model_name='gpt-3.5-turbo',
        openai_api_key=st.secrets.openai_api_key  # Substitua pela sua chave de API
    )

# Função para criar o LLMChain com memória de conversação
def obter_llm_chain():
    template = """
    Você é Zoe, uma assistente virtual especializada em perfumes de todas as marcas disponíveis na AmoBeleza, uma loja que vende cosméticos, e não uma marca de perfume.
    Seu objetivo é fornecer informações precisas e claras sobre perfumes, ajudando os clientes com dúvidas, reclamações ou solicitações.
    Você tem profundo conhecimento sobre as características, fragrâncias, descrições, marcas e links de compra dos perfumes oferecidos pela AmoBeleza.
    Lembre-se de manter uma linguagem amigável e objetiva.

    Histórico da conversa até agora:
    {historico_conversa}

    Pergunta atual do usuário:
    {pergunta}

    Com base no histórico e na pergunta, forneça uma resposta clara e útil:
    """
    prompt_template = PromptTemplate.from_template(template)
    memoria = ConversationBufferMemory(memory_key="historico_conversa")

    chain = LLMChain(
        llm=obter_llm(),
        prompt=prompt_template,
        verbose=True,
        memory=memoria
    )
    return chain

# Função para carregar histórico de conversas dos últimos 7 dias
def carregar_historico_conversas():
    caminho_base = "./mensagens_amobeleza"
    data_atual = datetime.now()
    historico_conversas = ""

    for i in range(7):
        data_pasta = (data_atual - timedelta(days=i)).strftime("%Y%m%d")
        caminho_pasta = os.path.join(caminho_base, data_pasta)

        if os.path.exists(caminho_pasta):
            arquivos_conversa = glob.glob(os.path.join(caminho_pasta, "*.txt"))
            for arquivo in arquivos_conversa:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    historico_conversas += f.read() + "\n"

    return historico_conversas.strip()  # Remove espaços extras

# Função para salvar as mensagens trocadas em um arquivo de texto
def salvar_mensagens():
    caminho_base = "./mensagens_amobeleza"
    pasta_data = datetime.now().strftime("%Y%m%d")
    caminho_pasta = os.path.join(caminho_base, pasta_data)
    
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)
    
    nome_arquivo = f"zoe_mensagens_{st.session_state['data_inicio_conversa']}.txt"
    caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        for msg in st.session_state[MENSAGENS]:
            f.write(f"{msg.ator}: {msg.conteudo}\n")

# Função para salvar a contagem de mensagens em um arquivo
def salvar_contagem_mensagens():
    caminho_base = "./contagem_mensagem_amobeleza"
    pasta_data = datetime.now().strftime("%Y%m%d")
    caminho_pasta = os.path.join(caminho_base, pasta_data)
    
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)
    
    nome_arquivo = f"zoe_qtd_mensagem_{st.session_state['data_inicio_conversa']}.txt"
    caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
    
    with open(caminho_arquivo, 'w') as f:
        f.write(f"Total de mensagens trocadas: {st.session_state['contagem_mensagens']}\n")

# Função para armazenar as últimas mensagens no histórico recente (até 4 mensagens)
def armazenar_mensagem_no_historico_recente(mensagem):
    if "historico_recente" not in st.session_state:
        st.session_state["historico_recente"] = []  # Inicializa uma lista vazia se não existir

    # Adiciona a nova mensagem
    st.session_state["historico_recente"].append(mensagem)

    # Limita o tamanho da lista a 4 mensagens
    if len(st.session_state["historico_recente"]) > 4:
        st.session_state["historico_recente"].pop(0)  # Remove a mensagem mais antiga

# Função para recuperar as últimas 4 mensagens do histórico recente
def obter_historico_recente():
    return st.session_state.get("historico_recente", [])  # Retorna uma lista vazia se não existir histórico

# Função para armazenar a mensagem no histórico completo
def armazenar_mensagem_no_historico_completo(mensagem):
    if "historico_completo" not in st.session_state:
        st.session_state["historico_completo"] = ""  # Inicializa uma string vazia se não existir

    # Adiciona a nova mensagem
    st.session_state["historico_completo"] += mensagem + "\n"

# Função para obter o histórico completo
def obter_historico_completo():
    return st.session_state.get("historico_completo", "")  # Retorna uma string vazia se não existir histórico


# Função para inicializar a contagem de mensagens e criar o arquivo no início da conversa
def iniciar_conversa():
    if "data_inicio_conversa" not in st.session_state:
        data_hora_inicio = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state["data_inicio_conversa"] = data_hora_inicio
        st.session_state["contagem_mensagens"] = 0
        salvar_contagem_mensagens()
        salvar_mensagens()  # Salva o estado inicial das mensagens

# Função para inicializar o estado da sessão
def inicializar_estado_sessao():
    # Definir a saudação de acordo com a hora do dia
    current_hour = datetime.now().hour
    
    if current_hour < 12:
        saudacao = "Bom dia"
    elif 12 <= current_hour < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    # Inicializar mensagens na sessão, se ainda não estiverem
    if MENSAGENS not in st.session_state:
        st.session_state[MENSAGENS] = [
            Mensagem(
                ator=ASSISTENTE,
                conteudo=f"{saudacao}, sou a Zoe, especialista em perfumes na AmoBeleza. Em que posso ajudá-lo?"
            )
        ]
    
    # Carregar o histórico de conversas dos últimos 7 dias
    caminho_base = "./mensagens_amobeleza"
    if "llm_chain" not in st.session_state:
        try:
            historico_conversas = carregar_historico_conversas()
        except Exception as e:
            st.error(f"Erro ao carregar histórico de conversas: {e}")
            historico_conversas = None

        # Inicializar 'historico_conversa' como uma string vazia, caso não haja histórico
        st.session_state["historico_conversa"] = historico_conversas if historico_conversas else ""
        
        # Inicializar o LLMChain
        st.session_state["llm_chain"] = obter_llm_chain()

    # Definir o caminho para o arquivo de perfumes
    caminho_arquivo_perfumes = "./produtos/perfumes.csv"  # Substitua pelo caminho correto
    if "perfumes" not in st.session_state:
        try:
            st.session_state["perfumes"] = carregar_perfumes(caminho_arquivo_perfumes)
        except FileNotFoundError:
            st.error(f"Arquivo de perfumes não encontrado no caminho: {caminho_arquivo_perfumes}")
            st.session_state["perfumes"] = {}  # Inicializa como dicionário vazio em caso de falha
        except Exception as e:
            st.error(f"Erro ao carregar perfumes: {e}")
            st.session_state["perfumes"] = {}  # Inicializa como dicionário vazio em caso de falha

    iniciar_conversa()  # Inicializar o arquivo e contagem de mensagens

# Inicializando a sessão
inicializar_estado_sessao()

# Exibir as mensagens na tela
for msg in st.session_state[MENSAGENS]:
    st.chat_message(msg.ator).write(msg.conteudo)

# Entrada do usuário
prompt = st.chat_input("Digite sua pergunta aqui")

# Processamento do prompt do usuário
if prompt:
    st.session_state["contagem_mensagens"] += 1  # Atualiza contagem de mensagens
    st.session_state[MENSAGENS].append(Mensagem(ator=USUARIO, conteudo=prompt))
    st.chat_message(USUARIO).write(prompt)

    # Armazenar a consulta no histórico recente e completo
    armazenar_mensagem_no_historico_recente(f"Usuário: {prompt}")
    armazenar_mensagem_no_historico_completo(f"Usuário: {prompt}")

    with st.spinner("Por favor, aguarde..."):
        llm_chain = st.session_state["llm_chain"]
        
        # Obter o histórico recente
        historico_recente = "\n".join(obter_historico_recente())
        
        resposta, novo_historico = processar_resposta_com_intencao(
            prompt, 
            st.session_state["perfumes"], 
            llm_chain, 
            historico_recente  # Passamos o histórico recente para o processamento
        )

        # Armazenar a resposta no histórico recente e completo
        armazenar_mensagem_no_historico_recente(f"Zoe: {resposta}")
        armazenar_mensagem_no_historico_completo(f"Zoe: {resposta}")

        # Adicionar a resposta da Zoe
        st.session_state[MENSAGENS].append(Mensagem(ator=ASSISTENTE, conteudo=resposta))
        st.chat_message(ASSISTENTE).write(resposta)

        # Atualiza o histórico de conversa completo com a nova resposta
        st.session_state["historico_conversa"] = novo_historico
        
        # Salva o estado atualizado das mensagens e contagem
        salvar_mensagens()  # Salva o estado atualizado das mensagens
        salvar_contagem_mensagens()  # Salva a contagem de mensagens trocadas
