class ReactionBase:
    """
    Base class for all reactions.

    :param parameters: Dictionary of reaction-specific parameters.
    :param globals: Dictionary of global parameters.
    """
    def __init__(self, parameters, globals, clips_dict=None):
        self.parameters = parameters
        self.globals = globals
        self.clips_dict = clips_dict
        
    def run(self, protocol):
        raise NotImplementedError("Subclasses must implement the run method.")
