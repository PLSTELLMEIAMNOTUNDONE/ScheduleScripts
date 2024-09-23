import unittest
from src.python.schedule.state_init import *
from src.python.model_operation import *
from ortools.sat.python import cp_model


def counted(f):
    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return f(*args, **kwargs)

    wrapped.calls = 0
    return wrapped


class TestModelOp(unittest.TestCase):
    def test_build(self):
        state = init_state()
        order = []
        @counted
        def dummy1(state: SchState, plausable, schedule: dict, model):
            order.append(dummy1.calls)

        @counted
        def dummy2(state: SchState, plausable, schedule: dict, model):
            order.append(dummy2.calls)

        model = cp_model.CpModel()
        build(state, dummy_plausable, {}, model, dummy1)(dummy1)(dummy1)(dummy2)(dummy2, end=True)
        assert order == [1, 2, 3, 1, 2]

    def test_init_model(self):
        state = init_state()

        @counted
        def dummy(state: SchState, plausable, schedule: dict, model):
            return

        model = cp_model.CpModel()
        build(state, dummy_plausable, {}, model, init_model)(dummy, end=True)
        assert dummy.calls == 1

    def test_full_sequence(self):
        state = init_state()

        model = cp_model.CpModel()
        build(state=state, plausable=dummy_plausable, model=model, schedule={}, fun=init_model)(
            at_most_one_group_for_time)(
            at_most_one_room_for_time)(
            exact_amount_of_classes_for_group)(
            clustering, end=True
        )

