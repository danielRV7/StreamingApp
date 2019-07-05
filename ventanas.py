# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Mar 25 2019)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import subprocess

###########################################################################
## Class VentanaPrincipal
###########################################################################

class VentanaPrincipal ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"JordiStream 2.0", pos = wx.DefaultPosition, size = wx.Size( 749,505 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.SetBackgroundColour( wx.Colour( 253, 204, 101 ) )

		Cuadricula = wx.GridSizer( 5, 1, 0, 0 )

		self.textobienvenida = wx.StaticText( self, wx.ID_ANY, u"Bienvenido a la aplicación de streaming de la asignatura Comunicaciones Multimedia.", wx.Point( -1,-1 ), wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.textobienvenida.Wrap( -1 )

		self.textobienvenida.SetFont( wx.Font( 15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		Cuadricula.Add( self.textobienvenida, 0, wx.ALIGN_CENTER, 5 )

		direccionyPuerto = wx.BoxSizer( wx.HORIZONTAL )

		self.campoIP = wx.TextCtrl( self, wx.ID_ANY, u"Dirección IP", wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.campoIP.SetMaxLength( 0 )
		self.campoIP.SetBackgroundColour( wx.Colour( 230, 230, 229 ) )

		direccionyPuerto.Add( self.campoIP, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.campoPuerto = wx.TextCtrl( self, wx.ID_ANY, u"Puerto", wx.DefaultPosition, wx.Size( 100,-1 ), 0 )
		self.campoPuerto.SetMaxLength( 0 )
		self.campoPuerto.SetBackgroundColour( wx.Colour( 230, 230, 229 ) )

		direccionyPuerto.Add( self.campoPuerto, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		Cuadricula.Add( direccionyPuerto, 1, wx.ALIGN_CENTER, 5 )

		codecsChoices = [ u"H.264", u"H.265" ]
		self.codecs = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, codecsChoices, 0 )
		self.codecs.SetSelection( 0 )
		Cuadricula.Add( self.codecs, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.botonPlay = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0|wx.BORDER_NONE )

		self.botonPlay.SetBitmap( wx.Bitmap( u"play-circle.png", wx.BITMAP_TYPE_ANY ) )
		Cuadricula.Add( self.botonPlay, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		self.SetSizer( Cuadricula )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.botonPlay.Bind( wx.EVT_BUTTON, self.lanzarStream )

		self.streaming = None
		self.receptor = None

	def __del__( self ):
		if self.streaming:
			self.streaming.terminate()
		
		if self.receptor:
			self.receptor.terminate()

	# Virtual event handlers, overide them in your derived class
	def lanzarStream( self, event ):
		self.streaming = subprocess.Popen(['python3','streaming.py',self.campoIP.GetValue(), self.campoPuerto.GetValue(), str(self.codecs.GetSelection())])
		self.receptor = subprocess.Popen(['python3', 'receptor.py', self.campoPuerto.GetValue(), str(self.codecs.GetSelection())])
		