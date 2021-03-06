from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonSliderElement import ButtonSliderElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from ConfigurableButtonElement import ConfigurableButtonElement
from DeviceControllerComponent import DeviceControllerComponent
from SpecialSessionComponent import SpecialSessionComponent
from InstrumentControllerComponent import InstrumentControllerComponent
from SubSelectorComponent import *
from StepSequencerComponent2 import StepSequencerComponent
from _Framework.MomentaryModeObserver import MomentaryModeObserver

class MainSelectorComponent(ModeSelectorComponent):
	""" Class that reassigns the button on the launchpad to different functions """

	def __init__(self, matrix, top_buttons, side_buttons, config_button, parent):
		assert isinstance(matrix, ButtonMatrixElement)
		assert ((matrix.width() == 8) and (matrix.height() == 8))
		assert isinstance(top_buttons, tuple)
		assert (len(top_buttons) == 8)
		assert isinstance(side_buttons, tuple)
		assert (len(side_buttons) == 8)
		assert isinstance(config_button, ButtonElement)
		ModeSelectorComponent.__init__(self)
		self._parent = parent
		self._compact = False
		self._session = SpecialSessionComponent(matrix.width(), matrix.height())
		self._zooming = SessionZoomingComponent(self._session)
		self._session.name = 'Session_Control'
		self._zooming.name = 'Session_Overview'
		self._matrix = matrix
		self._side_buttons = side_buttons
		self._nav_buttons = top_buttons[:4]
		self._config_button = config_button
		self._zooming.set_empty_value(LED_OFF)
		self._all_buttons = []
		for button in self._side_buttons + self._nav_buttons:
			self._all_buttons.append(button)

		self._sub_modes = SubSelectorComponent(matrix, side_buttons, self._session)
		self._sub_modes.name = 'Mixer_Modes'
		self._sub_modes.set_update_callback(self._update_control_channels)
		self._stepseq = StepSequencerComponent(self._matrix, self._side_buttons, self._nav_buttons, self)
		self._instrument_controller = InstrumentControllerComponent( self._matrix, self._side_buttons, self._nav_buttons,self)
		self._device_controller = DeviceControllerComponent(self._matrix, self._side_buttons, self._nav_buttons, self)
		self._init_session()
		self._all_buttons = tuple(self._all_buttons)
		self._mode_index=0
		self._previous_mode_index=-1
		self._sub_mode_index=[0,0,0,0]
		for index in range(4):
			self._sub_mode_index[index]=0
		self.set_mode_buttons(top_buttons[4:])

	def disconnect(self):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)

		self._session = None
		self._zooming = None
		for button in self._all_buttons:
			button.set_on_off_values(127, LED_OFF)

		self._config_button.turn_off()
		self._matrix = None
		self._side_buttons = None
		self._nav_buttons = None
		self._config_button = None
		ModeSelectorComponent.disconnect(self)

	def session_component(self):
		return self._session

	def _update_mode(self):
		mode = self._modes_heap[-1][0]
		assert mode in range(self.number_of_modes())
		if self._mode_index==mode:
			if self._mode_index==1:
				#user mode 1 and device controller and instrument mode
				self._sub_mode_index[self._mode_index] = (self._sub_mode_index[self._mode_index]+1)%3
				self.update()
			elif self._mode_index==2:
				#user mode 2  and step sequencer
				self._sub_mode_index[self._mode_index] = (self._sub_mode_index[self._mode_index]+1)%2
				self.update()
			elif self._mode_index==3:
				self.update()
			else:
				self._sub_mode_index[self._mode_index] = 0
			self._previous_mode_index=self._mode_index	
		else:
			self._mode_index = mode
			self.update()
	
	def set_mode(self, mode):
		self._clean_heap()
		self._modes_heap = [(mode, None, None)]
		#if ((self._mode_index != mode) or (mode == 3) or True):
		#self._mode_index = mode
			#self._update_mode()
		#	self.update()
	
	def number_of_modes(self):
		return 4

	def on_enabled_changed(self):
		self.update()

	def _update_mode_buttons(self):
		for index in range(4):
			if(self._sub_mode_index[index]==0):
				self._modes_buttons[index].set_on_off_values(AMBER_FULL,AMBER_THIRD)
			if(self._sub_mode_index[index]==1):
				self._modes_buttons[index].set_on_off_values(GREEN_FULL,GREEN_THIRD)
			if(self._sub_mode_index[index]==2):
				self._modes_buttons[index].set_on_off_values(RED_FULL,RED_THIRD)
				
			if (index == self._mode_index):	
				self._modes_buttons[index].turn_on()
			else:
				self._modes_buttons[index].turn_off()


	def channel_for_current_mode(self):
		if self._compact:
		
			if self._mode_index==0:
				new_channel =  2 #session 

			elif self._mode_index==1:
				if self._sub_mode_index[self._mode_index]==0:
					new_channel = 2 #instrument controller 11,12,13,14
					if self._instrument_controller != None:
						self._instrument_controller.base_channel = new_channel
				elif self._sub_mode_index[self._mode_index]==1:
					new_channel = 2 #device controler
				else : 
					new_channel = 0 #plain user mode 1

			elif self._mode_index==2:
				if self._sub_mode_index[self._mode_index]==0:	
					new_channel = 1 #user 2
				else:
					new_channel = 2 + self._sub_mode_index[self._mode_index] #step seq 2,3

			elif self._mode_index==3: #mixer modes
				new_channel = 2 + self._sub_modes.mode() # 2,3,4,5,6
				
		else:
			
			if self._mode_index==0:
				new_channel =  0 #session 

			elif self._mode_index==1:
				if self._sub_mode_index[self._mode_index]==0:
					new_channel = 11 #instrument controller 11,12,13,14
					if self._instrument_controller != None:
						self._instrument_controller.base_channel = new_channel
				elif self._sub_mode_index[self._mode_index]==1:
					new_channel = 3 #device controler
				else : 
					new_channel = 4 #plain user mode 1

			elif self._mode_index==2:
				if self._sub_mode_index[self._mode_index]==0:	
					new_channel = 5 #user 2
				else:
					new_channel = 1 + self._sub_mode_index[self._mode_index] #step seq 1,2

			elif self._mode_index==3: #mixer modes
				new_channel = 6 + self._sub_modes.mode() # 6,7,8,9,10
		return new_channel

	def update(self):
		assert (self._modes_buttons != None)
		if self.is_enabled():

			self._update_mode_buttons()
			
			as_active = True
			as_enabled = True
			self._session.set_allow_update(False)
			self._zooming.set_allow_update(False)
			self._config_button.send_value(40)
			self._config_button.send_value(1)
			
			if (self._mode_index == 0):
				#session
				self._setup_mixer(not as_active)
				self._setup_device_controller(not as_active)
				self._setup_step_sequencer(not as_active)
				self._setup_instrument_controller(not as_active)
				self._setup_session(as_active, as_enabled)
				self._update_control_channels()
				
			elif (self._mode_index == 1):
				self._setup_session(not as_active, not as_enabled)
				self._setup_step_sequencer(not as_active)
				self._setup_mixer(not as_active)
				#user mode + device controller + instrument controller
				if (self._sub_mode_index[self._mode_index]==0):
					self._setup_device_controller(not as_active)
					self._update_control_channels()
					self._setup_instrument_controller(as_active)
				elif (self._sub_mode_index[self._mode_index]==1):
					self._setup_instrument_controller(not as_active)
					self._setup_device_controller(as_active)
					self._update_control_channels()
				else:
					self._setup_device_controller(not as_active)
					self._setup_instrument_controller(not as_active)
					self._setup_user_mode(True, True, False, True)
					self._update_control_channels()
			elif (self._mode_index == 2):
				self._setup_session(not as_active, not as_enabled)
				self._setup_instrument_controller(not as_active)
				self._setup_device_controller(not as_active)
				self._setup_mixer(not as_active)
				if (self._sub_mode_index[self._mode_index]==0):
					self._setup_step_sequencer(not as_active)
					self._setup_user_mode(False, False, False, False)
				else:
					self._setup_step_sequencer(as_active, self._sub_mode_index[self._mode_index])
				self._update_control_channels()
			elif (self._mode_index == 3):
				self._setup_device_controller(not as_active)
				self._setup_step_sequencer(not as_active)
				self._setup_instrument_controller(not as_active)
				self._setup_session(not as_active, as_enabled)
				self._setup_mixer(as_active)
				self._update_control_channels()
			else:
				assert False
			
			self._previous_mode_index=self._mode_index
			
			self._session.set_allow_update(True)
			self._zooming.set_allow_update(True)
				
				

	def _setup_session(self, as_active, as_enabled):
		assert isinstance(as_active, type(False))
		for button in self._nav_buttons:
			if as_enabled:
				button.set_on_off_values(GREEN_FULL, GREEN_THIRD)
			else:
				button.set_on_off_values(127, LED_OFF)

		#matrix
		for scene_index in range(8):
			scene = self._session.scene(scene_index)
			if as_active:
				self._activate_matrix(True)
				scene_button = self._side_buttons[scene_index]
				scene_button.set_on_off_values(127, LED_OFF)
				scene.set_launch_button(scene_button)
			else:
				scene.set_launch_button(None)
			for track_index in range(8):
				if as_active:
					button = self._matrix.get_button(track_index, scene_index)
					button.set_on_off_values(127, LED_OFF)
					scene.clip_slot(track_index).set_launch_button(button)
				else:
					scene.clip_slot(track_index).set_launch_button(None)

		#zoom
		if as_active:
			self._zooming.set_zoom_button(self._modes_buttons[0])
			self._zooming.set_button_matrix(self._matrix)
			self._zooming.set_scene_bank_buttons(self._side_buttons)
			self._zooming.set_nav_buttons(self._nav_buttons[0], self._nav_buttons[1], self._nav_buttons[2], self._nav_buttons[3])
			self._zooming.update()
		else:
			self._zooming.set_zoom_button(None)
			self._zooming.set_button_matrix(None)
			self._zooming.set_scene_bank_buttons(None)
			self._zooming.set_nav_buttons(None, None, None, None)

		#nav buttons
		if as_enabled:
			self._session.set_track_bank_buttons(self._nav_buttons[3], self._nav_buttons[2])
			self._session.set_scene_bank_buttons(self._nav_buttons[1], self._nav_buttons[0])
		else:
			self._session.set_track_bank_buttons(None, None)
			self._session.set_scene_bank_buttons(None, None)

	def _setup_instrument_controller(self, enabled):
		if self._instrument_controller != None:
			if enabled:
				self._activate_matrix(False)
				self._activate_scene_buttons(True)
				self._activate_navigation_buttons(True)
			else:
				for scene_index in range(8):
					scene_button = self._side_buttons[scene_index]
					scene_button.use_default_message()
					scene_button.force_next_send()
					for track_index in range(8):
						button = self._matrix.get_button(track_index, scene_index)
						button.use_default_message()
						button.force_next_send()
			self._instrument_controller.set_enabled(enabled)
		

	def _setup_device_controller(self, as_active):
		if self._device_controller!=None:
			if as_active:
				self._activate_scene_buttons(True)
				self._activate_matrix(True)
				self._activate_navigation_buttons(True)
 				self._device_controller._is_active = True
				self._config_button.send_value(32)
				self._device_controller.set_enabled(True)
				self._device_controller.update()
 			else:
				self._device_controller._is_active = False
				self._device_controller.set_enabled(False)



				
	def _setup_user_mode(self, release_matrix=True, release_side_buttons=True, release_nav_buttons = True, drum_rack_mode = True):
	
		for scene_index in range(8):
			scene_button = self._side_buttons[scene_index]
			scene_button.set_on_off_values(127, LED_OFF)
			scene_button.force_next_send()
			scene_button.turn_off()
			scene_button.set_enabled((not release_side_buttons))
				
			for track_index in range(8):
				button = self._matrix.get_button(track_index, scene_index)
				button.set_on_off_values(127, LED_OFF)
				button.turn_off()
				button.set_enabled((not release_matrix))

		for button in self._nav_buttons:
			button.set_on_off_values(127, LED_OFF)
			button.turn_off()
			button.set_enabled((not release_nav_buttons))

		if drum_rack_mode:
			self._config_button.send_value(2)
		self._config_button.send_value(32)



	def _setup_step_sequencer(self, as_active, mode=0):
		if(self._stepseq!=None):
			if(self._stepseq.is_enabled()!=as_active or self._stepseq._mode!=mode):
				if as_active: 
					self._activate_scene_buttons(True)
					self._activate_matrix(True)
					self._activate_navigation_buttons(True)
					self._config_button.send_value(32)
					self._stepseq.set_enabled(True)
				else:
					self._stepseq.set_enabled(False)


	def _setup_mixer(self, as_active):
		assert isinstance(as_active, type(False))
		if as_active:
			self._activate_navigation_buttons(True)
			self._activate_scene_buttons(True)
			self._activate_matrix(True)
			if(self._sub_modes.is_enabled()):
				#go back to default mode
				self._sub_modes.set_mode(-1)
		self._sub_modes.set_enabled(as_active)
		


	def _init_session(self):
		self._session.set_stop_track_clip_value(AMBER_BLINK)
		for scene_index in range(self._matrix.height()):
			scene = self._session.scene(scene_index)
			scene.set_triggered_value(GREEN_BLINK)
			scene.name = 'Scene_' + str(scene_index)
			for track_index in range(self._matrix.width()):
				clip_slot = scene.clip_slot(track_index)
				clip_slot.set_triggered_to_play_value(GREEN_BLINK)
				clip_slot.set_triggered_to_record_value(RED_BLINK)
				clip_slot.set_stopped_value(AMBER_FULL)
				clip_slot.set_started_value(GREEN_FULL)
				clip_slot.set_recording_value(RED_FULL)
				clip_slot.set_record_button_value(RED_THIRD)
				#clip_slot.set_clip_palette(CLIP_COLOR_TABLE)
				#clip_slot.set_clip_rgb_table(RGB_COLOR_TABLE)
				clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
				self._all_buttons.append(self._matrix.get_button(track_index, scene_index))

		self._zooming.set_stopped_value(RED_FULL)
		self._zooming.set_selected_value(AMBER_FULL)
		self._zooming.set_playing_value(GREEN_FULL)



	def _activate_navigation_buttons(self,active):
		for button in self._nav_buttons:
			button.set_enabled(active)

	def _activate_scene_buttons(self,active):
		for button in self._side_buttons:
			button.set_enabled(active)
			
	def _activate_matrix(self,active):
		for scene_index in range(8):
			for track_index in range(8):
				self._matrix.get_button(track_index, scene_index).set_enabled(active)
				
	def log_message(self, msg):
		self._parent.log_message(msg)
		
	#Update the channels of the buttons in the user modes..
	def _update_control_channels(self):
		new_channel = self.channel_for_current_mode()
		for button in self._all_buttons:
			button.set_channel(new_channel)
			button.set_force_next_value()


CLIP_COLOR_TABLE = {15549221: AMBER_FULL,
 12411136: AMBER_FULL,
 11569920: AMBER_FULL,
 8754719: AMBER_FULL,
 5480241: AMBER_FULL,
 695438: AMBER_FULL,
 31421: AMBER_FULL,
 197631: AMBER_FULL,
 3101346: AMBER_FULL,
 6441901: AMBER_FULL,
 8092539: AMBER_FULL,
 3947580: AMBER_FULL,
 16712965: AMBER_FULL,
 12565097: AMBER_FULL,
 10927616: AMBER_FULL,
 8046132: AMBER_FULL,
 4047616: AMBER_FULL,
 49071: AMBER_FULL,
 1090798: AMBER_FULL,
 5538020: AMBER_FULL,
 8940772: AMBER_FULL,
 10701741: AMBER_FULL,
 12008809: AMBER_FULL,
 9852725: AMBER_FULL,
 16149507: AMBER_FULL,
 12581632: AMBER_FULL,
 8912743: AMBER_FULL,
 1769263: AMBER_FULL,
 2490280: AMBER_FULL,
 6094824: AMBER_FULL,
 1698303: AMBER_FULL,
 9160191: AMBER_FULL,
 9611263: AMBER_FULL,
 12094975: AMBER_FULL,
 14183652: AMBER_FULL,
 16726484: AMBER_FULL,
 16753961: AMBER_FULL,
 16773172: AMBER_FULL,
 14939139: AMBER_FULL,
 14402304: AMBER_FULL,
 12492131: AMBER_FULL,
 9024637: AMBER_FULL,
 8962746: AMBER_FULL,
 10204100: AMBER_FULL,
 8758722: AMBER_FULL,
 13011836: AMBER_FULL,
 15810688: AMBER_FULL,
 16749734: AMBER_FULL,
 16753524: AMBER_FULL,
 16772767: AMBER_FULL,
 13821080: AMBER_FULL,
 12243060: AMBER_FULL,
 11119017: AMBER_FULL,
 13958625: AMBER_FULL,
 13496824: AMBER_FULL,
 12173795: AMBER_FULL,
 13482980: AMBER_FULL,
 13684944: AMBER_FULL,
 14673637: AMBER_FULL,
 16777215: AMBER_BLINK}