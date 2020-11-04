from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid

from .model import EpsteinCivilViolence
from .agent import Citizen, Cop


COP_COLOR = "#000000"
AGENT_QUIET_EMPLOYED_NOT_CORRUPT_COLOR = "#0066CC"
AGENT_QUIET_EMPLOYED_CORRUPT_COLOR = "#CC6600"
AGENT_QUIET_UNEMPLOYED_NOT_CORRUPT_COLOR = "#00CC14"
AGENT_QUIET_UNEMPLOYED_CORRUPT_COLOR = "#F2FF00"
AGENT_REBEL_COLOR = "#CC0000"
JAIL_COLOR = "#757575"


def citizen_cop_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "Shape": "circle",
        "x": agent.pos[0],
        "y": agent.pos[1],
        "Filled": "true",
    }

    if type(agent) is Citizen:
        if (agent.is_employed == 1 and agent.moral_state != "Corrupted"):
            color = (AGENT_QUIET_EMPLOYED_NOT_CORRUPT_COLOR if
                     agent.condition == "Quiescent" else AGENT_REBEL_COLOR)
        elif (agent.is_employed == 1 and agent.moral_state == "Corrupted"):
            color = (AGENT_QUIET_EMPLOYED_CORRUPT_COLOR if
                     agent.condition == "Quiescent" else AGENT_REBEL_COLOR)
        elif (agent.is_employed == 0 and agent.moral_state != "Corrupted"):
            color = (AGENT_QUIET_UNEMPLOYED_NOT_CORRUPT_COLOR if
                     agent.condition == "Quiescent" else AGENT_REBEL_COLOR)
        elif (agent.is_employed == 0 and agent.moral_state == "Corrupted"):
            color = (AGENT_QUIET_UNEMPLOYED_CORRUPT_COLOR if
                     agent.condition == "Quiescent" else AGENT_REBEL_COLOR)
        color = JAIL_COLOR if agent.jail_sentence else color
        portrayal["Color"] = color
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    elif type(agent) is Cop:
        portrayal["Color"] = COP_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1
    return portrayal


model_params = dict(
    height=40,
    width=40,
    citizen_density=0.7,
    cop_density=0.074,
    citizen_vision=7,
    cop_vision=7,
    legitimacy=0.8,
    corruption_transmission_prob=UserSettableParameter(
        "slider",
        "corruption_transmission_prob",
        0.06,
        0,
        0.25,
        0.0025,
        description="corruption transmission probability",
    ),
    corruption_level=UserSettableParameter(
        "slider",
        "corruption_level",
        0.1,
        0,
        1,
        0.01,
        description="corruption level",
    ),
    initial_unemployment_rate=UserSettableParameter(
        "slider",
        "initial_unemployment_rate",
        0.1,
        0,
        1,
        0.01,
        description="initial unemployment rate",
    ),

    max_jail_term=UserSettableParameter(
        "slider",
        "max_jail_term",
        1000,
        0,
        2500,
        100,
        description="maximal jail term",
    ),
)

canvas_element = CanvasGrid(citizen_cop_portrayal, 40, 40, 480, 480)
server = ModularServer(
    EpsteinCivilViolence, [canvas_element],
    "Epstein Civil Violence", model_params
)
