import math

from mesa import Agent


class Citizen(Agent):
    """
    A member of the general population, may or may not be in active rebellion.
    Summary of rule: If grievance - risk > threshold, rebel.

    Attributes:
        unique_id: unique int
        x, y: Grid coordinates
        hardship: Agent's 'perceived hardship (i.e., physical or economic
            privation).' Exogenous, drawn from U(0,1).
        regime_legitimacy: Agent's perception of regime legitimacy, equal
            across agents.  Exogenous.
        risk_aversion: Exogenous, drawn from U(0,1).
        threshold: if (grievance - (risk_aversion * arrest_probability)) >
            threshold, go/remain Active
        vision: number of cells in each direction (N, S, E and W) that agent
            can inspect
        condition: Can be "Quiescent" or "Active;" deterministic function of
            greivance, perceived risk, and
        grievance: deterministic function of hardship and regime_legitimacy;
            how aggrieved is agent at the regime?
        arrest_probability: agent's assessment of arrest probability, given
            rebellion

    """

    def __init__(
        self,
        unique_id,
        model,
        pos,
        hardship,
        legitimacy,
        regime_legitimacy,
        risk_aversion,
        active_threshold,
        threshold,
        vision,
        is_employed,
        moral_state,
        corruption_transmission_prob = 0.06,
        honest_transmission_prob = 0.02,
        max_unemployed_saturation = 0.45
        
        
      
    ):
        """
        Create a new Citizen.
        Args:
            unique_id: unique int
            x, y: Grid coordinates
            hardship: Agent's 'perceived hardship (i.e., physical or economic
                privation).' Exogenous, drawn from U(0,1).
            regime_legitimacy: Agent's perception of regime legitimacy, equal
                across agents.  Exogenous.
            risk_aversion: Exogenous, drawn from U(0,1).
            threshold: if (grievance - (risk_aversion * arrest_probability)) >
                threshold, go/remain Active
            vision: number of cells in each direction (N, S, E and W) that
                agent can inspect. Exogenous.
            model: model instance
        """
        super().__init__(unique_id, model)
        self.breed = "citizen"
        self.pos = pos
        self.hardship = hardship
        self.legitimacy=legitimacy
        self.regime_legitimacy = regime_legitimacy
        self.risk_aversion = risk_aversion
        self.active_threshold = active_threshold
        self.threshold = threshold
        self.condition = "Quiescent"
        self.vision = vision
        self.jail_sentence = 0
        self.grievance = self.hardship * (1 - self.regime_legitimacy)
        self.arrest_probability = None
        self.is_employed = is_employed
        self.moral_state = moral_state
        self.corruption_transmission_prob = corruption_transmission_prob
        self.honest_transmission_prob = corruption_transmission_prob
        self.max_unemployed_saturation = max_unemployed_saturation
        
    def step(self):
        """
        Decide whether to activate, then move if applicable.
        """
        if self.jail_sentence:
            self.jail_sentence -= 1
            return  # no other changes or movements if agent is in jail.
        self.update_neighbors()
        self.update_estimated_arrest_probability()
        #update regime legitimacy based on corruption observed in nehborhood (see definition below)
        self.update_estimated_regime_legitimacy()
        #update employment status each round (see definition below)
        #self.update_employment_status()
        #update net risk
        net_risk = self.risk_aversion * self.arrest_probability
        ## random weight to determine unemployment contribution in revolt threshold
        w_unemployment = self.random.uniform(0.03,0.43)
        ## random weight to determine corruption contribution in revolt threshold
        w_corruption = self.random.uniform(0.01,0.03)
        ## computing total contribution unemployment + corruption
        total_contribution = (w_unemployment * self.model.get_unemployed_saturation(self.model,True)) + (w_corruption * self.model.get_corrupted_saturation(self.model,True)) 
        if (
            self.condition == "Quiescent"
            and (self.grievance - net_risk) > self.threshold - total_contribution  #- self.random.uniform(0.01,0.3)*(self.model.get_unemployed_saturation(self.model,False) + self.model.get_corrupted_saturation(self.model,False))
        ):
            self.condition = "Active"
        elif (
            self.condition == "Active" and (self.grievance - net_risk) <= self.threshold - total_contribution
        ):
            self.condition = "Quiescent"
            
        if self.model.movement and self.empty_neighbors:
            new_pos = self.random.choice(self.empty_neighbors)
            self.model.grid.move_agent(self, new_pos)
        #agent has to be quiescent to become susceptible; it wouldn't make sense that a rebel becomes corrupt
        ## getting susceptible neighbors
        susceptible_neighbors = [a for a in self.neighbors if a.breed == "citizen" 
                                                     and a.moral_state =="Susceptible" and a.condition == "Quiescent"]
        ## getting employed neighbors
        employed_non_corrupted = [a for a in self.neighbors if a.breed == "citizen" 
                                                     and a.moral_state !="Corrupted" and a.is_employed == 1 ]
        
         
         
        ## a corrupted agent can corrupt another Susceptible agent 
        if self.breed == "citizen" and self.moral_state == "Corrupted":
            ## checks if the agent has any neighbors
            if len(self.neighbors) > 1:
                  if self.moral_state == "Corrupted":        
                            ## only spread corruption if the current corruption saturation < max_corruption_saturation. 
                                    if len(susceptible_neighbors) > 0:
                                        ## randomly scales the corruption transmission probability
                                        corr_prob = self.corruption_transmission_prob *self.random.uniform(0.001,0.1)
                                        ## pick a target susceptible neighbor
                                        target_neighbor = self.random.choice(susceptible_neighbors)
                                        ## an unemployed agent is easier to be corrupted than an employed agent
                                        if target_neighbor.is_employed == 1 and self.random.random() < corr_prob or target_neighbor.is_employed == 0 and self.random.random() < corr_prob + 0.07:
                                            # ensures the percentage of corrupted is less than the maximum allowed
                                                  if self.model.get_corrupted_saturation(self.model,False) < self.model.max_corruption_saturation:
                                                      target_neighbor.moral_state = "Corrupted"
                                                  # assign a job to the newly corrupted agent & take a job from another non corrupted agent
                                                  if len(employed_non_corrupted) > 0 and self.random.random() < 0.06 and target_neighbor.is_employed == 0:
                                                        victim_neighbor = self.random.choice(employed_non_corrupted) 
                                                        victim_neighbor.is_employed = 0
                                                        target_neighbor.is_employed = 1
        ## Honest agent can turn another Susceptible agent to honest 
        if self.breed == "citizen" and self.moral_state == "Honest":
            
            if len(self.neighbors) > 1:
                            
                            if len(susceptible_neighbors) > 0:
                                target_neighbor = self.random.choice(susceptible_neighbors)
                                honest_prob = self.honest_transmission_prob *self.random.uniform(0.01,0.1)
                                if  self.random.random() < honest_prob and self.model.get_honest_saturation(self.model,False) < self.model.max_honest_saturation:
                                          target_neighbor.moral_state = "Honest"
                                          
         ### randomly assign/take agents job. Adding randomness element to the employment/unemployment numbers. Each agent can earn or lose a job at each step.                                  
        if self.breed == "citizen" and self.is_employed == 1 and self.model.get_unemployed_saturation(self.model,False) < self.model.max_unemployed_saturation: 
            if self.random.random() < self.random.uniform(0.0,0.09) * self.model.get_corrupted_saturation(self.model,False):
                self.is_employed = 0
        elif self.breed == "citizen" and self.is_employed == 0: 
            if self.random.random() < self.random.uniform(0.0,0.009) * self.model.get_honest_saturation(self.model,False):
                self.is_employed = 1
                
    def update_neighbors(self):
        """
        Look around and see who my neighbors are
        """
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=1
        )
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
      
        self.empty_neighbors = [
            c for c in self.neighborhood if self.model.grid.is_cell_empty(c)
        ]

    def update_estimated_arrest_probability(self):
        """
        Based on the ratio of cops to actives in my neighborhood, estimate the
        p(Arrest | I go active).

        """
        cops_in_vision = len([c for c in self.neighbors if c.breed == "cop"])
        actives_in_vision = 1.0  # citizen counts herself
        for c in self.neighbors:
            if (
                c.breed == "citizen"
                and c.condition == "Active"
                and c.jail_sentence == 0
            ):
                actives_in_vision += 1
        self.arrest_probability = 1 - math.exp(
            -1 * self.model.arrest_prob_constant * (cops_in_vision / actives_in_vision)
        )

    def update_estimated_regime_legitimacy(self):
        """
        Based on the nr of corrupts in vision, update self.regime.legitimacy.

        """
        corrupts_in_vision = len([c for c in self.neighbors if c.breed == "citizen" and c.moral_state=="Corrupted"])
        others_in_vision = len([c for c in self.neighbors if c.breed == "citizen" and c.moral_state!="Corrupted"])
         
        if (
            self.moral_state!="Corrupted"
            and self.jail_sentence == 0
        ):
            
            corruption_saturation = self.model.get_corrupted_saturation(self.model, exclude_jailed=True)
            self.regime_legitimacy = self.legitimacy -(corrupts_in_vision / (1+others_in_vision))
            unemployment_sat = self.model.get_unemployed_saturation(self.model, exclude_jailed=True) 
            weight = self.random.uniform(0.3,0.4)* (unemployment_sat+ corruption_saturation)
            
            self.regime_legitimacy = self.legitimacy - weight  
          #  print('*******')
          #  net_risk = (self.risk_aversion * self.arrest_probability)
           # print('regime_legitimacy %f'%self.regime_legitimacy)
           # print('net risk %f'%(self.risk_aversion * self.arrest_probability))
           # print('self.grievance %f'%self.grievance )
           # print('condition %f'%(self.grievance - net_risk))
           # print('Threshold %f'%(self.threshold))


    def update_employment_status(self):
        """
        Based on the agent's activity, if they become rebels or get jailed they lose their jobs.

        """
        unemployment_sat = self.model.get_unemployed_saturation(self.model, exclude_jailed=True)
                
        if(
            unemployment_sat < self.max_unemployed_saturation
            and self.is_employed==1 and self.condition=="Active" or self.jail_sentence > 0
        ):
            self.is_employed=0
            
                      
    def update_hardship_grievance_threshold(self):
        """
        If agent becomes unemployed hardship, thershold and grievance get updated.

        """             
        
        if(
            self.is_employed==0
        ):
            self.hardship=self.random.random()-(self.is_employed*self.random.uniform(0.05,0.15))
            self.grievance = self.hardship * (1 - self.regime_legitimacy)
            threshold=self.active_threshold+(self.is_employed*self.random.uniform(0.05,0.15))
    
class Cop(Agent):
    """
    A cop for life.  No defection.
    Summary of rule: Inspect local vision and arrest a random active agent.

    Attributes:
        unique_id: unique int
        x, y: Grid coordinates
        vision: number of cells in each direction (N, S, E and W) that cop is
            able to inspect
    """

    def __init__(self, unique_id, model, pos, vision):
        """
        Create a new Cop.
        Args:
            unique_id: unique int
            x, y: Grid coordinates
            vision: number of cells in each direction (N, S, E and W) that
                agent can inspect. Exogenous.
            model: model instance
        """
        super().__init__(unique_id, model)
        self.breed = "cop"
        self.pos = pos
        self.vision = vision

    def step(self):
        """
        Inspect local vision and arrest a random active agent. Move if
        applicable.
        """
        self.update_neighbors()
        active_neighbors = []
        for agent in self.neighbors:
            if (
                agent.breed == "citizen"
                and agent.condition == "Active"
                and agent.jail_sentence == 0
            ):
                active_neighbors.append(agent)
        if active_neighbors:
            arrestee = self.random.choice(active_neighbors)
            sentence = self.random.randint(0, self.model.max_jail_term)
            arrestee.jail_sentence = sentence
            arrestee.condition = "Queit"
        if self.model.movement and self.empty_neighbors:
            new_pos = self.random.choice(self.empty_neighbors)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        """
        Look around and see who my neighbors are.
        """
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=1
        )
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [
            c for c in self.neighborhood if self.model.grid.is_cell_empty(c)
        ]
