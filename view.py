import wx
import os

class PicturePanel(wx.Panel):
	def __init__(self,parent):
		wx.Panel.__init__(self,parent,size=(600,300))
		self.frame=parent
		self.Bind(wx.EVT_PAINT,self.onPaint)
		
	def onPaint(self, evt):
		"""
		Add a picture to the background
		"""
		# yanked from ColourDB.py
		dc = None
		if not dc:
			dc = wx.ClientDC(self)
			rect = self.GetUpdateRegion().GetBox()
			dc.SetClippingRect(rect)
		dc.Clear()
		bmp = wx.Bitmap("/home/riju/Pictures/diwali.jpg")
		dc.DrawBitmap(bmp, 0, 0)


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
		dpanel=wx.Panel(self)
		panel=wx.Panel(self)
		picPanel=PicturePanel(self)
		dash=wx.BoxSizer(wx.HORIZONTAL)
		nextButton=wx.Button(dpanel,label=">")
		prevButton=wx.Button(dpanel,label="<")
		dpanel.SetSizer(dash)
		dpanel.Layout()
		dash.Add(prevButton,0,wx.LEFT)
		dash.Add(nextButton,0,wx.RIGHT)
		mainBox=wx.BoxSizer(wx.VERTICAL)
		mainBox.Add(picPanel,0,wx.EXPAND)
		mainBox.Add(dpanel,0,wx.BOTTOM)
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
