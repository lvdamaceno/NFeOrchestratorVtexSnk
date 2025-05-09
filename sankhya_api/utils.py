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
