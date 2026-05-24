from .Token import TipoToken, Token

class Lexer:
    def __init__(self, texto):
        self.texto = texto; self.pos = 0
        self.char = self.texto[self.pos] if self.texto else None

    def advance(self):
        self.pos += 1
        self.char = self.texto[self.pos] if self.pos < len(self.texto) else None

    def skip_whitespace(self):
        while self.char and self.char.isspace(): self.advance()

    def numero(self):
        res = ""
        while self.char and self.char.isdigit(): res += self.char; self.advance()
        if self.char == '.':
            res += '.'; self.advance()
            while self.char and self.char.isdigit(): res += self.char; self.advance()
            return Token(TipoToken.NUMERO_REAL, float(res))
        return Token(TipoToken.NUMERO_INTEIRO, int(res))

    def identificador(self):
        res = ""
        while self.char and (self.char.isalnum() or self.char == '_'): res += self.char; self.advance()
        keywords = {
            "mostrar": TipoToken.EXIBIR, "checar": TipoToken.CHECAR,
            "senao": TipoToken.SENAO, "criar": TipoToken.ATRIBUTO,
            "e": TipoToken.AND, "ou": TipoToken.OR
        }
        return Token(keywords.get(res, TipoToken.IDENTIFICADOR), res)

    def get_tokens(self):
        tokens = []
        while self.char:
            if self.char.isspace(): self.skip_whitespace(); continue
            if self.char.isdigit(): tokens.append(self.numero()); continue
            if self.char.isalpha(): tokens.append(self.identificador()); continue

            # Operadores Relacionais e Atribuição
            if self.char == '=':
                self.advance()
                if self.char == '=': tokens.append(Token(TipoToken.IGUAL_IGUAL, '==')); self.advance()
                else: tokens.append(Token(TipoToken.IGUAL, '='))
                continue
            elif self.char == '>':
                self.advance()
                if self.char == '=': tokens.append(Token(TipoToken.MAIOR_IGUAL, '>=')); self.advance()
                else: tokens.append(Token(TipoToken.MAIOR, '>'))
                continue
            elif self.char == '<':
                self.advance()
                if self.char == '=': tokens.append(Token(TipoToken.MENOR_IGUAL, '<=')); self.advance()
                else: tokens.append(Token(TipoToken.MENOR, '<'))
                continue
            
            # Outros Símbolos
            simbolos = {
                '+': TipoToken.SOMA, '-': TipoToken.SUBTRACAO, '*': TipoToken.MULTIPLICACAO,
                '/': TipoToken.DIVISAO, '^': TipoToken.POTENCIA, '(': TipoToken.ABRE_PARENTESES,
                ')': TipoToken.FECHA_PARENTESES, '{': TipoToken.ABRE_BLOCO, '}': TipoToken.FECHA_BLOCO,
                '%': TipoToken.MODULO, ';': TipoToken.PONTO_VIRGULA
            }
            if self.char in simbolos:
                tokens.append(Token(simbolos[self.char], self.char))
            else: raise Exception(f"Erro: {self.char}")
            self.advance()
            
        tokens.append(Token(TipoToken.EOF, None))
        return tokens