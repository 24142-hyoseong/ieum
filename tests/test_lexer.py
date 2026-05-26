import unittest
from lexer import Lexer
from tokens import TokenType

class TestLexer(unittest.TestCase):
    """이음(Ieum) 프로그래밍 언어의 렉서를 검증하는 테스트 클래스입니다."""

    def test_keywords(self):
        """1. 모든 키워드 토큰화 (변수, 함수, 만약, 아니면, 반복, 반환, 참, 거짓 등)"""
        source = "변수 함수 만약 아니면 반복 반환 참 거짓 없음 그리고 또는 아니다"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        expected_types = [
            TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.ELSE,
            TokenType.FOR, TokenType.RETURN, TokenType.TRUE, TokenType.FALSE,
            TokenType.NIL, TokenType.AND, TokenType.OR, TokenType.NOT,
            TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_identifiers(self):
        """2. 한글 식별자 토큰화 (예: 이름, 안녕, 더하기)"""
        source = "이름 안녕 더하기 a1_"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].lexeme, "이름")
        self.assertEqual(tokens[2].lexeme, "더하기")
        self.assertEqual(tokens[3].lexeme, "a1_")

    def test_numbers(self):
        """3. 숫자 리터럴 (정수 10, 실수 3.14)"""
        source = "10 3.14"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 10)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].literal, 3.14)

    def test_strings(self):
        """4. 문자열 리터럴 ("안녕", 빈 문자열, 한글 문자열)"""
        source = '"안녕, 이음!" ""'
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "안녕, 이음!")
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].literal, "")

    def test_operators(self):
        """5. 모든 연산자 (+ - * / % == != < > <= >= =)"""
        source = "+ - * / % == != < > <= >= ="
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
            TokenType.PERCENT, TokenType.EQ_EQ, TokenType.BANG_EQ, TokenType.LT,
            TokenType.GT, TokenType.LT_EQ, TokenType.GT_EQ, TokenType.ASSIGN,
            TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_delimiters(self):
        """6. 구분자 ( { } ( ) , ; )"""
        source = "{ } ( ) , ;"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        expected_types = [
            TokenType.LBRACE, TokenType.RBRACE, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.COMMA, TokenType.SEMICOLON, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_single_line_comments(self):
        """7. 한 줄 주석 (// ...) 무시"""
        source = "변수 x = 10 // 이것은 주석입니다\n변수 y = 20"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        # x 선언 (변수, x, =, 10) 다음 바로 y 선언이 나와야 함
        self.assertEqual(tokens[4].type, TokenType.VAR)
        self.assertEqual(tokens[5].lexeme, "y")
        self.assertEqual(tokens[4].line, 2)

    def test_multi_line_comments(self):
        """8. 여러 줄 주석 (/* ... */) 무시"""
        source = "변수 a = 1 /* 여러 줄\n주석\n입니다 */ 변수 b = 2"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        # 주석이 무시되고 a 할당 다음 바로 b 할당이 나와야 함
        self.assertEqual(tokens[4].type, TokenType.VAR)
        self.assertEqual(tokens[5].lexeme, "b")

    def test_line_tracking(self):
        """9. 줄 번호 추적 (여러 줄 입력에서 정확한 line 번호)"""
        source = "출력\n(\n10\n)"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        self.assertEqual(tokens[0].line, 1)  # 출력
        self.assertEqual(tokens[1].line, 2)  # (
        self.assertEqual(tokens[2].line, 3)  # 10
        self.assertEqual(tokens[3].line, 4)  # )

    def test_error_handling(self):
        """10. 잘못된 입력에 대한 에러 처리"""
        source = "변수 @ = 10"  # 허용되지 않는 특수문자 '@'
        lexer = Lexer(source)
        
        # SyntaxError를 발생시키는지 확인
        with self.assertRaises(SyntaxError):
            lexer.scan_tokens()

if __name__ == '__main__':
    unittest.main()
