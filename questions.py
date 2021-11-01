import operator
import random


class TrueFalseMathQuestion(object):
    OPERATOR_STR = {
        operator.add: "+",
        operator.sub: "-",
        operator.mul: "X",
    }

    def __init__(self, arg1, arg2, op):
        self._arg1 = arg1
        self._arg2 = arg2
        self._op = op
        self._real_result = op(arg1, arg2)
        self._result = self._real_result + random.randint(0, 2)

    @property
    def answer(self):
        return self._real_result == self._result

    def __str__(self):
        return " ".join([str(self._arg1), self.OPERATOR_STR[self._op], str(self._arg2), "=?", str(self._result)])

    @classmethod
    def generate(cls):
        return cls(random.randint(1, 10), random.randint(1, 10), random.choice(list(cls.OPERATOR_STR.keys())))