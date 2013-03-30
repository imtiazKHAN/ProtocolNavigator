import wx
import re
import datetime
import experimentsettings as exp
import wx.lib.masked as masked
import locale
import math
from experimentsettings import ExperimentSettings
from wx.lib.masked import NumCtrl
from addrow import RowBuilder
from collections import OrderedDict
# TO DO: make the onSavingData coherent with experimentsettings file method. Also Step builder should use addrow.py ; Finally check current passage date is later than last passage date.

meta = exp.ExperimentSettings.getInstance()
locale.setlocale(locale.LC_ALL, "")

Passage_Protocol ={
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'HARVEST' : None,
    'RESEED' : None,
    'VESSEL' : None,
    'Step1' : ['Remove medium with a stripette','','', ''],
    'Step2' : ['Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    'Step3' : ['Gently tip to ensure trypsin reaches all surfaces','','', ''],
    'Step4' : ['Immediately remove trypsin with either a pipette or syringe','','', ''],
    'Step5' : ['Add approx. 0.5ml of trypsin as before, close the flask (if used)','','', ''],
    'Step6' : ['Incubate','5','', 'Beware! A few cell lines need less than this'],
    'Step7' : ['Check under the microscope to see if the cells are detached, Return to incubator for a further few minutes if not detached','','', ''],
    'Step8' : ['Add medium (DMEM) to your dish or flask','','', ''],
    'Step9' : ['Flush off the cells and then pipette your trypsinised cells into the appropriate new container.','','', 'Excess cells should be placed in container and treated appropriately. Waste cells must not be sucked into traps.  The trypsin should not really be >10% of your final volume.  If it does you should spin down your cells (5mins at 1000rpm), draw off most of the supernatant and replace with fresh medium.'],
    }
Seed_Protocol ={
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['Remove medium with a stripette','','', ''],
    'Step2' : ['Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    }
Thaw_Protocol ={
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['Remove medium with a stripette','','', ''],
    'Step2' : ['Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    }
Freeze_Protocol ={
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['Remove medium with a stripette','','', ''],
    'Step2' : ['Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    }
Enrich_Protocol ={
    'ADMIN' : ['Your Name', '', ''],
    'SEED' : None,
    'VESSEL' : None,
    'Step1' : ['Remove medium with a stripette','','', ''],
    'Step2' : ['Add trypsin in the following volumes - 1ml for the 60mm dish or T25 flask OR 2ml for 100mm dish or T75 flask','','', ''],
    }
 
class MaintainAction(wx.Dialog):
    def __init__(self, parent, protocol, curractionNo, action_type):
        wx.Dialog.__init__(self, parent, -1, size=(850,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

	self.protocol = protocol
	self.curractionNo = curractionNo
	self.action_type = action_type
	self.action_attr = '%s %s'%(self.action_type, str(self.curractionNo))	
	
	self.SetTitle(self.action_attr)
	
	self.top_panel = wx.Panel(self)
	self.bot_panel = wx.ScrolledWindow(self)	
	
	self.settings_controls = {}
	self.curr_protocol = {}
	self.admin_info = {}  	
	self.mandatory_tags = []
	self.labels = {}	
	
	self.today_datetime = datetime.datetime.now()
	
	self.tag_stump = exp.get_tag_stump(self.protocol, 2)
	self.instance = exp.get_tag_attribute(self.protocol)
	
	if self.action_type == 'Passage':	
	    if meta.get_field(self.tag_stump+'|Passage%s|%s' %(str(self.curractionNo-1), self.instance)) is None:
		self.curr_protocol = Passage_Protocol
	    else:
		d =  meta.get_field(self.tag_stump+'|Passage%s|%s' %(str(self.curractionNo-1), self.instance))
		for k, v in d:
		    self.curr_protocol[k] = v	
	if self.action_type == 'Seed':	
	    if meta.get_field(self.tag_stump+'|Seed%s|%s' %(str(self.curractionNo-1), self.instance)) is None:
		self.curr_protocol = Seed_Protocol
	    else:
		d =  meta.get_field(self.tag_stump+'|Seed%s|%s' %(str(self.curractionNo-1), self.instance))
		for k, v in d:
		    self.curr_protocol[k] = v
	if self.action_type == 'Thaw':	
	    if meta.get_field(self.tag_stump+'|Thaw%s|%s' %(str(self.curractionNo-1), self.instance)) is None:
		self.curr_protocol = Thaw_Protocol
	    else:
		d =  meta.get_field(self.tag_stump+'|Thaw%s|%s' %(str(self.curractionNo-1), self.instance))
		for k, v in d:
		    self.curr_protocol[k] = v	
	if self.action_type == 'Freeze':	
	    if meta.get_field(self.tag_stump+'|Freeze%s|%s' %(str(self.curractionNo-1), self.instance)) is None:
		self.curr_protocol = Freeze_Protocol
	    else:
		d =  meta.get_field(self.tag_stump+'|Freeze%s|%s' %(str(self.curractionNo-1), self.instance))
		for k, v in d:
		    self.curr_protocol[k] = v
	if self.action_type == 'Enrich':	
	    if meta.get_field(self.tag_stump+'|Enrich%s|%s' %(str(self.curractionNo-1), self.instance)) is None:
		self.curr_protocol = Enrich_Protocol
	    else:
		d =  meta.get_field(self.tag_stump+'|Enrich%s|%s' %(str(self.curractionNo-1), self.instance))
		for k, v in d:
		    self.curr_protocol[k] = v
		    
	date= None	
	self.initial_datetime = None
	self.initial_seed_density = None	
	#self.curr_protocol['PD'] = []
	self.curr_protocol['HARVEST'] = []
	self.curr_protocol['RESEED'] = []	
	
	#datetime.datetime.fromtimestamp(wx.DateTime.Now().GetTicks()) 
	#wx.DateTimeFromTimeT(time.mktime(datetime.datetime.now().timetuple())) 
	if self.curr_protocol['ADMIN'][1]:
	    date = self.curr_protocol['ADMIN'][1].split('/')
	    time = self.curr_protocol['ADMIN'][2].split(':')
	    self.initial_datetime = datetime.datetime(*map(int, [date[2],date[1],date[0],time[0],time[1], time[2]]))
	if self.curr_protocol['SEED']:
	    self.initial_seed_density = self.curr_protocol['SEED'][0]

	#Admin	
	self.settings_controls['Admin|0'] = wx.TextCtrl(self.top_panel, size=(70,-1), value=self.curr_protocol['ADMIN'][0])	
	self.settings_controls['Admin|1'] = wx.DatePickerCtrl(self.top_panel, style = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
	if date is None:
	    self.curr_protocol['ADMIN'][1] = str(self.today_datetime.day)+'/'+str(self.today_datetime.month)+'/'+str(self.today_datetime.year)
	else:
	    self.settings_controls['Admin|1'].SetValue(wx.DateTimeFromDMY(int(date[0]), int(date[1])-1, int(date[2])))
	self.settings_controls['Admin|2'] = masked.TimeCtrl( self.top_panel, -1, name="24 hour control", fmt24hr=True )
	h = self.settings_controls['Admin|2'].GetSize().height
	spin1 = wx.SpinButton( self.top_panel, -1, wx.DefaultPosition, (-1,h), wx.SP_VERTICAL )
	self.settings_controls['Admin|2'].BindSpinButton( spin1 )	
	self.curr_protocol['ADMIN'][2] = str(self.today_datetime.hour)+':'+str(self.today_datetime.minute)+':'+str(self.today_datetime.second)
	self.settings_controls['Admin|2'].SetValue(self.curr_protocol['ADMIN'][2])
	
	self.set_curr_time = wx.Button(self.top_panel, -1, 'Set Current Date Time')

	if (self.action_type == 'Passage') or (self.action_type == 'Seed'): 
	    self.settings_controls['Seed|0'] = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Seed|1'] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    #if self.curr_protocol['SEED']:
		#self.settings_controls['Seed|0'].SetValue(self.curr_protocol['SEED'][0])
		#self.settings_controls['Seed|0'].Disable()	
		#self.settings_controls['Seed|1'].Append(self.curr_protocol['SEED'][1])
		#self.settings_controls['Seed|1'].SetStringSelection(self.curr_protocol['SEED'][1])
		#self.settings_controls['Seed|1'].Disable()
	    self.settings_controls['Seed|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Seed|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)		
	if (self.action_type == 'Passage'):     
	    self.settings_controls['Harvest|0'] = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    unit_choices =['nM2', 'uM2', 'mM2','Other']
	    self.settings_controls['Harvest|1'] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    #self.settings_controls['Reseed|0'] = wx.lib.masked.NumCtrl(self.top_panel, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	    #unit_choices =['nM2', 'uM2', 'mM2','Other']
	    #self.settings_controls['Reseed|1'] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	    self.settings_controls['Harvest|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls['Harvest|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)	
	    #self.settings_controls['Reseed|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    #self.settings_controls['Reseed|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)	    
	
	# CHANGE IT VESSEL DESIGN TWO SELECTIONS
	vessel_types =['T75', 'T25', '6WellPlate','12WellPlate', 'Other']
	self.settings_controls['Vessel|0'] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (100,20), vessel_types, wx.LB_SINGLE)
	if self.curr_protocol['VESSEL']:
	    self.settings_controls['Vessel|0'].Append(self.curr_protocol['VESSEL'][0])
	    self.settings_controls['Vessel|0'].SetStringSelection(self.curr_protocol['VESSEL'][0]) 
	    
	    
	self.pd_text = wx.StaticText(self.top_panel, -1, '')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	self.pd_text.SetFont(font)	
	
	self.selection_btn = wx.Button(self, wx.ID_OK, 'Record')
        self.close_btn = wx.Button(self, wx.ID_CANCEL)  
	
	#self.selection_btn.Disable()
	
	#Bind
	self.settings_controls['Admin|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls['Admin|1'].Bind(wx.EVT_DATE_CHANGED, self.OnSavingData)
	self.settings_controls['Admin|2'].Bind(wx.EVT_TEXT, self.OnSavingData)	 
	self.settings_controls['Vessel|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	self.set_curr_time.Bind(wx.EVT_BUTTON, self.setCurrDateTime)

	# Sizers and layout
	staticbox = wx.StaticBox(self.top_panel, -1, "Admin")
	adminsizer = wx.StaticBoxSizer(staticbox, wx.HORIZONTAL)	
	adminsizer.Add(wx.StaticText(self.top_panel, -1, 'Operator Name'),0, wx.RIGHT, 5)
	adminsizer.Add(self.settings_controls['Admin|0'] , 0, wx.EXPAND)
	adminsizer.Add(wx.StaticText(self.top_panel, -1, 'Date'),0, wx.RIGHT|wx.LEFT, 5)
	adminsizer.Add(self.settings_controls['Admin|1'], 0, wx.EXPAND)
	adminsizer.Add(wx.StaticText(self.top_panel, -1, 'Time'),0, wx.LEFT, 5)
	adminsizer.Add(self.settings_controls['Admin|2'], 0, wx.EXPAND)
	adminsizer.Add( spin1, 0, wx.ALIGN_CENTRE )
	adminsizer.Add(self.set_curr_time, 0, wx.ALIGN_RIGHT|wx.LEFT, 15)

	stat_fgs = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)
	if (self.action_type == 'Seed'): 
	    stat_fgs.Add(wx.StaticText(self.top_panel, -1, 'Seed Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    stat_fgs.Add(self.settings_controls['Seed|0'], 0, wx.EXPAND)
	    stat_fgs.Add(wx.StaticText(self.top_panel, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    stat_fgs.Add(self.settings_controls['Seed|1'], 0, wx.EXPAND)
	if (self.action_type == 'Passage'):  
	    stat_fgs.Add(wx.StaticText(self.top_panel, -1, 'Harvest Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    stat_fgs.Add(self.settings_controls['Harvest|0'], 0, wx.EXPAND)
	    stat_fgs.Add(wx.StaticText(self.top_panel, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    stat_fgs.Add(self.settings_controls['Harvest|1'], 0, wx.EXPAND)
	    stat_fgs.Add(wx.StaticText(self.top_panel, -1, '(Re)seed Density'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    stat_fgs.Add(self.settings_controls['Seed|0'], 0, wx.EXPAND)
	    stat_fgs.Add(wx.StaticText(self.top_panel, -1, ' cells/'),0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
	    stat_fgs.Add(self.settings_controls['Seed|1'], 0, wx.EXPAND)	    
		
	    
	stat_fgs.Add(wx.StaticText(self.top_panel, -1, 'Vessel Type'),0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	stat_fgs.Add(self.settings_controls['Vessel|0'], 0, wx.EXPAND)
	
	staticbox = wx.StaticBox(self.top_panel, -1, "Statistics")
	statsizer = wx.StaticBoxSizer(staticbox, wx.HORIZONTAL)	
	statsizer.Add(stat_fgs, 0, wx.ALIGN_LEFT)
	statsizer.Add(self.pd_text, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT|wx.ALL, 20)
	

 	self.top_panel_sizer = wx.BoxSizer(wx.VERTICAL)
	self.top_panel_sizer.Add(adminsizer, 0, wx.EXPAND|wx.ALL, 5)
	self.top_panel_sizer.Add(statsizer, 0, wx.EXPAND|wx.ALL, 5)
	
	self.fgs = wx.FlexGridSizer(cols=7, hgap=5, vgap=5)	
	
	self.showSteps()
	
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	btnSizer.Add(self.selection_btn  , 0, wx.ALL, 5)
	btnSizer.Add(self.close_btn , 0, wx.ALL, 5)	

        self.top_panel.SetSizer(self.top_panel_sizer)
	self.bot_panel.SetSizer(self.fgs)
        self.bot_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	btnSizer.Add(self.selection_btn  , 0, wx.ALL, 5)
	btnSizer.Add(self.close_btn , 0, wx.ALL, 5)	

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.top_panel, 0, wx.EXPAND|wx.ALL, 5)
	self.Sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
	self.Sizer.Add(self.bot_panel, 1, wx.EXPAND|wx.ALL, 5)
	self.Sizer.Add(btnSizer)
        self.Show()         
          
    def showSteps(self):
	# get the sorted steps in passaging
	steps = sorted([step for step in self.curr_protocol.keys()
		 if step.startswith('Step')] , key = meta.stringSplitByNumbers)
		
	#-- Header --#		
	desp_header = wx.StaticText(self.bot_panel, -1, 'Description')
	dur_header = wx.StaticText(self.bot_panel, -1, 'Duration\n(min)')
	temp_header = wx.StaticText(self.bot_panel, -1, 'Temp\n(C)')
	tips_header = wx.StaticText(self.bot_panel, -1, 'Tips')
	
	font = wx.Font(6, wx.SWISS, wx.NORMAL, wx.BOLD)
	desp_header.SetFont(font)
	dur_header.SetFont(font)
	temp_header.SetFont(font)
	tips_header.SetFont(font)
	
	self.fgs.Add(wx.StaticText(self.bot_panel, -1, ''))
	self.fgs.Add(desp_header, 0, wx.ALIGN_CENTRE)
	self.fgs.Add(dur_header, 0, wx.ALIGN_CENTRE)
	self.fgs.Add(temp_header, 0, wx.ALIGN_CENTRE)
	self.fgs.Add(tips_header, 0, wx.ALIGN_CENTER)
	self.fgs.Add(wx.StaticText(self.bot_panel, -1, ''))
	self.fgs.Add(wx.StaticText(self.bot_panel, -1, ''))

	for step in steps:    
	    stepNo = int(step.split('Step')[1])
	    step_info =  self.curr_protocol[step]
	   
	    if not step_info:  # if this is newly added empty step
		step_info = ['','','','']

	    #-- Widgets ---#
	    self.settings_controls[step+'|0'] = wx.TextCtrl(self.bot_panel, size=(200,-1), value=step_info[0], style=wx.TE_PROCESS_ENTER)
	    self.settings_controls[step+'|1'] = wx.TextCtrl(self.bot_panel, size=(30,-1), value=step_info[1], style=wx.TE_PROCESS_ENTER)
	    self.settings_controls[step+'|2'] = wx.TextCtrl(self.bot_panel, size=(30,-1), value=step_info[2], style=wx.TE_PROCESS_ENTER)	
	    self.settings_controls[step+'|3'] = wx.TextCtrl(self.bot_panel, size=(100,-1), value=step_info[3], style=wx.TE_PROCESS_ENTER)
	    if step_info[3]:
		self.settings_controls[step+'|3'].SetForegroundColour(wx.RED) 
	    self.del_btn = wx.Button(self.bot_panel, id=stepNo, label='Del -') 
	    self.add_btn = wx.Button(self.bot_panel, id=stepNo, label='Add +')
	    #--- Tooltips --#
	    self.settings_controls[step+'|0'].SetToolTipString(step_info[0])
	    self.settings_controls[step+'|3'].SetToolTipString(step_info[3])
	    #-- Binding ---#
	    self.settings_controls[step+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.settings_controls[step+'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.del_btn.step_to_delete = step
	    self.del_btn.Bind(wx.EVT_BUTTON, self.OnDelStep) 	    
	    self.add_btn.Bind(wx.EVT_BUTTON, self.OnAddStep) 	    
	    #--- Layout ---#
	    self.fgs.Add(wx.StaticText(self.bot_panel, -1, 'Step%s'%str(stepNo)), 0, wx.ALIGN_CENTRE) 
	    self.fgs.Add(self.settings_controls[step+'|0'], 1, wx.EXPAND|wx.ALL, 5) 
	    self.fgs.Add(self.settings_controls[step+'|1'], 0, wx.ALIGN_CENTRE)
	    self.fgs.Add(self.settings_controls[step+'|2'], 0, wx.ALIGN_CENTRE)
	    self.fgs.Add(self.settings_controls[step+'|3'], 0, wx.ALIGN_CENTRE)
	    self.fgs.Add(self.add_btn, 0, wx.ALIGN_CENTRE)
	    self.fgs.Add(self.del_btn, 0, wx.ALIGN_CENTRE)
	    
	    if stepNo == 1:
		self.del_btn.Hide()
	    
	    # Sizers update
	    self.bot_panel.SetSizer(self.fgs)
	    self.bot_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	    
	    self.Sizer = wx.BoxSizer(wx.VERTICAL)
	    self.Sizer.Add(self.top_panel, 0, wx.EXPAND|wx.ALL, 5)
	    self.Sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
	    self.Sizer.Add(self.bot_panel, 1, wx.EXPAND|wx.ALL, 10)	                   
		
	
    def OnAddStep(self, event):
	meta = ExperimentSettings.getInstance()
	
	steps = sorted([step for step in self.curr_protocol.keys()
	 if not step.startswith('ADMIN')] , key = meta.stringSplitByNumbers)
	
	for step in steps:
	    if not self.curr_protocol[step]:
		dial = wx.MessageDialog(None, 'Please fill the description in %s !!' %step, 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return

	ctrl = event.GetEventObject()
	
	 #Rearrange the steps numbers in the experimental settings
	temp_steps = {}
	
	for step in steps:
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
	
	self.fgs.Clear(deleteWindows=True)
	
	self.showSteps()
	   

    def OnDelStep(self, event):
	
	self.del_btn = event.GetEventObject()
	
	#delete the step from the experimental settings 
	del self.curr_protocol[self.del_btn.step_to_delete]
	
	# Rearrange the steps numbers in the experimental settings
	steps = sorted([step for step in self.curr_protocol.keys()
		 if not step.startswith('ADMIN')] , key = meta.stringSplitByNumbers)
	
	temp_steps = {}
	for stepNo in range(len(steps)):
	    temp_steps[stepNo+1] = self.curr_protocol[steps[stepNo]]
	    del self.curr_protocol[steps[stepNo]]
	    
	for stepNo in sorted(temp_steps.iterkeys()):
	    self.curr_protocol['Step%s'%str(stepNo)] = temp_steps[stepNo]
	
	#clear the bottom panel
	self.fgs.Clear(deleteWindows=True)
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
	#elif tag.startswith('Reseed'):	
	    #self.curr_protocol['SEED'] = [self.settings_controls['Reseed|0'].GetValue(), 
	                                  #self.settings_controls['Reseed|1'].GetStringSelection()
	                                    #]
	elif tag.startswith('Vessel'):	
	    self.curr_protocol['VESSEL'] = [self.settings_controls['Vessel|0'].GetStringSelection()]
	    
	else:   # if this is a step 
	    step = tag.split('|')[0]
	    # get the sibling controls like description, duration, temp controls for this step
	    info = []
	    for tg in [t for t, c in self.settings_controls.items()]:
		if exp.get_tag_stump(tag, 1) == exp.get_tag_stump(tg, 1) and tg.startswith('Step'):
		    c_num = int(tg.split('|')[1])
		    if isinstance(self.settings_controls[tg], wx.Choice):
			info.insert(c_num, self.settings_controls[tg].GetStringSelection())
		    elif isinstance(self.settings_controls[tg], wx.ListBox):
			info.insert(c_num, self.settings_controls[tg].GetStringSelection())		    
		    else:
			user_input = self.settings_controls[tg].GetValue()
			user_input.rstrip('\n')
			user_input.rstrip('\t')
			info.insert(c_num, user_input)
		    
	    self.curr_protocol[step] = info
	
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