import tkinter as tk
from tkinter import messagebox
import random
from enum import Enum
import time

class CaseEtat(Enum):
    VIDE = 0
    NAVIRE = 1
    TOUCHE = 2
    MANQUE = 3
    COULE = 4

class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

class Navire:
    def __init__(self, taille, nom):
        self.taille = taille
        self.nom = nom
        self.positions = []
        self.touches = set()
        
    def est_coule(self):
        return len(self.touches) == self.taille
        
    def ajouter_position(self, x, y):
        self.positions.append((x, y))
        
    def est_touche(self, x, y):
        if (x, y) in self.positions:
            self.touches.add((x, y))
            return True
        return False

class Plateau:
    def __init__(self, taille=10):
        self.taille = taille
        self.grille = [[CaseEtat.VIDE for _ in range(taille)] for _ in range(taille)]
        self.navires = []
        
    def placer_navire(self, navire, x, y, orientation):
        if self.peut_placer_navire(navire.taille, x, y, orientation):
            for i in range(navire.taille):
                if orientation == Orientation.HORIZONTAL:
                    self.grille[y][x + i] = CaseEtat.NAVIRE
                    navire.ajouter_position(x + i, y)
                else:
                    self.grille[y + i][x] = CaseEtat.NAVIRE
                    navire.ajouter_position(x, y + i)
            self.navires.append(navire)
            return True
        return False
        
    def peut_placer_navire(self, taille, x, y, orientation):
        if orientation == Orientation.HORIZONTAL:
            if x + taille > self.taille:
                return False
            return all(self.grille[y][x + i] == CaseEtat.VIDE for i in range(taille))
        else:
            if y + taille > self.taille:
                return False
            return all(self.grille[y + i][x] == CaseEtat.VIDE for i in range(taille))
            
    def recevoir_tir(self, x, y):
        if self.grille[y][x] == CaseEtat.NAVIRE:
            self.grille[y][x] = CaseEtat.TOUCHE
            for navire in self.navires:
                if navire.est_touche(x, y):
                    if navire.est_coule():
                        for px, py in navire.positions:
                            self.grille[py][px] = CaseEtat.COULE
                    return True
        elif self.grille[y][x] == CaseEtat.VIDE:
            self.grille[y][x] = CaseEtat.MANQUE
        return False
        
    def tous_navires_coules(self):
        return all(navire.est_coule() for navire in self.navires)

class BatailleNavale:
    def __init__(self):
        self.fenetre = tk.Tk()
        self.fenetre.title("Bataille Navale")
        self.taille_plateau = 10
        self.taille_case = 40
        
        self.plateau_joueur = Plateau()
        self.plateau_ordi = Plateau()
        
        self.creer_interface()
        self.placer_navires_ordi()
        self.phase_placement = True
        self.navire_actuel = 0
        self.navires_a_placer = [
            Navire(5, "Porte-avions"),
            Navire(4, "Croiseur"),
            Navire(3, "Destroyer"),
            Navire(3, "Destroyer"),
            Navire(2, "Sous-marin"),
            Navire(2, "Sous-marin")
        ]
        self.orientation = Orientation.HORIZONTAL
        
    def creer_interface(self):
        # Création des plateaux
        frame_plateaux = tk.Frame(self.fenetre)
        frame_plateaux.pack(pady=20)
        
        # Plateau joueur
        frame_joueur = tk.Frame(frame_plateaux)
        frame_joueur.pack(side=tk.LEFT, padx=20)
        tk.Label(frame_joueur, text="Votre plateau").pack()
        
        self.boutons_joueur = []
        plateau_joueur = tk.Frame(frame_joueur)
        plateau_joueur.pack()
        
        for i in range(self.taille_plateau):
            ligne = []
            for j in range(self.taille_plateau):
                bouton = tk.Button(plateau_joueur, width=2, height=1,
                                 command=lambda x=j, y=i: self.clic_plateau_joueur(x, y))
                bouton.grid(row=i, column=j)
                ligne.append(bouton)
            self.boutons_joueur.append(ligne)
            
        # Plateau ordinateur
        frame_ordi = tk.Frame(frame_plateaux)
        frame_ordi.pack(side=tk.LEFT, padx=20)
        tk.Label(frame_ordi, text="Plateau adversaire").pack()
        
        self.boutons_ordi = []
        plateau_ordi = tk.Frame(frame_ordi)
        plateau_ordi.pack()
        
        for i in range(self.taille_plateau):
            ligne = []
            for j in range(self.taille_plateau):
                bouton = tk.Button(plateau_ordi, width=2, height=1,
                                 command=lambda x=j, y=i: self.clic_plateau_ordi(x, y))
                bouton.grid(row=i, column=j)
                ligne.append(bouton)
            self.boutons_ordi.append(ligne)
            
        # Contrôles
        frame_controles = tk.Frame(self.fenetre)
        frame_controles.pack(pady=10)
        
        self.btn_orientation = tk.Button(frame_controles, text="Changer orientation",
                                       command=self.changer_orientation)
        self.btn_orientation.pack(side=tk.LEFT, padx=5)
        
        self.label_statut = tk.Label(frame_controles, text="Placez vos navires")
        self.label_statut.pack(side=tk.LEFT, padx=5)
        
    def changer_orientation(self):
        if self.orientation == Orientation.HORIZONTAL:
            self.orientation = Orientation.VERTICAL
        else:
            self.orientation = Orientation.HORIZONTAL
            
    def placer_navires_ordi(self):
        navires = [
            Navire(5, "Porte-avions"),
            Navire(4, "Croiseur"),
            Navire(3, "Destroyer"),
            Navire(3, "Destroyer"),
            Navire(2, "Sous-marin"),
            Navire(2, "Sous-marin")
        ]
        
        for navire in navires:
            place = False
            while not place:
                x = random.randint(0, self.taille_plateau - 1)
                y = random.randint(0, self.taille_plateau - 1)
                orientation = random.choice(list(Orientation))
                place = self.plateau_ordi.placer_navire(navire, x, y, orientation)
                
    def clic_plateau_joueur(self, x, y):
        if self.phase_placement and self.navire_actuel < len(self.navires_a_placer):
            navire = self.navires_a_placer[self.navire_actuel]
            if self.plateau_joueur.placer_navire(navire, x, y, self.orientation):
                self.navire_actuel += 1
                self.actualiser_affichage()
                
                if self.navire_actuel >= len(self.navires_a_placer):
                    self.phase_placement = False
                    self.label_statut.config(text="À vous de jouer!")
                    self.btn_orientation.config(state=tk.DISABLED)
                else:
                    self.label_statut.config(text=f"Placez votre {self.navires_a_placer[self.navire_actuel].nom}")
                    
    def clic_plateau_ordi(self, x, y):
        if not self.phase_placement:
            if self.plateau_ordi.grille[y][x] in [CaseEtat.VIDE, CaseEtat.NAVIRE]:
                touche = self.plateau_ordi.recevoir_tir(x, y)
                self.actualiser_affichage()
                
                if self.plateau_ordi.tous_navires_coules():
                    messagebox.showinfo("Victoire!", "Vous avez gagné!")
                    self.fenetre.quit()
                else:
                    self.tour_ordinateur()
                    
    def tour_ordinateur(self):
        while True:
            x = random.randint(0, self.taille_plateau - 1)
            y = random.randint(0, self.taille_plateau - 1)
            if self.plateau_joueur.grille[y][x] in [CaseEtat.VIDE, CaseEtat.NAVIRE]:
                self.plateau_joueur.recevoir_tir(x, y)
                self.actualiser_affichage()
                
                if self.plateau_joueur.tous_navires_coules():
                    messagebox.showinfo("Défaite!", "L'ordinateur a gagné!")
                    self.fenetre.quit()
                break
                
    def actualiser_affichage(self):
        # Actualiser plateau joueur
        for y in range(self.taille_plateau):
            for x in range(self.taille_plateau):
                etat = self.plateau_joueur.grille[y][x]
                bouton = self.boutons_joueur[y][x]
                
                if etat == CaseEtat.VIDE:
                    bouton.config(bg="white")
                elif etat == CaseEtat.NAVIRE:
                    bouton.config(bg="gray")
                elif etat == CaseEtat.TOUCHE:
                    bouton.config(bg="red")
                elif etat == CaseEtat.MANQUE:
                    bouton.config(bg="blue")
                elif etat == CaseEtat.COULE:
                    bouton.config(bg="black")
                    
        # Actualiser plateau ordinateur
        for y in range(self.taille_plateau):
            for x in range(self.taille_plateau):
                etat = self.plateau_ordi.grille[y][x]
                bouton = self.boutons_ordi[y][x]
                
                if etat == CaseEtat.VIDE or etat == CaseEtat.NAVIRE:
                    bouton.config(bg="white")
                elif etat == CaseEtat.TOUCHE:
                    bouton.config(bg="red")
                elif etat == CaseEtat.MANQUE:
                    bouton.config(bg="blue")
                elif etat == CaseEtat.COULE:
                    bouton.config(bg="black")
                    
    def demarrer(self):
        self.fenetre.mainloop()

if __name__ == "__main__":
    jeu = BatailleNavale()
    jeu.demarrer()
