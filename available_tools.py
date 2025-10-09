import logging

class VersionException(Exception):
    pass

class FileTypeException(Exception):
    pass

class AvailableTools:
    """
    This class is used for storing dictionaries of all the available
    personalities, taskflows, and prompts.
    """
    def __init__(self, yamls: dict):
        self.personalities = {}
        self.taskflows = {}
        self.prompts = {}
        self.toolboxes = {}

        # Iterate through all the yaml files and divide them into categories.
        # Each file should contain a header like this:
        #
        #   seclab-taskflow-agent:
        #     type: taskflow
        #     version: 1
        #
        for path, yaml in yamls.items():
            try:
                header = yaml['seclab-taskflow-agent']
                version = header['version']
                if version != 1:
                    raise VersionException(str(version))
                filetype = header['type']
                if filetype == 'personality':
                    self.personalities.update({path: yaml})
                elif filetype == 'taskflow':
                    self.taskflows.update({path: yaml})
                elif filetype == 'prompt':
                    self.prompts.update({path: yaml})
                elif filetype == 'toolbox':
                    self.toolboxes.update({path: yaml})
                else:
                    raise FileTypeException(str(filetype))
            except KeyError as err:
                logging.error(f'{path} does not contain the key {err.args[0]}')
            except VersionException as err:
                logging.error(f'{path}: seclab-taskflow-agent version {err.args[0]} is not supported')
            except FileTypeException as err:
                logging.error(f'{path}: seclab-taskflow-agent file type {err.args[0]} is not supported')
