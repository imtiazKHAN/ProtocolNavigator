import wx
import sys
import wx.lib.mixins.listctrl as listmix
import icons
from experimentsettings import *
from wx.lib.agw import ultimatelistctrl as ULC

DATA_METADATA = {}

class ShowMetaDataLinkListDialog(wx.Dialog):
    def __init__(self, parent, file_paths):
        wx.Dialog.__init__(self, parent, -1, size=(700,350), title='Metadata Links', style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = ULC.ULC_REPORT|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)       
        
        meta = ExperimentSettings.getInstance()

        self.ultimateList.InsertColumn(0, 'Data URL')
        self.ultimateList.InsertColumn(1, 'Metadata')
	self.ultimateList.SetColumnWidth(0, 190)
	self.ultimateList.SetColumnWidth(1, 300)
	self.data_metadata = DATA_METADATA
	
        for data_file_path in file_paths:
	    index = self.ultimateList.InsertStringItem(sys.maxint, data_file_path, self.data_metadata)
	    self.data_metadata[data_file_path] = ''
	    text_ctrl = wx.TextCtrl(self.ultimateList, -1, "",style=wx.TE_READONLY)
	    self.drop_target = MyFileDropTarget(text_ctrl, data_file_path)
	    text_ctrl.SetDropTarget(self.drop_target)  
	    self.ultimateList.SetItemWindow(index, 1, wnd=text_ctrl, expand=True)
        
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
        self.Show()

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window, fp):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.fp = fp
	
    def OnDropFiles(self, x, y, filenames):
	if len(filenames)>1:
	    error_dia = wx.MessageDialog(None, 'Only 1 metadata file can be linked per data file' %filenames[0], 'Error', wx.OK | wx.ICON_ERROR)
	    if error_dia.ShowModal() == wx.ID_OK:	 
		return
	self.window.AppendText("%s" % filenames[0]) # single metadata file url per image/data
	DATA_METADATA[self.fp] = filenames[0]