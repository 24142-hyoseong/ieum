from __future__ import annotations

from ast_nodes import (
    Assign,
    Binary,
    BlockStmt,
    Call,
    Expr,
    ExpressionStmt,
    ForStmt,
    FunctionStmt,
    Grouping,
    IfStmt,
    Literal,
    ReturnStmt,
    Stmt,
    Unary,
    VarStmt,
    Variable,
)
from tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt]:
        # EOF를 만날 때까지 선언 또는 문장을 하나씩 읽어 AST 목록으로 만듭니다.
        statements: list[Stmt] = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return statements

    def _declaration(self) -> Stmt:
        if self._match(TokenType.FUNC):
            return self._function_declaration()
        if self._match(TokenType.VAR):
            return self._var_declaration()
        return self._statement()

    def _function_declaration(self) -> FunctionStmt:
        name = self._consume(TokenType.IDENTIFIER, "함수 이름이 필요합니다.")
        self._consume(TokenType.LPAREN, "'('가 필요합니다.")

        params: list[Token] = []
        if not self._check(TokenType.RPAREN):
            while True:
                params.append(self._consume(TokenType.IDENTIFIER, "매개변수 이름이 필요합니다."))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "')'가 필요합니다.")
        self._consume(TokenType.LBRACE, "함수 본문 앞에 '{'가 필요합니다.")
        body = self._block()
        return FunctionStmt(name, params, body)

    def _var_declaration(self) -> VarStmt:
        name = self._consume(TokenType.IDENTIFIER, "변수 이름이 필요합니다.")

        initializer: Expr | None = None
        if self._match(TokenType.ASSIGN, TokenType.EQ):
            initializer = self._expression()

        return VarStmt(name, initializer)

    def _statement(self) -> Stmt:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.LBRACE):
            return BlockStmt(self._block())

        return self._expression_statement()

    def _if_statement(self) -> IfStmt:
        self._consume(TokenType.LPAREN, "'('가 필요합니다.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "')'가 필요합니다.")

        then_branch = self._statement()
        else_branch = self._statement() if self._match(TokenType.ELSE) else None

        return IfStmt(condition, then_branch, else_branch)

    def _for_statement(self) -> ForStmt:
        self._consume(TokenType.LPAREN, "'('가 필요합니다.")

        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
            self._consume(TokenType.SEMICOLON, "';'가 필요합니다.")
        else:
            initializer = self._expression_statement()
            self._consume(TokenType.SEMICOLON, "';'가 필요합니다.")

        condition: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "';'가 필요합니다.")

        increment: Expr | None = None
        if not self._check(TokenType.RPAREN):
            increment = self._expression()
        self._consume(TokenType.RPAREN, "')'가 필요합니다.")

        body = self._statement()
        return ForStmt(initializer, condition, increment, body)

    def _return_statement(self) -> ReturnStmt:
        keyword = self._previous()

        if self._check(TokenType.RBRACE) or self._check(TokenType.EOF):
            value = None
        else:
            value = self._expression()

        return ReturnStmt(keyword, value)

    def _block(self) -> list[Stmt]:
        # 여는 중괄호는 이미 소비된 상태이며, 닫는 중괄호 전까지 문장을 반복해서 읽습니다.
        statements: list[Stmt] = []

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RBRACE, "'}'가 필요합니다.")
        return statements

    def _expression_statement(self) -> ExpressionStmt:
        return ExpressionStmt(self._expression())

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._or()

        if self._match(TokenType.ASSIGN, TokenType.EQ):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)

            raise SyntaxError(f"줄 {equals.line}: 대입할 수 없는 대상입니다.")

        return expr

    def _or(self) -> Expr:
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = Binary(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = Binary(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.EQ_EQ, TokenType.BANG_EQ):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(TokenType.LT, TokenType.GT, TokenType.LT_EQ, TokenType.GT_EQ):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._call()

    def _call(self) -> Expr:
        # primary 뒤에 괄호가 이어지면 함수 호출로 확장합니다.
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Call:
        arguments: list[Expr] = []

        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        paren = self._consume(TokenType.RPAREN, "')'가 필요합니다.")
        return Call(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "')'가 필요합니다.")
            return Grouping(expr)

        token = self._peek()
        raise SyntaxError(f"줄 {token.line}: 표현식이 필요합니다.")

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()

        token = self._peek()
        raise SyntaxError(f"줄 {token.line}: {message}")

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
