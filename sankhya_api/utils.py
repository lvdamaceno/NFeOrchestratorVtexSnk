def limpar_telefone(telefone: str) -> str:
    if telefone.startswith("+55"):
        return telefone[3:]
    return telefone


def limpar_cep(cep: str) -> str:
    """
    Remove o hífen de um CEP, se existir.
    Ex: '66077-630' → '66077630'
    """
    return cep.replace('-', '') if cep else ''


def buscar_abreviacoes(nome_completo: str, dicionario: dict) -> list[str]:
    return [abreviacao for abreviacao, nome in dicionario.items() if nome.lower() == nome_completo.lower()]


def extrair_prefixo_sufixo_logradouro(logradouro: str) -> list[str]:
    """
    Divide um logradouro em prefixo e nome. Ex:
    'Travessa Campos Sales' → ['Travessa', 'Campos Sales']
    """
    if not logradouro:
        return ["", ""]

    prefixos = [
        "Rua", "R", "R.", "Avenida", "Av", "Av.", "Travessa", "Trav", "Trav.", "Alameda", "Al", "Al.",
        "Praça", "Pç", "Pç.", "Rodovia", "Estrada", "Via", "Viela", "Vila", "Largo", "Passeio", "Beco",
        "Caminho", "Servidão", "Boulevard", "Blvd", "Marginal", "Esplanada", "Balneário", "Colônia",
        "Conjunto", "Distrito", "Estação", "Favela", "Feira", "Jardim", "Jd", "Jd.", "Ladeira",
        "Loteamento", "Morro", "Núcleo", "Parque", "Passagem", "Passarela", "Ponte", "Porto", "Projeção",
        "Quadra", "Ramal", "Recanto", "Residencial", "Setor", "Sítio", "Trav", "Trecho", "Trevo", "Vale",
        "Vereda", "Vila", "Zona", "Complexo", "Condomínio", "Área", "Anel Rodoviário", "Desvio", "Contorno",
        "Reta", "Rodoanel", "Terminal", "Estradinha", "Alto", "Aclive", "Declive", "Encosta", "Vinculo"
    ]

    partes = logradouro.strip().split()
    if not partes:
        return ["", ""]

    primeira = partes[0].capitalize()

    if primeira in prefixos:
        prefixo = primeira
        sufixo = " ".join(partes[1:]).strip()
    else:
        prefixo = ""
        sufixo = logradouro.strip()

    return [prefixo, sufixo]