#!/usr/bin/python
# coding=UTF-8

PLAYER_SPAWN = {'x': 0, 'y': 0}

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

@ScreenClass('STARTUP')
@ScreenClass('GAME')
class GameScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.game = MyGame( )
		self.game.unpause( )
		self.camera = Camera( )

		self.camera.focus_x = 0
		self.camera.focus_y = 0

		self.addLayer(StaticBackgroundLauer('rc/img/1Kx1Kbg.png','scale'))

		self.addLayer(GameWorldLayer(self.game,self.camera))

		GAME_CONSOLE.write('Game screen created.')


	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

		self.camera.scale = 0.5 * min(float(width) / float(MyGame.WORLD_WIDTH),float(height) / float(MyGame.WORLD_HEIGHT))

	def on_mouse_scroll(self,x,y,sx,sy):
		# self.camera.scale *= 2 ** (sy*0.02)
		pass

	def on_key_press(self,key,mod):
		GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		self.game.handle_key_press(key)

	def on_key_release(self,key,mod):
		GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		self.game.handle_key_release(key)

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
				{'img':'rc/img/MineCat_Run_256x64.png','t':0.07,'anchor':(22,58),'rect':(96*0,0,96,96)},
				{'img':'rc/img/MineCat_Run_256x64.png','t':0.12,'anchor':(22,58),'rect':(96*1,0,96,96)},
				{'img':'rc/img/MineCat_Run_256x64.png','t':0.10,'anchor':(22,58),'rect':(96*2,0,96,96)},
				{'img':'rc/img/MineCat_Run_256x64.png','t':0.08,'anchor':(22,58),'rect':(96*3,0,96,96)}
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
	LIMIT_LEFT = -400
	LIMIT_RIGHT = 400
	LIMIT_TOP = 400
	LIMIT_BOTTOM = -400
	WORLD_WIDTH = LIMIT_RIGHT - LIMIT_LEFT
	WORLD_HEIGHT = LIMIT_TOP - LIMIT_BOTTOM
	def __init__(self):
		Game.__init__(self)

		self.world_space = LimitedWorldSpace(MyGame.LIMIT_LEFT,MyGame.LIMIT_RIGHT,MyGame.LIMIT_TOP,MyGame.LIMIT_BOTTOM)

		self.init_entities( )

	def init_entities(self):
		self.player = Player( )
		self.addEntity(self.player)
		self.addEntity(MineCat(50,50,1))

	def handle_key_press(self,key):
		if key == KEY.UP:
			self.player.start_move(1)
		if key == KEY.DOWN:
			self.player.start_move(-1)
		if key == KEY.LEFT:
			self.player.start_turn(-1)
		if key == KEY.RIGHT:
			self.player.start_turn(1)

	def handle_key_release(self,key):
		if key in (KEY.LEFT,KEY.RIGHT):
			self.player.stop_turn()
		if key in (KEY.UP,KEY.DOWN):
			self.player.stop_move()

class Player(AnimatedGameEntity):
	ANIMATION_LIST = AnimationList({
		'idle':[
			{'img':'rc/img/64x64fg.png','anchor':'center','rect':(0,0,64,64)}
		]
	})

	def __init__(self):
		AnimatedGameEntity.__init__(self,Player.ANIMATION_LIST)
		self.set_animation('idle')
		self.x = PLAYER_SPAWN['x']
		self.y = PLAYER_SPAWN['y']
		self.update_direction( )

		self.vx = 0.0
		self.vy = 0.0

		self.dirx = 0.0
		self.diry = -1.0

		self.va = 0.0
		self.vm = 0.0

	def start_move(self,d):
		self.vm = d * 300.0

	def start_turn(self,d):
		self.va = d * 80.0

	def stop_move(self):
		self.vm = 0.0

	def stop_turn(self):
		self.va = 0.0

	def update_direction(self):
		rrad = (self.rotation / 180.0) * math.pi
		self.dirx,self.diry = math.sin(rrad),math.cos(rrad)
		# print 'UD:',str(self.rotation),str(self.dirx),str(self.diry)

	def update(self,dt):
		self.rotation += self.va * dt
		self.update_direction( )

		self.x += self.dirx * self.vm * dt
		self.y += self.diry * self.vm * dt
		print str(self.x),str(self.y),str(self.vx),str(self.vy)

		self.end_update_coordinates( )
