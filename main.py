import os
import pygame


gravite = 0.25
LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = (LARGEUR_ECRAN*0.8)
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))

class personnage(pygame.sprite.Sprite):

    def __init__(self,char_type, x, y, echelle, vitesse, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.vitesse = vitesse
        self.ammo = ammo
        self.start_ammo = ammo
        self.delai_tire = 0
        self.grenades = grenades
        self.vie = 100
        self.max_vie = self.vie
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
                image = pygame.image.load(f'Ressources/Images/Perso/{self.char_type}/{animation}/{i}.png').convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width() * echelle), int(image.get_height() * echelle)))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        
    def update(self):
        self.animation()
        self.check_vie()
        if self.delai_tire >0:
            self.delai_tire -=1
        

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

        if self.rect.bottom +py > 600:
            py = 600 - self.rect.bottom
            self.dans_air = False

        self.rect.x += px
        self.rect.y += py

    def shoot(self):
        if self.delai_tire == 0 and self.ammo > 0 :
            self.delai_tire = 20
            munitions = balle(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            groupe_balle.add(munitions)
            self.ammo -= 1


    def animation(self):
        animation_refresh = 100
        self.image = self.animation_list[self.action][self.image_index]
        if pygame.time.get_ticks() - self.update_time > animation_refresh:
            self.update_time = pygame.time.get_ticks()
            self.image_index += 1
        if self.image_index >= len(self.animation_list[self.action]):
            if self.action == 3 :
                self.image_index = len(self.animation_list[self.action]) - 1
            else :
                self.image_index = 0

    def new_action(self, nouvelle_action: int):
        if nouvelle_action != self.action:
            self.action = nouvelle_action
            self.image_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_vie(self):
        if self.vie <= 0:
            self.vie = 0
            self.vitesse = 0
            self.alive = False
            self.new_action(3)

    def affiche(self):
        ecran.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

image_balle = pygame.image.load('Ressources/Images/balle.png').convert_alpha()
groupe_balle = pygame.sprite.Group()

class balle(pygame.sprite.Sprite):

    def __init__(self,x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.vitesse = 10
        self.image = image_balle
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.vitesse)
        #check que la balle va pas en dehors de l'écran
        if self.rect.right < 0 or self.rect.left > LARGEUR_ECRAN:
            self.kill()
        #check si il n'y a pas de colision
        if pygame.sprite.spritecollide(perso1,groupe_balle, False):
            if perso1.alive:
                perso1.vie -= 5
                self.kill()
        for enemi in groupe_enemi:
            if pygame.sprite.spritecollide(enemi,groupe_balle, False):
                if enemi.alive:
                    enemi.vie -= 25
                    self.kill()

image_grenade = pygame.image.load('Ressources/Images/grenade.png').convert_alpha()

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -6
        self.vitesse = 7
        self.image = image_grenade
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    def update(self):
        self.vel_y += gravite
        px = self.direction * self.vitesse
        py = self.vel_y
        #collision avec le sol
        if self.rect.bottom +py > 600:
            py = 600 - self.rect.bottom
            self.vitesse = 0
        #collision sur le mur
        if self.rect.left + px < 0 or self.rect.right + px > LARGEUR_ECRAN:
            self.direction *= -1
            px = self.direction * self.vitesse

        self.rect.x += px
        self.rect.y += py 

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            groupe_explosion.add(explosion)
            if abs(self.rect.centerx - perso1.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - perso1.rect.centery) < TILE_SIZE * 2 :
                perso1.vie -= 50
            for enemy in groupe_enemi :
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2 :
                    enemy.vie -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x, y, echelle):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(7):
            image = pygame.image.load(f'Ressources/Images/Explosion/{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width() * echelle), int(image.get_height() * echelle)))
            self.images.append(image)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        vitesse_explosion = 4
        self.counter += 1
        if self.counter >= vitesse_explosion:
            self.counter = 0
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.image_index]

vitesse_image = pygame.time.Clock()
FPS = 144

gravite = 0.25
TILE_SIZE = 40
# mouvement du personnage
bouger_droite = False
bouger_gauche = False
shoot = False
grenade = False
lancer_grenade = False

# Couleurs
couleur_bg = (0,0,0)
couleur_ligne = (255,0,0)

def backgroung():
    ecran.fill(couleur_bg)
    pygame.draw.line(ecran, couleur_ligne,(0, 600),(LARGEUR_ECRAN, 600))

groupe_enemi = pygame.sprite.Group()
groupe_balle = pygame.sprite.Group()
groupe_grenade = pygame.sprite.Group()
groupe_explosion = pygame.sprite.Group()

perso1 = personnage(2, 150, 150, 2, 2, 20, 5)
enemi = personnage(1, 300, 560, 2, 2, 20, 0)
enemi2 = personnage(1, 400, 560, 2, 2, 20, 0)
groupe_enemi.add(enemi)
groupe_enemi.add(enemi2)
# Génerer la fenêtre de jeu
run = True
while run:
    vitesse_image.tick(FPS)

    backgroung()

    perso1.update()
    perso1.affiche()

    for enemi in groupe_enemi:
        enemi.update()
        enemi.affiche()

    groupe_balle.update()
    groupe_grenade.update()
    groupe_explosion.update()

    groupe_balle.draw(ecran)
    groupe_grenade.draw(ecran)
    groupe_explosion.draw(ecran)

    if perso1.alive:
        if shoot:
            perso1.shoot()
        elif grenade and lancer_grenade == False and perso1.grenades > 0:
            grenade = Grenade(perso1.rect.centerx + (0.6 * perso1.rect.size[0] * perso1.direction),\
                            perso1.rect.top, perso1.direction)
            groupe_grenade.add(grenade)
            lancer_grenade = True
            perso1.grenades -= 1
        elif perso1.dans_air:
            perso1.new_action(2)
        elif bouger_gauche or bouger_droite:
            perso1.new_action(1)
        else:
            perso1.new_action(0)
        perso1.bouger(bouger_droite, bouger_gauche)

    for event in pygame.event.get():
        # Quitter le jeu
        if event.type == pygame.QUIT:
            run = False
        # Touches du clavier appuyées
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                bouger_droite = True
            if event.key == pygame.K_q:
                bouger_gauche = True
            if event.key == pygame.K_x:
                shoot = True
            if event.key == pygame.K_a:
                grenade = True
            if event.key == pygame.K_SPACE and perso1.alive:
                perso1.saut = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # Touches clavier non appuyées
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                bouger_droite = False
            if event.key == pygame.K_q:
                bouger_gauche = False
            if event.key == pygame.K_x:
                shoot = False
            if event.key == pygame.K_a:
                grenade = False
                lancer_grenade = False

    pygame.display.update()
pygame.quit()