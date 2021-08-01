import random, string
from typing import Generator, List

state = random.getstate()  # save the internal state to restore in tests


def my_collecion_generator() -> Generator[
    str, None, None
]:  # <- this reads as "Generator that produces (yields) only strings"
    # ! Important: wrapping this function call in a list will hang your interpreter
    """This is a function that returns a generator.
    for the difference between iterator and generator see that SO question: https://stackoverflow.com/questions/2776829/difference-between-pythons-generators-and-iterators

    this one is endless, it will never end
    """
    import string

    # str.join takes a list and "joins" all elements into one string; separator between elements is the string providing this method, see https://docs.python.org/3/library/stdtypes.html#str.join
    # string.ascii_lowercase is just a constant
    while True:
        random_str = "".join([random.choice(string.ascii_lowercase) for _ in range(8)])
        yield random_str


def take_n(g: Generator[str, None, None], n: int) -> List[str]:
    """Takes n elements from generator g

    Args:
        n (int): number of elements to take
        g (Generator[str, None, None]): generator to take elements from

    Returns:
        List[str]: List of taken elements
    """
    return [next(g) for _ in range(n)]


class InfiniteGeneratorWrapper:
    """This class should wrap a generator we defined above (tests will pass it to the __init__)
    and do the following:
       • implement an iterator method that will do the following for each element BEFORE returning:
            • reverse a string
            • and encode the whole string as hex using `binascii.hexlify`. see: https://docs.python.org/3/library/binascii.html#binascii.hexlify
            Hint: you want to look at `take_n` code for inspiration
            Note: binascii will asks for bytes, but you have a str, to convert str to bytes, you'll need to use str.encode https://docs.python.org/3/library/stdtypes.html#str.encode
       • return AT MOST max_elements! (Don't forget that generator is infinite!)
    """
    def __init__(self, g: Generator[str, None, None], max_elements=1000) -> None:
        # insert code here
        self.g = g
        self.max_elements = max_elements
        self.index = 0

        self.l = []
        for _ in range(self.max_elements):
            self.l.append(next(self.g))

    def __iter__(self):
        return self

    def __next__(self):
        import binascii

        if self.index == self.max_elements:
            raise StopIteration

        elem = self.l[self.index]
        elem = elem[::-1]
        elem_bytes = str.encode(elem)
        elem_hex = binascii.hexlify(elem_bytes)
        elem_str = elem_hex.decode()
        self.index += 1
        return elem_str
        pass


class BaseRule:  # this is our base class
    deny_reason = "decided to keep {item} because i'm a base class"
    allow_reason = "allow {item}, because i'm a base class"

    def __init__(self) -> None:
        self.x = 42

    def allow(self, item):  # instance method
        print(self.allow_reason.format(item=item))
        return True

    def deny(self, item):
        print(self.deny_reason.format(item=item))
        return False

    def check(self, item) -> bool:
        return self.allow(item)


# For next two classes (KeepEverythingStartsFrom and DenyEverythingStartsFrom) your task is to fill the code according to
# the following specification:
#  both classes should inherit from BaseRule
#  for both classes, initializer (__init__) should accept argument named `starts_from` of type str.
#  for KeepEverythingStartsFrom:
#    • check method should allow items that startswith `starts_from`. Deny everything else.
#
#  for DenyEverythingStartsFrom the inverse is true:
#    • check method should deny items that startswith `starts_from`. Allow everything else.
#
# The `test_ruleset` function is used by tests to verify the actual logic.


class KeepEverythingStartsFrom(BaseRule):
    def __init__(self, starts_from: str):
        super().__init__()
        self.starts_from = starts_from

    def check(self, item):
        if item.startswith(self.starts_from):
            return self.allow(item)
        else:
            return self.deny(item)
    pass


class DenyEverythingStartsFrom(BaseRule):
    def __init__(self, starts_from: str):
        self.starts_from = starts_from

    def check(self, item):
        if item.startswith(self.starts_from):
            return self.deny(item)
        else:
            return self.allow(item)
    pass





def test_ruleset(items):
    rules = [
        DenyEverythingStartsFrom(starts_from="ab"),
        KeepEverythingStartsFrom(starts_from="a"),
    ]
    passed = []
    for item in items:
        evaluation_result = False  # deny everything until proven wrong
        for rule in rules:
            evaluation_result |= rule.check(item)
            if not evaluation_result:
                # break on deny
                break
        if evaluation_result:
            passed.append(item)
    return passed


#### TEST CODE HERE ####
# Beware of dragons: please don't try too much to understand tests code
# for now it's specifically written in "obfuscated" way, so i won't spoil all answers!


import unittest
import marshal
import itertools


class TestHomework4(unittest.TestCase):
    def setUp(self) -> None:
        # Ignore that function please
        super().setUp()
        self.do_a_barrel_roll = (
            lambda x: "it doesn't really matter"
        )  # construct a fn object
        black_magic_str = b"\xe3\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00C\x00\x00\x00s\x1c\x00\x00\x00|\x00d\x00d\x00d\x01\x85\x03\x19\x00}\x00|\x00\xa0\x00d\x02\xa1\x01\xa0\x01\xa1\x00S\x00)\x03N\xe9\xff\xff\xff\xffz\x05utf-8)\x02\xda\x06encode\xda\x03hex)\x01\xda\x02el\xa9\x00r\x05\x00\x00\x00\xfa <ipython-input-175-f5f41df25338>\xda\x10do_a_barrel_roll\x01\x00\x00\x00s\x04\x00\x00\x00\x00\x01\x0e\x01"
        # this is an obfuscation technique that loads bytecode for a function into function's code object. Please forgive me
        self.do_a_barrel_roll.__code__ = marshal.loads(black_magic_str)
        # end of ignore block

    def test_barrel_roll(self):
        self.assertEqual(self.do_a_barrel_roll("52"), "3235")

    def test_generator_wrapper(self):
        source_of_truth = take_n(my_collecion_generator(), 5)
        random.setstate(
            state
        )  # restore state so generator above and generator beyond will have the same outputs
        wrapper = InfiniteGeneratorWrapper(my_collecion_generator(), max_elements=5)
        for (truth, candidate) in itertools.zip_longest(source_of_truth, wrapper):
            truth = self.do_a_barrel_roll(truth)
            self.assertEqual(truth, candidate)

    def test_ruleset_passed(self):
        items = ["aa", "ab", "abc", "acd"]
        should_stay = ["aa", "acd"]
        self.assertEqual(test_ruleset(items), should_stay)

    def test_ruleset_preserves_vars(self):
        base = BaseRule()
        keep = KeepEverythingStartsFrom(starts_from="x")
        self.assertEqual(keep.x, base.x)


if __name__ == "__main__":
    unittest.main()
