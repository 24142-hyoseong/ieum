class IeumRuntimeError(RuntimeError):
    """이음 프로그램 실행 중 발생한 오류입니다."""


class ReturnSignal(Exception):
    """함수 반환 값을 실행 흐름 밖으로 전달하기 위한 내부 신호입니다."""

    def __init__(self, value: object):
        self.value = value
