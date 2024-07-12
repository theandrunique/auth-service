import punq
from fastapi import Depends, Request, params


def get_container(request: Request) -> punq.Container:
    try:
        return request.app.state.container
    except AttributeError:
        raise AttributeError("Container not found, add container to the app state")


def validate_dependency(dependency: type, container: punq.Container) -> None:
    try:
        container.resolve(dependency)
    except punq.MissingDependencyError:
        raise Exception(f"Failed to resolve {dependency.__name__}")


def Provide[T](dependency: type[T]) -> T:
    async def _dependency(container: punq.Container = Depends(get_container)) -> T:
        return container.resolve(dependency)  # type: ignore

    return params.Depends(_dependency)  # type: ignore
