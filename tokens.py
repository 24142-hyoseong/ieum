from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    # 키워드 토큰: 이음 언어에서 미리 정해진 의미를 가지는 한글 단어입니다.
    VAR = auto()
    FUNC = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    TRUE = auto()
    FALSE = auto()
    NIL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # 리터럴 토큰: 숫자, 문자열, 식별자처럼 코드 안에서 실제 값을 표현합니다.
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # 연산자 토큰: 산술, 비교, 할당 연산을 표현합니다.
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    EQ_EQ = auto()
    BANG_EQ = auto()
    LT = auto()
    GT = auto()
    LT_EQ = auto()
    GT_EQ = auto()
    ASSIGN = auto()

    # 구분자 토큰: 괄호, 중괄호, 쉼표, 세미콜론처럼 코드 구조를 나눕니다.
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    # EOF 토큰: 소스 코드의 끝을 나타냅니다.
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        return (
            f"Token(type={self.type.name}, "
            f"lexeme={self.lexeme!r}, "
            f"literal={self.literal!r}, "
            f"line={self.line})"
        )


# 키워드 매핑 딕셔너리: 렉서가 식별자를 읽은 뒤 예약어인지 확인할 때 사용합니다.
KEYWORDS = {
    "변수": TokenType.VAR,
    "함수": TokenType.FUNC,
    "반환": TokenType.RETURN,
    "만약": TokenType.IF,
    "아니면": TokenType.ELSE,
    "반복": TokenType.FOR,
    "참": TokenType.TRUE,
    "거짓": TokenType.FALSE,
    "없음": TokenType.NIL,
    "그리고": TokenType.AND,
    "또는": TokenType.OR,
    "아니다": TokenType.NOT,
}
