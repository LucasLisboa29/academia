"""
Ponte entre o aplicativo e o compilador próprio (FitCode).

Em vez de só salvar números no banco, o app DELEGA ao compilador o cálculo
das métricas do treino. A função `analisar_treino`:

  1. Gera um programa-fonte na linguagem própria do FitCode a partir dos
     exercícios (usa 'criar', operadores aritméticos e o condicional 'checar').
  2. Roda o pipeline do compilador: Lexer -> Parser -> Interpretador.
  3. LÊ de volta os valores calculados na tabela de símbolos do interpretador
     (interp.vars) e devolve para o aplicativo USAR.

Ou seja: as métricas exibidas ao usuário são produzidas pelo nosso motor.
Se o compilador for removido, a funcionalidade de análise deixa de funcionar.
"""
from .Lexer import Lexer
from .Sintático import Parser
from .Token import Interpretador, TipoToken


def _num(v):
    """Formata um número para o código-fonte (inteiro quando possível)."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        v = 0.0
    if v < 0:                      # a linguagem não tem menos unário
        v = 0.0
    return str(int(v)) if v == int(v) else str(v)


def gerar_codigo(exercicios):
    """Monta o programa na linguagem FitCode que calcula as métricas do treino."""
    linhas = ["criar volume_total = 0;"]

    for i, ex in enumerate(exercicios):
        s = _num(ex.get("series", 0))
        r = _num(ex.get("repeticoes", 0))
        c = _num(ex.get("carga", 0))
        # volume do exercício = séries * repetições * carga
        linhas.append(f"criar vol{i} = {s} * {r} * {c};")
        linhas.append(f"volume_total = volume_total + vol{i};")

    # Classificação da intensidade decidida por REGRAS escritas na própria
    # linguagem (condicional 'checar'). 1 = Leve, 2 = Moderado, 3 = Intenso.
    linhas.append("criar intensidade = 1;")
    linhas.append("checar (volume_total > 4000) { intensidade = 2; }")
    linhas.append("checar (volume_total > 8000) { intensidade = 3; }")
    linhas.append("mostrar(volume_total);")

    return "\n".join(linhas)


def _executar(codigo):
    """Roda o compilador sobre o código e devolve o interpretador (com vars)."""
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
    """
    Calcula, VIA COMPILADOR, as métricas do treino.
    Retorna um dicionário que o aplicativo usa de verdade.
    """
    codigo = gerar_codigo(exercicios)
    interp = _executar(codigo)

    # Os valores são LIDOS da tabela de símbolos do nosso interpretador:
    volume = interp.vars.get("volume_total", 0)
    intensidade_cod = interp.vars.get("intensidade", 1)

    return {
        "sucesso": True,
        "volume_total": round(float(volume), 1),
        "intensidade": _ROTULO_INTENSIDADE.get(int(intensidade_cod), "Leve"),
        "intensidade_nivel": int(intensidade_cod),
        "total_exercicios": len(exercicios),
        "codigo_gerado": codigo,   # exposto para fins de demonstração
    }


def compilar_treino(nome, exercicios):
    """Mantida por compatibilidade: delega para a análise real."""
    return analisar_treino(exercicios)
