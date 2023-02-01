import pygame

LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = (LARGEUR_ECRAN*0.8)

ecran = pygame.display.set_mode((LARGEUR_ECRAN,HAUTEUR_ECRAN))

class personnage(pygame.sprite.Sprite):

    def __init__(self,char_type, x, y, echelle, vitesse):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.vitesse = vitesse
        self.direction = 1
        self.flip = False
        image = pygame.image.load(f'Ressources/Images/{self.char_type}/0.png')
        # Modifier l'échelle de l'image ex : augmenter taille du personnage
        self.image = pygame.transform.scale(image, (int(image.get_width() * echelle), int(image.get_height() * echelle)))
        self.rectangle = self.image.get_rect()
        self.rectangle.center = (x,y)

    def bouger(self, bouger_droite, bouger_gauche):
        px = 0
        py = 0
        if bouger_droite:
            px += self.vitesse
            self.flip = False
            self.direction = 1
        if bouger_gauche:
            px -= self.vitesse
            self.flip = True
            self.direction = -1

        self.rectangle.x += px
        self.rectangle.y += py


    def affiche(self):
        ecran.blit(pygame.transform.flip(self.image, self.flip, False), self.rectangle)