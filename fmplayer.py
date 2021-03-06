#!/usr/bin/env python2

import time
import thread
import json
import gst

class Player(object):
	def __init__(self, on_end = None):
		self.current = None
		self.progress = 0
		self.length = 0
		self.playing = False
		self.on_end = on_end

		self.playbin = gst.element_factory_make("playbin2", "player")
		thread.start_new_thread(self._loop, ())

	def _loop(self):
		while True:
			time.sleep(1)

			if not self.playing:
				continue

			try:
				self.progress = self.playbin.query_position(gst.FORMAT_TIME, None)[0] / 1000000000
				self.length = self.playbin.query_duration(gst.FORMAT_TIME, None)[0] / 1000000000
			except:
				pass

			if self.progress > 0 and self.progress >= self.length:
				self.stop()
				if self.on_end:
					self.setSong(self.on_end())
				self.play()

	def setSong(self, song):
		self.current = song

	def play(self):
		if not self.current and self.on_end:
			self.setSong(self.on_end())
		if self.current:
			self.playbin.set_property("uri", self.current.url)
			self.playing = True
			self.playbin.set_state(gst.STATE_PLAYING)

	def stop(self):
		self.playing = False
		self.progress = self.length = 0
		self.playbin.set_state(gst.STATE_NULL)

	def pause(self):
		self.playing = False
		self.playbin.set_state(gst.STATE_PAUSED)

	def info(self):
		if not self.playing:
			return json.dumps({ 'status': 'not playing' })
		else:
			return json.dumps({ 'status': 'playing', 'progress': self.progress, 'length': self.length, 'song': self.current.toObj() })
