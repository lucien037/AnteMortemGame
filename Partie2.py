import pygame
from personnage import personnage
pygame.init()

LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = (LARGEUR_ECRAN*0.8)

ecran = pygame.display.set_mode((LARGEUR_ECRAN,HAUTEUR_ECRAN))
pygame.display.set_caption('ANTE MORTEM')


# Vitesse image
vitesse_image = pygame.time.Clock()
FPS = 144
# mouvement du personnage
bouger_droite = False
bouger_gauche = False
# Couleurs
couleur_bg = (255,255,255)

def backgroung():
    ecran.fill(couleur_bg)



perso1 = personnage(0, 150, 150, 2, 2)
ennemi = personnage(2,300,150, 2, 2)

# Ajouter une image dans la fenêtre en fonction des coordonnées x,y
# x = 200
# y = 200
# echelle = 2

# Génerer la fenêtre de jeu
run = True
while run:
    vitesse_image.tick(FPS)
    backgroung()
    perso1.affiche()
    ennemi.affiche()

    perso1.bouger(bouger_droite, bouger_gauche)
    for event in pygame.event.get():
        # Quitter le jeu
        if event.type == pygame.QUIT:
            run = False
        # Touches du clavier appuyées
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                bouger_droite = True
                # perso1.bouger(bouger_droite)
            if event.key == pygame.K_q:
                bouger_gauche = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # Touches clavier non appuyées
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                bouger_droite = False
            if event.key == pygame.K_q:
                bouger_gauche = False

    pygame.display.update()
pygame.quit()
