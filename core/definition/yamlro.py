from yaml import load, dump

# https://pyyaml.org/wiki/PyYAMLDocumentation

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class YamlRO:

    @staticmethod
    def read(yml, keys):
        try:
            result: any = yml
            for key in keys:
                result = result[key]
            return result
        except Exception as e:
            raise e

    @staticmethod
    def modify(yml, keys, value):
        if len(keys) == 1:
            yml[keys[0]] = value
        elif len(keys) == 2:
            yml[keys[0]][keys[1]] = value
        elif len(keys) == 3:
            yml[keys[0]][keys[1]][keys[2]] = value
        else:
            raise KeyError(f'invalid keys ! {str(keys)}')
        return yml

    @staticmethod
    def write(target, yml):
        with open(target, 'w', encoding='utf8') as f:
            dump(yml, f, default_flow_style=False, Dumper=Dumper)

    @staticmethod
    def get_yaml_from_file(filepath: str):
        with open(filepath, 'r', encoding='utf8') as f:
            return load(f, Loader=Loader)
