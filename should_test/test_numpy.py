import monadic_chaining as mc
import numpy

from .core import Matching


# class ANumpyArray()


class ANumpyArray(Matching):
    def __init__(self, value):
        super(ANumpyArray, self).__init__()
        self.value = value

    @property
    def should(self):
        val = ANumpyArrayShould(self.value)
        val.trace = self.trace
        return val


class ANumpyArrayShould(Matching):
    def __init__(self, st):
        super(ANumpyArrayShould, self).__init__()
        self.num = st

    def _be_equal_to_general(self, equals, other, extramessage, equality_str):
        # type: (np.array[bool], np.array) -> MatchResult
        result = equals.any()
        one_and_other = "{one} and {other}".format(one=self.num, other= other)
        message = [one_and_other, " are not equal", extramessage] + \
                  mc.List(zip(equals, range(len(equals)))) \
                      ._filter(lambda x: not x[0]) \
                      ._map(lambda x: x[1]) \
                      ._map(lambda x:
                            "\nat position {pos}: {one} {eq} {other}".format(
                                pos=x, one=self.num[x], eq=equality_str, other=other[x])
                            )

        return self.get_match_result(
            bool(result),
            "".join(message),
            one_and_other + " are equal" + extramessage
        )
    def be_equal_to(self, other):
        equals = self.num == other
        return self._be_equal_to_general(
            self.num == other, other, ".", "!="
        )

    def all_be_equal_to(self, other):

        equals = self.num != other
        result = equals.any()
        one_and_other = "{one} is not all equal to {other}".format(self.num, other)
        message = [one_and_other] + \
                  mc.List(zip(equals, len(equals))) \
                      ._filter(lambda x: not x[0]) \
                      ._map(lambda x: x[1]) \
                      ._map(lambda x:
                            "\nat position {pos}: {one} != {other}".format(
                                pos=x, one=self.num[x], other=other)
                            )
        return result, message

    def be_equal_to_with_precision(self, other, decimal_places):
        real_precision = 10 ** (-decimal_places)
        equals = numpy.isclose(self.num, other, rtol= real_precision, atol=real_precision, equal_nan=True)
        return self._be_equal_to_general(
            equals,
            other,
            extramessage=" up to {}.".format(real_precision),
            equality_str="!~"
        )

def test_numpy_array_equal():
    result = ANumpyArray(numpy.array([1.0,2.0,3.0])).should.be_equal_to(numpy.array([1.0, 2.0, 3.0]))
    assert result.__dict__ == {
        'matches': True,
        'failure': '[ 1.  2.  3.] and [ 1.  2.  3.] are not equal.',
        'negated_failure': '[ 1.  2.  3.] and [ 1.  2.  3.] are equal.'
    }

def test_numpy_array_equal_with_precision():
    result = ANumpyArray(numpy.array([1.0,2.00001,3.0]))\
        .should.be_equal_to_with_precision(numpy.array([1.0, 2.0, 3.0]), decimal_places=3)
    expected = {
        'matches': True,
        'failure': '[ 1.       2.00001  3.     ] and [ 1.  2.  3.] are not equal up to 0.001.',
        'negated_failure': '[ 1.       2.00001  3.     ] and [ 1.  2.  3.] are equal up to 0.001.'
    }
    assert result.__dict__ == expected, \
        "{} != {}".format(result.__dict__, expected)

