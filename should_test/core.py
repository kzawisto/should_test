import sys
import os


class AnsiColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestPrinter(object):
    def __init__(self):
        self.show_success = False
        self.colors = True
        self.verbose = os.environ["ST_VERBOSE"] if "ST_VERBOSE" in os.environ else 0
        pass

    def failure_meesage_print(self, message, exception=None):
        print AnsiColors.FAIL + exception.__class__.__name__ + "\n" +\
            message + AnsiColors.ENDC
        raise exception

    def success_message_print(self, message):
        if self.verbose:
            print AnsiColors.OKGREEN + message + AnsiColors.ENDC


printer = TestPrinter()


class MatchResult(object):
    def __init__(
            self,
            matches,
            failure,
            negated_failure,
            is_negated,
            trace
    ):
        self.matches = matches
        self.failure = failure
        self.negated_failure = negated_failure
        assert isinstance(matches, bool)
        assert isinstance(failure, str)
        assert isinstance(negated_failure, str)
        if matches and is_negated:
            printer.failure_meesage_print(
                str(self._failure(trace, negated_failure)),
                self._failure(trace, negated_failure)
            )
        elif not matches and not is_negated:
            printer.failure_meesage_print(
                str(self._failure(trace, failure)),
                self._failure(trace, failure)
            )
        elif matches and not is_negated:
            printer.success_message_print(
                negated_failure
            )
        else:
            printer.success_message_print(
                failure
            )

    def _failure(self, trace, what):
        return AssertionError("{} - {}: {}".format(
            trace.filename,
            trace.lineno,
            what
        ))


class Matching(object):
    def __init__(self, upper_trace=None):
        from inspect import getframeinfo, stack
        self.negated = False
        self.val = None
        if upper_trace is None:
            count = 0
            while True or count > 10:
                self.trace = getframeinfo(stack()[count][0])
                if self.trace.function != "__init__":
                    break
                if count == 10:
                    raise Exception("stack trace too deep")
                count += 1
        pass

    @property
    def never(self):
        self.negated = True
        return self

    def get_match_result(self, result, failure, failure_negated):
        return MatchResult(
            result, failure, failure_negated, self.negated, self.trace
        )


class ANumberShould(Matching):
    def __init__(self, num):
        super(ANumberShould, self).__init__()
        self.num = num

    @property
    def be_nan(self):
        import math
        return self.get_match_result(
            math.isnan(self.num),
            self._failure_nan(value=self.num),
            self._failure_not_nan()
        )

    def be_equal_with_precision_to(self, value, precision):
        result = abs(self.num - value) / max(abs(self.num),
                                             abs(value)) < 10**(-precision)
        return self.get_match_result(
            result,
            "{} is not equal to {} up to {} digits".format(
                self.num, value, precision),
            "{} is equal to {} up to {} digits".format(
                self.num, value, precision)
        )

    def be_equal_to(self, value):
        return self.get_match_result(
            self.num == value,
            "{} is not equal to {}".format(self.num, value),
            "{} is equal to {}".format(self.num, value)
        )

    def _failure_nan(self, value):
        return "{} is not nan".format(value)

    def _failure_not_nan(self):
        return "Value is nan"


class ANumber(Matching):
    def __init__(self, num):
        super(ANumber, self).__init__()
        self.num = num

    @property
    def should(self):
        num = ANumberShould(self.num)
        num.trace = self.trace
        return num


class AString(Matching):
    def __init__(self, st):
        super(AString, self).__init__()
        self.val = st

    @property
    def should(self):
        num = AStringShould(self.val)
        num.trace = self.trace
        return num

    @property
    def after_being(self, func):
        self.val = self.val.strip
        return self

    @property
    def after_being_stripped(self):
        self.val = self.val.strip()
        return self

    @property
    def after_being_uppercased(self):
        self.val = self.val.upper()
        return self

    @property
    def after_being_lowercased(self):
        self.val = self.val.strip()
        return self


class AStringShould(Matching):
    def __init__(self, st):
        super(AStringShould, self).__init__()
        self.num = st

    @property
    def be_equal_to(self):
        num = AStringShould(self.num)
        num.trace = self.trace
        return num


"""
ANumber(10).should.be_equal_to(9)
ANumber(200).should.be_nan
ANumber(float('nan')).should.be_nan
ANumber(100.1).should.never.be_equal_with_precision_to(100.00001, 3)
"""
