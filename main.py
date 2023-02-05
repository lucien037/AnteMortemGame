#Importation des différents modules necessaire au bon fonctionnement du jeu
import pygame
import os
import random
import csv
import cv2
import numpy as np
import pyglet
from pygame.locals import *
from pygame import mixer
import button

pygame.init()

#Largeur et Hauteur de la fenêtre de jeu
LARGEUR_ECRAN = 800
HAUTEUR_ECRAN = int(LARGEUR_ECRAN * 0.8)

#Lancement de la fenêtre de jeu
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
pygame.display.set_caption('AnteMortem')

#Choix des FPS (Image Par Seconde)
clock = pygame.time.Clock()
FPS = 60

#Création des variables de jeu
GRAVITE = 0.75
DEFILEMENT = 200
LIGNE = 16
COLONNE = 150
TAILLE_BOX = HAUTEUR_ECRAN // LIGNE
TYPES_BOX = 21
NIVEAU_MAX = 7
ecran_defilement = 0
defilement_fond = 0
Niveau = 1
debut_jeu = False
Intro = False

#definir les variables du joueur
bouger_gauche = False
bouger_droite = False
tir = False
grenade = False
jet_grenade = False

#chargement des sons
saut_fx = pygame.mixer.Sound('Ressources/Bruitage/saut.mp3')
saut_fx.set_volume(0.5)
tir_fx = pygame.mixer.Sound('Ressources/Bruitage/shot.mp3')
tir_fx.set_volume(0.3)
explosion_fx = pygame.mixer.Sound('Ressources/Bruitage/grenade.wav')
explosion_fx.set_volume(0.8)
mort_fx = pygame.mixer.Sound('Ressources/Bruitage/mort.mp3')
mort_fx.set_volume(0.8)

#chargement image
bouton_jouer = pygame.image.load('Ressources/Bouton/jouer_btn.png').convert_alpha()
bouton_quitter = pygame.image.load('Ressources/Bouton/quitter_btn.png').convert_alpha()
bouton_rejouer = pygame.image.load('Ressources/Bouton/rejouer_btn.png').convert_alpha()

img_debut = pygame.image.load('Ressources/Images/start.png').convert_alpha()
image_debut = pygame.transform.scale(img_debut, (int(img_debut.get_width() * 0.8), int(img_debut.get_height() * 0.8)))
arbre1_img = pygame.image.load('Ressources/Fond/arbre1.png').convert_alpha()
arbre2_img = pygame.image.load('Ressources/Fond/arbre2.png').convert_alpha()
montagne_img = pygame.image.load('Ressources/Fond/montagne.png').convert_alpha()
ciel_img = pygame.image.load('Ressources/Fond/ciel.png').convert_alpha()

#chargement video
video = cv2.VideoCapture("Ressources/Video_Son/cinematique.mp4")
x = ecran.get_size()
fond = pygame.image.load("Ressources/Images/start.png")
fond1 = pygame.transform.scale(fond, (x)) # (1920, 1080))


#mettre tout les blocs dans une listes
img_list = []
for x in range(TYPES_BOX):
	img = pygame.image.load(f'Ressources/Blocs/{x}.png')
	img = pygame.transform.scale(img, (TAILLE_BOX, TAILLE_BOX))
	img_list.append(img)
#balle
balle_img = pygame.image.load('Ressources/Images/balle.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('Ressources/Images/grenade.png').convert_alpha()
#box(vie / balle / grenade)
box_vie_img = pygame.image.load('Ressources/Blocs/19.png').convert_alpha()
box_balle_img = pygame.image.load('Ressources/Blocs/17.png').convert_alpha()
box_grenade_img = pygame.image.load('Ressources/Blocs/18.png').convert_alpha()
item_boxes = {
	'Vie'	: box_vie_img,
	'balle'		: box_balle_img,
	'Grenade'	: box_grenade_img
}


#definition des différentes couleurs dans le jeu
ROUGE = (255, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 255, 0)
NOIR = (0, 0, 0)
GRIS = (30, 29, 30)

#définition de la police d'écriture dans le jeu
Police = pygame.font.SysFont('Futura', 30)


def choix_texte(text, Police, text_col, x, y):
	img = Police.render(text, True, text_col)
	ecran.blit(img, (x, y))


def choix_element_fond():
	largeur = ciel_img.get_width()
	for x in range(5):
		ecran.blit(ciel_img, ((x * largeur) - defilement_fond * 0.5,0))
		ecran.blit(montagne_img, ((x * largeur) - defilement_fond * 0.6, HAUTEUR_ECRAN- montagne_img.get_height() - 300))
		ecran.blit(arbre1_img, ((x * largeur) - defilement_fond * 0.7, HAUTEUR_ECRAN- arbre1_img.get_height() - 150))
		ecran.blit(arbre2_img, ((x * largeur) - defilement_fond * 0.7, HAUTEUR_ECRAN- arbre2_img.get_height()))

#Réinitialisation du niveau
def reset_Niveau():
		ennemi_groupe.empty()
		bullet_group.empty()
		grenade_group.empty()
		explosion_group.empty()
		item_box_group.empty()
		decoration_group.empty()
		water_group.empty()
		exit_group.empty()

		data = []
		for row in range(LIGNE):
			r = [-1] * COLONNE
			data.append(r)
		return data

#création de notre classe personnage
class Personnage(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, echelle, vitesse, balle, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.en_vie = True
		self.char_type = char_type
		self.vitesse = vitesse
		self.balle = balle
		self.start_balle = balle
		self.tir_delais = 0
		self.grenades = grenades
		self.Vie = 100
		self.max_Vie = self.Vie
		self.direction = 1
		self.vel_y = 0
		self.saut = False
		self.dans_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()

		#variable pour les ia
		self.bouger_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		
		#chargement de toutes les images des personnages
		animation_types = ['inactif','courrir','saut','mort','accroupi']
		for animation in animation_types:
			#remise à 0 de la liste
			temp_list = []
			#compte le nombre de fichier dans le dossier
			nombre_d_image = len(os.listdir(f'Ressources/Images/Perso/{self.char_type}/{animation}'))
			for i in range(nombre_d_image):
				img = pygame.image.load(f'Ressources/Images/Perso/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * echelle), int(img.get_height() * echelle)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.largeur = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_envie()
		#update cooldown
		if self.tir_delais > 0:
			self.tir_delais -= 1


	def bouger(self, bouger_gauche, bouger_droite):
		#réininitialiser les mouvements variables
		ecran_defilement = 0
		dx = 0
		dy = 0

		#assign mouvement variables if moving left or right
		if bouger_gauche:
			dx = -self.vitesse
			self.flip = True
			self.direction = -1
		if bouger_droite:
			dx = self.vitesse
			self.flip = False
			self.direction = 1

		#saut
		if self.saut == True and self.dans_air == False:
			self.vel_y = -11
			self.saut = False
			self.dans_air = True

		#application de la gravité
		self.vel_y += GRAVITE
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#vérification des collisions
		for tile in map_monde.obstacle_list:
			#vérification des collisions horizontales
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.largeur, self.height):
				dx = 0
				if self.char_type == 1 :
					self.direction *= -1
					self.bouger_counter = 0
			#vérification des collisions verticales
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.largeur, self.height):
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.dans_air = False
					dy = tile[1].top - self.rect.bottom

		if pygame.sprite.spritecollide(self, water_group, False):
			self.Vie = 0
		#vérification des collisions
		Niveau_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			Niveau_complete = True

		if self.rect.bottom > HAUTEUR_ECRAN:
			self.Vie = 0

		if self.char_type == 0:
			if self.rect.left + dx < 0 or self.rect.right + dx > LARGEUR_ECRAN:
				dx = 0
		#mise à jour des positions
		self.rect.x += dx
		self.rect.y += dy

		if self.char_type == 0:
			if (self.rect.right > LARGEUR_ECRAN - DEFILEMENT and defilement_fond < (map_monde.Niveau_length * TAILLE_BOX) - LARGEUR_ECRAN)\
				 or (self.rect.left < DEFILEMENT and defilement_fond > abs(dx)):
				self.rect.x -= dx
				ecran_defilement -= dx

		return ecran_defilement, Niveau_complete

	def tir(self):
		if self.tir_delais == 0 and self.balle > 0:
			self.tir_delais = 20
			bullet = Balle(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduction du nombre de balle à chaque tir 
			self.balle -= 1
			tir_fx.play()


	def ia(self):
		if self.en_vie and personnage_principal.en_vie:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			#check if the ai in near the personnage_principal
			if self.vision.colliderect(personnage_principal.rect):
				#stop running and face the personnage_principal
				self.update_action(0)#0: idle
				#tir
				self.tir()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_bouger_droite = True
					else:
						ai_bouger_droite = False
					ai_bouger_gauche = not ai_bouger_droite
					self.bouger(ai_bouger_gauche, ai_bouger_droite)
					self.update_action(1)#1: animation de courrir
					self.bouger_counter += 1
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.bouger_counter > TAILLE_BOX:
						self.direction *= -1
						self.bouger_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False
		self.rect.x += ecran_defilement





	def update_animation(self):
		#mise à jour des animations
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0


	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_envie(self):
		if self.Vie <= 0:
			self.Vie = 0
			self.vitesse = 0
			self.en_vie = False
			self.update_action(3)


	def dessin(self):
		ecran.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Monde():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.Niveau_length = len(data[0])
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TAILLE_BOX
					img_rect.y = y * TAILLE_BOX
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Eau(img, x * TAILLE_BOX, y * TAILLE_BOX)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TAILLE_BOX, y * TAILLE_BOX)
						decoration_group.add(decoration)
					elif tile == 15:#création de notre personnage
						personnage_principal = Personnage(0, x * TAILLE_BOX, y * TAILLE_BOX, 1.65, 5, 20, 5)
						Vie_bar = VieBar(10, 10, personnage_principal.Vie, personnage_principal.Vie)
					elif tile == 16:#création de nos ennemis
						ennemi = Personnage(1, x * TAILLE_BOX, y * TAILLE_BOX, 1.65, 2, 20, 0)
						ennemi_groupe.add(ennemi)
					elif tile == 17:#création box de balle
						item_box = Box_ITEM('balle', x * TAILLE_BOX, y * TAILLE_BOX)
						item_box_group.add(item_box)
					elif tile == 18:#création box de grenade 
						item_box = Box_ITEM('Grenade', x * TAILLE_BOX, y * TAILLE_BOX)
						item_box_group.add(item_box)
					elif tile == 19:#création box de vie 
						item_box = Box_ITEM('Vie', x * TAILLE_BOX, y * TAILLE_BOX)
						item_box_group.add(item_box)
					elif tile == 20:#création exit
						exit = Quitter(img, x * TAILLE_BOX, y * TAILLE_BOX)
						exit_group.add(exit)

		return personnage_principal, Vie_bar


	def dessin(self):
		for tile in self.obstacle_list:
			tile[1][0] += ecran_defilement
			ecran.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TAILLE_BOX // 2, y + (TAILLE_BOX - self.image.get_height()))
	def update(self):
		self.rect.x += ecran_defilement

class Eau(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TAILLE_BOX // 2, y + (TAILLE_BOX - self.image.get_height()))
	def update(self):
		self.rect.x += ecran_defilement

class Quitter(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TAILLE_BOX // 2, y + (TAILLE_BOX - self.image.get_height()))
	def update(self):
		self.rect.x += ecran_defilement


class Box_ITEM(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TAILLE_BOX // 2, y + (TAILLE_BOX - self.image.get_height()))

	def update(self):
		self.rect.x += ecran_defilement
		#vérifie sur le personnage à recuperer la box
		if pygame.sprite.collide_rect(self, personnage_principal):
			#vérifie quel type de box c'était
			if self.item_type == 'Vie':
				personnage_principal.Vie += 25
				if personnage_principal.Vie > personnage_principal.max_Vie:
					personnage_principal.Vie = personnage_principal.max_Vie
			elif self.item_type == 'balle':
				personnage_principal.balle += 15
			elif self.item_type == 'Grenade':
				personnage_principal.grenades += 3
			#delete the item box
			self.kill()


class VieBar():
	def __init__(self, x, y, Vie, max_Vie):
		self.x = x
		self.y = y
		self.Vie = Vie
		self.max_Vie = max_Vie

	def dessin(self, Vie):
		#maj de la vie
		self.Vie = Vie
		#calcul du ratio pour pouvoir faire la barre de vie 
		ratio = self.Vie / self.max_Vie
		pygame.draw.rect(ecran, NOIR, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(ecran, ROUGE, (self.x, self.y, 150, 20))
		pygame.draw.rect(ecran, VERT, (self.x, self.y, 150 * ratio, 20))


class Balle(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.vitesse = 10
		self.image = balle_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#mouvement de la balle
		self.rect.x += (self.direction * self.vitesse) + ecran_defilement
		#vérifie que la balle est en dehors de l'écran
		if self.rect.right < 0 or self.rect.left > LARGEUR_ECRAN:
			self.kill()
		for tile in map_monde.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#vérifie si la balle touche un personnage
		if pygame.sprite.spritecollide(personnage_principal, bullet_group, False):
			if personnage_principal.en_vie:
				personnage_principal.Vie -= 5
				self.kill()
		for ennemi in ennemi_groupe:
			if pygame.sprite.spritecollide(ennemi, bullet_group, False):
				if ennemi.en_vie:
					ennemi.Vie -= 25
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.vitesse = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.largeur = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITE
		dx = self.direction * self.vitesse
		dy = self.vel_y

		#vérifie les collision avec les obstacles 
		for tile in map_monde.obstacle_list:
			#vérifie les collisions avec les murs
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.largeur, self.height):
				self.direction *= -1
				dx = self.direction * self.vitesse
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.largeur, self.height):
				self.vitesse = 0
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		#maj de la position de la grenade
		self.rect.x += dx + ecran_defilement
		self.rect.y += dy 

		#timer pour l'explosion de la grenade
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			#mise en place des dégâts
			if abs(self.rect.centerx - personnage_principal.rect.centerx) < TAILLE_BOX * 2 and \
				abs(self.rect.centery - personnage_principal.rect.centery) < TAILLE_BOX * 2:
				personnage_principal.Vie -= 50
			for ennemi in ennemi_groupe:
				if abs(self.rect.centerx - ennemi.rect.centerx) < TAILLE_BOX * 2 and \
					abs(self.rect.centery - ennemi.rect.centery) < TAILLE_BOX * 2:
					ennemi.Vie -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, echelle):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for i in range(7):
			img = pygame.image.load(f'Ressources/Images/Explosion/{i}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * echelle), int(img.get_height() * echelle)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		self.rect.x += ecran_defilement
		EXPLOSION_vitesse = 4
		#animation de l'explosion 
		self.counter += 1

		if self.counter >= EXPLOSION_vitesse:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]

class ecranFade():
	def __init__(self, direction, colour, vitesse):
		self.direction = direction
		self.colour = colour
		self.vitesse = vitesse
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.vitesse
		if self.direction == 1:
			pygame.draw.rect(ecran, self.colour, (0 - self.fade_counter, 0, LARGEUR_ECRAN // 2, HAUTEUR_ECRAN))
			pygame.draw.rect(ecran, self.colour, (LARGEUR_ECRAN // 2 + self.fade_counter, 0, LARGEUR_ECRAN, HAUTEUR_ECRAN))
			pygame.draw.rect(ecran, self.colour, (0, 0 - self.fade_counter, LARGEUR_ECRAN, HAUTEUR_ECRAN // 2))
			pygame.draw.rect(ecran, self.colour, (0, HAUTEUR_ECRAN // 2 +self.fade_counter, LARGEUR_ECRAN, HAUTEUR_ECRAN))
		if self.direction == 2:
			pygame.draw.rect(ecran, self.colour, (0, 0, LARGEUR_ECRAN, 0 + self.fade_counter))
		if self.fade_counter >= LARGEUR_ECRAN:
			fade_complete = True

		return fade_complete

#création des animations de transition d'écran
intro_fade = ecranFade(1, NOIR, 4)
death_fade = ecranFade(2, GRIS, 4)

start_button = button.Button(LARGEUR_ECRAN // 2 - 280, HAUTEUR_ECRAN // 2 + 100, bouton_jouer,0.8)
exit_button = button.Button(LARGEUR_ECRAN // 2 + 80, HAUTEUR_ECRAN // 2 + 100, bouton_quitter,0.8)
restart_button = button.Button(LARGEUR_ECRAN // 2 - 110, HAUTEUR_ECRAN // 2 - 50, bouton_rejouer,1)

#création des groupes de sprite
ennemi_groupe = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()




map_monde_data = []
for row in range(LIGNE):
	r = [-1] * COLONNE
	map_monde_data.append(r)
#chargement des données du niveau en cour
with open(f'Niveau{Niveau}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			map_monde_data[x][y] = int(tile)
map_monde = Monde()
personnage_principal, Vie_bar = map_monde.process_data(map_monde_data)



run = True
while run:
    	
	clock.tick(FPS)

	if debut_jeu == False:
		#cinématique du début
		ecran.fill(GRIS)
		son = 'Ressources/Video_Son/son_cinematique.mp3'
		play = pyglet.media.personnage_principal()
		source = pyglet.media.StreamingSource()
		MediaLoad = pyglet.media.load(son)
		play.queue(MediaLoad)
		play.play()
		while video.isOpened():
			# Lire le prochain cadre de la vidéo
			ret, frame = video.read()
			# Si le cadre est valide
			if ret:
				frame = cv2.flip(frame, 1)
				# Convertir l'image de OpenCV en format Pygame
				frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				frame = np.rot90(frame)
				frame = pygame.surfarray.make_surface(frame)
				# Afficher l'image dans la fenêtre de Pygame
				ecran.blit(frame, (40, 100))
				pygame.display.update()

				if cv2.waitKey(22) & 0xFF == ord('q'):
					break
			else:
				play.pause()
				ecran.blit(image_debut, (0,0))
				if start_button.draw(ecran):
					debut_jeu = True
					Intro = True
					play.pause()
				if exit_button.draw(ecran):
					run = False
					play.pause()
				pygame.display.update()
				break


		
	else :
		
		#maj fond
		choix_element_fond()
		#dessin map_monde map
		map_monde.dessin()
		#affiche la vie du personnage
		Vie_bar.dessin(personnage_principal.Vie)
		#affiche les balles
		choix_texte('balle : ', Police, BLANC, 10, 35)
		for x in range(personnage_principal.balle):
			ecran.blit(balle_img, (90 + (x * 10), 40))
		#affiches les grenades
		choix_texte('Grenade : ', Police, BLANC, 10, 60)
		for x in range(personnage_principal.grenades):
			ecran.blit(grenade_img, (135 + (x * 15), 60))


		personnage_principal.update()
		personnage_principal.dessin()

		for ennemi in ennemi_groupe:
			ennemi.ia()
			ennemi.update()
			ennemi.dessin()

		#maj et dessin des différents groupes établit au dessus
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(ecran)
		grenade_group.draw(ecran)
		explosion_group.draw(ecran)
		item_box_group.draw(ecran)
		decoration_group.draw(ecran)
		water_group.draw(ecran)
		exit_group.draw(ecran)

		if Intro == True:

			if intro_fade.fade():
				Intro = False
				intro_fade.fade_counter = 0

			pygame.mixer.music.load(f'Ressources/Video_son/map/5.mp3')
			pygame.mixer.music.set_volume(0.3)
			pygame.mixer.music.play(-1, 0.0, 5000)
		if personnage_principal.en_vie:
			#tir
			if tir:
				personnage_principal.tir()
			#lancer de grenade
			elif grenade and jet_grenade == False and personnage_principal.grenades > 0:
				grenade = Grenade(personnage_principal.rect.centerx + (0.5 * personnage_principal.rect.size[0] * personnage_principal.direction),\
							personnage_principal.rect.top, personnage_principal.direction)
				grenade_group.add(grenade)
				personnage_principal.grenades -= 1
				jet_grenade = True
			if personnage_principal.dans_air:
				personnage_principal.update_action(2)#2: saut
			elif bouger_gauche or bouger_droite:
				personnage_principal.update_action(1)#1: courrir
			else:
				personnage_principal.update_action(0)#0: statique
			ecran_defilement, Niveau_complete = personnage_principal.bouger(bouger_gauche, bouger_droite)
			defilement_fond -= ecran_defilement

			if Niveau_complete:
				pygame.mixer.music.stop()
				Niveau += 1
				indicateur = Niveau - 1
				defilement_fond = 0
				ecran.fill(NOIR)
				video = cv2.VideoCapture(f"Ressources/Video_Son/cinematique_m{indicateur}.mp4")

				x = ecran.get_size()
				fond = pygame.image.load("Ressources/Images/start.png")
				fond1 = pygame.transform.scale(fond, (x)) # (1920, 1080))

				son = (f'Ressources/Video_Son/audio_m{indicateur}.mp3')
				personnage_principal = pyglet.media.personnage_principal()
				source = pyglet.media.StreamingSource()
				MediaLoad = pyglet.media.load(son)
				personnage_principal.queue(MediaLoad)
				personnage_principal.play()
				def text_objects(text, Police):
					textSurface = Police.render(text, True, BLANC)
					return textSurface, textSurface.get_rect()

				def button(msg,x,y,w,h,ic,ac,action=None):
					mouse = pygame.mouse.get_pos()
					click = pygame.mouse.get_pressed()

					if x+w > mouse[0] > x and y+h > mouse[1] > y:
						pygame.draw.rect(ecran, ac,(x,y,w,h))
						if click[0] == 1 and action != None:
							action()
					else:
						pygame.draw.rect(ecran, ic,(x,y,w,h))
					smallText = pygame.Police.SysPolice("comicsansms",20)
					textSurf, textRect = text_objects(msg, smallText)
					textRect.center = ( (x+(w/2)), (y+(h/2)) )
					ecran.blit(textSurf, textRect)

				def quitgame():
					pygame.quit()
					quit()

				def on_dessin():
					if personnage_principal.source and personnage_principal.source.video_format:
						personnage_principal.get_texture().blit(50,50)

				# Boucle tant que la vidéo est en cours de lecture
				while video.isOpened():
					# Lire le prochain cadre de la vidéo
					ret, frame = video.read()
					# Si le cadre est valide
					if ret:
						frame = cv2.flip(frame, 1)
						# Convertir l'image de OpenCV en format Pygame
						frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
						frame = np.rot90(frame)
						frame = pygame.surfarray.make_surface(frame)
						# Afficher l'image dans la fenêtre de Pygame
						ecran.blit(frame, (40,100))

						pygame.display.update()

						if cv2.waitKey(25) & 0xFF == ord('q'):
							break
					else:
						# Si la vidéo est terminée, sortir de la boucle
						# ecran.blit(fond1, (0, 0))
						# button("EXIT", 315, 175, 100, 50, NOIR, BLANC, quitgame)
						pygame.display.update()

						break

				map_monde_data = reset_Niveau()
				if Niveau <= NIVEAU_MAX:
					with open(f'Niveau{Niveau}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								map_monde_data[x][y] = int(tile)
					map_monde = Monde()
					personnage_principal, Vie_bar = map_monde.process_data(map_monde_data)
		else:
			ecran_defilement = 0
			if death_fade.fade():
				if restart_button.draw(ecran):
					death_fade.fade_counter = 0
					Intro = True
					defilement_fond = 0
					map_monde_data = reset_Niveau()
					with open(f'Niveau{Niveau}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								map_monde_data[x][y] = int(tile)
					map_monde = Monde()
					personnage_principal, Vie_bar = map_monde.process_data(map_monde_data)

	for event in pygame.event.get():
		#quitter le jeu
		if event.type == pygame.QUIT:
			run = False
		#touche pour les déplacements presser
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				bouger_gauche = True
			if event.key == pygame.K_d:
				bouger_droite = True
			if event.key == pygame.K_x:
				tir = True
			if event.key == pygame.K_a:
				grenade = True
			if event.key == pygame.K_SPACE and personnage_principal.en_vie:
				personnage_principal.saut = True
				saut_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False


		#touche pour les déplacement une fois relacher
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_q:
				bouger_gauche = False
			if event.key == pygame.K_d:
				bouger_droite = False
			if event.key == pygame.K_x:
				tir = False
			if event.key == pygame.K_a:
				grenade = False
				jet_grenade = False


	pygame.display.update()
pyglet.app.run()
video.release()
pygame.quit()
