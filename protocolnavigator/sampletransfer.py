import wx
from experimentsettings import *
from wx.lib.masked import NumCtrl
from addrow import RowBuilder
from collections import OrderedDict

ICON_SIZE = 22.0
meta = ExperimentSettings.getInstance()
########################################################################        
########       Popup Dialog showing sample transfer activity        ####
########################################################################            
class SampleTransferDialog(wx.Dialog):
    def __init__(self, parent, cell_line, h_inst, s_inst,  token, vesselpanel, vesselScroller, platedesign, harvest_location):
	wx.Dialog.__init__(self, parent, -1, "Sample transfer", size=(750,550), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
	
	self.settings_controls = {}
	
	self.cell_line = cell_line
	self.h_inst = h_inst
	self.s_inst = s_inst
	self.token = token
	self.vesselpanel = vesselpanel
	self.vesselScroller = vesselScroller
	self.platedesign = platedesign
	self.mandatory_tags = []
	
	self.splitwindow = wx.SplitterWindow(self)
	self.top_panel = wx.ScrolledWindow(self.splitwindow)
	self.bot_panel = wx.Panel(self.splitwindow)
	
	self.splitwindow.SplitHorizontally(self.top_panel, self.bot_panel)
	self.splitwindow.SetSashGravity(0.3)	
	
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl',50, -1, '']),
		                              ('Description', ['TextCtrl', 100, -1, '']),
		                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
		                              ('Temp\n(C)', ['TextCtrl', 30, -1, '']),
		                              ('Tips', ['TextCtrl', 50, -1, ''])
		                            ])		
	
	#------- Harvesting ---#
	h_fgs = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	pic=wx.StaticBitmap(self.top_panel)
	pic.SetBitmap(icons.harvest.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	text = wx.StaticText(self.top_panel, -1, 'Harvested from %s'%harvest_location)
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	h_titleSizer = wx.BoxSizer(wx.HORIZONTAL)
	h_titleSizer.Add(pic)
	h_titleSizer.AddSpacer((5,-1))	
	h_titleSizer.Add(text, 0)	
	h_titleSizer.Add((-1,5))
	# Cell Line 
	self.h_cell_line = wx.TextCtrl(self.top_panel, -1, value=self.cell_line, style=wx.TE_PROCESS_ENTER) 
	self.h_cell_line.Disable()
	h_fgs.Add(wx.StaticText(self.top_panel, -1, 'Cell Line'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	h_fgs.Add(self.h_cell_line, 0, wx.EXPAND)
	h_fgs.Add(wx.StaticText(self.top_panel, -1, ''), 0)
	# Density - value
	hdensityTAG = 'Transfer|Harvest|HarvestingDensity|%s'%self.h_inst
	harvestdensity = meta.get_field(hdensityTAG, [])
	self.settings_controls[hdensityTAG+'|0'] = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(harvestdensity) > 0:
	    self.settings_controls[hdensityTAG+'|0'].SetValue(harvestdensity[0])		
	self.settings_controls[hdensityTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	unit_choices =['nM2', 'uM2', 'mM2','Other']	
	self.settings_controls[hdensityTAG+'|1'] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(harvestdensity) > 1:
	    self.settings_controls[hdensityTAG+'|1'].SetStringSelection(harvestdensity[1])
	self.settings_controls[hdensityTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	h_fgs.Add(wx.StaticText(self.top_panel, -1, 'Density'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	h_fgs.Add(self.settings_controls[hdensityTAG+'|0'], 0, wx.EXPAND)	
	h_fgs.Add(self.settings_controls[hdensityTAG+'|1'], 0, wx.EXPAND)
	# Process
	staticbox = wx.StaticBox(self.top_panel, -1, "Procedure")
	h_proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	h_procedure = RowBuilder(self.top_panel, 'Transfer|Harvest|%s'%self.h_inst, self.token, COLUMN_DETAILS, self.mandatory_tags)
	h_proceduresizer.Add(h_procedure, 0, wx.ALL, 5)	
	
	hSizer = wx.BoxSizer(wx.VERTICAL)
	hSizer.Add(h_titleSizer)
	hSizer.AddSpacer((-1,10))
	hSizer.Add(h_fgs)
	hSizer.Add(h_proceduresizer)
	
	#------- Seeding ---#
	s_fgs = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	pic=wx.StaticBitmap(self.top_panel)
	pic.SetBitmap(icons.seed.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	text = wx.StaticText(self.top_panel, -1, 'Seed')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	s_titleSizer = wx.BoxSizer(wx.HORIZONTAL)
	s_titleSizer.Add(pic)
	s_titleSizer.AddSpacer((5,-1))	
	s_titleSizer.Add(text, 0)	
	s_titleSizer.Add((-1,5))
	# Cell Line 
	self.s_cell_line = wx.TextCtrl(self.top_panel, -1, value=self.cell_line, style=wx.TE_PROCESS_ENTER) 
	self.s_cell_line.Disable()
	s_fgs.Add(wx.StaticText(self.top_panel, -1, 'Cell Line'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	s_fgs.Add(self.s_cell_line, 0, wx.EXPAND)
	s_fgs.Add(wx.StaticText(self.top_panel, -1, ''), 0)
	# Density - value
	seeddensityTAG = 'Transfer|Seed|SeedingDensity|%s'%self.s_inst
	seeddensity = meta.get_field(seeddensityTAG, [])
	self.settings_controls[seeddensityTAG+'|0'] = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(seeddensity) > 0:
	    self.settings_controls[seeddensityTAG+'|0'].SetValue(seeddensity[0])	
	self.settings_controls[seeddensityTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	unit_choices =['nM2', 'uM2', 'mM2','Other']
	self.settings_controls[seeddensityTAG+'|1'] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(seeddensity) > 1:
	    self.settings_controls[seeddensityTAG+'|1'].SetStringSelection(seeddensity[1])
	self.settings_controls[seeddensityTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	s_fgs.Add(wx.StaticText(self.top_panel, -1, 'Density'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	s_fgs.Add(self.settings_controls[seeddensityTAG+'|0'], 0, wx.EXPAND)	
	s_fgs.Add(self.settings_controls[seeddensityTAG+'|1'], 0, wx.EXPAND)	
	# Process
	staticbox = wx.StaticBox(self.top_panel, -1, "Procedure")
	s_proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	s_procedure = RowBuilder(self.top_panel, 'Transfer|Seed|%s'%self.s_inst, self.token, COLUMN_DETAILS, self.mandatory_tags)
	s_proceduresizer.Add(s_procedure, 0, wx.ALL, 5)   
	
	sSizer = wx.BoxSizer(wx.VERTICAL)
	sSizer.Add(s_titleSizer)
	sSizer.AddSpacer((-1,10))
	sSizer.Add(s_fgs)
	sSizer.Add(s_proceduresizer)
	
	infoSizer = wx.BoxSizer(wx.HORIZONTAL)
	infoSizer.Add(hSizer, 1, wx.ALL|wx.EXPAND, 10)
	infoSizer.Add(sSizer, 1, wx.ALL|wx.EXPAND, 10)
	       
	
	# VESSEL Panel 
	label = wx.StaticText(self.bot_panel, -1, 'Select Destination Vessel(s)')
	font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)
	label.SetFont(font)
	self.vpanel = self.vesselScroller(self.bot_panel)
	for plate_id in sorted(self.platedesign.get_plate_ids(), key=meta.alphanumeric_sort):
	    self.vpanel.add_vessel_panel(
	        self.vesselpanel(self.vpanel, plate_id),
	        plate_id)
	self.done = wx.Button(self, wx.ID_OK, 'Transfer')
	self.cancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')

	button_sizer = wx.BoxSizer(wx.HORIZONTAL)
	button_sizer.AddStretchSpacer()
	button_sizer.Add(self.done)
	button_sizer.AddSpacer((10,-1))
	button_sizer.Add(self.cancel)
	
	#---------------Layout with sizers---------------		
	top_sizer = wx.BoxSizer(wx.VERTICAL)
	top_sizer.Add(infoSizer, 1, wx.EXPAND|wx.ALL, 10)
	self.top_panel.SetSizer(top_sizer)
	self.top_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	bot_sizer = wx.BoxSizer(wx.VERTICAL)
	bot_sizer.Add(label, 0, wx.ALL, 20)
	bot_sizer.Add(self.vpanel, 1, wx.EXPAND|wx.ALL, 10)
	self.bot_panel.SetSizer(bot_sizer)
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.splitwindow, 1, wx.EXPAND)
	self.Sizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 10)
	self.SetSizer(self.Sizer)	
		
    def get_selected_platewell_ids(self):
	return self.vpanel.get_selected_platewell_ids()     
    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	meta.saveData(ctrl, tag, self.settings_controls)    