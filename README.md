# Epstein Civil Violence Model

## Summary

This model is based on Joshua Epstein's simulation of how civil unrest grows and is suppressed. Citizen agents wander the grid randomly, and in the original model they are endowed with individual risk aversion and hardship levels; there is also a universal regime legitimacy value. In our implementation, we added corruption and unemployment into the equation: agent can be honest or corrupted and corruption levels influence an agent's perceived regime legitimacy and the agent's threshold for rebelling; the agent can also be employed or unemployed which will further influence their perceived hardship, grievance and threshold for rebelling; honest and employed agents risk losing their jobs if they are surrounded with corrupt neighbors, while an unemployed agent is more easily corrupted in the first place. Corruption can be understood as a property of the ruling power, therefore actively rebelling agents can never be corrupted; if a quiescent agent is corrupted it symbolizes that they become part of the regime. There are also Cop agents, who work on behalf of the regime and are neither honest nor corrupted. Cops arrest Citizens who are actively rebelling; Citizens decide whether to rebel based on their hardship and the regime legitimacy, and their perceived probability of arrest. 

The model generates mass uprising as self-reinforcing processes: if enough agents are rebelling, the probability of any individual agent being arrested is reduced, making more agents more likely to join the uprising. However, the more rebelling Citizens the Cops arrest, the less likely additional agents become to join.

## How to Run

To run the model in jupyter notebook, open ``EpsteinCivilViolence.ipynb`` from this directory. e.g.

```
    EpsteinCivilViolence.ipynb
``` 
To run the model in python :

```
    $ python run.py    
``` 
The required packages for running the model can be found in the requirements.txt 
