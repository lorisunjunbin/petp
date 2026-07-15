import yaml

# https://pyyaml.org/wiki/PyYAMLDocumentation
#
# Security note:
# We never use yaml.Loader / yaml.UnsafeLoader / yaml.FullLoader for reading project
# YAML files (executions, pipelines). Those loaders honor `!!python/object/apply:...`
# style tags and can execute arbitrary code at load time.
#
# Instead we build PETPSafeLoader on top of SafeLoader and *explicitly* register only
# the four project classes that are allowed to be deserialized: Execution, Task,
# Pipeline, Loop. Any unknown !!python/* tag (or any other unregistered tag) raises
# yaml.constructor.ConstructorError instead of silently instantiating arbitrary code.

try:
    from yaml import CSafeLoader as _SafeLoaderBase, CDumper as Dumper
except ImportError:
    from yaml import SafeLoader as _SafeLoaderBase, Dumper


class PETPSafeLoader(_SafeLoaderBase):
    """SafeLoader extended to construct only PETP's own data classes."""
    pass


def _register_class(cls):
    tag = f'tag:yaml.org,2002:python/object:{cls.__module__}.{cls.__name__}'

    def _construct(loader, node):
        instance = cls.__new__(cls)
        yield instance
        state = loader.construct_mapping(node, deep=True)
        if hasattr(instance, '__setstate__'):
            instance.__setstate__(state)
        else:
            instance.__dict__.update(state)

    PETPSafeLoader.add_constructor(tag, _construct)


def _register_petp_classes():
    # Imported lazily to avoid circular imports at module load time.
    from core.execution import Execution
    from core.task import Task
    from core.pipeline import Pipeline
    from core.loop import Loop

    for cls in (Execution, Task, Pipeline, Loop):
        _register_class(cls)


_PETP_CLASSES_REGISTERED = False


def _ensure_classes_registered():
    global _PETP_CLASSES_REGISTERED
    if not _PETP_CLASSES_REGISTERED:
        _register_petp_classes()
        _PETP_CLASSES_REGISTERED = True


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
    def write(target, yml):
        with open(target, 'w', encoding='utf8') as f:
            yaml.dump(yml, f, default_flow_style=False, Dumper=Dumper)

    @staticmethod
    def get_yaml_from_file(filepath: str):
        _ensure_classes_registered()
        with open(filepath, 'r', encoding='utf8') as f:
            return yaml.load(f, Loader=PETPSafeLoader)
