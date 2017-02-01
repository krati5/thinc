# encoding: utf8
from __future__ import unicode_literals
import pytest
from flexmock import flexmock
from hypothesis import given, strategies

from ...neural._classes import model as base
from ...neural.ops import NumpyOps


@pytest.fixture
def model_with_no_args():
    model = base.Model()
    return model


def test_Model_defaults_to_name_model(model_with_no_args):
    assert model_with_no_args.name == 'model'


def test_changing_instance_name_doesnt_change_class_name():
    model = base.Model()
    assert model.name != 'changed'
    model.name = 'changed'
    model2 = base.Model()
    assert model2.name != 'changed'


def test_changing_class_name_doesnt_change_default_instance_name():
    model = base.Model()
    assert model.name != 'changed'
    base.Model.name = 'changed'
    assert model.name != 'changed'
    # Reset state
    base.Model.name = 'model'

def test_changing_class_name_doesnt_changes_nondefault_instance_name():
    model = base.Model(name='nondefault')
    assert model.name == 'nondefault'
    base.Model.name = 'changed'
    assert model.name == 'nondefault'


def test_Model_defaults_to_cpu(model_with_no_args):
    assert isinstance(model_with_no_args.ops, NumpyOps)


def test_models_get_different_ids(model_with_no_args):
    model1 = base.Model()
    model2 = base.Model()
    assert model1.id != model2.id

def test_init_assigns_attributes():
    model = base.Model()
    model._mem
    assert model._layers == []
    assert model._operators == {}


def test_init_installs_via_descriptions():
    def mock_install(attr, self):
        setattr(self, attr, 'model=' + self.name)
    base.Model.descriptions = [("myattr", mock_install)]
    model = base.Model(name='model1')
    assert model.myattr == 'model=%s' % 'model1'
    model2 = base.Model(name='model2')
    assert model2.myattr == 'model=%s' % 'model2'


def test_init_calls_hooks():
    def mock_init_hook(self, *args, **kwargs):
        setattr(self, 'hooked', (args, kwargs))
    base.Model.on_init_hooks = [mock_init_hook]
    model = base.Model(0, 1, 2)
    assert model.hooked == ((0, 1, 2), {})
    model2 = base.Model(value='something')
    assert model2.hooked == (tuple(), {'value': 'something'})


def test_use_device():
    dev_id = id(base.Model.ops)
    with base.Model.use_device(base.Model.ops.device):
        assert id(base.Model.ops) == dev_id
    with base.Model.use_device('gpu'):
        assert id(base.Model.ops) != dev_id
    assert id(base.Model.ops) == dev_id


def test_bind_plus():
    with base.Model.define_operators({'+': lambda a, b: (a.name, b.name)}):
        m = base.Model(name='a') + base.Model(name='b')
        assert m == ('a', 'b')

def test_plus_chain():
    with base.Model.define_operators({'+': lambda a, b: a}):
        m = base.Model(name='a') + base.Model(name='b') + base.Model(name='c') + base.Model(name='d')
        assert m.name == 'a'


@pytest.mark.parametrize('op', '+ - * @ / // % ** << >> & ^ |'.split())
def test_all_operators(op):
    m1 = base.Model(name='a')
    m2 = base.Model(name='b')
    with base.Model.define_operators({op: lambda a, b: a.name + b.name}):
        if op == '+':
            value = m1 + m2
        else:
            with pytest.raises(TypeError):
                value = m1 + m2
        if op == '-':
            value = m1 - m2
        else:
            with pytest.raises(TypeError):
                value = m1 - m2

        if op == '*':
            value = m1 * m2
        else:
            with pytest.raises(TypeError):
                value = m1 * m2

        if op == '@':
            value = m1.__matmul__(m2) # Be kind to Python 2...
        else:
            with pytest.raises(TypeError):
                value = m1.__matmul__(m2)

        if op == '/':
            value = m1 / m2
        else:
            with pytest.raises(TypeError):
                value = m1 / m2

        if op == '//':
            value = m1 // m2
        else:
            with pytest.raises(TypeError):
                value = m1 // m2
        if op == '^':
            value = m1 ^ m2
        else:
            with pytest.raises(TypeError):
                value = m1 ^ m2
        if op == '%':
            value = m1 % m2
        else:
            with pytest.raises(TypeError):
                value = m1 % m2
        if op == '**':
            value = m1 ** m2
        else:
            with pytest.raises(TypeError):
                value = m1 ** m2
        if op == '<<':
            value = m1 << m2
        else:
            with pytest.raises(TypeError):
                value = m1 << m2
        if op == '>>':
            value = m1 >> m2
        else:
            with pytest.raises(TypeError):
                value = m1 >> m2
        if op == '&':
            value = m1 & m2
        else:
            with pytest.raises(TypeError):
                value = m1 & m2
        if op == '^':
            value = m1 ^ m2
        else:
            with pytest.raises(TypeError):
                value = m1 ^ m2
        if op == '|':
            value = m1 | m2
        else:
            with pytest.raises(TypeError):
                value = m1 | m2
    assert base.Model._operators == {}
