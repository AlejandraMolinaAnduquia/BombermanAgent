# Importación de módulos desde AgentArquitecture
from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.bomb import BombAgent  # Importa el agente de bombas
from AgentArquitecture.powerup import PowerupAgent  # Importa el agente de comodines
from AgentArquitecture.explosion import ExplosionAgent  # Importa el agente de explosión

class AgentIdentity:
    """
    Clase de utilidad para crear instancias de diferentes tipos de agentes en el juego.

    Métodos:
        create_agent: Método estático para crear instancias de agentes según el tipo especificado.
    """
    
    @staticmethod
    def create_agent(type, unique_id, model, search_strategy=None, **kwargs):
        """
        Crea y retorna una instancia del agente especificado por el parámetro `type`.
        
        Args:
            type (str): Tipo de agente a crear.
            unique_id (int): ID único para el agente.
            model: El modelo de la simulación al que pertenece el agente.
            search_strategy (str, optional): Estrategia de búsqueda para BombermanAgent.
            kwargs: Argumentos adicionales necesarios para algunos tipos de agentes.

        Returns:
            Agent: Una instancia del agente correspondiente.

        Raises:
            ValueError: Si se proporciona un tipo de agente no válido.
        """
        
        # Verifica el tipo de agente y crea la instancia adecuada
        if type == "bomberman":
            # Crea un BombermanAgent con estrategia de búsqueda opcional
            return BombermanAgent(unique_id, model, search_strategy)
        
        elif type == "goal":
            # Crea un agente de meta o salida
            return GoalAgent(unique_id, model)
        
        elif type == "metal":
            # Crea un agente de tipo Metal, que actúa como un obstáculo indestructible
            return MetalAgent(unique_id, model)
        
        elif type == "road":
            # Crea un agente de tipo Road (camino) por donde pueden moverse los agentes
            return RoadAgent(unique_id, model)
        
        elif type == "rock":
            # Crea un agente Rock (roca), que puede ser destruido por bombas
            return RockAgent(unique_id, model)
        
        elif type == "globe":
            # Crea un GlobeAgent, que representa un enemigo en la simulación
            return GlobeAgent(unique_id, model)
        
        elif type == "bomb":
            # Crea un BombAgent, usando `position` y `destruction_power` pasados en `kwargs`
            return BombAgent(unique_id, model, kwargs['position'], kwargs['destruction_power'])
        
        elif type == "explosion":
            # Crea un ExplosionAgent, usa `position` y `duration` de `kwargs`
            return ExplosionAgent(unique_id, model, kwargs['position'], kwargs['duration'])
        
        elif type == "powerup":
            # Crea un PowerupAgent (agente de comodín)
            return PowerupAgent(unique_id, model)
        
        else:
            # Lanza un error si el tipo de agente no es válido
            raise ValueError("Invalid agent type")
