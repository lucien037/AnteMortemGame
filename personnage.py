import os

import pygame

gravite = 0.25

LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = (LARGEUR_ECRAN*0.8)

ecran = pygame.display.set_mode((LARGEUR_ECRAN,HAUTEUR_ECRAN))

class personnage(pygame.sprite.Sprite):

    def __init__(self,char_type, x, y, echelle, vitesse):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.vitesse = vitesse
        self.direction = 1
        self.vel_y = 0
        self.saut = False
        self.dans_air = True
        self.flip = False
        self.animation_list = []
        self.image_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        type_animation = ['inactif','courrir','saut','mort','accroupi']
        for animation in type_animation:

            temp_list = []
            nb_images = len(os.listdir(f'Ressources/Images/Perso/{self.char_type}/{animation}'))
            for i in range(nb_images):
                # Modifier l'image l'échelle de l'image ex : augmenter taille du personnage
                image = pygame.image.load(f'Ressources/Images/Perso/{self.char_type}/{animation}/{i}.png')
                image = pygame.transform.scale(image, (int(image.get_width() * echelle), int(image.get_height() * echelle)))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.image_index]
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
        if self.saut and self.dans_air == False :
            self.vel_y = -7
            self.saut = False
            self.dans_air = True

        self.vel_y += gravite
        if self.vel_y > 10:
            self.vel_y
        py += self.vel_y

        if self.rectangle.bottom +py > 600:
            py = 600 -self.rectangle.bottom
            self.dans_air = False

        self.rectangle.x += px
        self.rectangle.y += py

    def animation(self):
        animation_refresh = 100
        self.image = self.animation_list[self.action][self.image_index]
        if pygame.time.get_ticks() - self.update_time > animation_refresh:
            self.update_time = pygame.time.get_ticks()
            self.image_index += 1
        if self.image_index >= len(self.animation_list[self.action]):
            self.image_index = 0

    def new_action(self, nouvelle_action: int):
        if nouvelle_action != self.action:
            self.action = nouvelle_action
            self.image_index = 0
            self.update_time = pygame.time.get_ticks()


    def affiche(self):
        ecran.blit(pygame.transform.flip(self.image, self.flip, False), self.rectangle)