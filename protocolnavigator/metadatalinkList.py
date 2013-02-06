import wx
import sys
import wx.lib.mixins.listctrl as listmix
import icons
from experimentsettings import *
from wx.lib.agw import ultimatelistctrl as ULC


class ShowMetaDataLinkListDialog(wx.Dialog):
    def __init__(self, parent, file_paths):
        wx.Dialog.__init__(self, parent, -1, size=(500,350), title='Metadata Links', style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = ULC.ULC_REPORT|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)       
        
        meta = ExperimentSettings.getInstance()

        self.ultimateList.InsertColumn(0, 'Data URL')
        self.ultimateList.InsertColumn(1, 'Metadata')
	self.ultimateList.SetColumnWidth(0, 190)
	self.ultimateList.SetColumnWidth(1, 300)
	
	self.settings_controls = {}
        self.files_metadata = {}
	
        for fp in file_paths:
            index = self.ultimateList.InsertStringItem(sys.maxint, fp)
	    self.files_metadata[fp] = ''
	    
	    #self.settings_controls[fp] = wx.TextCtrl(self.ultimateList,  value='', style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	    self.settings_controls[fp] = wx.TextCtrl(self.ultimateList, -1, "",style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
	    self.drop_target = MyFileDropTarget(self.settings_controls[fp])
	    #self.settings_controls[fp].Bind(wx.EVT_TEXT, self.SavingMetadata)
	    self.ultimateList.SetItemWindow(index, 1, wnd=self.settings_controls[fp], expand=True)
        
        self.ok_btn = wx.Button(self, wx.ID_OK)
	self.cancel_btn = wx.Button(self, wx.ID_CANCEL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.ultimateList, 1, wx.EXPAND)
        hbox2.Add(self.ok_btn, 1)
	hbox2.AddSpacer((10,-1))
	hbox2.Add(self.cancel_btn, 1)
        vbox.Add(hbox1, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        vbox.Add(hbox2, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        self.SetSizer(vbox)
        self.Center()


    def SavingMetadata(self, event):
	ctrl = event.GetEventObject()
	file_path = [fp for fp, c in self.settings_controls.items() if c==ctrl][0]
	self.files_metadata[file_path] = ctrl.GetValue()

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