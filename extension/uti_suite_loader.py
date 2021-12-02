import json
import unitti
from importlib import import_module


def load_test(test_config_file):
    suites = []
    with open(test_config_file) as f:
        data = json.load(f)
        for i in data['suites']:
            classes = []
            for k in i.get('classes', ()):
                module, class_name = k.rsplit('.', 1)
                classes.append(getattr(import_module(module), class_name))
            ig, eg = i.get('include_group', ()), i.get('exclude_group', ())
            pool_size = i.get('pool_size', 32)
            ret = unitti.load_classes(*classes, include=ig, exclude=eg, pool_size=pool_size)
            suites.append(ret)
        return suites
