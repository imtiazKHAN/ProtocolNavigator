import wx
import re
import datetime
import experimentsettings as exp
import wx.lib.masked as masked
import locale
import math
import wx.lib.agw.flatnotebook as fnb
import random
from experimentsettings import ExperimentSettings
from wx.lib.masked import NumCtrl
from addrow import RowBuilder
from collections import OrderedDict
# TO DO: make the onSavingData coherent with experimentsettings file method. Also Step builder should use addrow.py ; Finally check current passage date is later than last passage date.

meta = exp.ExperimentSettings.getInstance()
#locale.setlocale(locale.LC_ALL, "")

STD_PROTOCOLS ={
'Passage' :{
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'HARVEST' : None,
    'VESSEL' : None,
    'Step1' : ['Remove','Remove medium with a stripette','','', ''],
    'Step2' : ['Trypsinise','Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    'Step3' : ['Check','Gently tip to ensure trypsin reaches all surfaces','','', ''],
    'Step4' : ['Remove','Immediately remove trypsin with either a pipette or syringe','','', ''],
    'Step5' : ['Add','Add approx. 0.5ml of trypsin as before, close the flask (if used)','','', ''],
    'Step6' : ['Incubate','Incubate','5','', 'Beware! A few cell lines need less than this'],
    'Step7' : ['Check','Check under the microscope to see if the cells are detached, Return to incubator for a further few minutes if not detached','','', ''],
    'Step8' : ['Add','Add medium (DMEM) to your dish or flask','','', ''],
    'Step9' : ['Flush','Flush off the cells and then pipette your trypsinised cells into the appropriate new container.','','', 'Excess cells should be placed in container and treated appropriately. Waste cells must not be sucked into traps.  The trypsin should not really be >10% of your final volume.  If it does you should spin down your cells (5mins at 1000rpm), draw off most of the supernatant and replace with fresh medium.'],
    },
'Seed': {
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['seed','Remove medium with a stripette','','', ''],
    'Step2' : ['seed','Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    },
'Freeze' :{
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['freeze','Remove medium with a stripette','','', ''],
    'Step2' : ['freeze','Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    },
'Enrich' :{
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['enrich','Sort cells in flowcytometer','','', ''],
    'Step2' : ['enrich','add medium','','', ''],
    }
 }
class MaintainAction(wx.Dialog):
    def __init__(self, parent, protocol, curractionNo, action_type, ldt):
        wx.Dialog.__init__(self, parent, -1, size=(850,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

	self.protocol = protocol
	self.curractionNo = curractionNo
	self.action_type = action_type
	self.last_date_time = ldt
	self.action_attr = '%s %s'%(self.action_type, str(self.curractionNo))		
	self.tag_stump = exp.get_tag_stump(self.protocol, 2)
	self.instance = exp.get_tag_attribute(self.protocol)		
	
	self.SetTitle(self.action_attr)
	
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	
	self.settings_controls = {}
	self.curr_protocol = {}
	self.admin_info = {}  	
	self.mandatory_tags = []
	self.labels = {}	
	
	# Set Protocol (if prev instance is there copy that else set STD protocol
	if meta.get_field(self.tag_stump+'|%s%s|%s' %(self.action_type, str(self.curractionNo-1), self.instance)):
	    d =  meta.get_field(self.tag_stump+'|%s%s|%s' %(self.action_type, str(self.curractionNo-1), self.instance))
	    for k, v in d:
		self.curr_protocol[k] = v		
	else:
	    self.curr_protocol = STD_PROTOCOLS[self.action_type]
    
	# Set the time	prev or curr
	if self.last_date_time:
	    self.initial_datetime = datetime.datetime(*map(int,self.last_date_time))
	else:
	    self.initial_datetime = datetime.datetime.now()
	
	self.sel_date_time = map(int, [self.initial_datetime.year,self.initial_datetime.month,self.initial_datetime.day,
	                               self.initial_datetime.hour,self.initial_datetime.minute, self.initial_datetime.second])
	# set the cell density    
	self.initial_seed_density = None	
	#self.curr_protocol['PD'] = []
	self.curr_protocol['HARVEST'] = []	

	if self.curr_protocol['SEED']:
	    self.initial_seed_density = self.curr_protocol['SEED'][0]

	#Admin	
	self.settings_controls['Admin|0'] = wx.TextCtrl(self.sw, size=(70,-1), value=self.curr_protocol['ADMIN'][0])	
	self.settings_controls['Admin|1'] = wx.DatePickerCtrl(self.sw, style = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
	self.settings_controls['Admin|1'].SetValue(wx.DateTimeFromDMY(self.initial_datetime.day, self.initial_datetime.month-1, self.initial_datetime.year))
	self.curr_protocol['ADMIN'][1] = str(self.initial_datetime.day)+'/'+str(self.initial_datetime.month)+'/'+str(self.initial_datetime.year)
	self.settings_controls['Admin|2'] = masked.TimeCtrl( self.sw, -1, name="24 hour control", fmt24hr=True )
	h = self.settings_controls['Admin|2'].GetSize().height
	spin1 = wx.SpinButton( self.sw, -1, wx.DefaultPosition, (-1,h), wx.SP_VERTICAL )
	self.settings_controls['Admin|2'].BindSpinButton( spin1 )
	self.settings_controls['Admin|2'].SetValue(wx.DateTimeFromHMS(self.initial_datetime.hour, self.initial_datetime.minute, self.initial_datetime.second))
	self.curr_protocol['ADMIN'][2] = str(self.initial_datetime.hour)+':'+str(self.initial_datetime.minute)+':'+str(self.initial_datetime.second)

	self.set_curr_time = wx.Button(self.sw, -1, 'Set Current Date Time')
	self.attr_fgs = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)
	
	if self.action_type == 'Seed': 
	    self.settings_controls['Seed|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Seed|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    self.settings_controls['Seed|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    vessel_types =['T75', 'T25', '6WellPlate','12WellPlate', 'Other']
	    self.settings_controls['Vessel|0'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (100,20), vessel_types, wx.LB_SINGLE)
	    if self.curr_protocol['VESSEL']:
		self.settings_controls['Vessel|0'].Append(self.curr_protocol['VESSEL'][0])
		self.settings_controls['Vessel|0'].SetStringSelection(self.curr_protocol['VESSEL'][0])
	    self.settings_controls['Vessel|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData)

	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Seed Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|0'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|1'], 0, wx.EXPAND)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Vessel Type'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Vessel|0'], 0, wx.EXPAND)	    
	
	if self.action_type == 'Passage': 
	    self.settings_controls['Harvest|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Harvest|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    self.settings_controls['Harvest|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Harvest|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)    
	    self.settings_controls['Seed|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Seed|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    self.settings_controls['Seed|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    vessel_types =['T75', 'T25', '6WellPlate','12WellPlate', 'Other']
	    self.settings_controls['Vessel|0'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (100,20), vessel_types, wx.LB_SINGLE)
	    if self.curr_protocol['VESSEL']:
		self.settings_controls['Vessel|0'].Append(self.curr_protocol['VESSEL'][0])
		self.settings_controls['Vessel|0'].SetStringSelection(self.curr_protocol['VESSEL'][0]) 		
	    self.settings_controls['Vessel|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Harvest Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Harvest|0'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Harvest|1'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, '(Re)seed Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|0'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|1'], 0, wx.EXPAND)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Vessel Type'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Vessel|0'], 0, wx.EXPAND)
	
	if self.action_type == 'Freeze':     
	    self.settings_controls['Split'] = wx.Choice(self.sw, -1,  choices= map(str, range(1,21)), style=wx.TE_PROCESS_ENTER)
	    self.settings_controls['Split'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	    self.settings_controls['Make'] = wx.TextCtrl(self.sw, size=(70,-1), value='Test')
	    self.settings_controls['Make'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Model'] = wx.TextCtrl(self.sw, size=(70,-1), value='Test')
	    self.settings_controls['Make'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Seed|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    self.settings_controls['Seed|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)	    
	    vessel_types =['T75', 'T25', '6WellPlate','12WellPlate', 'Other']
	    self.settings_controls['Vessel|0'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (100,20), vessel_types, wx.LB_SINGLE)
	    self.settings_controls['Vessel|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Split 1: '),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Split'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Make'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Make'], 0, wx.EXPAND)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' Model'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Model'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, '(Re)seed Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|0'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|1'], 0, wx.EXPAND)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Vessel Type'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Vessel|0'], 0, wx.EXPAND)
	    
	if self.action_type == 'Enrich':   
	    self.settings_controls['Split'] = wx.Choice(self.sw, -1,  choices= map(str, range(1,21)), style=wx.TE_PROCESS_ENTER)
	    self.settings_controls['Split'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	    self.settings_controls['Make'] = wx.TextCtrl(self.sw, size=(70,-1), value='Test')
	    self.settings_controls['Make'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Model'] = wx.TextCtrl(self.sw, size=(70,-1), value='Test')
	    self.settings_controls['Make'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Seed|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    self.settings_controls['Seed|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)	    
	    vessel_types =['T75', 'T25', '6WellPlate','12WellPlate', 'Other']
	    self.settings_controls['Vessel|0'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (100,20), vessel_types, wx.LB_SINGLE)
	    self.settings_controls['Vessel|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Split 1: '),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Split'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Flow Cytometer'),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ''),0)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Make'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Make'], 0, wx.EXPAND)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' Model'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Model'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, '(Re)seed Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|0'], 0, wx.EXPAND)
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Seed|1'], 0, wx.EXPAND)	    
	    self.attr_fgs.Add(wx.StaticText(self.sw, -1, 'Vessel Type'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    self.attr_fgs.Add(self.settings_controls['Vessel|0'], 0, wx.EXPAND)
	        
	self.selection_btn = wx.Button(self, wx.ID_OK, 'Record')
        self.close_btn = wx.Button(self, wx.ID_CANCEL)  
	
	#self.selection_btn.Disable()
	
	#Bind
	self.settings_controls['Admin|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls['Admin|1'].Bind(wx.EVT_DATE_CHANGED, self.OnSavingData)
	self.settings_controls['Admin|2'].Bind(wx.EVT_TEXT, self.OnSavingData)	 
	self.set_curr_time.Bind(wx.EVT_BUTTON, self.setCurrDateTime)

	# Sizers and layout
	staticbox = wx.StaticBox(self.sw, -1, "Admin")
	adminsizer = wx.StaticBoxSizer(staticbox, wx.HORIZONTAL)	
	adminsizer.Add(wx.StaticText(self.sw, -1, 'Operator Name'),0, wx.RIGHT, 5)
	adminsizer.Add(self.settings_controls['Admin|0'] , 0, wx.EXPAND)
	adminsizer.Add(wx.StaticText(self.sw, -1, 'Date'),0, wx.RIGHT|wx.LEFT, 5)
	adminsizer.Add(self.settings_controls['Admin|1'], 0, wx.EXPAND)
	adminsizer.Add(wx.StaticText(self.sw, -1, 'Time'),0, wx.LEFT, 5)
	adminsizer.Add(self.settings_controls['Admin|2'], 0, wx.EXPAND)
	adminsizer.Add( spin1, 0, wx.ALIGN_CENTRE )
	adminsizer.Add(self.set_curr_time, 0, wx.ALIGN_RIGHT|wx.LEFT, 15)

		
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	btnSizer.Add(self.selection_btn  , 0, wx.ALL, 5)
	btnSizer.Add(self.close_btn , 0, wx.ALL, 5)	
	
	self.step_fgs = wx.FlexGridSizer(cols=8, hgap=5, vgap=5)
	
	self.staticbox = wx.StaticBox(self.sw, -1, "Actions")
	self.staticbox_sizer = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)	
	self.staticbox_sizer.Add(self.attr_fgs, 0, wx.EXPAND|wx.ALL, 5)
	self.staticbox_sizer.Add((-1,10))
	self.staticbox_sizer.Add(self.step_fgs, 0, wx.EXPAND|wx.ALL, 5)	

	self.swsizer.Add(adminsizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(self.staticbox_sizer,0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.Sizer.Add(btnSizer)
	self.SetSizer(self.Sizer)

	self.showSteps()
	

    def showSteps(self):
	# get the sorted steps in passaging
	steps = sorted([step for step in self.curr_protocol.keys()
		 if step.startswith('Step')] , key = meta.stringSplitByNumbers)

	#-- Header --#	
	name_header = wx.StaticText(self.sw, -1, 'Name')
	desp_header = wx.StaticText(self.sw, -1, 'Description')
	dur_header = wx.StaticText(self.sw, -1, 'Duration\n(min)')
	temp_header = wx.StaticText(self.sw, -1, 'Temp\n(C)')
	tips_header = wx.StaticText(self.sw, -1, 'Tips')
	
	font = wx.Font(6, wx.SWISS, wx.NORMAL, wx.BOLD)
	name_header.SetFont(font)
	desp_header.SetFont(font)
	dur_header.SetFont(font)
	temp_header.SetFont(font)
	tips_header.SetFont(font)
	
	self.step_fgs.Add(wx.StaticText(self.sw, -1, ''))
	self.step_fgs.Add(name_header, 0, wx.ALIGN_CENTRE)
	self.step_fgs.Add(desp_header, 0, wx.ALIGN_CENTRE)
	self.step_fgs.Add(dur_header, 0, wx.ALIGN_CENTRE)
	self.step_fgs.Add(temp_header, 0, wx.ALIGN_CENTRE)
	self.step_fgs.Add(tips_header, 0, wx.ALIGN_CENTER)
	self.step_fgs.Add(wx.StaticText(self.sw, -1, ''))
	self.step_fgs.Add(wx.StaticText(self.sw, -1, ''))

	for step in steps:    
	    stepNo = int(step.split('Step')[1])
	    step_info =  self.curr_protocol[step]
	   
	    if not step_info:  # if this is newly added empty step
		step_info = ['','','','','']

	    #-- Widgets ---#
	    self.settings_controls[step+'|0'] = wx.TextCtrl(self.sw, size=(70,-1), value=step_info[0], style=wx.TE_PROCESS_ENTER)
	    self.settings_controls[step+'|1'] = wx.TextCtrl(self.sw, size=(200,-1), value=step_info[1], style=wx.TE_PROCESS_ENTER)
	    self.settings_controls[step+'|2'] = wx.TextCtrl(self.sw, size=(30,-1), value=step_info[2], style=wx.TE_PROCESS_ENTER)
	    self.settings_controls[step+'|3'] = wx.TextCtrl(self.sw, size=(30,-1), value=step_info[3], style=wx.TE_PROCESS_ENTER)	
	    self.settings_controls[step+'|4'] = wx.TextCtrl(self.sw, size=(100,-1), value=step_info[4], style=wx.TE_PROCESS_ENTER)
	    if step_info[4]:
		self.settings_controls[step+'|4'].SetForegroundColour(wx.RED) 
	    self.del_btn = wx.Button(self.sw, id=stepNo, label='Del -') 
	    self.add_btn = wx.Button(self.sw, id=stepNo, label='Add +')
	    #--- Tooltips --#
	    self.settings_controls[step+'|1'].SetToolTipString(step_info[1])
	    self.settings_controls[step+'|4'].SetToolTipString(step_info[4])
	    #-- Binding ---#
	    self.settings_controls[step+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.del_btn.step_to_delete = step
	    self.del_btn.Bind(wx.EVT_BUTTON, self.OnDelStep) 	    
	    self.add_btn.Bind(wx.EVT_BUTTON, self.OnAddStep) 	    
	    #--- Layout ---#
	    self.step_fgs.Add(wx.StaticText(self.sw, -1, 'Step%s'%str(stepNo)), 0, wx.ALIGN_CENTRE) 
	    self.step_fgs.Add(self.settings_controls[step+'|0'], 1, wx.EXPAND|wx.ALL, 5) 
	    self.step_fgs.Add(self.settings_controls[step+'|1'], 0, wx.ALIGN_CENTRE)
	    self.step_fgs.Add(self.settings_controls[step+'|2'], 0, wx.ALIGN_CENTRE)
	    self.step_fgs.Add(self.settings_controls[step+'|3'], 0, wx.ALIGN_CENTRE)
	    self.step_fgs.Add(self.settings_controls[step+'|4'], 0, wx.ALIGN_CENTRE)
	    self.step_fgs.Add(self.add_btn, 0, wx.ALIGN_CENTRE)
	    self.step_fgs.Add(self.del_btn, 0, wx.ALIGN_CENTRE)
	    
	    if stepNo == 1:
		self.del_btn.Hide()
	    
	    #--- Sizers -------
	    self.sw.SetSizer(self.swsizer)
	    self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0) 
	    self.sw.FitInside()	    
		
	
    def OnAddStep(self, event):
	meta = ExperimentSettings.getInstance()
	steps = []
	for step in self.curr_protocol.keys():
	    if step not in ['ADMIN','SEED','HARVEST','VESSEL']:
		steps.append(step)
		
	for step in sorted(steps, key = meta.stringSplitByNumbers):
	    if not self.curr_protocol[step]:
		dial = wx.MessageDialog(None, 'Please fill the description in %s !!' %step, 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return
	ctrl = event.GetEventObject()
	#Rearrange the steps numbers in the experimental settings
	temp_steps = {}
	for step in sorted(steps, key = meta.stringSplitByNumbers):
	    stepNo = int(step.split('Step')[1])
	    step_info =  self.curr_protocol[step]	    	    
	    if stepNo > ctrl.GetId() and temp_steps[stepNo] is not []:
		temp_steps[stepNo+1] =self.curr_protocol[step]
		del self.curr_protocol[step]
	    else:
		temp_steps[stepNo] = self.curr_protocol[step]
		temp_steps[stepNo+1] = []
		del self.curr_protocol[step]
	for stepNo in sorted(temp_steps.iterkeys()):
	    self.curr_protocol['Step%s'%str(stepNo)] = temp_steps[stepNo]	
	self.step_fgs.Clear(deleteWindows=True)
	
	self.showSteps()
	   

    def OnDelStep(self, event):	
	self.del_btn = event.GetEventObject()	
	#delete the step from the experimental settings 
	del self.curr_protocol[self.del_btn.step_to_delete]
	# Rearrange the steps numbers in the experimental settings
	steps = sorted([element for element in self.curr_protocol.keys()
		 if element.startswith('Step')] , key = meta.stringSplitByNumbers)
	temp_steps = {}
	for stepNo in range(len(steps)):
	    temp_steps[stepNo+1] = self.curr_protocol[steps[stepNo]]
	    del self.curr_protocol[steps[stepNo]]
	for stepNo in sorted(temp_steps.iterkeys()):
	    self.curr_protocol['Step%s'%str(stepNo)] = temp_steps[stepNo]
	#clear the bottom panel
	self.step_fgs.Clear(deleteWindows=True)
	#redraw the panel
	self.showSteps()
    

    #----------------------------------------------------------------------
    def setCurrDateTime(self, event):
	"""This method sets current date and time to the ctrl"""
	now = wx.DateTime_Now()
	self.settings_controls['Admin|1'].SetValue(now)
	self.settings_controls['Admin|2'].SetValue(now)
    

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if isinstance(ctrl, wx.ListBox) and ctrl.GetStringSelection() == 'Other':
		other = wx.GetTextFromUser('Insert Other', 'Other')
		ctrl.Append(other)
		ctrl.SetStringSelection(other)
	
	if tag.startswith('Admin'): # if this is an Admin 
	    date = self.settings_controls['Admin|1'].GetValue()
	    self.curr_protocol['ADMIN'] = [self.settings_controls['Admin|0'].GetValue(), 
	                                   '%02d/%02d/%4d'%(date.Day, date.Month+1, date.Year), 
	                                   self.settings_controls['Admin|2'].GetValue()
	                                   ]
	elif tag.startswith('Seed'):	
	    self.curr_protocol['SEED'] = [self.settings_controls['Seed|0'].GetValue(), 
	                                  self.settings_controls['Seed|1'].GetStringSelection()
	                                    ]	    
	elif tag.startswith('Harvest'):	
	    self.curr_protocol['HARVEST'] = [self.settings_controls['Harvest|0'].GetValue(), 
	                                  self.settings_controls['Harvest|1'].GetStringSelection()
	                                    ]
	elif tag.startswith('Vessel'):	
	    self.curr_protocol['VESSEL'] = [self.settings_controls['Vessel|0'].GetStringSelection()]
	    
	elif tag.startswith('Split'):	
	    self.curr_protocol['SPLIT'] = self.settings_controls['Split'].GetStringSelection()
	    print self.curr_protocol['SPLIT']
	    
	else:   # if this is a step 
	    step = tag.split('|')[0]
	    self.curr_protocol[step] = [self.settings_controls[step+'|0'].GetValue(),
	                                self.settings_controls[step+'|1'].GetValue(),
	                                self.settings_controls[step+'|2'].GetValue(),
	                                self.settings_controls[step+'|3'].GetValue(),
	                                self.settings_controls[step+'|4'].GetValue()]
	
	date = self.curr_protocol['ADMIN'][1].split('/')
	time = self.curr_protocol['ADMIN'][2].split(':')
	self.sel_date_time = map(int, [date[2],date[1],date[0],time[0],time[1], time[2]])
	self.selected_datetime = datetime.datetime(*map(int, [date[2],date[1],date[0],time[0],time[1], time[2]]))
	#if (self.initial_datetime and self.initial_seed_density and self.curr_protocol['HARVEST']):
	    ## *** Harvest density can be less then seed density if cells die
	    ## the forumula is different check with Paul  #=elapsedtime*LN(2)/LN(harvest density/seed density)
	    ## ** time resloution can be days or hours
	    
	    #time_elapsed =  (self.selected_datetime-self.initial_datetime)
	    #elapsed_minutes = (time_elapsed.days * 1440) + (time_elapsed.seconds / 60)
	    #if elapsed_minutes < 360:
		#dlg = wx.MessageDialog(None, 'Difference of seed-harvest time should be minimum 6 hr.\nReselect time', 'Time selection error', wx.OK| wx.ICON_STOP)
		#dlg.ShowModal()
		#return 		
	    #if (self.selected_datetime>self.initial_datetime and self.curr_protocol['HARVEST'][0] > self.initial_seed_density):
		#cell_growth = max(math.log(self.curr_protocol['HARVEST'][0]/self.initial_seed_density), 1)
		#pdt = (elapsed_minutes*math.log(2)/cell_growth)/60
		#self.pd_text.SetLabel('PD Time %.2f Hr' %pdt)
		#self.curr_protocol['PD'].append(pdt)
		#self.curr_protocol['PD'].append((elapsed_minutes/60)/pdt)
		#self.curr_protocol['PD'].append((elapsed_minutes/60))
    
		
	if self.initial_seed_density and self.curr_protocol['HARVEST']:
	    self.selection_btn.Enable()
	if (self.initial_seed_density is None) and self.curr_protocol['SEED']:
	    self.selection_btn.Enable()	
    
