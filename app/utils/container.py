class Container:
    def __init__(self) -> None:
        self._container: dict = {}

    def resolve(self, class_):
        return self._container.get(class_)

    def register(self, class_) -> None:
        self._container[class_]
