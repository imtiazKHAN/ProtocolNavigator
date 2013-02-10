import wx
import sys
import icons
from experimentsettings import *

meta = ExperimentSettings.getInstance()

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class FileListDialog(wx.Dialog):
    def __init__(self, parent, tag, file_list):
        wx.Dialog.__init__(self, parent, -1, "Linking data files", size=(550,300), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.file_list = file_list
        self.tag = tag
        
        self.label = wx.StaticText(self, -1, "Drag and drop files in the box bellow")
        self.text_box = wx.TextCtrl(self, -1, "",style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
        self.drop_target = MyFileDropTarget(self.text_box)
        self.text_box.SetDropTarget(self.drop_target)        
	
        cut_bmp = icons.cut.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	self.clear_btn = wx.BitmapButton(self, wx.ID_CLEAR, cut_bmp)
	self.clear_btn.SetToolTipString("Clear file links.")
        self.ok_btn = wx.Button(self, wx.ID_OK)
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL)
       
        self.clear_btn.Bind(wx.EVT_BUTTON, self.clearList)
        
        self.drop_target.showFiles()
        
        # Sizers
	container = wx.BoxSizer(wx.VERTICAL)
	container.Add(self.label, 0, wx.ALL, 5)
	container.Add(self.text_box, 1, wx.EXPAND|wx.ALL, 5)	
	bottom = wx.BoxSizer(wx.HORIZONTAL)
	bottom.Add(self.clear_btn)
	bottom.Add((0, 0), 1, wx.EXPAND)
	bottom.Add(self.ok_btn)
	bottom.AddSpacer((5,-1))
	bottom.Add(self.cancel_btn)
	container.Add(bottom, 0, wx.ALL|wx.EXPAND, 5)        
        self.SetSizer(container)
        self.Show()
        
        
    def clearList(self, event):
        if self.file_list:
            del self.file_list[:]
            if meta.get_field(self.tag) is not None:
                meta.remove_field(self.tag)
        self.drop_target.showFiles()

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        list = []
        for file in filenames:
            list.append(file)
        self.window.GetParent().file_list.extend(list)    
        self.showFiles()
    
    def showFiles(self): 
        self.window.Clear()
        for f in self.window.GetParent().file_list:
            self.window.AppendText("%s\n" % f)
            
