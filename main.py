from __future__ import annotations

import sys
from pathlib import Path

from evaluator import Evaluator
from errors import IeumRuntimeError
from lexer import Lexer
from parser import Parser


USAGE_ERROR = 64
SYNTAX_ERROR = 65
RUNTIME_ERROR = 70


def run(source: str) -> None:
    tokens = Lexer(source).scan_tokens()
    statements = Parser(tokens).parse()
    Evaluator().interpret(statements)


def run_file(path: str) -> None:
    source_path = Path(path)
    if source_path.suffix != ".ieum":
        raise IeumRuntimeError(".ieum 파일만 실행할 수 있습니다.")

    source = source_path.read_text(encoding="utf-8")
    run(source)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("사용법: python main.py <파일.ieum>", file=sys.stderr)
        return USAGE_ERROR

    try:
        run_file(argv[0])
    except SyntaxError as error:
        print(f"문법 오류: {error}", file=sys.stderr)
        return SYNTAX_ERROR
    except IeumRuntimeError as error:
        print(f"실행 오류: {error}", file=sys.stderr)
        return RUNTIME_ERROR
    except OSError as error:
        print(f"파일 오류: {error}", file=sys.stderr)
        return RUNTIME_ERROR

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
