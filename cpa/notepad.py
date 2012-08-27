import wx
import sys
import os
from experimentsettings import *

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class NotePad(wx.Dialog):
    def __init__(self, parent, noteType, timepoint, page_counter):
        wx.Dialog.__init__(self, parent, -1, size=(270,320), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        self.ok_btn = wx.Button(self, wx.ID_OK)
        self.close_btn = wx.Button(self, wx.ID_CANCEL)
	
	self.butt_sizer = wx.BoxSizer(wx.HORIZONTAL)
	self.butt_sizer.Add(self.ok_btn, 1)
	self.butt_sizer.AddSpacer((5,-1))
	self.butt_sizer.Add(self.close_btn, 1)

	meta = ExperimentSettings.getInstance()
	self.sw = wx.ScrolledWindow(self)
	self.noteType = noteType
	self.timepoint = timepoint
	self.page_counter = page_counter
 
	self.titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	self.top_fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)	
	self.bot_fgs = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
		
	self.noteSelect = wx.Choice(self.sw, -1,  choices=['CriticalPoint', 'Rest', 'Hint', 'URL', 'Video'])
	self.note_label = wx.StaticText(self.sw, -1, 'Note type')
	self.noteSelect.SetStringSelection('')
	self.noteSelect.Bind(wx.EVT_CHOICE, self.onCreateNotepad)
	self.titlesizer.Add(self.note_label)
	self.titlesizer.AddSpacer((10,-1))
	self.titlesizer.Add(self.noteSelect, 0, wx.EXPAND)
	
	#---------------Layout with sizers---------------
	self.mainSizer = wx.BoxSizer(wx.VERTICAL)
	self.mainSizer.Add(self.titlesizer)
	self.mainSizer.AddSpacer((-1,5))	
	self.mainSizer.Add(self.top_fgs)
	self.mainSizer.AddSpacer((-1,5))
	self.mainSizer.Add(self.bot_fgs)
	self.sw.SetSizer(self.mainSizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	if self.page_counter is not None:
	    self.createNotePad()
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)	
	self.Sizer.Add(self.butt_sizer,  0, wx.ALL|wx.ALIGN_RIGHT, 5)	
	
		

    def onCreateNotepad(self, event):
	ctrl = event.GetEventObject()
	self.noteType = ctrl.GetStringSelection()
	self.createNotePad()
    
    def createNotePad(self):	
	meta = ExperimentSettings.getInstance()
	
	self.note_label.Hide()
	self.noteSelect.Hide()	
	
	if self.noteType=='CriticalPoint':
	    self.noteDescrip = wx.TextCtrl(self.sw,  value=meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.noteDescrip.SetInitialSize((250, 300))
	
	    text = wx.StaticText(self.sw, -1, 'Critical Note')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)

	    self.titlesizer.Add(text, 0) 
	    self.bot_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.bot_fgs.Add(wx.StaticText(self.sw, -1, ''), 0)
	    
	if self.noteType=='Hint':
	    self.noteDescrip = wx.TextCtrl(self.sw,  value=meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.noteDescrip.SetInitialSize((250, 300))
	
	    text = wx.StaticText(self.sw, -1, 'Hint')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)
	    
	    self.titlesizer.Add(text, 0) 
	    self.bot_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.bot_fgs.Add(wx.StaticText(self.sw, -1, ''), 0)	
	    
	if self.noteType=='Rest':
	    self.noteDescrip = wx.TextCtrl(self.sw,  value=meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.noteDescrip.SetInitialSize((250, 300))
	    
	    text = wx.StaticText(self.sw, -1, 'Rest')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)
	    
	    self.titlesizer.Add(text, 0) 
	    self.bot_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.bot_fgs.Add(wx.StaticText(self.sw, -1, ''), 0)	
	

	if self.noteType == 'URL':
	    self.noteDescrip = wx.TextCtrl(self.sw,  value=meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter)), default='http://www.jove.com/'))
	    self.noteDescrip.SetInitialSize((250, 20))
	    
	    goURLBtn = wx.Button(self.sw, -1, 'Go to URL')
	    goURLBtn.Bind(wx.EVT_BUTTON, self.goURL)
	    text = wx.StaticText(self.sw, -1, 'URL')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)

	    self.titlesizer.Add(text, 0) 
	    self.top_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.top_fgs.Add(goURLBtn, 0)	    
	    
	if self.noteType == 'Video':
	    self.mediaTAG = 'Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter))
	    self.noteDescrip = wx.TextCtrl(self.sw, value=meta.get_field(self.mediaTAG, default=''))	    
	    self.browseBtn = wx.Button(self.sw, -1, 'Load Media File')
	    self.browseBtn.Bind(wx.EVT_BUTTON, self.loadFile)
	    self.mediaplayer = MediaPlayer(self.sw)
	    text = wx.StaticText(self.sw, -1, 'Video')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)	    
	    
	    if meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter))) is not None:	
		self.mediaplayer.mc.Load(meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter))))		
    
	    self.titlesizer.Add(text, 0) 
	    self.top_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.top_fgs.Add(self.browseBtn, 0)	    	
	    self.bot_fgs.Add(self.mediaplayer, 0)

	self.sw.SetSizer(self.mainSizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
	
    def loadFile(self, event):
	meta = ExperimentSettings.getInstance()
	dlg = wx.FileDialog(None, "Select a media file",
	                        defaultDir=os.getcwd(), wildcard='*.mp4;*.mp3;*.mpg;*.mid;*.wav; *.wmv;*.au;*.avi', style=wx.OPEN|wx.FD_CHANGE_DIR)
		# read the supp protocol file
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    self.noteDescrip.SetValue(file_path)
	    self.mediaplayer.mc.Load(file_path)
		
    def onFileLoad(self, event):
	self.path = self.fbb.GetValue()
	self.mediaplayer.mc.Load(self.path)    
    
    def goURL(self, event):
	try:
	    webbrowser.open(self.noteDescrip.GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return

    #def OnSavingData(self, event):	
	#meta = ExperimentSettings.getInstance()    
	#self.noteTAG = 'Notes|%s|Description|%s' %(self.noteType, str(self.page_counter))
	#meta.set_field(self.noteTAG, self.noteDescrip.GetValue())


class MediaPlayer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,  size=(250, 300))
        self.SetBackgroundColour(self.GetBackgroundColour())

        try:
            self.mc = wx.media.MediaCtrl(self)
        except:
            dial = wx.MessageDialog(None, 'Unable to play media file', 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.mc, 0, border=10)
        self.SetSizer(vsizer)
        
        self.mc.ShowPlayerControls()
