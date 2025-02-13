class AutomationError(Exception):
    pass


class ExtensionAlreadyInstalledError(Exception):
    pass


class ExtensionNotFoundError(Exception):
    pass


class ProfilesNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


class NoFreePortsError(Exception):
    def __init__(self, message="no free ports available"):
        super().__init__(message)
