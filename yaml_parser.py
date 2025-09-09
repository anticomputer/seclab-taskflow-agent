import os
import yaml
from pathlib import Path
import logging

class YamlParser:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def get_yaml_dict(self, recurse=True, dir_namespace=False) -> dict:
        """Return a directory of yaml files as a dictionary of file name indexed yaml dicts"""
        dir_path = Path(__file__).parent.resolve() / Path(self.path)
        yaml_dict = {}
        if recurse:
            files = dir_path.rglob('*')
        else:
            files = list(dir_path.iterdir())
        for f in files:
            if f.is_file() and not f.name.startswith('.') and f.suffix in ['.yaml', '.yml']:
                try:
                    with open(os.path.join(dir_path, f)) as stream:
                        try:
                            p = yaml.safe_load(stream)
                            # namespace to a full relative path e.g. /subdir/file
                            if dir_namespace:
                                namespaced_stem = str(f.relative_to(dir_path).with_suffix(''))
                                yaml_dict[namespaced_stem] = p
                            else:
                                yaml_dict[Path(f).stem] = p
                        except yaml.YAMLError as e:
                            logging.error(e)
                except FileNotFoundError as e:
                    # deal with editor temp files etc. that might have disappeared
                    logging.error(f"File not found (editor tmp file?): {e}")
                    continue
        return yaml_dict
