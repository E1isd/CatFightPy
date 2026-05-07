import pygame


class Effects():
    """Klasse, die die verschiedenen Effekte für die Animationen verwaltet"""
    def __init__(self):
        # Dictonarys für die Effekte und Katzen-Animation. Erklärung: Image: Das zugehörige Spritesheet für die Animation, 
        # Size: Originalgröße eines einzelnen Animationssprite, Scale: Vergrößerungsfaktor der Grafik, wie sie auf den Bildschirm gezeichnet
        # wird. frames: Anzahl der Frames der gesamten Animation. Effect-Start: Gibt an, nach wievielen Katzen-Animationframes die
        # Effektanimation startet, um beide Animationen gut auf einander abzustimmen. Wait: Gibt an, ob die Katzenanimation nach dem 
        # Erreichen des letzen Frames aufhören soll zu spielen oder so lange in ihrem letzten Frame verharren soll, bis die Effekt-
        # Animation zu Ende gespielt hat.



        # Effekte für Abilitys
        self.dict_p_of_res = {"image": "images/Effects/p-of-sesurrection-sheet.png","size":35,"scale":7, "frames":20}

        # Katzen und Gegner-Animationen
        self.dict_cleric_pray = {"image":"images/Cat-Healer/cat-healer-pray-sheet.png","size":48,"scale":3, "frames":7,"effect_start":1,"wait": False,"loop":True,"loop-start":5,"loop_frames":2}










