import logging


def vtex_payment_system(payment_system):
    mapping = {
        125: 220,  # PIX
        2: 701,  # VISA
        3: 710,  # DINERS
        4: 702,  # MASTERCARD
        9: 713,  # ELO
    }
    try:
        key = int(payment_system)
    except (TypeError, ValueError):
        logging.warning(f"⚠️ payment_system inválido (não numérico): {payment_system}")
        return None

    codtipvenda = mapping.get(key)
    if codtipvenda is None:
        logging.warning(f"⚠️ payment_system desconhecido: {payment_system}")
    return codtipvenda
