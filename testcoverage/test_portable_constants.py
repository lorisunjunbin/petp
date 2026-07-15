"""Verify HTTP_RESPONSE_KEY constant sunk into core and re-exported.
Run: python testcoverage/test_portable_constants.py  (exit 0 = pass)
"""
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_core_constants_defined():
    from core.constants import HTTP_RESPONSE_KEY, HTTP_REQUEST_ID_KEY
    assert HTTP_RESPONSE_KEY == '__http_response_key__'
    assert HTTP_REQUEST_ID_KEY == '__http_request_id__'


def test_httpservice_reexports_same_object():
    from core.constants import HTTP_RESPONSE_KEY as core_k
    from httpservice.constants import HTTP_RESPONSE_KEY as http_k
    assert core_k is http_k


if __name__ == '__main__':
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn(); print(f'PASS {name}')
            except Exception as e:
                fails += 1; print(f'FAIL {name}: {e}')
    sys.exit(1 if fails else 0)
