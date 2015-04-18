#!/usr/bin/python
# coding=UTF-8

from framework import *
import math, random

@ScreenClass('STARTUP')
class StartupScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.addLayer(StaticBackgroundLauer('rc/256x256bg.png','fill'))

		GAME_CONSOLE.write('Startup screen created.')

	def on_key_press(self,key,mod):
		GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')

@ScreenClass('GAME')
class GameScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.game = MyGame(pbar,slbl,avap)
		self.game.unpause( )
		self.camera = Camera( )

		self.addLayer(GameWorldLayer(self.game,self.camera))

		GAME_CONSOLE.write('Game screen created.')

	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

	def on_mouse_scroll(self,x,y,sx,sy):
		self.camera.scale *= 2 ** (sy*0.02)

	def on_key_press(self,key,mod):
		GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')

	def on_mouse_press(self,x,y,button,modifiers):
		pass

class MineCat(AnimatedGameEntity):
	# цифры из предыдущего проекта
	ANIMATION_LIST = AnimationList({
			'Stand':[
				{'img':'rc/img/MineCat_Stand_256x64.png','t':0.1,'anchor':(22,58),'rect':(96*0,0,96,96)},
				{'img':'rc/img/MineCat_Stand_256x64.png','t':0.1,'anchor':(22,58),'rect':(96*1,0,96,96)},
				{'img':'rc/img/MineCat_Stand_256x64.png','t':0.1,'anchor':(22,58),'rect':(96*2,0,96,96)},
				{'img':'rc/img/MineCat_Stand_256x64.png','t':0.1,'anchor':(22,58),'rect':(96*3,0,96,96)}
			],
			'Run':[
				{'img':'rc/img/MineCat_Run_256x64.png.png','t':0.07,'anchor':(22,58),'rect':(96*0,0,96,96)},
				{'img':'rc/img/MineCat_Run_256x64.png.png','t':0.12,'anchor':(22,58),'rect':(96*1,0,96,96)},
				{'img':'rc/img/MineCat_Run_256x64.png.png','t':0.10,'anchor':(22,58),'rect':(96*2,0,96,96)},
				{'img':'rc/img/MineCat_Run_256x64.png.png','t':0.08,'anchor':(22,58),'rect':(96*3,0,96,96)}
			]
		}
	)
	def __init__(self,sx,sy,id):
		AnimatedGameEntity.__init__(self, MineCat.ANIMATION_LIST)
		self.id = id
		self.x = sx
		self.y = sy
		self.vx = 1.0
		self.vy = 0.0
		self.angle = 0
		self.angVelocity = 0
		self.timer = 30
		self.scale = 1
		#установка начальной скорости типа
		self.setup_task()

	def update(self,dt):
		self.timer -= dt
		k=400
		self.affectAngleVelocity(dt)	
		self.x += self.vx*dt*k
		self.y += self.vy*dt*k
		self.end_update_coordinates()

	def spawn(self):
		AnimatedGameEntity.spawn(self)
		self.set_animation('Run')

	def velocity(self):
		return math.sqrt(self.vx*self.vx + self.vy*self.vY)

	def setVelocity(slef, k = 1):
		self.vx = k*self.vx
		self.vy = k*self.vy

	def setup_task(self):
		#нормальное распределение М[],сигма
		self.angVelocity = (random.normalvariate(0,60))
		self.angVelocityRad = self.angVelocity / 180 * math.pi
		self.timer = random.random()*3+0.5

	def affectAngleVelocity(self, dt):
		dr = self.angVelocity * dt
		self.rotation += -dr
		drr = (dr / 180) * math.pi
		self.vx, self.vy =\
		self.vx * math.cos(drr) - self.vy * math.sin(drr),\
		self.vx * math.sin(drr) + self.vy * math.cos(drr)
 
	#возвращает расстояние от текущей сущности до указанной
	def distance(self, entity):
		dx = ent.x - self.x
		dy = ent.y - self.y
		return math.sqrt(dx*dx + dy*dy)-entity.radius

	#действие столкновения
	def on_collision(self, ent, dx, dy):
		pass
		# elif ent.__class__.__name__ == 'Worm':
		# 	#скалярное проиведение
		# 	scalarMul = self.vx*ent.vx + self.vy*ent.vy
		# 	self.vx = self.vx - 2 * dx * scalarMul
		# 	self.vy = self.vy - 2 * dy * scalarMul
		# 	ent.vx = ent.vx - 2 * dx * scalarMul
		# 	ent.vy = ent.vy - 2 * dy * scalarMul
		# 	self.lastTurn = 0
		# 	ent.lastTurn = 0

	def eat(self):
		#анимка, звук поедания яблока или надо будет переопределить для каждого червя
		pass


class MyGame(Game):
	def __init__(self,progress_bar,text_bar,apples_bar):
		Game.__init__(self)
		self.init_entities( )

	def init_entities(self):
		pass

