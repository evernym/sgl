def load_all():

    import json
    import os

    from ..principal import Principal
    from ..rule import Rule
    from ..condition import Condition

    examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../examples'))

    class DynLoad:
        def __init__(self, cls):
            self.cls = cls
            self.dicts = []
            self.objs = []

    def load(which):
        x = DynLoad(which)
        cname = which.__name__.lower() + 's'
        if cname == 'criterions': cname = 'condition'
        folder = os.path.join(examples_dir, cname)
        try:
            for fname in os.listdir(folder):
                name = fname[:-5]
                with open(os.path.join(folder, fname), 'rt') as f:
                    txt = f.read()
                dict = json.loads(txt)
                obj = which.from_dict(dict)
                setattr(x, name + '_dict', dict)
                setattr(x, name, obj)
                x.dicts.append(dict)
                x.objs.append(obj)
        except:
            print(f"Exception while loading {folder}/{cname}")
            raise
        return x

    return load(Principal), load(Condition), load(Rule)


p, c, r = load_all()
del load_all
