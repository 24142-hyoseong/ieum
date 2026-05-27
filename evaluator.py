from __future__ import annotations

from typing import Callable, Protocol

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
from environment import Environment
from errors import IeumRuntimeError, ReturnSignal
from tokens import Token, TokenType


class IeumCallable(Protocol):
    def arity(self) -> int:
        ...

    def call(self, evaluator: Evaluator, arguments: list[object]) -> object:
        ...


class NativePrint:
    def arity(self) -> int:
        return 1

    def call(self, evaluator: Evaluator, arguments: list[object]) -> object:
        evaluator.output(evaluator.stringify(arguments[0]))
        return None

    def __str__(self) -> str:
        return "<내장 함수 출력>"


class IeumFunction:
    def __init__(self, declaration: FunctionStmt, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, evaluator: Evaluator, arguments: list[object]) -> object:
        environment = Environment(self.closure)
        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)

        try:
            evaluator.execute_block(self.declaration.body, environment)
        except ReturnSignal as signal:
            return signal.value

        return None

    def __str__(self) -> str:
        return f"<함수 {self.declaration.name.lexeme}>"


class Evaluator:
    def __init__(self, output: Callable[[str], None] = print):
        self.globals = Environment()
        self.environment = self.globals
        self.output = output

        self.globals.define("출력", NativePrint())

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except ReturnSignal:
            raise IeumRuntimeError("반환은 함수 안에서만 사용할 수 있습니다.")

    def execute(self, statement: Stmt) -> None:
        if isinstance(statement, ExpressionStmt):
            self.evaluate(statement.expression)
            return

        if isinstance(statement, VarStmt):
            value = None
            if statement.initializer is not None:
                value = self.evaluate(statement.initializer)
            self.environment.define(statement.name.lexeme, value)
            return

        if isinstance(statement, BlockStmt):
            self.execute_block(statement.statements, Environment(self.environment))
