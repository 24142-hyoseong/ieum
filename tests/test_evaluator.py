import unittest

from errors import IeumRuntimeError
from evaluator import Evaluator
from lexer import Lexer
from parser import Parser


def run_and_collect_output(source):
    outputs = []
    tokens = Lexer(source).scan_tokens()
    statements = Parser(tokens).parse()
    Evaluator(output=outputs.append).interpret(statements)
    return outputs


class TestEvaluator(unittest.TestCase):
    def test_arithmetic_output(self):
        outputs = run_and_collect_output("출력(1 + 2 * 3)")

        self.assertEqual(outputs, ["7"])

    def test_variable_assignment(self):
        outputs = run_and_collect_output("변수 x = 1 x = x + 2 출력(x)")

        self.assertEqual(outputs, ["3"])

    def test_if_else_statement(self):
        source = '변수 x = 2 만약 (x > 1) { 출력("크다") } 아니면 { 출력("작다") }'

        outputs = run_and_collect_output(source)

        self.assertEqual(outputs, ["크다"])

    def test_for_statement(self):
        source = "반복 (변수 i = 0; i < 3; i = i + 1) { 출력(i) }"

        outputs = run_and_collect_output(source)

        self.assertEqual(outputs, ["0", "1", "2"])

    def test_function_call_and_return(self):
        source = "함수 더하기(a, b) { 반환 a + b } 출력(더하기(2, 3))"

        outputs = run_and_collect_output(source)

        self.assertEqual(outputs, ["5"])

    def test_boolean_logic(self):
        outputs = run_and_collect_output("출력(참 그리고 아니다 거짓)")

        self.assertEqual(outputs, ["참"])

    def test_undefined_variable_raises_runtime_error(self):
        with self.assertRaises(IeumRuntimeError):
            run_and_collect_output("출력(x)")

    def test_division_by_zero_raises_runtime_error(self):
        with self.assertRaises(IeumRuntimeError):
            run_and_collect_output("출력(10 / 0)")

    def test_function_arity_error(self):
        source = "함수 하나(a) { 반환 a } 출력(하나(1, 2))"

        with self.assertRaises(IeumRuntimeError):
            run_and_collect_output(source)


if __name__ == "__main__":
    unittest.main()
