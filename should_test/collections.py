from .core import Matching


class ADict(Matching):
    def __init__(self, value):
        super(ADict, self).__init__()
        self.value = value

    @property
    def should(self):
        val = ADict(self.value)
        val.trace = self.trace
        return val

class ADictShould(Matching):
    def __init__(self, value):
        super(ADictShould, self).__init__()
        self.value = value

    def _this_and_other(self, other):
        return "actual {} and expected {}".format(self.value, other)

    def verify_same_keys(self, other):
        keyset_actual = set(self.value.keys())
        keyset_other = set(other.keys())
        diff1= keyset_actual.difference(keyset_other)
        diff2= keyset_other.difference(keyset_actual)
        if len(diff1) != 0:
            message = self._this_and_other(other) + " have different keys:" + \
                      "{} are present in actual but not in expected".format(diff1)
            return self.get_match_result(
                False,
                message,
                "" # negated failure never happens
            )

        if len(diff2) != 0:
            message = self._this_and_other(other) + " have different keys:" + \
                      "{} are present in expected but not in actual".format(diff2)
            return self.get_match_result(
                False,
                message,
                "" # negated failure never happens
            )
        return None

    def verify_same_values(self, other):
        different_keys = [i for i in self.value.keys() if self.value.keys() != other]
        message = self._this_and_other(other) + " are not equal:\n " +\
        "\n".join([
            "at key {k}: {v1} is not equal to {v2}"
            .format(k=k, v1=self.value[k], v2=other[k])
            for k in different_keys
        ])

        return self.get_match_result(
            len(different_keys) == 0,
            message,
            self._this_and_other(other) + " are equal."
        )
    def be_equal_to(self, other):
        are_keys_not_same = self.verify_same_keys(other)
        if are_keys_not_same:
            return are_keys_not_same


