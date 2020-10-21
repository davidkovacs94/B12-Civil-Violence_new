from epstein_civil_violence.agent import Citizen, Cop
from epstein_civil_violence.model import EpsteinCivilViolence

model = EpsteinCivilViolence(height=25, 
                           width=25, 
                           citizen_density=.7, 
                           cop_density=.044, 
                           citizen_vision=7, 
                           cop_vision=7, 
                           legitimacy=.8, 
                           max_jail_term=4, 
                           initial_unemployment_rate = 0.05,
                           corruption_level = 0.20,
                           honest_level = 0.05,
                           corruption_transmission_prob = 0.001,
                           honest_transmission_prob = 0.0001,
                           max_corruption_saturation = 0.34,
                           max_honest_saturation = 0.14,
                           max_iters=60)

model.run_model()

model_out = model.datacollector.get_model_vars_dataframe()
print(model_out)