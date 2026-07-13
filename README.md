# 이음(Ieum)

이음은 한국어 키워드를 사용하는 작은 프로그래밍 언어입니다. Python 3.10 이상에서 동작하는 트리워킹 인터프리터 방식으로 구현합니다.

## 목표

- 한국어 키워드 기반 문법 설계
- 소스 코드 렉싱, 파싱, AST 생성 과정 이해
- AST를 직접 실행하는 인터프리터 구현
- 예제와 테스트를 통해 언어 기능 검증

## 실행 방법

```bash
python main.py examples/hello.ieum
```

Windows PowerShell에서는 다음처럼 실행할 수 있습니다.

```powershell
python main.py examples\hello.ieum
```

## 기본 문법

| 기능 | 예시 |
| --- | --- |
| 출력 | `출력("안녕")` |
| 변수 선언 | `변수 x = 10` |
| 변수 대입 | `x = x + 1` |
| 조건문 | `만약 (x > 0) { 출력("양수") } 아니면 { 출력("아님") }` |
| 반복문 | `반복 (변수 i = 0; i < 3; i = i + 1) { 출력(i) }` |
| 함수 선언 | `함수 더하기(a, b) { 반환 a + b }` |
| 함수 호출 | `출력(더하기(2, 3))` |
| 논리값 | `참`, `거짓`, `없음` |
| 논리 연산 | `그리고`, `또는`, `아니다` |

## 예제

```ieum
함수 더하기(a, b) {
    반환 a + b
}

출력(더하기(2, 3))
```

실행 결과:

```text
5
```

## 프로젝트 구조

```text
ieum-main/
  tokens.py
  lexer.py
  ast_nodes.py
  parser.py
  environment.py
  evaluator.py
  main.py
  errors.py
  examples/
  tests/
  docs/
```

## 역할 분담

효성은 핵심 인터프리터 구현을 담당합니다.

- `tokens.py`
- `lexer.py`
- `ast_nodes.py`
- `parser.py`
- `environment.py`
- `evaluator.py`
- `main.py`
- `errors.py`

현우는 예제, 테스트, 문서, 발표 자료를 담당합니다.

- `examples/*.ieum`
- `tests/test_lexer.py`
- `tests/test_parser.py`
- `tests/test_evaluator.py`
- `README.md`
- `docs/발표_아웃라인.md`
- `docs/탐구_보고서_초안.md`

## 현재 구현 범위

- 숫자, 문자열, 참, 거짓, 없음 리터럴
- 변수 선언과 대입
- 산술 연산과 비교 연산
- 논리 연산
- 조건문
- 반복문
- 함수 선언, 호출, 반환
- 내장 함수 `출력`

## 앞으로 보완할 점

- 문장 구분 규칙 명확화
- 오류 메시지 예시 정리
- 예제 파일 추가
- 통합 테스트 보강
- 발표용 실행 시연 흐름 정리

## 테스트 예제

-추가로 전체 테스트도 확인하면 좋습니다: python -m unittest discover -s tests

-그리고 간단한 직접 테스트 파일도 가능해:

-cat > test.ieum <<'EOF'

-출력("안녕")

-출력(1 + 2 * 3)

-EOF


-python main.py test.ieum

