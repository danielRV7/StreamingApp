import wx

from ventanas import VentanaPrincipal

app = wx.App(False)
frame = VentanaPrincipal(None)
frame.Show(True)
app.MainLoop()