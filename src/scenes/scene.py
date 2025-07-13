from abc import abstractmethod
from components.statemachine import State


class Scene(State):
    @abstractmethod
    def enter(self) -> None: ...

    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def exit(self) -> None: ...
