from mesa import Model
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector

from .agent import Cop, Citizen


class EpsteinCivilViolence(Model):
    """
    Model 1 from "Modeling civil violence: An agent-based computational
    approach," by Joshua Epstein
    http://www.pnas.org/content/99/suppl_3/7243.full
    Attributes:
        height: grid height
        width: grid width
        citizen_density: approximate % of cells occupied by citizens.
        cop_density: approximate % of cells occupied by cops.
        citizen_vision: number of cells in each direction (N, S, E and W) that
            citizen can inspect
        cop_vision: number of cells in each direction (N, S, E and W) that cop
            can inspect
        legitimacy:  (L) citizens' perception of regime legitimacy, equal
            across all citizens
        max_jail_term: (J_max)
        active_threshold: if (grievance - (risk_aversion * arrest_probability))
            > threshold, citizen rebels
        arrest_prob_constant: set to ensure agents make plausible arrest
            probability estimates
        movement: binary, whether agents try to move at step end
        max_iters: model may not have a natural stopping point, so we set a
            max.
    Attributes added to implement Epstein's model with corruption and
    employment as additional factors:
        initial_unemployment_rate: approximate % of cells occupied
            by unemployed agents
        corruption_level: approximate % of cells occupied by agents
            in a "Corrupted" moral_state
        honest_level: approximate % of cells occupied by agents
            in an "Honest" moral_state
        corruption_transmission_prob: prespecified probability of a "Corrupt"
            agent transmitting the corrupt moral_state to a "Susceptible"
            neighbor
        honest_transmission_prob: probability of an "Honest" agent transmitting
            the honest moral_state to a "Susceptible" neighbor
        max_corruption_saturation: approximate % of cells that are allowed to
            be occupied by agents in a "Corrupt" moral_state
        max_honest_saturation: approximate % of cells that are allowed to be
           occupied by agents in an "Honest" moral_state
        max_unemployed_saturation: approximate % of cells that are allowed to
           be occupied by unemployed agents

    """

    def __init__(
        self,
        height=40,
        width=40,
        citizen_density=0.7,
        cop_density=0.074,
        citizen_vision=7,
        cop_vision=7,
        legitimacy=0.8,
        max_jail_term=1000,
        active_threshold=0.1,
        arrest_prob_constant=2.3,
        movement=True,
        initial_unemployment_rate=0.1,
        corruption_level=0.1,
        honest_level=0.6,
        corruption_transmission_prob=0.06,
        honest_transmission_prob=0.02,
        max_corruption_saturation=0.45,
        max_honest_saturation=0.35,
        max_unemployed_saturation=0.45,
        max_iters=1000,
    ):

        super().__init__()
        self.height = height
        self.width = width
        self.citizen_density = citizen_density
        self.cop_density = cop_density
        self.citizen_vision = citizen_vision
        self.cop_vision = cop_vision
        self.legitimacy = legitimacy
        self.max_jail_term = max_jail_term
        self.active_threshold = active_threshold
        self.arrest_prob_constant = arrest_prob_constant
        self.movement = movement
        self.initial_unemployment_rate = initial_unemployment_rate
        self.corruption_level = corruption_level
        self.honest_level = honest_level,
        self.susceptible_level = 1 - (corruption_level + honest_level)
        self.max_iters = max_iters
        self.iteration = 0
        self.schedule = RandomActivation(self)
        self.corruption_transmission_prob = corruption_transmission_prob
        self.honest_transmission_prob = honest_transmission_prob
        self.max_corruption_saturation = max_corruption_saturation
        self.max_honest_saturation = max_honest_saturation
        self.max_unemployed_saturation = max_unemployed_saturation

        self.grid = Grid(height, width, torus=True)
        model_reporters = {
            "Quiescent": lambda m: self.count_type_citizens(m, "Quiescent"),
            "Active": lambda m: self.count_type_citizens(m, "Active"),
            "Jailed": lambda m: self.count_jailed(m),
            "Employed": lambda m: self.count_employed(m),
            "Corrupted": lambda m:
                self.count_moral_type_citizens(m, "Corrupted"),
            "Honest": lambda m: self.count_moral_type_citizens(m, "Honest"),
            "Susceptible": lambda m:
                self.count_moral_type_citizens(m, "Susceptible")
        }
        agent_reporters = {
            "x": lambda a: a.pos[0],
            "y": lambda a: a.pos[1],
            "breed": lambda a: a.breed,
            "jail_sentence": lambda a: getattr(a, "jail_sentence", None),
            "condition": lambda a: getattr(a, "condition", None),
            "arrest_probability": lambda a:
                getattr(a, "arrest_probability", None),
            "is_employed": lambda a: getattr(a, "is_employed", None),
            "moral_condition": lambda a: getattr(a, "moral_condition", None),
        }
        self.datacollector = DataCollector(
            model_reporters=model_reporters, agent_reporters=agent_reporters
        )
        unique_id = 0
        if self.cop_density + self.citizen_density > 1:
            raise ValueError("Cop + citizen density must be less than 1")

        if self.initial_unemployment_rate > 1:
            raise ValueError("initial_unemployment_rate must be between [0,1]")

        if self.corruption_level + self.susceptible_level > 1:
            raise ValueError("corrupt + susceptible must be less than 1 ")

        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < self.cop_density:
                cop = Cop(unique_id, self, (x, y), vision=self.cop_vision)
                unique_id += 1
                self.grid[y][x] = cop
                self.schedule.add(cop)
            elif (self.random.random() <
                  (self.cop_density + self.citizen_density)):
                moral_state = "Honest"
                is_employed = 1
                if self.random.random() < self.initial_unemployment_rate:
                    is_employed = 0
                p = self.random.random()
                if p < self.corruption_level:
                    moral_state = "Corrupted"
                elif p < self.corruption_level + self.susceptible_level:
                    moral_state = "Susceptible"

                citizen = Citizen(
                    unique_id,
                    self,
                    (x, y),
                    # updated harship:
                    # hardship is alleviated by employment
                    hardship=(self.random.random() -
                              (is_employed*self.random.uniform(0.04, 0.08))),
                    legitimacy=self.legitimacy,
                    regime_legitimacy=self.legitimacy,
                    risk_aversion=self.random.random(),
                    active_threshold=self.active_threshold,
                    # updated threshold:
                    # if agent is employed threshold for rebelling is raised
                    threshold=(self.active_threshold +
                               (is_employed*self.random.uniform(0.04, 0.08))),
                    vision=self.citizen_vision,
                    is_employed=is_employed,
                    moral_state=moral_state,
                    corruption_transmission_prob=(
                        self.corruption_transmission_prob),
                )
                unique_id += 1
                self.grid[y][x] = citizen
                self.schedule.add(citizen)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step and collect data.
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        self.iteration += 1
        if self.iteration > self.max_iters:
            self.running = False

    @staticmethod
    def count_type_citizens(model, condition, exclude_jailed=False):
        """
        Helper method to count agents by Quiescent/Active.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.condition == condition:
                count += 1
        return count

    @staticmethod
    def get_unemployed_saturation(model, exclude_jailed=False):
        """
        Helper method to count unemployed agents.
        """
        unempl_count = 0
        total_count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.is_employed == 0:
                unempl_count += 1
            total_count += 1
        return unempl_count/total_count

    @staticmethod
    def get_corrupted_saturation(model, exclude_jailed=False):
        """
        Helper method to count corrupted agents.
        """
        corr_count = 0
        total_count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.moral_state == "Corrupted":
                corr_count += 1
            total_count += 1
        return corr_count/total_count

    @staticmethod
    def get_honest_saturation(model, exclude_jailed=False):
        """
        Helper method to count honest agents.
        """
        honest_count = 0
        total_count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.moral_state == "Honest":
                honest_count += 1
            total_count += 1
        return honest_count/total_count

    @staticmethod
    def count_moral_type_citizens(model, moral_condition,
                                  exclude_jailed=False):
        """
        Helper method to count agents by all moral conditions.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.moral_state == moral_condition:
                count += 1
        return count

    @staticmethod
    def count_jailed(model):
        """
        Helper method to count jailed agents.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "citizen" and agent.jail_sentence:
                count += 1
        return count

    @staticmethod
    def count_employed(model):
        """
        Helper method to count employed agents.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if agent.is_employed == 1:
                count += 1
        return count

    @staticmethod
    def count_corrupted(model):
        """
        Helper method to count corrupted agents.
        """
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if agent.is_corrupted == 1:
                count += 1
        return count
