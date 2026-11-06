class MusicError(Exception):
    pass


class UsernameTaken(MusicError):
    pass


class InvalidCredentials(MusicError):
    pass


class UserDeactivated(MusicError):
    pass


class InvalidToken(MusicError):
    pass
