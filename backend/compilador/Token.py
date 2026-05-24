from enum import Enum

class TipoToken(Enum):
    NUMERO_INTEIRO = 1; NUMERO_REAL = 2; IDENTIFICADOR = 3
    SOMA = 4; SUBTRACAO = 5; MULTIPLICACAO = 6; DIVISAO = 7; POTENCIA = 8
    ABRE_PARENTESES = 9; FECHA_PARENTESES = 10; EOF = 11
    MAIOR = 12; MENOR = 13; IGUAL = 14; AND = 15; OR = 16
    ATRIBUTO = 17; EXIBIR = 18; CHECAR = 19; SENAO = 20
    IGUAL_IGUAL = 21; DIFERENTE = 22
    MENOR_IGUAL = 23; MAIOR_IGUAL = 24; NOT = 25
    ABRE_BLOCO = 26; FECHA_BLOCO = 27; MODULO = 28; PONTO_VIRGULA = 29

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo; self.valor = valor
    def __repr__(self):
        return f"{self.tipo.name}({self.valor})"

class Number:
    def __init__(self, token): self.value = token.valor
    def __repr__(self): return f"Number({self.value})"

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

class Interpretador:
    def __init__(self): self.vars = {}
    def visit(self, node):
        if isinstance(node, Number): return node.value
        elif isinstance(node, Var): return self.vars[node.name]
        elif isinstance(node, BinOp):
            left, right = self.visit(node.left), self.visit(node.right)
            t = node.op.tipo
            if t == TipoToken.SOMA: return left + right
            if t == TipoToken.SUBTRACAO: return left - right
            if t == TipoToken.MULTIPLICACAO: return left * right
            if t == TipoToken.DIVISAO: return left / right
            if t == TipoToken.MODULO: return left % right
            if t == TipoToken.MAIOR: return left > right
            if t == TipoToken.MENOR: return left < right
            if t == TipoToken.MAIOR_IGUAL: return left >= right
            if t == TipoToken.MENOR_IGUAL: return left <= right
            if t == TipoToken.IGUAL_IGUAL: return left == right
            if t == TipoToken.DIFERENTE: return left != right
            if t == TipoToken.AND: return left and right
            if t == TipoToken.OR: return left or right
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