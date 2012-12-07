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
    def __init__(self, parent, cell_line, h_inst, s_inst,  vesselpanel, vesselScroller, platedesign):
	wx.Dialog.__init__(self, parent, -1, size=(650,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
	
	self.settings_controls = {}
	
	self.cell_line = cell_line
	self.h_inst = h_inst
	self.s_inst = s_inst	
	self.vesselpanel = vesselpanel
	self.vesselScroller = vesselScroller
	self.platedesign = platedesign
	
	# ****** initiates the ctrls like metadata panel with self.settings_controls  ***********
	
	self.splitwindow = wx.SplitterWindow(self)
	self.top_panel = wx.ScrolledWindow(self.splitwindow)
	self.bot_panel = wx.Panel(self.splitwindow)
	
	self.splitwindow.SplitHorizontally(self.top_panel, self.bot_panel)
	self.splitwindow.SetSashGravity(0.3)	
	
	#------- Harvesting ---#
	h_fgs = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	pic=wx.StaticBitmap(self.top_panel)
	pic.SetBitmap(icons.harvest.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	text = wx.StaticText(self.top_panel, -1, 'Harvest')
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
	self.h_cell_density = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(harvestdensity) > 0:
	    self.h_cell_density.SetValue(harvestdensity[0])		
	unit_choices =['nM2', 'uM2', 'mM2','Other']	
	self.h_cell_dunit = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(harvestdensity) > 1:
	    self.h_cell_dunit.SetStringSelection(harvestdensity[1])
	h_fgs.Add(wx.StaticText(self, -1, 'Density'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	h_fgs.Add(self.h_cell_density, 0, wx.EXPAND)	
	h_fgs.Add(self.h_cell_dunit, 0, wx.EXPAND)
	# Process
	staticbox = wx.StaticBox(self.top_panel, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl',50, -1, '']),
                                      ('Description', ['TextCtrl', 100, -1, '']),
                                      ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                      ('Temp\n(C)', ['TextCtrl', 30, -1, '']),
                                      ('Tips', ['TextCtrl', 50, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.top_panel, 'Transfer|Harvest|%s'%self.sample_inst, 'Step', COLUMN_DETAILS)
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	hSizer = wx.BoxSizer(wx.VERTICAL)
	hSizer.Add(h_titleSizer)
	hSizer.AddSpacer((-1,10))
	hSizer.Add(h_fgs)
	hSizer.Add(proceduresizer)
	
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
	seeddensity = meta.get_field('Transfer|Seed|SeedingDensity|%s'%self.sample_inst, [])
	self.s_cell_density = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(seeddensity) > 0:
	    self.s_cell_density.SetValue(seeddensity[0])			
	self.s_cell_dunit = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(seeddensity) > 1:
	    self.s_cell_dunit.SetStringSelection(seeddensity[1])
	s_fgs.Add(wx.StaticText(self.top_panel, -1, 'Density'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	s_fgs.Add(self.s_cell_density, 0, wx.EXPAND)	
	s_fgs.Add(self.s_cell_dunit, 0, wx.EXPAND)	
	# Process
	staticbox = wx.StaticBox(self.top_panel, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl',50, -1, '']),
                                      ('Description', ['TextCtrl', 100, -1, '']),
                                      ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                      ('Temp\n(C)', ['TextCtrl', 30, -1, '']),
                                      ('Tips', ['TextCtrl', 50, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.top_panel, 'Transfer|Seed|%s'%self.sample_inst, 'Step', COLUMN_DETAILS)
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)   
	
	sSizer = wx.BoxSizer(wx.VERTICAL)
	sSizer.Add(s_titleSizer)
	sSizer.AddSpacer((-1,10))
	sSizer.Add(s_fgs)
	sSizer.Add(proceduresizer)
	
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