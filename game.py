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
