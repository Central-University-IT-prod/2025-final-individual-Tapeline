from typing import Callable


def raises[CallableT: Callable[..., ...]](  # type: ignore
        exception_class: type[BaseException],
        when: str | None = None
) -> Callable[[CallableT], CallableT]:
    """Defines what exception method or function can raise and when."""
    def inner(func: CallableT) -> CallableT:
        already_raises: tuple[type[BaseException], ...] = tuple()
        if hasattr(func, "__raises__"):
            already_raises = func.__raises__  # pragma: no cover
        func.__raises__ = (exception_class, *already_raises)  # type: ignore
        func.__doc__ = (func.__doc__ or "") + (
            f"\nThrows {exception_class.__name__}" +
            (f" when {when}" if when else "") + "."
        )
        return func
    return inner
