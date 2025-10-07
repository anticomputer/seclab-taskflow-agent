class AvailableTools:
    """
    This class is used for storing dictionaries of all the available
    personalities, taskflows, and prompts.
    """
    def __init__(self, personalities: dict, taskflows: dict, prompts: dict):
        self.personalities = personalities
        self.taskflows = taskflows
        self.prompts = prompts
