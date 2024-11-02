# AgentArquitecture import
from AgentArquitecture.bomberman import BombermanAgent
from AgentArquitecture.goal import GoalAgent
from AgentArquitecture.metal import MetalAgent
from AgentArquitecture.road import RoadAgent
from AgentArquitecture.rock import RockAgent
from AgentArquitecture.globe import GlobeAgent
from AgentArquitecture.bomb import BombAgent  # Importar BombAgent
from AgentArquitecture.powerup import PowerupAgent  # Importar PowerupAgent
from AgentArquitecture.explosion import ExplosionAgent  # Importar ExplosionAgent

class AgentIdentity:
    @staticmethod
    def create_agent(type, unique_id, model, search_strategy=None, **kwargs):
        if type == "bomberman":
            return BombermanAgent(unique_id, model, search_strategy)
        elif type == "goal":
            return GoalAgent(unique_id, model)
        elif type == "metal":
            return MetalAgent(unique_id, model)
        elif type == "road":
            return RoadAgent(unique_id, model)
        elif type == "rock":
            return RockAgent(unique_id, model)
        elif type == "globe":
            return GlobeAgent(unique_id, model)
        elif type == "bomb":
            # Usa kwargs para pasar posición y poder de destrucción a BombAgent
            return BombAgent(unique_id, model, kwargs['position'], kwargs['destruction_power'])
        elif type == "explosion":
            
            return ExplosionAgent(unique_id, model, kwargs['position'], kwargs['duration'])
        elif type == "powerup":
            return PowerupAgent(unique_id, model)
        else:
            raise ValueError("Invalid agent type")
