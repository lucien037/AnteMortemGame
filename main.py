import pygame
pygame.init()

# Propriétés de la fenêtre de jeu
LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = (LARGEUR_ECRAN*0.8)

ecran = pygame.display.set_mode((LARGEUR_ECRAN,HAUTEUR_ECRAN))
pygame.display.set_caption('Ante Mortem')
icon = pygame.image.load('ressources/images/hero.png')
pygame.display.set_icon(icon)

class personnage(pygame.sprite.Sprite):
    def __init__(self,x,y,echelle):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('ressources/images/hero.png')
        # Modifier l'échelle de l'image ex : augmenter taille du personnage
        self.image = pygame.transform.scale(image, (int(image.get_width() * echelle), int(image.get_height() * echelle)))
        self.rectangle = self.image.get_rect()
        self.rectangle.center = (x,y)

    def affiche(self):
        ecran.blit(self.image, self.rectangle)

perso1 = personnage(150,150,2)

# Ajouter une image dans la fenêtre en fonction des coordonnées x,y
x = 200
y = 200
echelle = 2

# Génerer la fenêtre de jeu

run = True
while run:
    perso1.affiche()
    for event in pygame.event.get():
        # Quitter le jeu
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()
