from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tokens import Token


# Expr 기본 클래스: 값을 계산할 수 있는 모든 표현식 노드의 기준입니다.
class Expr:
    pass


# Stmt 기본 클래스: 실행 흐름을 이루는 모든 문장 노드의 기준입니다.
class Stmt:
    pass


# Literal: 숫자, 문자열, 참, 거짓, 없음 같은 실제 값을 담습니다.
@dataclass(frozen=True)
class Literal(Expr):
    value: Any


# Variable: 변수 이름 토큰을 통해 현재 환경에서 값을 찾는 표현식입니다.
@dataclass(frozen=True)
class Variable(Expr):
    name: Token


# Assign: 변수 이름과 새 값을 담아 대입 표현식을 나타냅니다.
@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr


# Binary: 왼쪽 값, 연산자, 오른쪽 값으로 이루어진 이항 연산 표현식입니다.
@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


# Unary: 연산자 하나와 대상 표현식 하나로 이루어진 단항 연산 표현식입니다.
@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr


# Grouping: 괄호로 감싸 우선순위를 명확히 한 표현식입니다.
@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr


# Call: 함수 이름이나 함수 표현식, 닫는 괄호 토큰, 인자 목록을 담습니다.
@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]


# ExpressionStmt: 표현식 하나를 독립된 문장으로 실행합니다.
@dataclass(frozen=True)
class ExpressionStmt(Stmt):
    expression: Expr


# VarStmt: 변수 이름과 선택적인 초기값 표현식을 담는 변수 선언문입니다.
@dataclass(frozen=True)
class VarStmt(Stmt):
    name: Token
    initializer: Expr | None


# BlockStmt: 중괄호 안에 들어 있는 문장 목록을 하나의 블록으로 묶습니다.
@dataclass(frozen=True)
class BlockStmt(Stmt):
    statements: list[Stmt]


# IfStmt: 조건식, 참일 때 실행할 문장, 선택적인 거짓 분기 문장을 담습니다.
@dataclass(frozen=True)
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None


# ForStmt: 초기화, 조건, 증감, 본문으로 이루어진 반복문을 나타냅니다.
@dataclass(frozen=True)
class ForStmt(Stmt):
    initializer: Stmt | None
    condition: Expr | None
    increment: Expr | None
    body: Stmt


# FunctionStmt: 함수 이름, 매개변수 토큰 목록, 함수 본문 문장 목록을 담습니다.
@dataclass(frozen=True)
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


# ReturnStmt: 반환 키워드 토큰과 선택적인 반환값 표현식을 담습니다.
@dataclass(frozen=True)
class ReturnStmt(Stmt):
    keyword: Token
    value: Expr | None
