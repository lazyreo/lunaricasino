"""Application-specific exceptions."""


class AppError(Exception):
    """Base exception for application failures."""


class ForwardError(AppError):
    """Raised when a message cannot be forwarded."""


class ClientNotStartedError(AppError):
    """Raised when the Telegram client is used before start."""


class MongoNotConnectedError(AppError):
    """Raised when MongoDB is used before connect."""


class ScheduleError(AppError):
    """Raised when schedule state cannot be loaded or saved."""
