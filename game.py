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

@ScreenClass('ENDING')
class EndScreen(AppScreen):
	def __init__(self,img,snd,sndmod,text=''):
		AppScreen.__init__(self)

		self.addLayer(StaticBackgroundLauer(img,'scale'))

		PlayMusic(snd,sndmod)

	def  on_key_press(self,key):
		if key == KEY.ESC:
			pass

@ScreenClass('STARTUP')
@ScreenClass('GAME')
class GameScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.camera = Camera( )

		self.camera.focus_x = 0
		self.camera.focus_y = 0

		self.addLayer(StaticBackgroundLauer('rc/img/background.png','scale'))

		tl = TipLayer(self.camera,None,0,20)
		tl.setText("")

		self.game = MyGame(tl)
		self.game.unpause( )

		self.addLayer(GameWorldLayer(self.game,self.camera))
		self.addLayer(tl)

		GAME_CONSOLE.write('Game screen created.')

		PlayMusic('rc/snd/ld32full.ogg',mode='loop')

	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

		self.camera.scale = 0.6 * min(float(width) / float(MyGame.WORLD_WIDTH),float(height) / float(MyGame.WORLD_HEIGHT))

	def on_mouse_scroll(self,x,y,sx,sy):
		# self.camera.scale *= 2 ** (sy*0.02)
		pass

	def on_key_press(self,key,mod):
		#GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		self.game.handle_key_press(key)
		if key == KEY.P:
			PlayMusic('rc/snd/ld32cello.ogg',mode='stop')
		if key == KEY.O:
			PlayMusic('rc/snd/ld32full.ogg',mode='loop')

	def on_key_release(self,key,mod):
		#GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		self.game.handle_key_release(key)

	def on_mouse_press(self,x,y,button,modifiers):
		pass

class TipLayer(GUITextItemLayer):
	def __init__(self,camera,entity,mar_x=0,mar_y=0):
		GUITextItemLayer.__init__(self,0.0,0.0,font_size=16)
		self.entity = entity
		self.camera = camera
		self.mar_x,self.mar_y = mar_x,mar_y

	def update_coordinates(self):
		if self.entity == None:
			return

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

class Door(GameEntity):
	KEYS = (KEY.Q,KEY.W,KEY.E)

	def __init__(self,x,y):
		GameEntity.__init__(self)
		self.x = x
		self.y = y
		self.openness = 0
		self.choose_key( )

	def spawn(self):
		GameEntity.spawn(self)
		self.game.add_entity_of_class('doors',self)

	def update(self,dt):
		if self.game.selector.entity == self:
			self.game.selector.set_entity(self)

	def on_collision(self, other):
		# обработка столкновений
		pass

	def choose_key(self):
		self.key = random.choice(Door.KEYS)

	def handle_key_press(self,key):
		if key == self.key:
			self.openness += 0.1
			self.choose_key( )
			GAME_CONSOLE.write('Door openness:',str(self.openness))

	def get_tip_text(self):
		return 'Press [{0}] to open door'.format(KEY.symbol_string(self.key))

class Window(GameEntity):
	def __init__(self,x,y,cat_limit = 1,id=None):
		self.id = id
		GameEntity.__init__(self)
		self.x = x
		self.y = y
		self.cat_limit = cat_limit 
		self.cats = []
		self.setup_timer()

	def spawn(self):
		GameEntity.spawn(self)
		self.game.add_entity_of_class('windows',self)
		self.initial_spawn_cats()
		self.end_update_coordinates( )

	def on_collision(self, other):
		# обработка столкновений
		pass

	def update(self, dt):
		if self.timer > 0:
			self.timer -= dt
		elif (len([cat for cat in self.cats if cat.is_visiable]) < self.cat_limit):
			self.setup_timer()
			self.spawn_cat()
			# print 'cat spawned'
		# else:
			# print len([cat for cat in self.cats if cat.is_visiable])

	def initial_spawn_cats(self):
		for i in range(self.cat_limit):
			cat = MineCat(self.x, self.y,0)
			cat.window = self
			self.cats.append(cat)
			self.game.addEntity(cat)

	def spawn_cat(self):
		for c in self.cats:
			if not c.is_visiable:
				c.x = self.x
				c.y = self.y
				c.throw()
				break

	def get_tip_text(self):
		if self.game.player.caught_cat != None:
			return 'Press [W] to throw cat'
		return 'Window'

	def setup_timer(self):
		self.timer = 2
		#self.timer = random.random()*10+20

class Selector(SpriteGameEntity):
	def __init__(self):
		SpriteGameEntity.__init__(self,'rc/img/selector.png')
		self.entity = None

	def spawn(self):
		SpriteGameEntity.spawn(self)
		self.game.selector = self
		self.game.tip_layer.entity = self

	def set_entity(self,ent):
		if ent == None or 'get_tip_text' not in dir(ent):
			self.game.tip_layer.setText('')
		else:
			self.game.tip_layer.setText(ent.get_tip_text())
		self.entity = ent

	def update(self,dt):
		if self.entity == None:
			return

		self.x,self.y = self.entity.x,self.entity.y

		self.rotation += dt * 180.0

		self.end_update_coordinates( )

	def handle_key_press(self,key):
		if self.entity != None and 'handle_key_press' in dir(self.entity):
			self.entity.handle_key_press(key)

class MineSignal(SpriteGameEntity):
	def __init__(self, cat):
		SpriteGameEntity.__init__(self,'rc/img/signal.png')
		self.cat = cat

	def update(self, dt):
		self.x, self.y = self.cat.x, self.cat.y
		self.set_scale()
		self.sprite.visible = self.cat.is_visiable
		self.end_update_coordinates()

	def set_scale(self):
		def pila(x,p):
			p = min(max(p+0.2,0.1),2.0)
			m = x % p
			if m > 0.5 * p:
				return 1.0 - (m-0.5*p) / p
			return 0
		self.scale = pila(self.game.time,self.cat.mine_timer * 0.5) * 0.7


class MineCat(AnimatedGameEntity):
	next_id = 0
	# цифры из предыдущего проекта
	ANIMATION_LIST = AnimationList({
			'Run':[
				{'img':'rc/img/cat-run.png','t':0.1,'anchor':'center','rect':(128*0,0,128,128)},
				{'img':'rc/img/cat-run.png','t':0.1,'anchor':'center','rect':(128*1,0,128,128)}
			]
		}
	)
	MG_KEYS=[KEY.Q,KEY.W,KEY.E,KEY.R,
			KEY.A,KEY.S,KEY.D,KEY.F,
			KEY.Z,KEY.X,KEY.C,KEY.V]

	def __init__(self,x,y,id):
		AnimatedGameEntity.__init__(self, MineCat.ANIMATION_LIST)
		if id is None:
			id = MineCat.next_id
			MineCat.next_id+=1
		self.id = id
		self.x = x
		self.y = y
		self.vx = 1.0
		self.vy = 0.0
		self.angle = 0
		self.angVelocity = 0
		self.timer = 3
		self.scale = 1
		self.window = None
		self.is_visiable = False
		self.mine_timer = 30

		self.MG_timer = 0
		self.MG_key = None
		self.MG_in = False
		self.MG_key_pressed = False

		self.setup_task()

	def update(self,dt):
		if self.mine_timer > 0:
			self.mine_timer -= dt
		else:
			self.boom()
		if self.is_caught():
			self.game.selector.set_entity(self) # to update tip text
			self.x,self.y = self.game.player.x,self.game.player.y
			self.rotation = self.game.player.rotation
			self.x += math.sin(self.rotation * math.pi / 180.0) * 30
			self.y += math.cos(self.rotation * math.pi / 180.0) * 30
			if self.MG_timer > 0:
				self.MG_timer -= dt
			elif not self.MG_key_pressed:
				self.game.player.caught_cat = None
			else:
				self.start_minigame()
		else:
			self.timer -= dt
			if self.timer <= 0:
				self.setup_task()
			k=400
			self.affectAngleVelocity(dt)	
			self.x += self.vx*dt*k
			self.y += self.vy*dt*k
		self.end_update_coordinates()

	def boom(self):
		GAME_CONSOLE.write('BOOOM')
		print 'BOOOM'

	def spawn(self):
		self.game.addEntity(MineSignal(self),2)

	def throw(self):
		# print 'cat spawned'
		AnimatedGameEntity.spawn(self)
		self.is_visiable = True
		self.set_animation('Run')
		self.game.add_entity_of_class('cats',self)

	def velocity(self):
		return math.sqrt(self.vx*self.vx + self.vy*self.vY)

	def setVelocity(slef, k = 1):
		self.vx = k*self.vx
		self.vy = k*self.vy

	def setup_task(self):
		#нормальное распределение М[],сигма
		self.angVelocity = (random.normalvariate(0,90))
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

	def destroy(self):
		self.is_visiable = False
		self.game.remove_entity_of_class('cats',self)
		#self.window.cats.remove(self)

	def handle_key_press(self,key):
		if not self.any_caught():
			if key == KEY.W:
				self.game.player.caught_cat = self
				self.start_minigame()
		else:
			self.game.player.caught_cat.handle_minigame_key_press(key)

	def start_minigame(self):
		self.MG_timer = 1
		self.MG_key_pressed = False
		self.MG_key = random.choice(MineCat.MG_KEYS)

	def handle_minigame_key_press(self,key):
		if key == self.MG_key:
			self.MG_key_pressed = True

	def get_minigame_tip(self):
		if self.MG_key_pressed:
			return ' '
		else:
			return 'Press [{0}] to hold cat'.format(KEY.symbol_string(self.MG_key))

	def any_caught(self):
		return self.game.player.caught_cat != None

	def is_caught(self):
		return self.game.player.caught_cat == self

	def get_tip_text(self):
		if not self.any_caught():
			return 'Press [W] to catch cat'
		else:
			return self.game.player.caught_cat.get_minigame_tip()

def get_level(i):
	return {
		0: {
			'entities': [
				{'class':Player,'kwargs':{'x':0,'y':0}},
				{'class':MineCat,'kwargs':{'x':100,'y':200,'id':0}},
				{'class':Window,'kwargs':{'x':MyGame.LIMIT_LEFT,'y':-250,'id':0}},
				{'class':Window,'kwargs':{'x':MyGame.LIMIT_RIGHT,'y':330,'id':0}},
				{'class':Door,'kwargs':{'x':270,'y':MyGame.LIMIT_BOTTOM}},
				{'class':Selector,'kwargs':{}}
			]
		}
	}[i];

class MyGame(Game):
	LIMIT_LEFT = -500
	LIMIT_RIGHT = 500
	LIMIT_TOP = 500
	LIMIT_BOTTOM = -500
	WORLD_WIDTH = LIMIT_RIGHT - LIMIT_LEFT
	WORLD_HEIGHT = LIMIT_TOP - LIMIT_BOTTOM
	def __init__(self,tip_layer):
		Game.__init__(self)

		self.containers = {}

		self.tip_layer = tip_layer

		self.world_space = LimitedWorldSpace(MyGame.LIMIT_LEFT,MyGame.LIMIT_RIGHT,MyGame.LIMIT_TOP,MyGame.LIMIT_BOTTOM)

		self.init_entities(get_level(0))

	def add_entity_of_class(self,eclass,entity):
		if eclass not in self.containers:
			self.containers[eclass] = []
		self.containers[eclass].append(entity)

	def remove_entity_of_class(self,eclass,entity):
		if eclass in self.containers:
			self.containers[eclass].remove(entity)

	def find_closest_of_classes(self,x,y,classes,max_dist,default):
		best = default
		best_dist = max_dist
		for cl in classes:
			for ent in self.containers.get(cl,[]):
				dist = math.sqrt(math.pow((ent.x-x),2) + math.pow((ent.y - y),2))
				if dist < best_dist:
					best_dist = dist
					best = ent
		return best

	def init_entities(self,levelinfo):
		ents = levelinfo['entities']
		for ed in ents:
			self.addEntity(ed['class'](**(ed['kwargs'])))

	def handle_key_press(self,key):
		if key in Player.DIR_KEYS:
			self.player.dirkeys[key] = 1
		self.selector.handle_key_press(key)

	def handle_key_release(self,key):
		if key in Player.DIR_KEYS:
			self.player.dirkeys[key] = 0

	def update(self,dt):
		Game.update(self,dt)
		selected = self.player

		if self.player.caught_cat != None:
			selected = self.find_closest_of_classes(self.player.x,self.player.y,('windows',),100.0,self.player)

		if selected == self.player:
			selected = self.find_closest_of_classes(self.player.x,self.player.y,('cats',),100.0,self.player)
			if selected == self.player:
				selected = self.find_closest_of_classes(self.player.x,self.player.y,('doors',),100.0,self.player)

		if selected != self.selector.entity:
			self.selector.set_entity(selected)

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

		self.caught_cat = None

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

		k = 400.0
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

	def get_tip_text(self):
		return 'Use arrow keys'

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
