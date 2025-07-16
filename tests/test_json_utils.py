import os
import importlib.util
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("tools", os.path.join(ROOT, "tools", "__init__.py"))
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)
dumps = tools.dumps
loads = tools.loads


def test_roundtrip_simple():
    data = {'a': 1, 'b': [1, 2, 3]}
    s = dumps(data)
    assert isinstance(s, str)
    back = loads(s)
    assert back == data
