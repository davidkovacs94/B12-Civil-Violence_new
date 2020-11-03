# Epstein Civil Violence Model

## Summary

This model is based on Joshua Epstein's simulation of how civil unrest grows and is suppressed. Citizen agents wander the grid randomly, and in the original model they are endowed with individual risk aversion and hardship levels; there is also a universal regime legitimacy value. In our implementation, we added corruption and unemployment into the equation: agent can be honest or corrupted and corruption levels influence an agent's perceived regime legitimacy and the agent's threshold for rebelling; the agent can also be employed or unemployed which will further influence their perceived hardship, grievance and threshold for rebelling; honest and employed agents risk losing their jobs if they are surrounded with corrupt neighbors, while an unemployed agent is more easily corrupted in the first place. Corruption can be understood as a property of the ruling power, therefore actively rebelling agents can never be corrupted; if a quiescent agent is corrupted it symbolizes that they become part of the regime. There are also Cop agents, who work on behalf of the regime and are neither honest nor corrupted. Cops arrest Citizens who are actively rebelling; Citizens decide whether to rebel based on their hardship and the regime legitimacy, and their perceived probability of arrest. 

The model generates mass uprising as self-reinforcing processes: if enough agents are rebelling, the probability of any individual agent being arrested is reduced, making more agents more likely to join the uprising. However, the more rebelling Citizens the Cops arrest, the less likely additional agents become to join.

## How to Run

To run the model in jupyter notebook, open ``EpsteinCivilViolence.ipynb`` from this directory. e.g.

```
    EpsteinCivilViolence.ipynb
``` 
To run the model from a terminal and in python, open "run.py" from this directory following the code:

```
    $ python run.py    
``` 

If you want to run the code from a python terminal use the following code:

```
    $ exec(open("run.py").read())    
``` 

For interactive visualization run the following python code from a terminal and from this directory (if this method fails , try copying the contents of the "Visualization.py" file into an IPYNB notebook document in Jupyter Notebook and run from there or try the second method):

```
    $ python Visualization.py    
``` 

If it results in an error message try the following code in a python terminal (depending on the terminal used an error message might appear due to a failure to launch the mesa server; the code below has been tried and works if ran from the console of the Spyder IDE):

```
    $ exec(open("Visualization.py").read())   
``` 

Color guide for the interactive visualization:

Quescient + Employed + Non-corrupted agents: BLUE

Quescient + Employed + Corrupted agents: BROWN

Quescient + Unemployed + Non-corrupted agents: GREEN

Quescient + Unemployed + Corrupted agents: YELLOW

Active agents: RED

Jailed agents: Grey

Cops: BLACK

The required packages for running the model can be found in the requirements.txt 
