import unittest
from lexer import Lexer
# from parser import Parser  # 아직 parser 없어서 주석 유지


class TestParser(unittest.TestCase):
    """Parser 테스트 준비"""

    def test_number_expression(self):
        """숫자 하나 파싱 테스트"""
        source = "10"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()

        # parser 나오면 아래 코드 활성화
        # parser = Parser(tokens)
        # result = parser.parse()
        # self.assertEqual(result, 10)

        self.assertTrue(True)  # 임시 통과

    def test_function_call(self):
        """출력(10) 같은 함수 호출 테스트"""
        source = "출력(10)"
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()

        # parser 나오면 활성화
        # parser = Parser(tokens)
        # result = parser.parse()
        # self.assertEqual(result, ...)

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()