from tokens import KEYWORDS, Token, TokenType


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self) -> None:
        char = self._advance()

        if char == "(":
            self._add_token(TokenType.LPAREN)
        elif char == ")":
            self._add_token(TokenType.RPAREN)
        elif char == "{":
            self._add_token(TokenType.LBRACE)
        elif char == "}":
            self._add_token(TokenType.RBRACE)
        elif char == ",":
            self._add_token(TokenType.COMMA)
        elif char == ";":
            self._add_token(TokenType.SEMICOLON)

        elif char == "+":
            self._add_token(TokenType.PLUS)
        elif char == "-":
            self._add_token(TokenType.MINUS)
        elif char == "*":
            self._add_token(TokenType.STAR)
        elif char == "%":
            self._add_token(TokenType.PERCENT)
        elif char == "=":
            self._add_token(TokenType.EQ_EQ if self._match("=") else TokenType.ASSIGN)
        elif char == "!":
            self._add_token(TokenType.BANG_EQ if self._match("=") else TokenType.NOT)
        elif char == "<":
            self._add_token(TokenType.LT_EQ if self._match("=") else TokenType.LT)
        elif char == ">":
            self._add_token(TokenType.GT_EQ if self._match("=") else TokenType.GT)

        elif char == "/":
            if self._match("/"):
                self._skip_line_comment()
            elif self._match("*"):
                self._skip_block_comment()
            else:
                self._add_token(TokenType.SLASH)

        elif char in (" ", "\t", "\r"):
            pass
        elif char == "\n":
            self.line += 1

        elif char == '"':
            self._string()
        elif self._is_digit(char):
            self._number()
        elif self._is_identifier_start(char):
            self._identifier()
        else:
            raise SyntaxError(f"줄 {self.line}: 알 수 없는 문자 '{char}'")

    def _identifier(self) -> None:
        while self._is_identifier_part(self._peek()):
            self._advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _number(self) -> None:
        while self._is_digit(self._peek()):
            self._advance()

        if self._peek() == "." and self._is_digit(self._peek_next()):
            self._advance()
            while self._is_digit(self._peek()):
                self._advance()

        text = self.source[self.start:self.current]
        self._add_token(TokenType.NUMBER, float(text) if "." in text else int(text))

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            self._advance()

        if self._is_at_end():
            raise SyntaxError(f"줄 {self.line}: 문자열이 닫히지 않았습니다.")

        self._advance()
        value = self.source[self.start + 1:self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _skip_line_comment(self) -> None:
        while self._peek() != "\n" and not self._is_at_end():
            self._advance()

    def _skip_block_comment(self) -> None:
        while not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
                self._advance()
            elif self._peek() == "*" and self._peek_next() == "/":
                self._advance()
                self._advance()
                return
            else:
                self._advance()

        raise SyntaxError(f"줄 {self.line}: 여러 줄 주석이 닫히지 않았습니다.")

    def _add_token(self, token_type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _is_digit(self, char: str) -> bool:
        return "0" <= char <= "9"

    def _is_hangul(self, char: str) -> bool:
        return "\uac00" <= char <= "\ud7af"

    def _is_alpha(self, char: str) -> bool:
        return "a" <= char <= "z" or "A" <= char <= "Z"

    def _is_identifier_start(self, char: str) -> bool:
        return self._is_hangul(char) or self._is_alpha(char) or char == "_"

    def _is_identifier_part(self, char: str) -> bool:
        return self._is_identifier_start(char) or self._is_digit(char)