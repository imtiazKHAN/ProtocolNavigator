import wx
import sys
import os
from experimentsettings import *

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class NotePad(wx.Dialog):
    def __init__(self, parent, noteType, timepoint, page_counter):
        wx.Dialog.__init__(self, parent, -1, size=(470,620), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
	
	meta = ExperimentSettings.getInstance()
		
	self.noteType = noteType
	self.timepoint = timepoint
	self.page_counter = page_counter
	
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

        self.ok_btn = wx.Button(self, wx.ID_OK)
        self.close_btn = wx.Button(self, wx.ID_CANCEL)
	
	self.butt_sizer = wx.BoxSizer(wx.HORIZONTAL)
	self.butt_sizer.Add(self.ok_btn, 1)
	self.butt_sizer.AddSpacer((5,-1))
	self.butt_sizer.Add(self.close_btn, 1)
 
	self.titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	self.top_fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)	
	self.bot_fgs = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
		
	
	self.noteSelect = wx.RadioBox(self, -1, "Note Type", wx.DefaultPosition, wx.DefaultSize,
		        ['Text', 'URL', 'MultiMedia', 'None'], 1, wx.RA_SPECIFY_ROWS
		        )
	if self.noteType:
	    self.noteSelect.SetStringSelection(self.noteType)
	    self.createNotePad()
	else:
	    self.noteSelect.SetStringSelection('None')
	    self.noteSelect.Bind(wx.EVT_RADIOBOX, self.onCreateNotepad)
	self.titlesizer.Add(self.noteSelect, 1, wx.ALL|wx.EXPAND, 5)		
	
	#---------------Layout with sizers---------------
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.titlesizer, 0)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)	
	self.Sizer.Add(self.butt_sizer,  0, wx.ALL|wx.ALIGN_RIGHT, 5)			

    def onCreateNotepad(self, event):
	ctrl = event.GetEventObject()
	self.noteType = ctrl.GetStringSelection()
	self.createNotePad()
    
    def createNotePad(self):	
	meta = ExperimentSettings.getInstance()
	
	self.noteSelect.Disable()	
	
	if self.noteType=='Text':
	    self.noteDescrip = wx.TextCtrl(self.sw,  value=meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.swsizer.Add(self.noteDescrip, 1, wx.EXPAND|wx.ALL, 10)	    

	if self.noteType == 'URL':
	    self.noteDescrip = wx.TextCtrl(self.sw,  value=meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter)), default=''))
	    self.noteDescrip.SetInitialSize((250, 20))
	    
	    goURLBtn = wx.Button(self.sw, -1, 'Go to URL')
	    goURLBtn.Bind(wx.EVT_BUTTON, self.goURL)
	    
	    urlsizer = wx.BoxSizer(wx.HORIZONTAL)
	    urlsizer.Add(self.noteDescrip, 0, wx.EXPAND|wx.ALL, 10)
	    urlsizer.Add(goURLBtn, 0, wx.ALIGN_CENTER_VERTICAL)
	    self.swsizer.Add(urlsizer, 0, wx.EXPAND|wx.ALL, 10)
	        
	if self.noteType == 'MultiMedia':
	    self.mediaTAG = 'Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter))
	    self.noteDescrip = wx.TextCtrl(self.sw, value=meta.get_field(self.mediaTAG, default=''))	    
	    self.browseBtn = wx.Button(self.sw, -1, 'Load Media File')
	    self.browseBtn.Bind(wx.EVT_BUTTON, self.loadFile)
	    self.mediaplayer = MediaPlayer(self.sw)	    
	    
	    if meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter))) is not None:	
		self.mediaplayer.mc.Load(meta.get_field('Notes|%s|%s|%s' %(self.noteType, str(self.timepoint), str(self.page_counter))))
		
		
	    mediasizer = wx.BoxSizer(wx.HORIZONTAL)
	    mediasizer.Add(self.noteDescrip, 0, wx.ALL, 10)
	    mediasizer.Add(self.browseBtn, 0, wx.ALIGN_CENTER_VERTICAL)
	    playersizer = wx.BoxSizer(wx.VERTICAL)
	    playersizer.Add(self.mediaplayer, 0, wx.ALIGN_CENTER_VERTICAL)
	    self.swsizer.Add(mediasizer, 0, wx.EXPAND|wx.ALL, 10)
	    self.swsizer.Add(playersizer, 1, wx.EXPAND|wx.ALL, 10)

	    
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	self.sw.Refresh()	

	
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
