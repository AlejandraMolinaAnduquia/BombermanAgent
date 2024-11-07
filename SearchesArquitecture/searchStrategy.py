from abc import ABC, abstractmethod
from typing import List, Tuple
from mesa import Agent

class SearchStrategy(ABC):
    """
    Clase abstracta que define la interfaz para implementar estrategias de búsqueda
    en el contexto de una simulación de agentes. Las subclases deben implementar
    los métodos `start_search` y `explore_step`, proporcionando la lógica específica
    para iniciar y realizar pasos de búsqueda.

    Métodos:
        start_search: Inicializa el proceso de búsqueda desde una posición dada.
        explore_step: Realiza un paso en la búsqueda, devolviendo la siguiente posición a explorar.
    """

    @abstractmethod
    def start_search(self, start: Tuple[int, int]) -> None:
        """
        Inicializa el proceso de búsqueda desde una posición inicial especificada.

        Args:
            start (Tuple[int, int]): Coordenadas (x, y) de la posición inicial de búsqueda.
        
        Raises:
            NotImplementedError: Si no es implementado en la subclase.
        """
        pass

    @abstractmethod
    def explore_step(self, agent: Agent) -> Tuple[int, int]:
        """
        Realiza un paso de búsqueda desde la posición actual del agente y devuelve
        la siguiente posición a la que se moverá.

        Args:
            agent (Agent): El agente que está ejecutando la búsqueda.
        
        Returns:
            Tuple[int, int]: La siguiente posición (x, y) en el proceso de búsqueda.
        
        Raises:
            NotImplementedError: Si no es implementado en la subclase.
        """
        pass
