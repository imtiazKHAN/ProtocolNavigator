import wx
import sys
from experimentsettings import *

meta = ExperimentSettings.getInstance()

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class FileListDialog(wx.Dialog):
    def __init__(self, parent, tag, file_list):
        wx.Dialog.__init__(self, parent, -1, size=(550,300), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.label = wx.StaticText(self, -1, "Drag and drop files in the box bellow")
        self.text_box = wx.TextCtrl(self, -1, "",style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
        self.file_list = file_list
        self.tag = tag
        
        self.drop_target = MyFileDropTarget(self.text_box)
        self.text_box.SetDropTarget(self.drop_target)        
        
        self.ok_btn = wx.Button(self, wx.ID_OK, 'Done')
        self.clear_btn = wx.Button(self, wx.ID_CLEAR)
        
        self.clear_btn.Bind(wx.EVT_BUTTON, self.clearList)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.clear_btn, 1, wx.ALL, 5)
        hbox.Add(self.ok_btn, 1, wx.ALL, 5)
        vbox.Add(self.label, 0, wx.ALL, 5)
        vbox.Add(self.text_box, 1, wx.EXPAND|wx.ALL, 5)
        vbox.Add(hbox, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        
        self.SetSizer(vbox)
        self.Center()
        self.drop_target.showFiles()
        
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
            
