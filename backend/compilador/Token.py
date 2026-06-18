from enum import Enum

class TipoToken(Enum):
    NUMERO_INTEIRO = 1; NUMERO_REAL = 2; IDENTIFICADOR = 3; TEXTO = 4
    SOMA = 5; MULTIPLICACAO = 6
    ABRE_PARENTESES = 7; FECHA_PARENTESES = 8; ABRE_BLOCO = 9; FECHA_BLOCO = 10
    MAIOR = 11; IGUAL = 12; VIRGULA = 13; PONTO_VIRGULA = 14
    ATRIBUTO = 15; EXIBIR = 16; CHECAR = 17; SENAO = 18; ADICIONAR = 19
    EOF = 20

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo; self.valor = valor
    def __repr__(self):
        return f"{self.tipo.name}({self.valor})"

class Number:
    def __init__(self, token): self.value = token.valor
    def __repr__(self): return f"Number({self.value})"

class Texto:
    def __init__(self, token): self.value = token.valor
    def __repr__(self): return f"Texto({self.value})"

class Var:
    def __init__(self, token): self.name = token.valor
    def __repr__(self): return f"Var({self.name})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left; self.op = op; self.right = right
    def __repr__(self): return f'BinOP({self.left}, {self.op.tipo.name}, {self.right})'

class Atributo:
    def __init__(self, nome, valor):
        self.nome = nome; self.valor = valor
    def __repr__(self): return f'Atributo({self.nome}, {self.valor})'

class Modificando:
    def __init__(self, nome, valor):
        self.nome = nome; self.valor = valor
    def __repr__(self): return f'Modificando({self.nome}, {self.valor})'

class Exibir:
    def __init__(self, expressao): self.expressao = expressao
    def __repr__(self): return f'Exibir({self.expressao})'

class Checar:
    def __init__(self, condicao, se_verdade, se_mentira):
        self.condicao = condicao; self.se_verdade = se_verdade; self.se_mentira = se_mentira

class Bloco:
    def __init__(self, comandos): self.comandos = comandos

class AdicionarExercicio:
    def __init__(self, nome, series, carga, repeticoes):
        self.nome = nome; self.series = series
        self.carga = carga; self.repeticoes = repeticoes
    def __repr__(self): return f'AdicionarExercicio({self.nome})'

class Interpretador:
    def __init__(self):
        self.vars = {}
        self.exercicios = []   # exercícios produzidos ao EXECUTAR o programa

    def visit(self, node):
        if isinstance(node, Number): return node.value
        elif isinstance(node, Texto): return node.value
        elif isinstance(node, Var): return self.vars[node.name]
        elif isinstance(node, AdicionarExercicio):
            ex = {
                "nome": self.visit(node.nome),
                "series": int(self.visit(node.series)),
                "carga": self.visit(node.carga),
                "repeticoes": int(self.visit(node.repeticoes)),
            }
            self.exercicios.append(ex)
            return ex
        elif isinstance(node, BinOp):
            left, right = self.visit(node.left), self.visit(node.right)
            t = node.op.tipo
            if t == TipoToken.SOMA: return left + right
            if t == TipoToken.MULTIPLICACAO: return left * right
            if t == TipoToken.MAIOR: return left > right
        elif isinstance(node, Atributo) or isinstance(node, Modificando):
            val = self.visit(node.valor); self.vars[node.nome] = val; return val
        elif isinstance(node, Exibir):
            val = self.visit(node.expressao); print('Saída:', val); return val
        elif isinstance(node, Bloco):
            res = None
            for c in node.comandos: res = self.visit(c)
            return res
        elif isinstance(node, Checar):
            if self.visit(node.condicao): return self.visit(node.se_verdade)
            elif node.se_mentira: return self.visit(node.se_mentira)
