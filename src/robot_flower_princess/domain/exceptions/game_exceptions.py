class GameException(Exception):
    """Base exception for game-related errors."""

    pass


class InvalidMoveException(GameException):
    """Raised when an invalid move is attempted."""

    pass


class InvalidActionException(GameException):
    """Raised when an invalid action is attempted."""

    pass


class GameOverException(GameException):
    """Raised when the game is over."""

    pass


class InvalidRotationException(GameException):
    """Raised when an invalid rotation is attempted."""

    pass


class InvalidPickException(GameException):
    """Raised when an invalid pick is attempted."""

    pass


class InvalidDropException(GameException):
    """Raised when an invalid drop is attempted."""

    pass


class InvalidGiveException(GameException):
    """Raised when an invalid give is attempted."""

    pass


class InvalidCleanException(GameException):
    """Raised when an invalid clean is attempted."""

    pass
