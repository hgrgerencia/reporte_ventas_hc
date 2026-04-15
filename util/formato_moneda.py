def format_latino(val):
    """Formatea números al estilo: $ 1.234,56"""
    try:
        return f"$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "$ 0,00"