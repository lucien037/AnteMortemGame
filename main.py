import pygame
pygame.init()

# Propriétés de la fenêtre de jeu
LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = (LARGEUR_ECRAN*0.8)

ecran = pygame.display.set_mode((LARGEUR_ECRAN,HAUTEUR_ECRAN))
pygame.display.set_caption('TEST')


class personnage(pygame.sprite.Sprite):
    def __init__(self):


# Ajouter une image dans la fenêtre en fonction des coordonnées x,y
x = 200
y = 200
echelle = 2
image = pygame.image.load() #ajouter le lien de l'image dans les ()
# Modifier l'échelle de l'image ex : augmenter taille du personnage
image = pygame.transform.scale((image, image.get_width()*echelle), (image, image.get_height * echelle))
# rectangle = image.get_rect()
# rectangle.center = x,y

# Génerer la fenêtre de jeu
run = True
while run:
    # ecran.blit(imge,rectangle)

    for action in pygame.action.get():
        # Quitter le jeu
        if action.type == pygame.quit():
            run = False
    pygame.display.update()
pygame.quit()