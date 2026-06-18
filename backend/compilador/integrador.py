from .Lexer import Lexer
from .Sintático import Parser
from .Token import Interpretador, TipoToken


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        v = 0.0
    if v < 0:                      
        v = 0.0
    return str(int(v)) if v == int(v) else str(v)


def gerar_codigo(exercicios):
    linhas = ["criar volume_total = 0;"]

    for i, ex in enumerate(exercicios):
        s = _num(ex.get("series", 0))
        r = _num(ex.get("repeticoes", 0))
        c = _num(ex.get("carga", 0))
        linhas.append(f"criar vol{i} = {s} * {r} * {c};")
        linhas.append(f"volume_total = volume_total + vol{i};")

    linhas.append("criar intensidade = 1;")
    linhas.append("checar (volume_total > 4000) { intensidade = 2; }")
    linhas.append("checar (volume_total > 8000) { intensidade = 3; }")
    linhas.append("mostrar(volume_total);")

    return "\n".join(linhas)


def _executar(codigo):
    tokens = Lexer(codigo).get_tokens()
    parser = Parser(tokens)

    ast = []
    while parser._current().tipo != TipoToken.EOF:
        node = parser._parse_statement()
        if node:
            ast.append(node)

    interp = Interpretador()
    for node in ast:
        interp.visit(node)
    return interp


_ROTULO_INTENSIDADE = {1: "Leve", 2: "Moderado", 3: "Intenso"}


def analisar_treino(exercicios):
    codigo = gerar_codigo(exercicios)
    interp = _executar(codigo)

    volume = interp.vars.get("volume_total", 0)
    intensidade_cod = interp.vars.get("intensidade", 1)

    return {
        "sucesso": True,
        "volume_total": round(float(volume), 1),
        "intensidade": _ROTULO_INTENSIDADE.get(int(intensidade_cod), "Leve"),
        "intensidade_nivel": int(intensidade_cod),
        "total_exercicios": len(exercicios),
        "codigo_gerado": codigo,   
    }


def compilar_treino(nome, exercicios):
    return analisar_treino(exercicios)
