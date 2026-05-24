from .Lexer import Lexer
from .Sintático import Parser
from .Token import Interpretador, TipoToken

def compilar_treino(nome, exercicios):
    codigo = ""

    for i, ex in enumerate(exercicios):
        codigo += f'criar series{i} = {ex["series"]};\n'
        codigo += f'criar carga{i} = {ex["carga"]};\n'
        codigo += f'criar repeticoes{i} = {ex["repeticoes"]};\n'
        codigo += f'mostrar(series{i});\n'

    lexer = Lexer(codigo)
    tokens = lexer.get_tokens()
    parser = Parser(tokens)

    ast = []
    while parser._current().tipo != TipoToken.EOF:
        node = parser._parse_statement()
        if node:
            ast.append(node)

    interp = Interpretador()
    for node in ast:
        interp.visit(node)

    return {"sucesso": True, "codigo_gerado": codigo}