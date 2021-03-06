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

		# use_tip = GUITextItemLayer(self.game.use_tip_focus.x, self.game.use_tip_focus.y, self.game.use_tip_text)
		# self.addLayer(use_tip)

		tl = TipLayer(self.camera,self.game.player,0,20)
		tl.setText("I'm player")
		self.addLayer(tl)

		GAME_CONSOLE.write('Game screen created.')


	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

		self.camera.scale = 0.5 * min(float(width) / float(MyGame.WORLD_WIDTH),float(height) / float(MyGame.WORLD_HEIGHT))

	def on_mouse_scroll(self,x,y,sx,sy):
		# self.camera.scale *= 2 ** (sy*0.02)
		pass

	def on_key_press(self,key,mod):
		#GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		self.game.handle_key_press(key)

	def on_key_release(self,key,mod):
		#GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		self.game.handle_key_release(key)

	def on_mouse_press(self,x,y,button,modifiers):
		pass

class TipLayer(GUITextItemLayer):
	def __init__(self,camera,entity,mar_x=0,mar_y=0):
		GUITextItemLayer.__init__(self,0.0,0.0)
		self.entity = entity
		self.camera = camera
		self.mar_x,self.mar_y = mar_x,mar_y

	def update_coordinates(self):
		cx,cy = self.entity.x - self.camera.focus_x,self.entity.y - self.camera.focus_y
		cx,cy = cx * self.camera.scale,cy * self.camera.scale
		cx,cy = cx + 0.5 * self.camera.width,cy + 0.5 * self.camera.height
		cx,cy = int(cx),int(cy)
		self.offset_x = cx + self.mar_x
		self.offset_y = cy + self.mar_y
		# self.update_rect( )
		self.on_resize(0,0)

	def draw(self):
		self.update_coordinates( )
		GUITextItemLayer.draw(self)


class Door(SpriteGameEntity):
	SPRITE = 'rc/img/Door.png'
	RADIUS = 50

	def __init__(self,x,y):
		SpriteGameEntity.__init__(self, Door.SPRITE)
		self.x = x
		self.y = y
		self.radius = Door.RADIUS

	def spawn(self):
		SpriteGameEntity.spawn(self)
		self.game.add_entity_of_class('doors',self)

	def on_collision(self, other):
		# обработка столкновений
		pass

class Window(SpriteGameEntity):
	SPRITE = 'rc/img/Window.png'
	RADIUS = 50

	def __init__(self,x,y,cat_limit = 1,id=None):
		self.id = id
		SpriteGameEntity.__init__(self, Window.SPRITE)
		self.x = x
		self.y = y
		self.cat_limit = cat_limit 
		self.cats = []
		self.alive_cats = 0
		self.setup_timer()
		self.radius = Window.RADIUS

	def spawn(self):
		SpriteGameEntity.spawn(self)
		self.game.add_entity_of_class('windows',self)
		self.initial_spawn_cats()
		self.end_update_coordinates()

	def on_collision(self, other):
		# обработка столкновений
		pass

	def update(self, dt):

		if self.timer > 0:
			self.timer -= dt
		elif self.alive_cats < self.cat_limit:
			self.setup_timer()
			self.spawn_cat()
			print 'cat spawned'
		else:
			pass

	def initial_spawn_cats(self):
		for i in range(self.cat_limit):
			cat = MineCat(self.x, self.y,0)
			cat.window = self
			self.cats.append(cat)
			self.game.addEntity(cat)

	def spawn_cat(self):
		for c in self.cats:
			if not c.sprite.visible:
				c.x = self.x
				c.y = self.y
				c.throw()
				break

	def setup_timer(self):
		self.timer = 2
		#self.timer = random.random()*10+20
	

class MineCat(AnimatedGameEntity):
	next_id = 0
	RADIUS = 50
	# цифры из предыдущего проекта
	ANIMATION_LIST = AnimationList({
			'Run':[
				{'img':'rc/img/cat-run.png','t':0.1,'anchor':'center','rect':(128*0,0,128,128)},
				{'img':'rc/img/cat-run.png','t':0.1,'anchor':'center','rect':(128*1,0,128,128)}
			]
		}
	)

	def __init__(self,x,y,id = None):
		AnimatedGameEntity.__init__(self, MineCat.ANIMATION_LIST)
		self.id = id
		self.x = x
		self.y = y
		self.vx = 1.0
		self.vy = 0.0
		self.angle = 0
		self.angVelocity = 0
		self.timer = 30
		self.scale = 1
		self.window = None
		self.radius = MineCat.RADIUS
		#установка начальной скорости типа
		self.setup_task()
		print 'cat created'


	def spawn(self):
		AnimatedGameEntity.spawn(self)
		self.sprite.visible = False

	def update(self,dt):
		if self.sprite.visible:
			self.timer -= dt
			if self.timer <= 0:
				self.setup_task()
			k=400 # скорости коэффициент
			self.affectAngleVelocity(dt)	
			self.x += self.vx*dt*k
			self.y += self.vy*dt*k
			self.end_update_coordinates()

	def throw(self):
		print 'cat spawned'
		self.window.alive_cats += 1
		self.set_animation('Run')
		self.game.add_entity_of_class('cats',self)
		self.sprite.visible = True

	def velocity(self):
		return math.sqrt(self.vx*self.vx + self.vy*self.vY)

	def setVelocity(self, k = 1):
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

	def destroy(self):
		self.sprite.visible = False
		self.game.remove_entity_of_class('cats',self)
		self.window.alive_cats -= 1
		#self.x = 9999
		#self.y = 9999
		#self.window.cats.remove(self)

	def select(self):
		self.game.set_use_tip(self,'Catch the cat!!!')

	def use(self,user):
		user.state = 'carry'
		self.stop()

	def stop(self):
		self.sprite.visible = False
		#self.game.remove_entity_of_class('cats',self)
		#GAME_CONSOLE.write('кот пойман','YRA')

	def run(self):
		self.sprite.visible = True
		#self.game.add_entity_of_class('cats',self)
		#GAME_CONSOLE.write('кот отпущен','yra')

class Selector(SpriteGameEntity):
	SPRITE = 'rc/img/selector.png'

	def __init__(self):
		SpriteGameEntity.__init__(self, Selector.SPRITE)
		self.target = None
		self.scale = 3.0

	def spawn(self):
		SpriteGameEntity.spawn(self)
		self.end_update_coordinates()

	def update(self, dt):
		self.end_update_coordinates()

	def select_around(self,entity,dist):
		if (entity is not None) and ((self.game.player.radius + entity.radius) > dist):
			self.target = entity
		else:
			self.target = self.game.player
		self.x = self.target.x
		self.y = self.target.y
		self.target.select()


def get_level(i):
	return {
		0: {
			'entities': [
				{'class':Player,'kwargs':{'x':0,'y':0}},
				#{'class':MineCat,'kwargs':{'x':100,'y':200,'id':0}},
				{'class':Window,'kwargs':{'x':0,'y':MyGame.LIMIT_BOTTOM,'id':0,'cat_limit':3}}
			]
		}
	}[i];

class MyGame(Game):
	LIMIT_LEFT = -400
	LIMIT_RIGHT = 400
	LIMIT_TOP = 400
	LIMIT_BOTTOM = -400
	WORLD_WIDTH = LIMIT_RIGHT - LIMIT_LEFT
	WORLD_HEIGHT = LIMIT_TOP - LIMIT_BOTTOM
	def __init__(self):
		Game.__init__(self)

		self.containers = {}

		self.world_space = LimitedWorldSpace(MyGame.LIMIT_LEFT,MyGame.LIMIT_RIGHT,MyGame.LIMIT_TOP,MyGame.LIMIT_BOTTOM)

		self.init_entities(get_level(0))
		self.use_tip_focus = None
		self.use_tip_text = None

	def set_use_tip(self, entity, text):
		self.use_tip_focus = entity
		self.use_tip_text = text

	def reset_use_tip(self):
		self.use_tip_focus = None
		self.use_tip_text = None

	def add_entity_of_class(self,eclass,entity):
		if eclass not in self.containers:
			self.containers[eclass] = []
		self.containers[eclass].append(entity)

	def remove_entity_of_class(self,eclass,entity):
		if eclass in self.containers:
			self.containers[eclass].remove(entity)

	def find_closest_of_classes(self,x,y,classes):
		min_distance = None
		closest = None
		for cl in classes:
			if cl in self.containers:
				for ent in self.containers[cl]:
					if not ent.sprite.visible:
						continue
					dist = math.sqrt(math.pow((ent.x-x),2) + math.pow((ent.y - y),2))
					if (min_distance is None) or (min_distance > dist):
						min_distance = dist
<<<<<<< HEAD
						closest = ent
			else:
				continue
				# class doesnt exists -> next class in container or gtfo
		return closest, min_distance
=======
					else:
						if min_distance > dist:
							min_distance = dist
					if dist < 100:
						GAME_CONSOLE.write('nearest: ', ent.id, 'dist:', dist)
						ent.stop()
			# если класса нет
			else:
				pass
>>>>>>> parent of 576cad7... unstable

	def init_entities(self,levelinfo):
		self.selector = Selector()
		self.addEntity(self.selector)
		ents = levelinfo['entities']
		for ed in ents:
			self.addEntity(ed['class'](**(ed['kwargs'])))

	def handle_key_press(self,key):
		if key in Player.DIR_KEYS:
			self.player.dirkeys[key] = 1

	def handle_key_release(self,key):
		if key in Player.DIR_KEYS:
			self.player.dirkeys[key] = 0

	def update(self,dt):
		Game.update(self,dt)
<<<<<<< HEAD
		self.selector.select_around(*self.find_closest_of_classes(self.player.x,self.player.y,self.interactive_items_list()))
		#closest,dist = self.find_closest_of_classes(self.player.x,self.player.y,self.interactive_items_list())
		# выделение близжайшего объекта
		#if (closest is not None):
		#	print closest.id
		#	closest.select()
=======
		self.find_closest_of_classes(self.player.x,self.player.y,self.interactive_items_list())
>>>>>>> parent of 576cad7... unstable

	def interactive_items_list(self):
		if self.player.state is 'run':
			return ('cats','doors')
		elif self.player.state is 'carry':
			return ('windows',)

class Player(AnimatedGameEntity):
	ANIMATION_LIST = AnimationList({
		'run':[
			{'img':'rc/img/player.png','t':0.1,'anchor':'center','rect':(0,0,128,128)},
			{'img':'rc/img/player.png','t':0.1,'anchor':'center','rect':(256,0,128,128)}
		],
		'idle':[
			{'img':'rc/img/player.png','t':0,'anchor':'center','rect':(128,0,128,128)}
		]
	})

	DIR_ANGLE_MAP = [
		[7,0,1],
		[6,None,2],
		[5,4,3]
	]

	DIR_KEYS = [KEY.LEFT,KEY.RIGHT,KEY.UP,KEY.DOWN]
	RADIUS = 50

	def __init__(self,x,y):
		AnimatedGameEntity.__init__(self,Player.ANIMATION_LIST)
		self.set_animation('idle')
		self.move_state = 'idle'
		self.x = x
		self.y = y

		self.vx = 0.0
		self.vy = 0.0

		self.dirx = 0.0
		self.diry = 0.0

		self.radius = Player.RADIUS

		self.dirkeys = {k:0 for k in Player.DIR_KEYS}

	def update_direction(self):
		if self.dirkeys[Player.DIR_KEYS[0]] != self.dirkeys[Player.DIR_KEYS[1]]:
			if self.dirkeys[Player.DIR_KEYS[0]] != 0:
				self.dirx = -1
			else:
				self.dirx = 1
		else:
			self.dirx = 0

		if self.dirkeys[Player.DIR_KEYS[2]] != self.dirkeys[Player.DIR_KEYS[3]]:
			if self.dirkeys[Player.DIR_KEYS[2]] != 0:
				self.diry = 1
			else:
				self.diry = -1
		else:
			self.diry = 0

		k = 200.0
		angle = Player.DIR_ANGLE_MAP[int(1-self.diry)][int(1+self.dirx)]

		if angle != None:
			self.rotation = angle * 45

		l2 = self.dirx * self.dirx + self.diry * self.diry

		if l2 != 0:
			l = 1.0 / math.sqrt(self.dirx * self.dirx + self.diry * self.diry)

			self.vx = self.dirx * l * k
			self.vy = self.diry * l * k
		else:
			self.vx = 0
			self.vy = 0

	def spawn(self):
		AnimatedGameEntity.spawn(self)
		self.game.player = self
		self.state = 'run'

	def update(self,dt):
		self.update_direction( )

		if abs(self.vx) + abs(self.vy) > 0:
			if self.move_state != 'run':
				self.set_animation('run')
				self.move_state = 'run'
		elif self.move_state != 'idle':
			self.set_animation('idle')
			self.move_state = 'idle'

		self.x += self.vx * dt
		self.y += self.vy * dt

		self.end_update_coordinates( )

	#возвращает расстояние от текущей сущности до указанной
	def distance(self, entity):
		dx = ent.x - self.x
		dy = ent.y - self.y
		return math.sqrt(dx*dx + dy*dy)-entity.radius

	def select(self):
		self.game.reset_use_tip()
		self.game.set_use_tip(self, 'Use arrows')

class MiniGame(GameEntity):
		DIFFICULTY_LOW = list('qwer')
		DIFFICULTY_MIDDLE = list('qwerasdf')
		DIFFICULTY_HIGH = list('qwerasdfzxcv')
		TIME = 10
		# Mode = 0 - endless, 1 - timer

		def __init__(self,difficulty,mode=0):
			GameEntity.__init__(self)
			self.difficulty = difficulty
			self.mode = mode
			self.task = None

		def generate(self):
			return random.choice(self.difficulty)

		def start_timer(self):
			self.timer = MiniGame.TIME

		def wait(self):
			if self.task is None:
				self.task = self.generate()




		def update(self,dt):
			if self.timer == 0:
				return
			if self.timer > 0:
				self.timer -= dt
			else:
				pass
				# Поражение в игре

