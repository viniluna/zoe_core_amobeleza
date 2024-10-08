from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import difflib

#################################################################################################################################################################################

# Função para obter o modelo LLM (GPT-3.5)
def obter_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model_name='gpt-3.5-turbo',
        openai_api_key=st.secrets.openai_token  # Substitua pela sua chave de API
    )

#################################################################################################################################################################################

# Função para classificar a intenção usando GPT-3.5
def identificar_intencao_gpt(consulta: str) -> str:
    """
    Usa o GPT-3.5 para identificar a intenção do usuário.
    Nunca esqueça que você é a Zoe, especialista em perfumes e cosméticos da AmoBeleza, que é uma loja que vende vários produtos cosméticos, 
    e que a AmoBeleza não é uma marca de perfume.
    Intenções possíveis:
    - 'listar_marcas'
    - 'listar_perfumes'
    - 'listar_por_fragrancia'
    - 'listar_por_marca'
    - 'obter_link_compra'
    - 'recomendacao'
    - 'outras_perguntas'
    """
    
    prompt = f"""
    Abaixo está a mensagem de um usuário. Por favor, classifique a intenção desta mensagem como uma das seguintes opções:

    1. **'listar_marcas'**: Quando o usuário deseja saber apenas as marcas de perfumes disponíveis. Exemplos de perguntas:
        - "Quais marcas de perfume vocês têm?"
        - "Me fale todas as marcas de perfume que você vende."
        - "Quais marcas perfumes vc tem na Amobeleza ?"

    2. **'listar_perfumes'**: Quando o usuário deseja ver todos os perfumes disponíveis, sem especificar uma marca ou fragrância. Exemplos de perguntas:
        - "Quais perfumes vocês têm?"
        - "Me mostre todos os perfumes disponíveis."
        - "Quais perfumes vc tem na Amobeleza ?""

    3. **'listar_por_fragrancia'**: Quando o usuário deseja ver perfumes de uma fragrância específica. Exemplos de perguntas:
        - "Quais perfumes vocês têm com fragrância de baunilha?"
        - "Me mostre perfumes com aroma floral."
        - "Qual a frangrancia do Gabriela Sabatini Eau de Toilette ?"
        - "Perfumes com fragrancia baunilha ?"
        - "Perfume com fragrancia Amadeirado ?"


    4. **'listar_por_marca'**: Quando o usuário deseja ver perfumes de uma marca específica. Exemplos de perguntas:
        - "Quais perfumes da marca Giorgio Armani vocês têm?"
        - "Me mostre perfumes da Lancôme."

    5. **'obter_link_compra'**: Quando o usuário deseja obter o link de compra de um perfume específico. Exemplos de perguntas:
        - "Qual é o link para comprar o perfume Chanel No. 5?"
        - "Como posso comprar o perfume Dior J'adore?"
        - "Gostaria do link de compra do Yves Saint Laurent Libre"
        - "me mande o link de compra do perfume Giorgio Armani Sì Passione"
    
    6. **'recomendacao'**: Quando o usuário pede uma recomendação de perfumes para uma ocasião ou propósito específico.
        - "Qual perfume me recomendaria para um jantar ?"
        - "Vou sair para um parque, que perfume me recomenda ?"
        - "Gostaria de um perfume para o dia a dia"

    7. **'outras_perguntas'**: Quando a intenção do usuário não se enquadra nas opções anteriores. Exemplos de perguntas:
        - "Qual é o perfume mais vendido?"
        - "Você pode me sugerir um perfume para presente?"
        - "me conte sobre o perfume Gabriela Sabatini Eau de Toilette ?"
        - "Quero saber Shakira ?"

    Mensagem do usuário: '{consulta}'

    Lembre-se: você é a Zoe, especialista em perfumes e cosméticos da AmoBeleza, que é uma loja que vende produtos cosméticos, 
    mas não é uma marca de perfume.
    
    Qual é a intenção desta mensagem?
    """
    
    llm = obter_llm()
    resposta = llm.predict(prompt)

    # Interpreta a resposta para retornar a intenção correta
    llm = obter_llm()
    resposta = llm.predict(prompt).strip().lower()

    if 'listar_marcas' in resposta:
        return 'listar_marcas'
    elif 'listar_perfumes' in resposta:
        return 'listar_perfumes'
    elif 'listar_por_fragrancia' in resposta:
        return 'listar_por_fragrancia'
    elif 'listar_por_marca' in resposta:
        return 'listar_por_marca'
    elif 'obter_link_compra' in resposta:
        return 'obter_link_compra'
    elif 'recomendacao' in resposta:
        return 'recomendacao'  # Nova intenção adicionada
    else:
        return 'outras_perguntas'

#################################################################################################################################################################################    

# Funções para extração de informações específicas
def listar_nomes_perfumes(perfumes):
    resposta = "Aqui estão os perfumes disponíveis na AmoBeleza:\n"
    for perfume in perfumes.values():
        resposta += f"- {perfume['nome']} (Marca: {perfume['marca']})\n"
    return resposta

#################################################################################################################################################################################

def listar_nomes_perfumes_llm(consulta: str, perfumes):
    """
    Usa a LLM para garantir que o usuário está pedindo uma lista de perfumes.
    """
    prompt = f"""
    O usuário fez a seguinte pergunta: '{consulta}'.
    Por favor, identifique se a intenção dele é listar os nomes de todos os perfumes disponíveis.
    Retorne 'sim' ou 'não'.
    """
    
    llm = obter_llm()
    resposta = llm.predict(prompt).strip().lower()
    
    if resposta == 'sim':
        return listar_nomes_perfumes(perfumes)
    else:
        return "Não consegui identificar que você deseja listar os perfumes. Pode repetir de outra forma?"

#################################################################################################################################################################################    

def listar_perfumes_por_marca_llm(consulta: str, perfumes):
    """
    Usa a LLM para identificar a marca mencionada pelo usuário e listar os perfumes correspondentes.
    """
    prompt = f"""
    O usuário fez a seguinte pergunta: '{consulta}'.
    Por favor, identifique o nome da marca de perfume que ele mencionou. 
    Retorne apenas o nome da marca em uma única linha de texto.
    """
    
    llm = obter_llm()
    marca = llm.predict(prompt).strip()
    
    if marca:
        return listar_perfumes_por_marca(marca.lower(), perfumes)
    else:
        return "Não consegui identificar a marca mencionada. Pode repetir?"
    
#################################################################################################################################################################################

def listar_perfumes_por_marca(marca, perfumes):
    marcas_disponiveis = [p['marca'] for p in perfumes.values()]
    marca_encontrada = difflib.get_close_matches(marca, marcas_disponiveis, n=1, cutoff=0.6)
    
    if marca_encontrada:
        perfumes_encontrados = [p for p in perfumes.values() if p['marca'] == marca_encontrada[0]]
        resposta = f"Os perfumes disponíveis da marca {marca_encontrada[0]} são:\n" + "\n".join([f"{p['nome']} (Marca: {p['marca']})" for p in perfumes_encontrados])
    else:
        resposta = f"Não encontrei perfumes de uma marca semelhante a '{marca}'."
    
    return resposta

#################################################################################################################################################################################

def buscar_perfume_por_fragrancia_llm(consulta: str, perfumes):
    """
    Usa a LLM para identificar a fragrância mencionada pelo usuário e buscar os perfumes correspondentes.
    """
    prompt = f"""
    O usuário fez a seguinte pergunta: '{consulta}'.
    Por favor, identifique a fragrância mencionada na pergunta, se houver.
    Retorne apenas o nome da fragrância.
    """
    
    llm = obter_llm()
    fragrancia = llm.predict(prompt).strip()
    fragrancia.lower()

    if fragrancia:
        perfumes_encontrados = buscar_perfume_por_fragrancia(fragrancia, perfumes)
        #fragrancia_lower = fragrancia.lower()
        if perfumes_encontrados:
            return f"Os perfumes com a fragrância de {fragrancia} são:\n" + "\n".join([f"{p['nome']} (Marca: {p['marca']})" for p in perfumes_encontrados])
        else:
            return f"Não encontrei perfumes com a fragrância de {fragrancia}."
    else:
        return "Não consegui identificar a fragrância mencionada. Pode repetir por favor ?"
    
#################################################################################################################################################################################    
    
def buscar_perfume_por_fragrancia(fragrancia, perfumes):
    fragrancias_de_perfumes = [p['fragrancia'] for p in perfumes.values()]
    fragrancia_encontrada = difflib.get_close_matches(fragrancia, fragrancias_de_perfumes, n=1, cutoff=0.6)
    
    if fragrancia_encontrada:
        perfumes_encontrados = [p for p in perfumes.values() if fragrancia_encontrada[0] == p['fragrancia']]
        return perfumes_encontrados
    else:
        return "Nenhum perfume encontrado com uma fragrância semelhante."

#################################################################################################################################################################################

def obter_link_de_compra_llm(consulta: str, perfumes):
    """
    Usa a LLM para identificar o perfume que o usuário mencionou e fornecer o link de compra.
    """
    prompt = f"""
    O usuário fez a seguinte pergunta: '{consulta}'.
    Por favor, identifique o nome do perfume que ele está pedindo para comprar.
    Retorne apenas o nome do perfume sem nenhum tipo de pontuaçao.
    """
    
    llm = obter_llm()
    perfume = llm.predict(prompt).strip()
    perfume = perfume.lower()

    if perfume:
        return obter_link_de_compra(perfume.lower(), perfumes)
    else:
        return "Não consegui identificar o perfume para gerar o link de compra. Pode repetir?"

#################################################################################################################################################################################    
    
def obter_link_de_compra(perfume, perfumes):
    nomes_de_perfumes = [p['nome'] for p in perfumes.values()]
    perfume_encontrado = difflib.get_close_matches(perfume, nomes_de_perfumes, n=1, cutoff=0.6)
    
    if perfume_encontrado:
        perfume_selecionado = [p for p in perfumes.values() if perfume_encontrado[0] == p['nome']]
        return f"Aqui está o link de compra para o perfume {perfume_selecionado[0]['nome']}: {perfume_selecionado[0]['link']}"
    else:
        return "Não encontrei o perfume específico para gerar o link de compra."
    
#################################################################################################################################################################################    

def recomendar_perfume_para_ocasiao_llm(consulta: str, perfumes):
    """
    Usa o GPT para analisar os perfumes listados e recomendar os mais adequados para a ocasião mencionada.
    """
    # Primeiro, listamos os perfumes disponíveis
    lista_perfumes = listar_nomes_perfumes(perfumes)  # Função existente que já lista os perfumes

    # Usamos o LLM para recomendar qual perfume é adequado com base na lista e na consulta
    prompt = f"""
    O usuário fez a seguinte pergunta: '{consulta}'.
    Aqui está uma lista de perfumes disponíveis: 
    {lista_perfumes}

    Com base na pergunta do usuário, qual desses perfumes você recomendaria para a ocasião mencionada? 
    Por favor, dê uma recomendação de perfume da lista e explique brevemente o porquê da escolha.
    """

    llm = obter_llm()
    recomendacao = llm.predict(prompt).strip()

    return recomendacao

#################################################################################################################################################################################
    
# Função para processar a resposta com base na intenção e código Python
def processar_resposta_com_intencao(consulta, perfumes, llm_chain, historico_conversa=""):
    # Garantir que o histórico de conversa seja uma string válida
    if historico_conversa is None:
        historico_conversa = ""

    # Adicionar a consulta do usuário ao histórico
    historico_conversa += f"Usuário: {consulta}\n"

    # Identificar a intenção usando o GPT-3.5
    intencao = identificar_intencao_gpt(consulta)
    
    if intencao == "listar_marcas":
        marcas = set([p['marca'] for p in perfumes.values()])
        resposta = f"As marcas disponíveis são: {', '.join(marcas)}."
        historico_conversa += f"Zoe: {resposta}\n"
    
    elif intencao == "listar_perfumes":
        resposta = listar_nomes_perfumes(perfumes)
        historico_conversa += f"Zoe: {resposta}\n"        
    
    elif intencao == "listar_por_fragrancia":
        resposta = buscar_perfume_por_fragrancia_llm(consulta, perfumes)
        historico_conversa += f"Zoe: {resposta}\n"
    
    elif intencao == "listar_por_marca":
        resposta = listar_perfumes_por_marca_llm(consulta, perfumes)
        historico_conversa += f"Zoe: {resposta}\n"        
    
    elif intencao == "obter_link_compra":
        resposta = obter_link_de_compra_llm(consulta, perfumes)
        historico_conversa += f"Zoe: {resposta}\n"    
    
    elif intencao == "recomendacao":
        resposta = recomendar_perfume_para_ocasiao_llm(consulta, perfumes)
    
    else:
        resposta = llm_chain.run(historico_conversa=historico_conversa, pergunta=consulta)
    
    # Adicionar a resposta da Zoe ao histórico
    historico_conversa += f"Zoe: {resposta}\n"
    
    return resposta, historico_conversa