import wx
from experimentsettings import *

########################################################################        
########       Popup Dialog showing multiline text                  ####
########################################################################            
class MultiLineShow(wx.Dialog):
    def __init__(self, parent, noteType, timepoint, page_counter, mltext):
        wx.Dialog.__init__(self, parent, -1, size=(470,620), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
	
	meta = ExperimentSettings.getInstance()
		
	self.noteType = noteType
	self.timepoint = timepoint
	self.page_counter = page_counter
	self.multi_line_text = mltext
	
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

        self.ok_btn = wx.Button(self, wx.ID_OK)
	
	self.butt_sizer = wx.BoxSizer(wx.HORIZONTAL)
	self.butt_sizer.Add(self.ok_btn, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
	
	self.createNotePad()
 

	#---------------Layout with sizers---------------
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)	
	self.Sizer.Add(self.butt_sizer,  0, wx.ALL|wx.ALIGN_RIGHT, 5)			

    
    def createNotePad(self):	
	self.noteDescrip = wx.TextCtrl(self.sw,  value=self.multi_line_text, style=wx.TE_MULTILINE|wx.TE_READONLY)
	self.swsizer.Add(self.noteDescrip, 1, wx.EXPAND|wx.ALL, 10)	    

	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	self.sw.Refresh()

