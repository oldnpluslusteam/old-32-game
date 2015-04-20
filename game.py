#!/usr/bin/python
# coding=UTF-8

from framework import *
import math, random

GAME_CONSOLE.visible = False

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
	def __init__(self,img,music,musmod,text=''):
		AppScreen.__init__(self)

		self.addLayer(StaticBackgroundLauer(img,'scale'))

		self.addLayer(GUITextItemLayer(text='PRESS ENTER TO RESTART',offset_x=0,offset_y=0))

		PlayMusic(music,musmod)

	def  on_key_press(self,key,mod):
		if key == KEY.ESCAPE:
			self.need_exit = True
		elif key == KEY.ENTER:
			self.set_next('GAME')

@ScreenClass('STARTUP')
@ScreenClass('GAME')
class GameScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.camera = Camera( )

		self.camera.focus_x = 0
		self.camera.focus_y = 0
		self.camera.scale = 0.5

		tl = TipLayer(self.camera,None,0,20)
		tl.setText("")

		self.game = MyGame(tl)
		self.game.unpause( )
		self.game.screen = self
		self.game.camera = self.camera

		self.addLayer(GameWorldLayer(self.game,self.camera))
		self.addLayer(tl)

		GAME_CONSOLE.write('Game screen created.')

		PlayMusic('rc/snd/ld32full.ogg',mode='loop')

	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

	def on_key_press(self,key,mod):
		self.game.handle_key_press(key)

	def on_key_release(self,key,mod):
		self.game.handle_key_release(key)

	def on_mouse_press(self,x,y,button,modifiers):
		pass

	def do_end(self,typ):
		SET = {
			'good'	: {'img':'rc/img/ending-good.png','music':'rc/snd/ld32cello.ogg','musmod':'stop'},
			'bad'	: {'img':'rc/img/ending-bad.png','music':'rc/snd/ld32bad.ogg','musmod':'stop'}
		}
		self.set_next('ENDING',**SET[typ])
		GAME_CONSOLE.write('SCR.ENDING:',typ)

	def exit(self):
		self.game.pause()

class TipLayer(GUITextItemLayer):
	def __init__(self,camera,entity,mar_x=0,mar_y=0):
		GUITextItemLayer.__init__(self,0.0,0.0,font_size=16,bold=True)
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

class DoorTip(SpriteGameEntity):
	def __init__(self,x,y,a,f):
		SpriteGameEntity.__init__(self,'rc/img/arrow.png')
		self.x0 = x
		self.y0 = y
		self.a = a
		self.f = f

	def update(self,dt):
		self.x = self.x0
		self.y = self.y0 + self.a * math.sin(self.f*self.game.time)
		self.end_update_coordinates( )

class Door(GameEntity):
	KEYS = (KEY.A,KEY.W,KEY.S,KEY.D)


	def __init__(self,x,y):
		GameEntity.__init__(self)
		self.x = x
		self.y = y

		self.openness = 0
		self.choose_key( )

	def update(self,dt):
		self.end_update_coordinates()

	def spawn(self):
		GameEntity.spawn(self)
		self.game.add_entity_of_class('doors',self)

		t = DoorTip(self.x,self.y + 100,20,10)
		self.tip = t
		self.game.addEntity(t)

	def update(self,dt):
		if self.game.selector.entity == self:
			self.game.selector.set_entity(self)

	def on_collision(self, other):
		# обработка столкновений
		pass

	def choose_key(self):
		self.key = random.choice(Door.KEYS)

	def handle_key_press(self,key):
		if key in Door.KEYS:
			if key == self.key:
				snd = random.choice(['rc/snd/door1.wav','rc/snd/door3.wav','rc/snd/door4.mp3'])
				PlayStaticSound(snd)
				self.tip.sprite.visible = False
				self.openness += 0.1
				self.game.selector.set_entity(self) 
				GAME_CONSOLE.write('Door openness:',str(self.openness))
				if self.openness >= 10:
					PlayStaticSound('rc/snd/door_open.wav')
					self.game.ending('good')
			self.choose_key( )

	def get_tip_text(self):
		return 'Press [{}] to hit door [{}%]'.format(KEY.symbol_string(self.key),int(self.openness*100.0/10.0))

class Window(GameEntity):
	def __init__(self,x,y,cat_limit = 1,id=None):
		self.id = id
		GameEntity.__init__(self)
		self.x = x
		self.y = y
		self.cat_limit = cat_limit 
		self.cats = []
		self.timer = 3

	def spawn(self):
		GameEntity.spawn(self)
		self.game.add_entity_of_class('windows',self)
		self.initial_spawn_cats()
		self.end_update_coordinates( )

	def on_collision(self, other):
		# обработка столкновений
		pass

	def update(self, dt):
		if (len([cat for cat in self.cats if cat.is_visiable]) < self.cat_limit):
			if self.timer > 0:
				self.timer -= dt
			else:
				self.spawn_cat()

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
				self.setup_timer()
				break

	def get_tip_text(self):
		if self.game.player.caught_cat != None:
			return 'Press [E] to throw cat'
		return 'Window'

	def handle_key_press(self,key):
		# выбрасывание кота в окно
		if key == KEY.E:
			self.game.player.caught_cat.destroy()

	def setup_timer(self):
		self.timer = 10
		#not test:
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
		if not self.sprite.visible:
			return
		def pila(x,p):
			p = min(max(p+0.6,0.5),2.0)
			m = x % p
			if m > 0.5 * p:
				return 1.0 - (m-0.5*p) / p
			return 0
		new_scale = pila(self.game.time,self.cat.mine_timer * 0.1) * 0.7
		self.cat.peep = (self.scale == 0 and new_scale != 0)
		self.scale = new_scale

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
	MG_KEYS=[KEY.W,KEY.A,KEY.S,KEY.D]

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
		self.velocity = 400.0
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

		self.peep = False

	def hide(self):
		self.sprite.visible = False
		self.x = 9999
	def show(self):
		self.sprite.visible = True

	def update(self,dt):
		if not self.is_visiable:
			self.x = self.y = 9999
			return
		if self.mine_timer > 0:
			self.mine_timer -= dt
		elif self.mine_timer < 0:
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
			self.affectAngleVelocity(dt)	
			self.x += self.vx*dt
			self.y += self.vy*dt
		self.end_update_coordinates()

	def boom(self):
		self.mine_timer = 0
		GAME_CONSOLE.write('CAT.boom')
		PlayStaticSound('rc/snd/explosion_inside.mp3')
		self.game.ending('bad')

	def spawn(self):
		AnimatedGameEntity.spawn(self)
		self.game.addEntity(MineSignal(self),2)
		self.hide()

	def throw(self):
		self.is_visiable = True
		self.mine_timer = 30
		self.set_animation('Run')
		self.game.add_entity_of_class('cats',self)
		self.show()

	def setup_task(self):
		#нормальное распределение М[],сигма
		self.angVelocity = (random.normalvariate(0,90))
		self.angVelocityRad = self.angVelocity / 180 * math.pi
		self.timer = random.random()*3+0.5

	def affectAngleVelocity(self, dt):
		dr = self.angVelocity * dt
		self.rotation += -dr
		rr = ((self.rotation+90) / 180) * math.pi
		self.vx, self.vy = math.sin(rr) * self.velocity,math.cos(rr) * self.velocity
 
	#возвращает расстояние от текущей сущности до указанной
	def distance(self, entity):
		dx = ent.x - self.x
		dy = ent.y - self.y
		return math.sqrt(dx*dx + dy*dy)-entity.radius

	def destroy(self):
		self.game.player.caught_cat = None
		self.is_visiable = False
		self.game.remove_entity_of_class('cats',self)
		self.hide()
		#self.window.cats.remove(self)

	def handle_key_press(self,key):
		if not self.any_caught():
			if key == KEY.W:
				self.game.player.caught_cat = self
				self.start_minigame()
		else:
			self.game.player.caught_cat.handle_minigame_key_press(key)

	def start_minigame(self):
		self.MG_timer = 2
		self.MG_key_pressed = False
		self.MG_key = random.choice(MineCat.MG_KEYS)

	def handle_minigame_key_press(self,key):
		if key in MineCat.MG_KEYS:
			if key == self.MG_key:
				self.MG_key_pressed = True
			else:
				self.game.player.caught_cat = None

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
				{'class':Window,'kwargs':{'x':MyGame.LIMIT_LEFT,'y':-250,'id':0,'cat_limit':3}},
				{'class':Window,'kwargs':{'x':MyGame.LIMIT_RIGHT,'y':330,'id':0}},
				{'class':Door,'kwargs':{'x':290,'y':MyGame.LIMIT_BOTTOM}},
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
	BG_IMAGE = LoadTexture('rc/img/background.png',anchor='center')
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

	def ending(self,t):
		self.screen.do_end(t)

	def remove_entity_of_class(self,eclass,entity):
		if (eclass in self.containers) and (entity in self.containers[eclass]):
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

	def draw_all(self):
		glPushMatrix()
		glScalef(1.666,1.666,1.0)
		MyGame.BG_IMAGE.blit(0,0)
		glPopMatrix()
		Game.draw_all(self)

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

		self.do_peep( )

	def do_peep(self):
		cat = None
		t = 100000
		for c in self.containers.get('cats',[]):
			if c.mine_timer < t:
				t = c.mine_timer
				cat = c
		if cat != None:
			GAME_CONSOLE.write('min t:',str(t))
			if cat.peep:
				PlayStaticSound('rc/snd/peep.wav')

class Player(AnimatedGameEntity):
	ANIMATION_LIST = AnimationList({
		'run':[
			{'img':'rc/img/pl/0.png','t':0.1,'anchor':'center','rect':(0,0,128,128)},
			{'img':'rc/img/pl/1.png','t':0.1,'anchor':'center','rect':(0,0,128,128)},
			{'img':'rc/img/pl/3.png','t':0.1,'anchor':'center','rect':(0,0,128,128)},
			{'img':'rc/img/pl/4.png','t':0.1,'anchor':'center','rect':(0,0,128,128)}
		],
		'idle':[
			{'img':'rc/img/pl/stand.png','t':0,'anchor':'center','rect':(0,0,128,128)}
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

		k = 500.0
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

		self.game.camera.focus_x,self.game.camera.focus_y = self.x,self.y

	#возвращает расстояние от текущей сущности до указанной
	def distance(self, entity):
		dx = ent.x - self.x
		dy = ent.y - self.y
		return math.sqrt(dx*dx + dy*dy)-entity.radius
