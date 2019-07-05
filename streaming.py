import sys
import os
import wx
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

class Streaming( ):

	def __init__(self):

		# Preparamos la informacion relativa a la ventana

		self.ip = sys.argv[1]
		self.puerto = int(sys.argv[2])
		self.valor = int(sys.argv[3])

		self.stop = False
		signal.signal(signal.SIGINT, self.exit)
		signal.signal(signal.SIGTERM, self.exit)

		# Creamos el Pipeline para Gstreamer

		self.pipeline = Gst.Pipeline.new()

		# Creamos el bus, que trata los eventos del pipeline.

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect('message::error', self.on_error)
		

		# Definimos los elementos que añadiremos al pipeline. Emisor.

		self.videosrc = Gst.ElementFactory.make('autovideosrc', None)	# El src, capturador de imagenes. Primera parte del pipeline.	
		self.vc = Gst.ElementFactory.make('videoconvert', None)			# Cambia el espacio de color del video.
		self.buffer = Gst.ElementFactory.make('rtpjitterbuffer', None)	# Buffer que nos permite solucionar algunos problemas de inestabilidad de la red.
		self.sink = Gst.ElementFactory.make('udpsink', None)			# Manda los datos por la red via UDP.

		if self.valor == 0:
			self.encoder = Gst.ElementFactory.make('x264enc', None)		# Encoder 264
			self.encoder.set_property("tune", "zerolatency")
			self.pay = Gst.ElementFactory.make('rtph264pay', None)		# Es el Payload-encoder de H264 para meter el video en los paquetes RTP. Empaquetador.

		if self.valor == 1:
			self.encoder = Gst.ElementFactory.make('x265enc', None)		# Encoder 265
			self.pay = Gst.ElementFactory.make('rtph265pay', None)		# Es el Payload-encoder de H265 para meter el video en los paquetes RTP. Empaquetador.


		self.sink.set_property("host", self.ip)							# Asignamos la IP destino (host) al emisor.
		self.sink.set_property("port", self.puerto)						# Asignamos el puerto al emisor.


		if(not self.pipeline or not self.videosrc or not self.pay or not self.vc or not self.sink or not self.encoder or not self.buffer):
			print("ERROR: Could not create all elements")
			sys.exit(1)

		# Añadimos los elementos al pipeline.

		self.pipeline.add(self.videosrc)
		self.pipeline.add(self.pay)
		self.pipeline.add(self.vc)
		self.pipeline.add(self.encoder)
		self.pipeline.add(self.sink)


		if not self.videosrc.link(self.vc):
			print("ERROR: Could not link 'videosrc' to vc")

		if not self.vc.link(self.encoder):
			print("ERROR: Could not link 'vc' to encoder")

		if not self.encoder.link(self.pay):
			print("ERROR: Could not link 'encoder' to pay")

		if not self.pay.link(self.sink):
			print("ERROR: Could not link 'pay' to sink")

	def run(self):
		ret = self.pipeline.set_state(Gst.State.PLAYING)
		if ret == Gst.StateChangeReturn.FAILURE:
			print("ERROR: Unable to set the pipeline to the playing state")
			sys.exit(1)
		
		while self.stop == False:
			time.sleep(1)

	def quit(self, event):
		self.pipeline.set_state(Gst.State.NULL)
		event.Skip()

	def on_error(self, msg):
		print('on_error():', msg.parse_error())

	def exit(self, signum, frame):
		self.stop = True

if __name__ == '__main__':
	streaming = Streaming()
	streaming.run()
	