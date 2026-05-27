from __future__ import annotations

from errors import IeumRuntimeError
from tokens import Token


class Environment:
    def __init__(self, enclosing: Environment | None = None):
        self.enclosing = enclosing
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        # 변수 정의는 항상 현재 스코프의 딕셔너리에 저장합니다.
        self.values[name] = value

    def get(self, name: Token | str) -> object:
        variable_name, line = self._extract_name_and_line(name)

        # 현재 스코프에서 먼저 찾고, 없으면 바깥 스코프를 차례대로 확인합니다.
        if variable_name in self.values:
            return self.values[variable_name]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise IeumRuntimeError(f"줄 {line}: 정의되지 않은 변수 '{variable_name}'입니다.")

    def assign(self, name: Token | str, value: object) -> None:
        variable_name, line = self._extract_name_and_line(name)

        # 대입은 이미 존재하는 변수에만 허용하며, 없으면 바깥 스코프로 위임합니다.
        if variable_name in self.values:
            self.values[variable_name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise IeumRuntimeError(
            f"줄 {line}: 정의되지 않은 변수 '{variable_name}'에 값을 대입할 수 없습니다."
        )

    def _extract_name_and_line(self, name: Token | str) -> tuple[str, int | str]:
        if isinstance(name, Token):
            return name.lexeme, name.line
        return name, "?"
