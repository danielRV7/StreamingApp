import sys
import wx
import os
import gi
import time
import signal

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst
from gi.repository import GstVideo
from gi.repository import GObject
from gi.repository import GLib

Gst.init(None)

class Receptor( wx.App ):

	def OnInit(self):

		window = wx.Frame(None)
		window.SetTitle("Reproductor")
		window.SetSize((640,480))
		window.Bind(wx.EVT_CLOSE, self.quit)
		self.SetTopWindow(window)

		video_window = wx.Panel(window)
		self.X_id = video_window.GetHandle()

		window.Layout()
		window.Show()

		# Preparamos la información relativa a la ventana

		self.puerto = int(sys.argv[1])
		self.decoder = int(sys.argv[2])

		# Creamos el Pipeline para Gstreamer

		self.pipeline = Gst.Pipeline.new()

		# Creamos el bus, que trata los eventos del pipeline.

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect('message::error', self.on_error)
		self.bus.connect('sync-message::element', self.on_sync_message)

		# Definimos los elementos que añadiremos al pipeline. Receptor.

		self.udpsrc = Gst.ElementFactory.make('udpsrc', None)			# La fuente recibida por UDP. Primera parte del pipeline.
			
		self.vc = Gst.ElementFactory.make('videoconvert', None)			# Cambia el espacio de color del video.
		self.buffer = Gst.ElementFactory.make('rtpjitterbuffer', None)	# Buffer que nos permite solucionar algunos problemas de inestabilidad de la red.
		self.sink = Gst.ElementFactory.make('autovideosink', None)		# Recibe los datos y los muestra.

		self.udpsrc.set_property("port", self.puerto)

		if self.decoder == 0:
			self.depay = Gst.ElementFactory.make('rtph264depay', None)
			self.decodebin = Gst.ElementFactory.make('avdec_h264', None)
			cadena = "application/x-rtp, media=(string)video, clock-rate=(int)90000, decoding-name=(string)h264, payload=(int)96"

		elif self.decoder == 1:
			self.depay = Gst.ElementFactory.make('rtph265depay', None)
			self.decodebin = Gst.ElementFactory.make('avdec_h265', None)
			cadena = "application/x-rtp, media=(string)video, clock-rate=(int)90000, decoding-name=(string)h265, payload=(int)96"
		
		else:
			print("ERROR: Decoder selection not valid.")
			sys.exit(1)


		if(not self.pipeline or not self.udpsrc or not self.depay or not self.vc or not self.sink or not self.decodebin or not self.buffer):
			print("ERROR: Could not create all elements")
			sys.exit(1)

		# Añadimos los elementos al pipeline.

		self.pipeline.add(self.udpsrc)
		self.pipeline.add(self.depay)
		self.pipeline.add(self.vc)
		self.pipeline.add(self.decodebin)
		self.pipeline.add(self.sink)
		self.pipeline.add(self.buffer)

		
		if not self.udpsrc.link_filtered(self.buffer, Gst.caps_from_string(cadena)):
			print("ERROR: Could not link 'udpsrc' to buffer")

		if not self.buffer.link(self.depay):
			print("ERROR: Could not link 'buffer' to depay")

		if not self.depay.link(self.decodebin):
			print("ERROR: Could not link 'depay' to decodebin")

		if not self.decodebin.link(self.vc):
			print("ERROR: Could not link 'decodebin' to vc")

		if not self.vc.link(self.sink):
			print("ERROR: Could not link 'vc' to sink")

	
		ret = self.pipeline.set_state(Gst.State.PLAYING)
		if ret == Gst.StateChangeReturn.FAILURE:
			print("ERROR: Unable to set the pipeline to the playing state")
			return False

		return True

		
	def on_sync_message(self, bus, message):
		if message.get_structure() is None:
			return True
		message_name = message.get_structure().get_name()
		if message_name == 'prepare-window-handle': #Assign the window id to display in
			imagesink = message.src
			imagesink.set_window_handle(self.X_id)
		return True
		

	def on_error(self, msg):
		print('on_error():', msg.parse_error())

	def quit(self, event):
		self.pipeline.set_state(Gst.State.NULL)
		event.Skip()

app = Receptor()
app.MainLoop()