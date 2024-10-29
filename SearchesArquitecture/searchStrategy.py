from abc import ABC, abstractmethod
from typing import List, Tuple
from mesa import Agent

class SearchStrategy(ABC):
    @abstractmethod
    def start_search(self, start: Tuple[int, int]) -> None:
        pass

    @abstractmethod
    def explore_step(self, agent: Agent) -> Tuple[int, int]:
        pass