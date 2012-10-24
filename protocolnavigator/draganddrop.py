import wx
import sys
from experimentsettings import *

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class FileListDialog(wx.Dialog):
    def __init__(self, parent, tag_prefix, selection_mode):
        wx.Dialog.__init__(self, parent, -1, size=(550,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.label = wx.StaticText(self, -1, "Drop some files here:")
        self.text_box = wx.TextCtrl(self, -1, "",style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
        
        self.drop_target = MyFileDropTarget(self.text_box)
        self.text_box.SetDropTarget(self.drop_target)        
        
        self.selection_btn = wx.Button(self, wx.ID_OK, 'Selection complete')
        self.close_btn = wx.Button(self, wx.ID_CANCEL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.selection_btn, 1)
        hbox.Add(self.close_btn, 1)
        vbox.Add(self.label, 0, wx.ALL, 5)
        vbox.Add(self.text_box, 1, wx.EXPAND|wx.ALL, 5)
        vbox.Add(hbox, 1, wx.ALIGN_RIGHT, 5)
        
        self.SetSizer(vbox)
        self.Center()
 

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.filelist = []

    def OnDropFiles(self, x, y, filenames):
        self.filelist = filenames
        for file in filenames:
            self.window.AppendText("%s\n" % file)
        
            


        