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

    def call(self, evaluator: "Evaluator", arguments: list[object]) -> object:
        ...


class NativePrint:
    def arity(self) -> int:
        return 1

    def call(self, evaluator: "Evaluator", arguments: list[object]) -> object:
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

    def call(self, evaluator: "Evaluator", arguments: list[object]) -> object:
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
            return

        if isinstance(statement, IfStmt):
            if self.is_truthy(self.evaluate(statement.condition)):
                self.execute(statement.then_branch)
            elif statement.else_branch is not None:
                self.execute(statement.else_branch)
            return

        if isinstance(statement, ForStmt):
            if statement.initializer is not None:
                self.execute(statement.initializer)

            while True:
                if statement.condition is not None:
                    if not self.is_truthy(self.evaluate(statement.condition)):
                        break

                self.execute(statement.body)

                if statement.increment is not None:
                    self.evaluate(statement.increment)
            return

        if isinstance(statement, FunctionStmt):
            function = IeumFunction(statement, self.environment)
            self.environment.define(statement.name.lexeme, function)
            return

        if isinstance(statement, ReturnStmt):
            value = None
            if statement.value is not None:
                value = self.evaluate(statement.value)
            raise ReturnSignal(value)

        raise IeumRuntimeError(f"알 수 없는 문장입니다: {type(statement).__name__}")

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expression: Expr) -> object:
        if isinstance(expression, Literal):
            return expression.value

        if isinstance(expression, Variable):
            return self.environment.get(expression.name)

        if isinstance(expression, Assign):
            value = self.evaluate(expression.value)
            self.environment.assign(expression.name, value)
            return value

        if isinstance(expression, Grouping):
            return self.evaluate(expression.expression)

        if isinstance(expression, Unary):
            right = self.evaluate(expression.right)
            return self.evaluate_unary(expression.operator, right)

        if isinstance(expression, Binary):
            return self.evaluate_binary(expression)

        if isinstance(expression, Call):
            return self.evaluate_call(expression)

        raise IeumRuntimeError(f"알 수 없는 표현식입니다: {type(expression).__name__}")

    def evaluate_unary(self, operator: Token, right: object) -> object:
        if operator.type == TokenType.MINUS:
            self.check_number_operand(operator, right)
            return -right

        if operator.type == TokenType.NOT:
            return not self.is_truthy(right)

        raise IeumRuntimeError(f"줄 {operator.line}: 알 수 없는 단항 연산자입니다.")

    def evaluate_binary(self, expression: Binary) -> object:
        operator = expression.operator

        if operator.type == TokenType.OR:
            left = self.evaluate(expression.left)
            if self.is_truthy(left):
                return left
            return self.evaluate(expression.right)

        if operator.type == TokenType.AND:
            left = self.evaluate(expression.left)
            if not self.is_truthy(left):
                return left
            return self.evaluate(expression.right)

        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        if operator.type == TokenType.PLUS:
            if self.is_number(left) and self.is_number(right):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise IeumRuntimeError(
                f"줄 {operator.line}: '+'는 숫자끼리 또는 문자열끼리만 사용할 수 있습니다."
            )

        if operator.type == TokenType.MINUS:
            self.check_number_operands(operator, left, right)
            return left - right

        if operator.type == TokenType.STAR:
            self.check_number_operands(operator, left, right)
            return left * right

        if operator.type == TokenType.SLASH:
            self.check_number_operands(operator, left, right)
            if right == 0:
                raise IeumRuntimeError(f"줄 {operator.line}: 0으로 나눌 수 없습니다.")
            return left / right

        if operator.type == TokenType.PERCENT:
            self.check_number_operands(operator, left, right)
            if right == 0:
                raise IeumRuntimeError(f"줄 {operator.line}: 0으로 나눌 수 없습니다.")
            return left % right

        if operator.type == TokenType.GT:
            self.check_number_operands(operator, left, right)
            return left > right

        if operator.type == TokenType.GT_EQ:
            self.check_number_operands(operator, left, right)
            return left >= right

        if operator.type == TokenType.LT:
            self.check_number_operands(operator, left, right)
            return left < right

        if operator.type == TokenType.LT_EQ:
            self.check_number_operands(operator, left, right)
            return left <= right

        if operator.type == TokenType.EQ_EQ:
            return left == right

        if operator.type == TokenType.BANG_EQ:
            return left != right

        raise IeumRuntimeError(f"줄 {operator.line}: 알 수 없는 이항 연산자입니다.")

    def evaluate_call(self, expression: Call) -> object:
        callee = self.evaluate(expression.callee)
        arguments = [self.evaluate(argument) for argument in expression.arguments]

        if not self.is_callable(callee):
            raise IeumRuntimeError(f"줄 {expression.paren.line}: 호출할 수 없는 값입니다.")

        expected = callee.arity()
        actual = len(arguments)
        if actual != expected:
            raise IeumRuntimeError(
                f"줄 {expression.paren.line}: 인자 {expected}개가 필요하지만 {actual}개를 받았습니다."
            )

        return callee.call(self, arguments)

    def is_callable(self, value: object) -> bool:
        return callable(getattr(value, "arity", None)) and callable(getattr(value, "call", None))

    def is_truthy(self, value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def is_number(self, value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def check_number_operand(self, operator: Token, operand: object) -> None:
        if self.is_number(operand):
            return
        raise IeumRuntimeError(f"줄 {operator.line}: 피연산자는 숫자여야 합니다.")

    def check_number_operands(self, operator: Token, left: object, right: object) -> None:
        if self.is_number(left) and self.is_number(right):
            return
        raise IeumRuntimeError(f"줄 {operator.line}: 두 피연산자는 숫자여야 합니다.")

    def stringify(self, value: object) -> str:
        if value is None:
            return "없음"
        if value is True:
            return "참"
        if value is False:
            return "거짓"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
