import wx
import os

class Viewer(wx.Frame):
	picPanel=None
	dash=None
	nextButton=None
	prevButton=None
	piclist=None
	albumSize=0
	def __init__(self,title,winsize,folder):
		
		wx.Frame.__init__(self,None,title=title,size=winsize)
		self.Bind(wx.EVT_CLOSE,self.onClose)
		self.setAlbumFolder(folder)
		panel=wx.Panel(self)
		picPanel=wx.Panel(panel,size=(400,400))
		dash=wx.BoxSizer(wx.HORIZONTAL)
		nextButton=wx.Button(panel,label=">")
		prevButton=wx.Button(panel,label="<")
		dash.Add(prevButton,0,wx.LEFT)
		dash.Add(nextButton,0,wx.RIGHT)
		mainBox=wx.BoxSizer(wx.VERTICAL)
		mainBox.Add(picPanel,0,wx.EXPAND)
		mainBox.Add(dash,0,wx.BOTTOM)
		bimg=wx.Image(self.piclist[0]).ConvertToBitmap()
		#picPanel.bitmap1=wx.StaticBitmap(self,-1,bimg,(0,0))
		dc=wx.WindowDC(picPanel)
		dc.Clear()
		dc.DrawBitmap(bimg, 0, 0)
		panel.SetSizer(mainBox)
		panel.Layout()
	def onClose(self,event)	:
		self.Destroy()
	
	def setAlbumFolder(self,x):
		if os.access(x,os.R_OK)==False:
			return
		z=os.listdir(x)
		if x.endswith("/")==False:
			x=x+"/"
		self.piclist={}
		self.albumSize=0
		for y in z:
			if y.endswith(".jpg") or y.endswith(".gif") or y.endswith(".png"):
				self.piclist[self.albumSize]=x+y
				self.albumSize=self.albumSize+1



app=wx.App(redirect=False)

view=Viewer(title="AeosPy Viewer",winsize=(500,400),folder="/home/riju/Pictures/")
view.Show()

app.MainLoop()
