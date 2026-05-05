import pygame

class Ability:
    """Hauptklasse für das Ability-Dictonary"""
    def __init__(self):

    # Für jede Fähigkeit im Spiel wird ein Dictonary angelegt. Folgende Einträge sind enthalten: Der Name, die MP-Kosten, der Text für den
    # Tooltip, das "target" - also ob es Gegner angreift oder die Katzen heilt -, die Anzahl der Targets - also ob es einen einzelnen Gegner/Katze
    # anvisiert oder die ganze Gruppe & der Name der Methode, der die Animation und die Berechnung der Schadenswerte oder Heilungswerte der 
    # Ability ausführt.

    ######## Fähigkeiten der Katzen ########
    # Kriegerfähigkeiten
        self.berserker_claw = {"name":"Berserker Claw","mp_cost":10,"tooltip":"Unleashes fury of claws upon one enemy","target":"enemy","t_number":"single","method":"berserker_claw"}
        self.knock_out = {"name": "Knock Out", "mp_cost":5,"tooltip":"Causes a modeate amount of damage and stuns the enemy for 1 turn.","target":"enemy","t_number":"single","method":"knock_out"}

    # Heilerfähigkeiten
        self.prayer_of_lesser_healing = {"name":"Prayer Of Lesser Healing","mp_cost":10,"tooltip": "Prayer to heal a single cat with a small amount of life","target":"cat","t_number":"single","method":"prayer_of_lesser_healing"}
        self.prayer_of_ressurection = {"name":"Prayer Of Ressurection","mp_cost":20,"tooltip":"Prayer to bring back a single cat with a small amount of life","target":"cat", "t_number":"single", "method":"prayer_of_ressurection"}
        self.prayer_of_healing_wind = {"name":"Prayer Of Healing Wind","mp_cost":20,"tooltip":"Prayer to heal all cats with a small amount of life", "target":"cat","t_number":"all","method":"prayer_of_healing_wind"}

    # Magierfähigkeiten
        self.fireball = {"name":"Fireball","mp_cost":10,"tooltip":"A small fireball for lesser fire damage upon one enemy","target":"enemy","t_number":"single","method":"fireball"}
        self.whirlwind = {"name":"Whirlwind","mp_cost":20,"tooltip":"A whirlwind bringing damage upon all enemies","target":"enemy","t_number":"all","method":"whirlwind"}
    

    ####### Fähigkeiten der Gegner #####

        self.simple_attack = {"target":"cat","t_number":"single","method":"default_attack"} # Standardangriff
        self.poison_claw = {"target":"cat","t_number":"single","method":"poison_claw"} 
        self.fury_claws = {"target":"cat","t_number":"all","method":"fury_claws"} 