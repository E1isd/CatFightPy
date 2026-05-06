import pygame

class Inventory:
    """Hauptklasse für das Inventar"""
    def __init__(self,cf_games):
        self.screen = cf_games.screen
        


    # Das Spielinventar als Dictonary: Hier sind zu jedem Item Informationen gespeichert und zum Abruf bereit. Wenn eine Instanz
    # dieser Klasse existiert lassen sich so auch die Werte ändern z.B. die aktuelle Anzahl. Zu jedem Item ist auch eine Tooltip-Message
    # für die Tooltip Box gespeichert.
        self.item_dict = {
            "Potion":{"name":"Potion","in_stock":3,"action":"heal","value":50,"tooltip":"Heals target cat"},
            "Antidote":{"name":"Antidote","in_stock":2,"action":"cure","status_effect":"poison","value":0,"tooltip":"Cures poision"},
            "Catnip":{"name":"Catnip","in_stock":1,"action":"revive","value":30,"tooltip":"Revives fallen cat"},
            "Ether":{"name":"Ether","in_stock":1,"action":"mp_restore","value":30,"tooltip":"Restores Mp"}
        }