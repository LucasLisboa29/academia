from .Token import TipoToken, Number, Var, Atributo, Exibir, Modificando, Bloco, Checar, BinOp

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0

    def _current(self): return self.tokens[self.pos]
    def _advance(self): self.pos += 1
    def _expect(self, tipo):
        if self._current().tipo == tipo: self._advance()
        else: raise SyntaxError(f"Esperado {tipo} mas recebeu {self._current().tipo}")

    def _parse_factor(self):
        t = self._current()
        if t.tipo in (TipoToken.NUMERO_INTEIRO, TipoToken.NUMERO_REAL): self._advance(); return Number(t)
        if t.tipo == TipoToken.IDENTIFICADOR: self._advance(); return Var(t)
        if t.tipo == TipoToken.ABRE_PARENTESES:
            self._advance(); node = self._parse_or(); self._expect(TipoToken.FECHA_PARENTESES); return node
        raise SyntaxError(f"Token inesperado: {t}")

    def _parse_term(self):
        node = self._parse_factor()
        while self._current().tipo in (TipoToken.MULTIPLICACAO, TipoToken.DIVISAO, TipoToken.MODULO):
            op = self._current(); self._advance(); node = BinOp(node, op, self._parse_factor())
        return node

    def _parse_expression(self):
        node = self._parse_term()
        while self._current().tipo in (TipoToken.SOMA, TipoToken.SUBTRACAO):
            op = self._current(); self._advance(); node = BinOp(node, op, self._parse_term())
        return node

    def _parse_comparison(self):
        node = self._parse_expression()
        relacionais = (TipoToken.MAIOR, TipoToken.MENOR, TipoToken.MAIOR_IGUAL, 
                       TipoToken.MENOR_IGUAL, TipoToken.IGUAL_IGUAL, TipoToken.DIFERENTE)
        while self._current().tipo in relacionais:
            op = self._current(); self._advance(); node = BinOp(node, op, self._parse_expression())
        return node

    def _parse_or(self): # Incluindo lógica AND/OR
        node = self._parse_comparison()
        while self._current().tipo == TipoToken.OR:
            op = self._current(); self._advance(); node = BinOp(node, op, self._parse_comparison())
        return node

    def _parse_statement(self):
        t = self._current()
        if t.tipo == TipoToken.PONTO_VIRGULA: self._advance(); return None
        if t.tipo == TipoToken.ATRIBUTO:
            self._advance(); nome = self._current().valor; self._advance()
            self._expect(TipoToken.IGUAL); val = self._parse_or(); self._expect(TipoToken.PONTO_VIRGULA)
            return Atributo(nome, val)
        if t.tipo == TipoToken.EXIBIR:
            self._advance(); self._expect(TipoToken.ABRE_PARENTESES)
            val = self._parse_or(); self._expect(TipoToken.FECHA_PARENTESES)
            self._expect(TipoToken.PONTO_VIRGULA); return Exibir(val)
        if t.tipo == TipoToken.CHECAR:
            self._advance(); self._expect(TipoToken.ABRE_PARENTESES)
            cond = self._parse_or(); self._expect(TipoToken.FECHA_PARENTESES)
            bt = self._parse_block(); bf = None
            if self._current().tipo == TipoToken.SENAO: self._advance(); bf = self._parse_block()
            return Checar(cond, bt, bf)
        if t.tipo == TipoToken.IDENTIFICADOR:
            nome = t.valor; self._advance(); self._expect(TipoToken.IGUAL)
            val = self._parse_or(); self._expect(TipoToken.PONTO_VIRGULA); return Modificando(nome, val)
        return None

    def _parse_block(self):
        self._expect(TipoToken.ABRE_BLOCO); cmds = []
        while self._current().tipo != TipoToken.FECHA_BLOCO:
            c = self._parse_statement()
            if c: cmds.append(c)
        self._expect(TipoToken.FECHA_BLOCO); return Bloco(cmds)