import os

def test_whether_sample_works():
    sample_fname = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../sample.py'))
    assert os.system(f"python {sample_fname}") == 0