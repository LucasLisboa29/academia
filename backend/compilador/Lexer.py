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
            "criar": TipoToken.ATRIBUTO, "mostrar": TipoToken.EXIBIR,
            "checar": TipoToken.CHECAR, "senao": TipoToken.SENAO,
            "adicionar": TipoToken.ADICIONAR
        }
        return Token(keywords.get(res, TipoToken.IDENTIFICADOR), res)

    def ler_texto(self):
        # lê uma string literal entre aspas: "Supino reto"
        self.advance()  # consome a aspa de abertura
        res = ""
        while self.char is not None and self.char != '"':
            res += self.char
            self.advance()
        self.advance()  # consome a aspa de fechamento
        return Token(TipoToken.TEXTO, res)

    def get_tokens(self):
        tokens = []
        while self.char:
            if self.char.isspace(): self.skip_whitespace(); continue
            if self.char.isdigit(): tokens.append(self.numero()); continue
            if self.char.isalpha(): tokens.append(self.identificador()); continue
            if self.char == '"': tokens.append(self.ler_texto()); continue

            simbolos = {
                '+': TipoToken.SOMA, '*': TipoToken.MULTIPLICACAO,
                '(': TipoToken.ABRE_PARENTESES, ')': TipoToken.FECHA_PARENTESES,
                '{': TipoToken.ABRE_BLOCO, '}': TipoToken.FECHA_BLOCO,
                '=': TipoToken.IGUAL, '>': TipoToken.MAIOR,
                ';': TipoToken.PONTO_VIRGULA, ',': TipoToken.VIRGULA
            }
            if self.char in simbolos:
                tokens.append(Token(simbolos[self.char], self.char))
            else:
                raise Exception(f"Erro: {self.char}")
            self.advance()

        tokens.append(Token(TipoToken.EOF, None))
        return tokens
