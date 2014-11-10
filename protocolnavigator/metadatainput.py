#!/usr/bin/env python
# Imtiaz Khan

import wx
import os
import re
import sys
import operator
import  wx.calendar
import wx.lib.agw.flatnotebook as fnb
import wx.lib.mixins.listctrl as listmix
import wx.lib.filebrowsebutton
import wx.gizmos   as  gizmos
import string, os
import wx.lib.agw.foldpanelbar as fpb
import experimentsettings as exp
import wx.html
import webbrowser
import wx.media
import glob
import icons
import subprocess
import wx.lib.plot as plot
import datetime
from functools import partial
from experimentsettings import *
from instancelist import *
from utils import *
from makechannel import ChannelBuilder
from rheometerstepbuilder import RheometerStepBuilder
from addrow import RowBuilder
from cellmaintainaction import *
from collections import OrderedDict
from draganddrop import FileListDialog
from multilinetextshow import MultiLineShow


ICON_SIZE = 22.0


class ExperimentSettingsWindow(wx.SplitterWindow):
    def __init__(self, parent, id=-1, **kwargs):
        wx.SplitterWindow.__init__(self, parent, id, **kwargs)
        
        self.tree = wx.TreeCtrl(self, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS|wx.NO_BORDER)

        root = self.tree.AddRoot('Experiment')

        stc = self.tree.AppendItem(root, 'SETTINGS')
        ovr = self.tree.AppendItem(stc, 'Overview')
        smp = self.tree.AppendItem(stc, 'Sample')
	self.tree.AppendItem(smp, 'Cell Line')
        ins = self.tree.AppendItem(stc, 'Instrument')
        self.tree.AppendItem(ins, 'Centrifuge')
	self.tree.AppendItem(ins, 'Flow Cytometer')
	self.tree.AppendItem(ins, 'Incubator')
	self.tree.AppendItem(ins, 'Microscope')
        self.tree.AppendItem(ins, 'Oven')
	self.tree.AppendItem(ins, 'Rheometer')
	
        exv = self.tree.AppendItem(stc, 'Experimental Matrix')
        self.tree.AppendItem(exv, 'Plate')
        self.tree.AppendItem(exv, 'Flask')
        self.tree.AppendItem(exv, 'Dish')
        self.tree.AppendItem(exv, 'Coverslip')
	self.tree.AppendItem(exv, 'Tube')
        stc = self.tree.AppendItem(root, 'ASSAY')
        cld = self.tree.AppendItem(stc, 'Sample Transfer')
        self.tree.AppendItem(cld, 'Seeding')
        ptb = self.tree.AppendItem(stc, 'Perturbation')
        self.tree.AppendItem(ptb, 'Chemical')
        self.tree.AppendItem(ptb, 'Biological')
	self.tree.AppendItem(ptb, 'Physical')
        lbl = self.tree.AppendItem(stc, 'Labeling Processes')
        self.tree.AppendItem(lbl, 'Dye')
        self.tree.AppendItem(lbl, 'Immunofluorescence')
        self.tree.AppendItem(lbl, 'Genetic')
	adp = self.tree.AppendItem(stc, 'Additional Processes')        
	self.tree.AppendItem(adp, 'Add Medium')	
	self.tree.AppendItem(adp, 'Initiation')
	self.tree.AppendItem(adp, 'Storage')
	self.tree.AppendItem(adp, 'Wash')
	inp = self.tree.AppendItem(stc, 'Instrumental Processes')
	self.tree.AppendItem(inp, 'Centrifugation')
	self.tree.AppendItem(inp, 'Drying')
	self.tree.AppendItem(inp, 'Incubation')
	self.tree.AppendItem(inp, 'Rheological Manipulation')	
        dta = self.tree.AppendItem(stc, 'Data Acquisition')
        self.tree.AppendItem(dta, 'Flow Cytometer File')
	self.tree.AppendItem(dta, 'Rheological Measurement')
	self.tree.AppendItem(dta, 'Static Image')
	self.tree.AppendItem(dta, 'Timelapse Image')
            
        self.tree.Expand(root)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)

        #self.openBenchBut = wx.Button(self, id=-1, label='Open Wrok Bench', pos=(20, 60), size=(175, 28))
        #self.openBenchBut.Bind(wx.EVT_BUTTON, self.onOpenWrokBench)

        self.settings_container = wx.Panel(self, wx.NO_BORDER)
        self.settings_container.SetSizer(wx.BoxSizer())
        self.settings_panel = wx.Panel(self, wx.NO_BORDER)

        self.SplitVertically(self.tree, self.settings_container)
	self.SetSashGravity(0.3)
        self.Centre()
    
    def OnLeafSelect(self):
	self.tree.ExpandAll()
    
    def ShowInstance(self, tag):
	
	meta =ExperimentSettings.getInstance()
	
	self.settings_panel.Destroy()
	self.settings_container.Sizer.Clear()
	
	if get_tag_type(tag) == 'Transfer' and get_tag_event(tag) == 'Harvest':
	    self.settings_panel = CellLineSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(meta.get_field('Transfer|Harvest|CellLineInstance|%s'%get_tag_instance(tag)))-1)  
	if get_tag_type(tag) == 'Transfer' and get_tag_event(tag) == 'Seed':  # may link with stock instance
	    self.settings_panel = CellSeedSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'Perturbation' and get_tag_event(tag) == 'Chemical':
	    self.settings_panel = ChemicalSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)	
	if get_tag_type(tag) == 'Perturbation' and get_tag_event(tag) == 'Biological':
            self.settings_panel = BiologicalSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'Perturbation' and get_tag_event(tag) == 'Physical':
	    self.settings_panel = PhysicalSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)	    
	if get_tag_type(tag) == 'Labeling' and get_tag_event(tag) == 'Dye':
	    self.settings_panel = DyeSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'Labeling' and get_tag_event(tag) == 'Immuno':
	    self.settings_panel = ImmunoSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'Labeling' and get_tag_event(tag) == 'Genetic':
	    self.settings_panel = GeneticSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	    
	if get_tag_type(tag) == 'InstProcess' and get_tag_event(tag) == 'RheoManipulation':
	    self.settings_panel = RheometerSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)    
	if get_tag_type(tag) == 'InstProcess' and get_tag_event(tag) == 'Drying':
	    self.settings_panel = DryingSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'InstProcess' and get_tag_event(tag) == 'Incubation':
	    self.settings_panel = IncubationSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'InstProcess' and get_tag_event(tag) == 'Centrifugation':
	    self.settings_panel = CentrifugationSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
		
	if get_tag_type(tag) == 'AddProcess' and get_tag_event(tag) == 'Wash':
	    self.settings_panel = WashSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'AddProcess' and get_tag_event(tag) == 'Medium':
	    self.settings_panel = AddMediumSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)
	if get_tag_type(tag) == 'AddProcess' and get_tag_event(tag) == 'Initiation':
	    self.settings_panel = InitiationSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)	
	if get_tag_type(tag) == 'AddProcess' and get_tag_event(tag) == 'Storage':
	    self.settings_panel = StorageSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(get_tag_instance(tag))-1)    
		
	if get_tag_type(tag) == 'DataAcquis' and get_tag_event(tag) == 'TLM':  
	    self.settings_panel = MicroscopeSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(meta.get_field('DataAcquis|TLM|MicroscopeInstance|%s'%get_tag_instance(tag)))-1)
	if get_tag_type(tag) == 'DataAcquis' and get_tag_event(tag) == 'HCS':  
	    self.settings_panel = MicroscopeSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(meta.get_field('DataAcquis|HCS|MicroscopeInstance|%s'%get_tag_instance(tag)))-1)	
	if get_tag_type(tag) == 'DataAcquis' and get_tag_event(tag) == 'FCS': 
	    self.settings_panel = FlowcytometerSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(meta.get_field('DataAcquis|FCS|FlowcytometerInstance|%s'%get_tag_instance(tag)))-1)
	if get_tag_type(tag) == 'DataAcquis' and get_tag_event(tag) == 'RHE':
	    self.settings_panel = RheometerSettingPanel(self.settings_container)
	    self.settings_panel.notebook.SetSelection(int(meta.get_field('DataAcquis|RHE|RheometerInstance|%s'%get_tag_instance(tag)))-1)

	    
	self.settings_container.Sizer.Add(self.settings_panel, 1, wx.EXPAND)        
	self.settings_container.Layout()
	self.settings_panel.ClearBackground()
	self.settings_panel.Refresh()
	


                
    def OnSelChanged(self, event):
        item =  event.GetItem()

        self.settings_panel.Destroy()
        self.settings_container.Sizer.Clear()
	
        if self.tree.GetItemText(item) == 'Overview':
            self.settings_panel = OverviewPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Cell Line':
            self.settings_panel = CellLineSettingPanel(self.settings_container)
        
        elif self.tree.GetItemText(item) == 'Microscope':
            self.settings_panel = MicroscopeSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Flow Cytometer':
            self.settings_panel = FlowcytometerSettingPanel(self.settings_container)  
	elif self.tree.GetItemText(item) == 'Rheometer':
	    self.settings_panel = RheometerSettingPanel(self.settings_container)  	
	elif self.tree.GetItemText(item) == 'Centrifuge':
	    self.settings_panel = CentrifugeSettingPanel(self.settings_container) 
	elif self.tree.GetItemText(item) == 'Oven':
	    self.settings_panel = OvenSettingPanel(self.settings_container) 	
	elif self.tree.GetItemText(item) == 'Incubator':
	    self.settings_panel = IncubatorSettingPanel(self.settings_container) 	 	
        
        elif self.tree.GetItemText(item) == 'Plate':
            self.settings_panel = PlateSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Flask':
            self.settings_panel = FlaskSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Dish':
            self.settings_panel = DishSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Coverslip':
            self.settings_panel = CoverslipSettingPanel(self.settings_container)        
        elif self.tree.GetItemText(item) == 'Culture Slide':
            self.settings_panel = CultureslideSettingPanel(self.settings_container)
	elif self.tree.GetItemText(item) == 'Tube':
	    self.settings_panel = TubeSettingPanel(self.settings_container)	
        
        elif self.tree.GetItemText(item) == 'Seeding':
            self.settings_panel = CellSeedSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Harvesting':
            self.settings_panel = CellHarvestSettingPanel(self.settings_container)    
            
        elif self.tree.GetItemText(item) == 'Chemical':
            self.settings_panel = ChemicalSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Biological':
            self.settings_panel = BiologicalSettingPanel(self.settings_container)  
	elif self.tree.GetItemText(item) == 'Physical':
	    self.settings_panel = PhysicalSettingPanel(self.settings_container)	
                 
        elif self.tree.GetItemText(item) == 'Centrifugation':
            self.settings_panel =  CentrifugationSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Wash':
            self.settings_panel =  WashSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Drying':
            self.settings_panel =  DryingSettingPanel(self.settings_container) 
        elif self.tree.GetItemText(item) == 'Add Medium':
            self.settings_panel =  AddMediumSettingPanel(self.settings_container)
	elif self.tree.GetItemText(item) == 'Initiation':
	    self.settings_panel =  InitiationSettingPanel(self.settings_container)
	elif self.tree.GetItemText(item) == 'Storage':
	    self.settings_panel =  StorageSettingPanel(self.settings_container)	
        elif self.tree.GetItemText(item) == 'Incubation':
            self.settings_panel = IncubationSettingPanel(self.settings_container)   
	elif self.tree.GetItemText(item) == 'Rheological Manipulation':
	    self.settings_panel = RheoManipulationSettingPanel(self.settings_container)   
	    
        elif self.tree.GetItemText(item) == 'Dye':
            self.settings_panel = DyeSettingPanel(self.settings_container)        
        elif self.tree.GetItemText(item) == 'Immunofluorescence':
            self.settings_panel =  ImmunoSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Genetic':
            self.settings_panel =  GeneticSettingPanel(self.settings_container)
                    
        elif self.tree.GetItemText(item) == 'Timelapse Image':
            self.settings_panel = TLMSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Static Image':
            self.settings_panel = HCSSettingPanel(self.settings_container)
        elif self.tree.GetItemText(item) == 'Flow Cytometer File':
            self.settings_panel = FCSSettingPanel(self.settings_container)
	elif self.tree.GetItemText(item) == 'Rheological Measurement':
	    self.settings_panel = RHESettingPanel(self.settings_container)   
            
        elif self.tree.GetItemText(item) == 'Notes':
                    self.settings_panel = NoteSettingPanel(self.settings_container)
          
        else:
            self.settings_panel = wx.Panel(self.settings_container)

        self.settings_container.Sizer.Add(self.settings_panel, 1, wx.EXPAND)        
        self.settings_container.Layout()
        # Annoying: not sure why, but the notebook tabs reappear on other 
        # settings panels even after the panel that owend them (and the notebook
        # itself) is destroyed. This seems to happen on Mac only.
        self.settings_panel.ClearBackground()
        self.settings_panel.Refresh()

########################################################################        
######                 OVERVIEW PANEL                        ###########
########################################################################
class OverviewPanel(wx.Panel):    
    def __init__(self, parent, id=-1, **kwargs):
        wx.Panel.__init__(self, parent, id, **kwargs)

	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()


	self.tag_stump = 'Overview|Project'
	self.mandatory_tags = [self.tag_stump+'|Title', self.tag_stump+'|ExptNum', self.tag_stump+'|ExptDate']
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump)+' Overview')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)			

        titleTAG = self.tag_stump+'|Title'
        self.settings_controls[titleTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(titleTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[titleTAG].SetInitialSize((300, 30))
        self.settings_controls[titleTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[titleTAG] = wx.StaticText(self.sw, -1, 'Project Title')
        self.labels[titleTAG].SetToolTipString('Insert the title of the experiment')
        attributesizer.Add(self.labels[titleTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[titleTAG], 0, wx.EXPAND)

        aimTAG = self.tag_stump+'|Aims'
        self.settings_controls[aimTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(aimTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[aimTAG].SetInitialSize((300, 50))
        self.settings_controls[aimTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[aimTAG] = wx.StaticText(self.sw, -1, 'Project Aim')
        self.labels[aimTAG].SetToolTipString('Describe here the aim of the experiment')
        attributesizer.Add(self.labels[aimTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[aimTAG], 0, wx.EXPAND)
    
	fundTAG = self.tag_stump+'|Fund'
	self.settings_controls[fundTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(fundTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[fundTAG].SetInitialSize((300, 20))
	self.settings_controls[fundTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[fundTAG] = wx.StaticText(self.sw, -1, 'Funding Code')
	self.labels[fundTAG].SetToolTipString('Project funding codes')
	attributesizer.Add(self.labels[fundTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[fundTAG], 0, wx.EXPAND)	
        
        keyTAG = self.tag_stump+'|Keywords'
        self.settings_controls[keyTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(keyTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[keyTAG].SetInitialSize((300, 50))
        self.settings_controls[keyTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[keyTAG] = wx.StaticText(self.sw, -1, 'Keywords') 
        self.labels[keyTAG].SetToolTipString('Keywords that indicates the experiment')
        attributesizer.Add(self.labels[keyTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[keyTAG], 0, wx.EXPAND)
        
        exnumTAG = self.tag_stump+'|ExptNum'
        self.settings_controls[exnumTAG] = wx.Choice(self.sw, -1,  choices=['1','2','3','4','5','6','7','8','9','10'])
        if meta.get_field(exnumTAG) is not None:
            self.settings_controls[exnumTAG].SetStringSelection(meta.get_field(exnumTAG))
        self.settings_controls[exnumTAG].Bind(wx.EVT_CHOICE, self.OnSavingData) 
	self.labels[exnumTAG] = wx.StaticText(self.sw, -1, 'Experiment Number')
        self.labels[exnumTAG].SetToolTipString('Experiment Number....')
        attributesizer.Add(self.labels[exnumTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[exnumTAG], 0, wx.EXPAND)
        
        exdateTAG = self.tag_stump+'|ExptDate'
        self.settings_controls[exdateTAG] = wx.DatePickerCtrl(self.sw, style = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY )
        if meta.get_field(exdateTAG) is not None:
            day, month, year = meta.get_field(exdateTAG).split('/')
            myDate = wx.DateTimeFromDMY(int(day), int(month)-1, int(year))
            self.settings_controls[exdateTAG].SetValue(myDate)
	else:
	    today = datetime.date.today()
	    meta.set_field(exdateTAG, '%02d/%02d/%4d'%(today.day, today.month+1, today.year))
        self.settings_controls[exdateTAG].Bind(wx.EVT_DATE_CHANGED,self.OnSavingData)
	self.labels[exdateTAG] = wx.StaticText(self.sw, -1, 'Experiment Start Date')
        self.labels[exdateTAG].SetToolTipString('Start date of the experiment')
        attributesizer.Add(self.labels[exdateTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[exdateTAG], 0, wx.EXPAND)
        
        exppubTAG = self.tag_stump+'|Publications'
        self.settings_controls[exppubTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(exppubTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[exppubTAG].SetInitialSize((300, 50))
        self.settings_controls[exppubTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[exppubTAG] = wx.StaticText(self.sw, -1, 'Related Publications')
        self.labels[exppubTAG].SetToolTipString('Experiment related publication list')
        attributesizer.Add(self.labels[exppubTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[exppubTAG], 0, wx.EXPAND)
        
        expnameTAG = self.tag_stump+'|Experimenter'
        self.settings_controls[expnameTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(expnameTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[expnameTAG].SetInitialSize((300, 20))
        self.settings_controls[expnameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[expnameTAG] = wx.StaticText(self.sw, -1, 'Name of Experimenter(s)')
        self.labels[expnameTAG].SetToolTipString('Name of experimenter(s)')
        attributesizer.Add(self.labels[expnameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[expnameTAG], 0, wx.EXPAND)
        
        instnameTAG = self.tag_stump+'|Institution'
        self.settings_controls[instnameTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(instnameTAG, default=''))
        self.settings_controls[instnameTAG].SetInitialSize((300, 20))
        self.settings_controls[instnameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[instnameTAG] = wx.StaticText(self.sw, -1, 'Name of Institution')
        self.labels[instnameTAG].SetToolTipString('Name of Institution')
        attributesizer.Add(self.labels[instnameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[instnameTAG], 0, wx.EXPAND)
        
        deptnameTAG = self.tag_stump+'|Department'
        self.settings_controls[deptnameTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(deptnameTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[deptnameTAG].SetInitialSize((300, 20))
        self.settings_controls[deptnameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[deptnameTAG] = wx.StaticText(self.sw, -1, 'Department Name')
        self.labels[deptnameTAG].SetToolTipString('Name of the Department')
        attributesizer.Add(self.labels[deptnameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[deptnameTAG], 0, wx.EXPAND)
        
        addressTAG = self.tag_stump+'|Address'
        self.settings_controls[addressTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(addressTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[addressTAG].SetInitialSize((300, 50))
        self.settings_controls[addressTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[addressTAG] = wx.StaticText(self.sw, -1, 'Address')
        self.labels[addressTAG].SetToolTipString('Postal address and other contact details')
        attributesizer.Add(self.labels[addressTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[addressTAG], 0, wx.EXPAND)
        
        statusTAG = self.tag_stump+'|Status'
        self.settings_controls[statusTAG] = wx.Choice(self.sw, -1, choices=['Complete', 'Ongoing', 'Pending', 'Discarded'])
        if meta.get_field(statusTAG) is not None:
            self.settings_controls[statusTAG].SetStringSelection(meta.get_field(statusTAG))
        self.settings_controls[statusTAG].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[statusTAG] = wx.StaticText(self.sw, -1, 'Status')
        self.labels[statusTAG].SetToolTipString('Status of the experiment, e.g. Complete, On-going, Discarded')
        attributesizer.Add(self.labels[statusTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[statusTAG], 0, wx.EXPAND)
	
	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)    
	        

########################################################################        
######          Cell Line (Stock Culture) SETTING PANEL           ######
########################################################################
class CellLineSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Sample|CellLine'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = CellLinePanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)        

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = CellLinePanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = CellLinePanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)         


class CellLinePanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Name|'+str(self.tab_number), 
	                       self.tag_stump+'|CatalogueNo|%s'%str(self.tab_number),
	                       self.tag_stump+'|Organism|%s'%str(self.tab_number)]
	self.currpassageNo = 0	
	self.elapsed_time = [0]
	self.master_elapsed_min = 0
	self.cumulative_pd = [0] 
	self.action_buttons = {}
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	
	self.action_pair = {
		    'Seed': ['Seed'],
		    'Passage': ['Seed'],
		    #'Freeze': ['Freeze','Passage', 'Enrich'],
		    #'Enrich': ['Enrich','Seed']
		}	

	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)	

	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[self.nameTAG].SetToolTipString('Cell Line selection')
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Cell Line/Designation')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")	
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 1, wx.EXPAND) 
	attributesizer.Add(self.save_btn, 0)
	
	
	#===== Administrative Information =====#
	admin_staticbox = wx.StaticBox(self.sw, -1, "Administrative Information")
	admin_fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	authorityTAG = self.tag_stump+'|Authority|%s'%str(self.tab_number)
	self.settings_controls[authorityTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(authorityTAG, default=''))
	self.settings_controls[authorityTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[authorityTAG].SetToolTipString('Cell Line selection')
	self.labels[authorityTAG] = wx.StaticText(self.sw, -1, 'Authority')
	admin_fgs.Add(self.labels[authorityTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	admin_fgs.Add(self.settings_controls[authorityTAG], 0, wx.EXPAND)	

        acttTAG = self.tag_stump+'|CatalogueNo|%s'%str(self.tab_number)
        self.settings_controls[acttTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(acttTAG, default=''))
        self.settings_controls[acttTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
        self.settings_controls[acttTAG].SetToolTipString('ATCC reference')
	self.labels[acttTAG] = wx.StaticText(self.sw, -1, 'Reference/Catalogue Number')
        admin_fgs.Add(self.labels[acttTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        admin_fgs.Add(self.settings_controls[acttTAG], 0, wx.EXPAND)	

	depositTAG = self.tag_stump+'|Depositors|%s'%str(self.tab_number)
	self.settings_controls[depositTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(depositTAG, default=''))
	self.settings_controls[depositTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[depositTAG].SetToolTipString('Depositors')
	self.labels[depositTAG] = wx.StaticText(self.sw, -1, 'Depositors')
	admin_fgs.Add(self.labels[depositTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	admin_fgs.Add(self.settings_controls[depositTAG], 0, wx.EXPAND)	

	biosafeTAG = self.tag_stump+'|Biosafety|%s'%str(self.tab_number)
	self.settings_controls[biosafeTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(biosafeTAG, default=''))
	self.settings_controls[biosafeTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[biosafeTAG].SetToolTipString('Biosafety Level')
	self.labels[biosafeTAG] = wx.StaticText(self.sw, -1, 'Biosafety Level')
	admin_fgs.Add(self.labels[biosafeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	admin_fgs.Add(self.settings_controls[biosafeTAG], 0, wx.EXPAND)	

	shipmentTAG = self.tag_stump+'|Shipment|%s'%str(self.tab_number)
	self.settings_controls[shipmentTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(shipmentTAG, default=''))
	self.settings_controls[shipmentTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[shipmentTAG].SetToolTipString('Shipment')
	self.labels[shipmentTAG] = wx.StaticText(self.sw, -1, 'Shipment')
	admin_fgs.Add(self.labels[shipmentTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	admin_fgs.Add(self.settings_controls[shipmentTAG], 0, wx.EXPAND)

	permitTAG = self.tag_stump+'|Permit|%s'%str(self.tab_number)
	self.settings_controls[permitTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(permitTAG, default=''))
	self.settings_controls[permitTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[permitTAG].SetToolTipString('Shipment')
	self.labels[permitTAG] = wx.StaticText(self.sw, -1, 'Permits Reference')
	admin_fgs.Add(self.labels[permitTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	admin_fgs.Add(self.settings_controls[permitTAG], 0, wx.EXPAND)	
	
	adminSizer = wx.StaticBoxSizer(admin_staticbox, wx.VERTICAL)	
	adminSizer.Add(admin_fgs,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	
	#===== Biological Information=====#        
	bio_staticbox = wx.StaticBox(self.sw, -1, "Biological Information")
	bio_fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	growpropTAG = self.tag_stump+'|GrowthProperty|%s'%str(self.tab_number)
	self.settings_controls[growpropTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(growpropTAG, default=''))
	self.settings_controls[growpropTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[growpropTAG].SetToolTipString('e.g adherent, suspended')
	self.labels[growpropTAG] = wx.StaticText(self.sw, -1, 'Growth Properties')
	bio_fgs.Add(self.labels[growpropTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[growpropTAG], 0, wx.EXPAND) 

	taxIdTAG = self.tag_stump+'|Organism|%s'%str(self.tab_number)
	organism_choices =['Homo Sapiens', 'Mus Musculus', 'Rattus Norvegicus', 'Other']
	self.settings_controls[taxIdTAG]= wx.ListBox(self.sw, -1, wx.DefaultPosition, (220,30), organism_choices, wx.LB_SINGLE)
	if meta.get_field(taxIdTAG) is not None:
	    self.settings_controls[taxIdTAG].Append(meta.get_field(taxIdTAG))
	    self.settings_controls[taxIdTAG].SetStringSelection(meta.get_field(taxIdTAG))
	self.settings_controls[taxIdTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)   
	self.settings_controls[taxIdTAG].SetToolTipString('Taxonomic ID of the species') 
	self.labels[taxIdTAG] = wx.StaticText(self.sw, -1, 'Organism')
	bio_fgs.Add(self.labels[taxIdTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[taxIdTAG], 0, wx.EXPAND)	

	morphTAG = self.tag_stump+'|Morphology|%s'%str(self.tab_number)
	self.settings_controls[morphTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(morphTAG, default=''))
	self.settings_controls[morphTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[morphTAG].SetToolTipString('Cell morphology e.g epithelial')
	self.labels[morphTAG] = wx.StaticText(self.sw, -1, 'Morphology')
	bio_fgs.Add(self.labels[morphTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[morphTAG], 0, wx.EXPAND) 

	organTAG = self.tag_stump+'|Organ|%s'%str(self.tab_number)
	self.settings_controls[organTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(organTAG, default=''))
	self.settings_controls[organTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[organTAG].SetToolTipString('Source organ')
	self.labels[organTAG] = wx.StaticText(self.sw, -1, 'Organ')
	bio_fgs.Add(self.labels[organTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[organTAG], 0, wx.EXPAND) 	

	diseaseTAG = self.tag_stump+'|Disease|%s'%str(self.tab_number)
	self.settings_controls[diseaseTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(diseaseTAG, default=''))
	self.settings_controls[diseaseTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[diseaseTAG].SetToolTipString('Disease specificity e.g. osteosarcoma')
	self.labels[diseaseTAG] = wx.StaticText(self.sw, -1, 'Disease')
	bio_fgs.Add(self.labels[diseaseTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[diseaseTAG], 0, wx.EXPAND) 

	productTAG = self.tag_stump+'|Products|%s'%str(self.tab_number)
	self.settings_controls[productTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(productTAG, default=''))
	self.settings_controls[productTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[productTAG].SetToolTipString('e.g osteosarcoma derived cell product (ODGF)')
	self.labels[productTAG] = wx.StaticText(self.sw, -1, 'Cellular Products')
	bio_fgs.Add(self.labels[productTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[productTAG], 0, wx.EXPAND) 	

	appTAG = self.tag_stump+'|Applications|%s'%str(self.tab_number)
	self.settings_controls[appTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(appTAG, default=''))
	self.settings_controls[appTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[appTAG].SetToolTipString('e.g transfection hosts')
	self.labels[appTAG] = wx.StaticText(self.sw, -1, 'Applications')
	bio_fgs.Add(self.labels[appTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[appTAG], 0, wx.EXPAND) 	

	receptorTAG = self.tag_stump+'|Receptors|%s'%str(self.tab_number)
	self.settings_controls[receptorTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(receptorTAG, default=''))
	self.settings_controls[receptorTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[receptorTAG].SetToolTipString('e.g insuline like growth factors I')
	self.labels[receptorTAG] = wx.StaticText(self.sw, -1, 'Receptors')
	bio_fgs.Add(self.labels[receptorTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[receptorTAG], 0, wx.EXPAND) 

	antigenTAG = self.tag_stump+'|Antigen|%s'%str(self.tab_number)
	self.settings_controls[antigenTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE, value=meta.get_field(antigenTAG, default=''))
	self.settings_controls[antigenTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[antigenTAG].SetToolTipString('e.g Blood type A')
	self.labels[antigenTAG] = wx.StaticText(self.sw, -1, 'Antigen Expression')
	bio_fgs.Add(self.labels[antigenTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[antigenTAG], 0, wx.EXPAND)  	

	dnaTAG = self.tag_stump+'|DNA|%s'%str(self.tab_number)
	self.settings_controls[dnaTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE, value=meta.get_field(dnaTAG, default=''))
	self.settings_controls[dnaTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[dnaTAG].SetToolTipString('DNA profile')
	self.labels[dnaTAG] = wx.StaticText(self.sw, -1, 'DNA Profile')
	bio_fgs.Add(self.labels[dnaTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[dnaTAG], 0, wx.EXPAND)

	cytogenTAG = self.tag_stump+'|Cytogenetic|%s'%str(self.tab_number)
	self.settings_controls[cytogenTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE, value=meta.get_field(cytogenTAG, default=''))
	self.settings_controls[cytogenTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[cytogenTAG].SetToolTipString('Cytogenetic Analysis')
	self.labels[cytogenTAG] = wx.StaticText(self.sw, -1, 'Cytogenetic Analysis')
	bio_fgs.Add(self.labels[cytogenTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[cytogenTAG], 0, wx.EXPAND) 	

	enzymeTAG = self.tag_stump+'|Isoenzymes|%s'%str(self.tab_number)
	self.settings_controls[enzymeTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE, value=meta.get_field(enzymeTAG, default=''))
	self.settings_controls[enzymeTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[enzymeTAG].SetToolTipString('Isoenzymes')
	self.labels[enzymeTAG] = wx.StaticText(self.sw, -1, 'Isoenzymes')
	bio_fgs.Add(self.labels[enzymeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[enzymeTAG], 0, wx.EXPAND) 

	ageTAG = self.tag_stump+'|Age|%s'%str(self.tab_number)
	self.settings_controls[ageTAG] = wx.TextCtrl(self.sw,  style=wx.TE_PROCESS_ENTER, value=meta.get_field(ageTAG, default=''))
	self.settings_controls[ageTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[ageTAG].SetToolTipString('Age of the organism in days when the cells were collected. .')
	self.labels[ageTAG] = wx.StaticText(self.sw, -1, 'Age of Organism (days)')
	bio_fgs.Add(self.labels[ageTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[ageTAG], 0, wx.EXPAND)

	gendTAG = self.tag_stump+'|Gender|%s'%str(self.tab_number)
	self.settings_controls[gendTAG] = wx.Choice(self.sw, -1,  choices=['Male', 'Female', 'Neutral'])
	if meta.get_field(gendTAG) is not None:
	    self.settings_controls[gendTAG].SetStringSelection(meta.get_field(gendTAG))
	self.settings_controls[gendTAG].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.settings_controls[gendTAG].SetToolTipString('Gender of the organism')
	self.labels[gendTAG] = wx.StaticText(self.sw, -1, 'Gender')
	bio_fgs.Add(self.labels[gendTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[gendTAG], 0, wx.EXPAND) 

	ethnicityTAG = self.tag_stump+'|Ethnicity|%s'%str(self.tab_number)
	self.settings_controls[ethnicityTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(ethnicityTAG, default=''))
	self.settings_controls[ethnicityTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[ethnicityTAG].SetToolTipString('Ethnicity')
	self.labels[ethnicityTAG] = wx.StaticText(self.sw, -1, 'Ethnicity')
	bio_fgs.Add(self.labels[ethnicityTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[ethnicityTAG], 0, wx.EXPAND)

	commentTAG = self.tag_stump+'|Comments|%s'%str(self.tab_number)
	self.settings_controls[commentTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE, value=meta.get_field(commentTAG, default=''))
	self.settings_controls[commentTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[commentTAG].SetToolTipString('Comments on the cell line')
	self.labels[commentTAG] = wx.StaticText(self.sw, -1, 'Comments')
	bio_fgs.Add(self.labels[commentTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[commentTAG], 0, wx.EXPAND) 		

	publicationTAG = self.tag_stump+'|Publications|%s'%str(self.tab_number)
	self.settings_controls[publicationTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE, value=meta.get_field(publicationTAG, default=''))
	self.settings_controls[publicationTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[publicationTAG].SetToolTipString('Reference Publications')
	self.labels[publicationTAG] = wx.StaticText(self.sw, -1, 'Publications')
	bio_fgs.Add(self.labels[publicationTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[publicationTAG], 0, wx.EXPAND) 

	relprodTAG = self.tag_stump+'|RelProduct|%s'%str(self.tab_number)
	self.settings_controls[relprodTAG] = wx.TextCtrl(self.sw, style=wx.TE_PROCESS_ENTER, value=meta.get_field(relprodTAG, default=''))
	self.settings_controls[relprodTAG].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[relprodTAG].SetToolTipString('Related Product')
	self.labels[relprodTAG] = wx.StaticText(self.sw, -1, 'Related Product')
	bio_fgs.Add(self.labels[relprodTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	bio_fgs.Add(self.settings_controls[relprodTAG], 0, wx.EXPAND) 	       

	bioSizer = wx.StaticBoxSizer(bio_staticbox, wx.VERTICAL)	
	bioSizer.Add(bio_fgs,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	
	# ==== Propagation  ====
	prop_staticbox = wx.StaticBox(self.sw, -1, "Cell History")	
	prop_fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

        self.orgpassTAG = self.tag_stump+'|OrgPassageNo|%s'%str(self.tab_number)
        self.settings_controls[self.orgpassTAG] = wx.lib.masked.NumCtrl(self.sw,  size=(20,-1), style=wx.TE_PROCESS_ENTER, value=meta.get_field(self.orgpassTAG, default=0))
        self.settings_controls[self.orgpassTAG].Bind(wx.EVT_TEXT, self.OnSavingData)    
        self.settings_controls[self.orgpassTAG].SetToolTipString('Numeric value of the passage of the cells under investigation')
	self.labels[self.orgpassTAG] = wx.StaticText(self.sw, -1, 'Original Passage No')
        prop_fgs.Add(self.labels[self.orgpassTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        prop_fgs.Add(self.settings_controls[self.orgpassTAG], 0, wx.EXPAND)
	if self.settings_controls[self.orgpassTAG].GetValue() > 0:
	    self.settings_controls[self.orgpassTAG].Disable()
	
	self.curr_pass_text = wx.StaticText(self.sw, -1, '')
	prop_fgs.Add(wx.StaticText(self.sw, -1, 'Current Passage No'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
	prop_fgs.Add(self.curr_pass_text, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)	
	self.updatePassageNo() #update the current passage number
	
	self.canvas = plot.PlotCanvas(self.sw)
	self.canvas.SetInitialSize(size=(400, 300))
	
	    
	self.showpasshisBut  = wx.Button(self.sw, -1, label="Show History")
	self.showpasshisBut.Bind(wx.EVT_BUTTON, self.onshowPassHistory)
	
	propSizer = wx.StaticBoxSizer(prop_staticbox, wx.VERTICAL)	
	propSizer.Add(prop_fgs,  0, wx.ALIGN_LEFT|wx.ALL, 5 )
	propSizer.Add(self.showpasshisBut, 0, wx.EXPAND|wx.ALL, 5)
	propSizer.Add(self.canvas, 0, wx.EXPAND|wx.ALL, 5)
	
	# Draw PD Chart from previous instances
	self.historyTAG = self.tag_stump+'|History|%s'%str(self.tab_number)
	self.cell_history = meta.get_field(self.historyTAG, default=[])
	
	if len(self.cell_history) > 1:
	    for a, action in enumerate(self.cell_history):
		if a+1 < len(self.cell_history):
		    min_diff = self.cell_history[a+1][3] - self.cell_history[a][3] 
		    last_seed_density = [info[1] for info in meta.get_field(self.tag_stump+'|%s|%s' %(self.cell_history[a][0], str(self.tab_number)))
					  if info[0]=='SEED']
		    curr_harvest_density = [info[1] for info in meta.get_field(self.tag_stump+'|%s|%s' %(self.cell_history[a+1][0], str(self.tab_number)))
					  if info[0]=='HARVEST']
		    if last_seed_density and curr_harvest_density and (min_diff > 0):
			self.master_elapsed_min += min_diff
			self.elapsed_time.append(self.master_elapsed_min/60)			
			cell_growth = max(math.log(curr_harvest_density[0][0]/last_seed_density[0][0]), 1)
			pdt = (min_diff*math.log(2)/cell_growth)/60
			self.cumulative_pd.append(self.cumulative_pd[-1]+pdt)
		    
	    self.drawPDChart()	

	act_staticbox = wx.StaticBox(self.sw, -1, "Actions")
	act_fgs = wx.FlexGridSizer(cols=5, hgap=5, vgap=5)
	
	self.action_buttons['Seed'] = wx.Button(self.sw, -1, label="Seed")
	self.action_buttons['Seed'].actiontype = "Seed"
	self.action_buttons['Passage'] = wx.Button(self.sw, -1, label="Passage")
	self.action_buttons['Passage'].actiontype = "Passage"
	#self.action_buttons['Freeze'] = wx.Button(self.sw, -1, label="Freeze")
	#self.action_buttons['Freeze'].actiontype = "Freeze"	
	#self.action_buttons['Enrich'] = wx.Button(self.sw, -1, label="Enrich")
	#self.action_buttons['Enrich'].actiontype = "Enrich"
	
	self.action_buttons['Seed'].Bind(wx.EVT_BUTTON, self.onRecordAction)
	self.action_buttons['Passage'].Bind(wx.EVT_BUTTON, self.onRecordAction)
	#self.action_buttons['Freeze'].Bind(wx.EVT_BUTTON, self.onRecordAction)
	#self.action_buttons['Enrich'].Bind(wx.EVT_BUTTON, self.onRecordAction)
	#self.recordPassageBtn.Bind(wx.EVT_BUTTON, self.onRecordPassage)
	
	act_fgs.Add(self.action_buttons['Seed'], 0)
	act_fgs.Add(self.action_buttons['Passage'], 0)
	#act_fgs.Add(self.action_buttons['Freeze'], 0)
	#act_fgs.Add(self.action_buttons['Enrich'], 0)
	actSizer = wx.StaticBoxSizer(act_staticbox, wx.HORIZONTAL)
	actSizer.Add(act_fgs, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
	#---------------Layout with sizers---------------		
	topsizer = wx.BoxSizer(wx.VERTICAL)
	topsizer.Add(titlesizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
	topsizer.Add((-1,10))
	topsizer.Add(attributesizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
	topsizer.Add(adminSizer, 0, wx.EXPAND|wx.ALL, 10)
	topsizer.Add(bioSizer, 0, wx.EXPAND|wx.ALL, 10)
	topsizer.Add(propSizer, 0, wx.EXPAND|wx.ALL, 10)
	topsizer.Add(actSizer, 0, wx.EXPAND|wx.ALL, 10)
        self.sw.SetSizer(topsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
  
    def onRecordAction(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):    
	    self.settings_controls[self.orgpassTAG].Disable()
	    
	    # find the current number of the action
	    # first identify what type of action it is
	    action = event.GetEventObject().actiontype
	    # Reset buttons
	    for act in self.action_buttons.keys():
		self.action_buttons[act].Enable()
	    for pa in self.action_pair[action]:
		self.action_buttons[pa].Disable()
	    # Get current action number	
	    last_date = []
	    if self.cell_history:
		prev_actions = [pv[0] for pv in self.cell_history
		                if pv[0].startswith(action)]
		last_date = self.cell_history[-1][2]
	    else:
		prev_actions = []
	    
	    if prev_actions:
		prev_act = sorted(prev_actions, key = meta.stringSplitByNumbers)[-1]
		curr_act_num = int(prev_act.split(action)[1])+1
	    else:
		curr_act_num = 1
		if action == 'Passage':
		    curr_act_num += int(meta.get_field(self.tag_stump+'|OrgPassageNo|%s'%str(self.tab_number), default = 0)) 
	    
	    # Show the passage dialog
	    dia = MaintainAction(self, self.protocol, curr_act_num, action, last_date)
	    if dia.ShowModal() == wx.ID_OK: 
		attribute = '%s%s'%(action, str(curr_act_num))
	        if self.cell_history and action == 'Passage':   
			# update master elapsed time
			last_pd_act = [pv[0] for pv in self.cell_history
		                       if re.match('Seed|Passage', pv[0])][-1]
			if last_pd_act:
			    ldt = [tg[2] for tg in self.cell_history if tg[0] == last_pd_act][-1]
			    last_tp = datetime.datetime(*map(int, [ldt[0],ldt[1],ldt[2],ldt[3],ldt[4],ldt[5]]))
			    time_diff = (dia.selected_datetime-last_tp)
			    min_diff = (time_diff.days * 1440) + (time_diff.seconds / 60)
			    self.master_elapsed_min += min_diff
			    self.elapsed_time.append(self.master_elapsed_min/60)
			    last_seed_density = [info[1] for info in meta.get_field(self.tag_stump+'|%s|%s' %(last_pd_act, str(self.tab_number)))
			      if info[0]=='SEED']
			    cell_growth = max(math.log(dia.curr_protocol['HARVEST'][0]/last_seed_density[0][0]), 1)
			    pdt = (min_diff*math.log(2)/cell_growth)/60
			    self.cumulative_pd.append(self.cumulative_pd[-1]+pdt)
			    
			    self.drawPDChart()
			    
		# Set the cell history
		self.cell_history.append((attribute, dia.curr_protocol['ADMIN'][0], dia.sel_date_time, self.master_elapsed_min))
		meta.set_field(self.historyTAG, self.cell_history)
		
		if action == 'Passage' or action == 'Seed':
		    meta.set_field(self.tag_stump+'|%s|%s' %(attribute, str(self.tab_number)), dia.curr_protocol.items())
		    self.updatePassageNo() #update the current passage number
		else:
		    meta.set_field(self.tag_stump+'|%s|%s' %(attribute, self.tab_number), dia.curr_protocol.items())
		    attr_list = meta.get_attribute_list_by_instance(self.tag_stump, self.tab_number)
		    for tab in range(1, int(dia.curr_protocol['SPLIT'])+1):
			for attr in attr_list:
			    meta.set_field(self.tag_stump+'|%s|%s'%(attr, str(int(self.tab_number)+tab)), 
			                   meta.get_field(self.tag_stump+'|%s|%s'%(attr, self.tab_number))) 
			panel = CellLinePanel(self.Parent, self.tag_stump, str(int(self.tab_number)+tab))
			self.Parent.AddPage(panel, 'Instance No: %s'%str(int(self.tab_number)+tab), True)			    
		
		    
	    dia.Destroy()   
	    
	    #panel = CellLinePanel(self.Parent, self.tag_stump, '2')
	    #self.Parent.AddPage(panel, 'Instance No: 2', True)
	    
	    # self.drawPDChart()
    def drawPDChart(self):
	data = []
	for i, timepoint in enumerate(self.elapsed_time):
	    data.append((timepoint, self.cumulative_pd[i]))
	line = plot.PolyLine(data, colour='green', width=1)
		## also draw markers, default colour is black and size is 2
		## other shapes 'circle', 'cross', 'square', 'dot', 'plus'
	marker = plot.PolyMarker(data, marker='circle', colour='green')
		## set up text, axis and draw
	gc = plot.PlotGraphics([line, marker], 'Population double chart', 'Accumulated Time (hours)', 'Accumulated PDs')
	self.canvas.Refresh()
	self.canvas.Draw(gc, xAxis=(0,max(self.elapsed_time)+24), yAxis=(0,max(self.cumulative_pd)+1))	

    def onRecordPassage(self, event):
        if meta.checkMandatoryTags(self.mandatory_tags):
	    orgPassNum = meta.get_field(self.tag_stump+'|OrgPassageNo|%s'%str(self.tab_number), default = 0)
	    
	    passages = [attr for attr in meta.get_attribute_list_by_instance(self.tag_stump, str(self.tab_number))
		                if attr.startswith('Passage')]
	    if passages:
		lastpassage = sorted(passages, key = meta.stringSplitByNumbers)[-1]
		self.currpassageNo = int(lastpassage.split('Passage')[1])+1
	    else:
		self.currpassageNo = int(orgPassNum)+1
	    
	    # Show the passage dialog
	    dia = PassageStepBuilder(self, self.protocol, self.currpassageNo, 'passage')
	    if dia.ShowModal() == wx.ID_OK: 
		meta.set_field(self.tag_stump+'|Passage%s|%s' %(str(self.currpassageNo), str(self.tab_number)), dia.curr_protocol.items())	# set the value as a list rather than a dictionary
		#self.showPassages()
	    dia.Destroy()
	    
    def onshowPassHistory(self, event):
	passages = [attr for attr in meta.get_attribute_list_by_instance(self.tag_stump, str(self.tab_number))
		                    if attr.startswith('Passage')]
	if passages: 
	    metadata = ''
	    for passage in reversed(sorted(passages, key=meta.alphanumeric_sort)):
		# make a foldable panel for each passage
		admin_info = self.getAdminInfo(passage)	    
		passage_info = meta.get_field(self.tag_stump+'|%s|%s' %(passage, str(self.tab_number)))
		curr_protocol = dict(passage_info)
		steps = sorted([step for step in curr_protocol.keys()
		         if step.startswith('Step')] , key = meta.stringSplitByNumbers)
		string = ''
		for s in steps:
		    step_info = curr_protocol.get(s)
		    string += s+': %s ' %step_info[0]
		    if len(step_info[1])> 0:
			string += 'for %s mins ' %step_info[1]
		    if len(step_info[2])> 0:
			string += 'at %s C ' %step_info[2]	  
		    if len(step_info[3])> 0:
			string += 'Tips: %s' %step_info[3]		    
		    string += '\n'
		    
		metadata += '\n'+passage+': %s\n'%admin_info	
		metadata += string
		
	    dia = MultiLineShow(self, '', '', '', metadata)
	    dia.ShowModal()

    def showPassages(self):
	'''This method writes the updated passage history in a sequence fashion'''
	passages = [attr for attr in meta.get_attribute_list_by_instance(self.tag_stump, str(self.tab_number))
		                    if attr.startswith('Passage')]

	if passages: 	    
	    self.curr_pass_text.SetLabel('%s' %re.sub("[^0-9]", "", sorted(passages, key=meta.alphanumeric_sort)[-1]))
	    
	    self.fpbsizer.Clear(deleteWindows=True)
	    self.settings_controls[self.tag_stump+'|OrgPassageNo|%s'%str(self.tab_number)].Disable()
	    #pass_title = wx.StaticText(self.bot_panel, -1, 'Passage History')
	    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
	    pass_title.SetFont(font)
	    self.fpbsizer.Add(pass_title, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)	  
	    self.elapsed_time = [0]
	    self.cumulative_pd = [0]
	    for passage in sorted(passages, key=meta.alphanumeric_sort):
		passage_info = meta.get_field(self.tag_stump+'|%s|%s' %(passage, str(self.tab_number)))
		pd_info = dict(passage_info).get('PD')
		if pd_info:
		    self.elapsed_time.append(self.elapsed_time[-1]+pd_info[2]) 
		    self.cumulative_pd.append(self.cumulative_pd[-1]+pd_info[1])
		data = []
		for i, timepoint in enumerate(self.elapsed_time):
		    data.append((timepoint, self.cumulative_pd[i]))
		line = plot.PolyLine(data, colour='green', width=1)
			## also draw markers, default colour is black and size is 2
			## other shapes 'circle', 'cross', 'square', 'dot', 'plus'
		marker = plot.PolyMarker(data, marker='circle', colour='green')
			## set up text, axis and draw
		gc = plot.PlotGraphics([line, marker], 'Population double chart', 'Accumulated Time (hours)', 'Accumulated PDs')
		self.canvas.Refresh()
		self.canvas.Draw(gc, xAxis=(0,max(self.elapsed_time)+24), yAxis=(0,max(self.cumulative_pd)+1))		

	    # Sizers update	
	    self.bot_panel.SetSizer(self.fpbsizer)
	    self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
    
    def OnPaneChanged(self, evt=None):
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	#self.bot_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
    #def passagePane(self, pane, passage):
	#''' This pane makes the microscope stand (backbone of the microscope)'''	
	
	#meta = ExperimentSettings.getInstance()
	#self.pane = pane
	
	#passage_info = meta.get_field(self.tag_stump+'|%s|%s' %(passage, str(self.tab_number)))
	#curr_protocol = dict(passage_info)
	
	#steps = sorted([step for step in curr_protocol.keys()
		 #if step.startswith('Step')] , key = meta.stringSplitByNumbers)
	
	#string = ''
	#for s in steps:
	    #step_info = curr_protocol.get(s)
	    #string += s+': %s ' %step_info[0]
	    #if len(step_info[1])> 0:
		#string += 'for %s mins ' %step_info[1]
	    #if len(step_info[2])> 0:
		#string += 'at %s C ' %step_info[2]	  
	    #if len(step_info[3])> 0:
		#string += 'Tips: %s' %step_info[3]		    
	    #string += '\n'
	    
	#wx.StaticText(self.pane, -1, string) 
	
 
    def validate(self):
        pass
    
    def updatePassageNo(self):
	self.curr_pass_text.SetLabel('%d' %self.settings_controls[self.orgpassTAG].GetValue())
	passages = [attr for attr in meta.get_attribute_list_by_instance(self.tag_stump, str(self.tab_number))
		                    if attr.startswith('Passage')]	
	if passages:
	    self.curr_pass_text.SetLabel('%d' %(len(passages)+self.settings_controls[self.orgpassTAG].GetValue()))
	    
    def getAdminInfo(self, passage):
	meta = ExperimentSettings.getInstance()
	passage_info = meta.get_field(self.tag_stump+'|%s|%s' %(passage, str(self.tab_number)))
	admin_info = dict(passage_info).get('ADMIN')
	return '%s passaged on %s at %s ' %(admin_info[0], admin_info[1], admin_info[2])
    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)   
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)    
    
    def OnSavingData(self, event):	
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)
	    
	self.updatePassageNo() #update the current passage number
	
    
	
########################################################################        
################## MICROSCOPE SETTING PANEL         ####################
########################################################################
class MicroscopeSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Instrument|Microscope'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = MicroscopePanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)        

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = MicroscopePanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = MicroscopePanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True) 


class MicroscopePanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	 
	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	
	# TAG
	self.tab_number = tab_number	# tab or instance number
	self.tag_stump = tag_stump                  # first two parts of tag (type|event) e.g Instrument|Centrifuge
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []        # mandatory fields 
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)	
	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)    
	#  Protocol Name
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))	
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.settings_controls[self.nameTAG].SetToolTipString('Type a unique name for the channel')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(wx.StaticText(self.sw, -1, 'Channel Name'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL) 
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0, wx.EXPAND)
	
	# Progress bar
	self.gauge = wx.Gauge(self.sw, -1, 100, size=(250, 20), style=wx.GA_SMOOTH)
	attributesizer.Add(wx.StaticText(self.sw, -1, 'Data filled so far'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL) 
	attributesizer.Add(self.gauge, 0)
	self.progpercent = wx.StaticText(self.sw, -1, '')
	attributesizer.Add(self.progpercent, 0)
	staticbox = wx.StaticBox(self.sw, -1, "Instrument Information")			
	attribute_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	attribute_Sizer.Add(attributesizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )		

	# ==== Local  ====
	localsizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	nickTAG = self.tag_stump+'|NickName|'+str(self.tab_number)
	self.settings_controls[nickTAG] = wx.TextCtrl(self.sw, name='Nick Name' ,  value=meta.get_field(nickTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[nickTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[nickTAG] = wx.StaticText(self.sw, -1, 'Nick Name')
	self.labels[nickTAG].SetToolTipString('Nick Name of the instrument')
	localsizer.Add(self.labels[nickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[nickTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	srlTAG = self.tag_stump+'|SerialNo|'+str(self.tab_number)
	self.settings_controls[srlTAG] = wx.TextCtrl(self.sw, name='Serial Number' ,  value=meta.get_field(srlTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[srlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[srlTAG] = wx.StaticText(self.sw, -1, 'Serial Number')
	self.labels[srlTAG].SetToolTipString('Serial Number')
	localsizer.Add(self.labels[srlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[srlTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	adrsTAG = self.tag_stump+'|Address|'+str(self.tab_number)
	self.settings_controls[adrsTAG] = wx.TextCtrl(self.sw, name='Address' ,  value=meta.get_field(adrsTAG, default=''), size=(-1, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.settings_controls[adrsTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[adrsTAG] = wx.StaticText(self.sw, -1, 'Address')
	self.labels[adrsTAG].SetToolTipString('Address where of the instrument location')
	localsizer.Add(self.labels[adrsTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[adrsTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	roomTAG = self.tag_stump+'|Room|'+str(self.tab_number)
	self.settings_controls[roomTAG] = wx.TextCtrl(self.sw, name='Room' ,  value=meta.get_field(roomTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[roomTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[roomTAG] = wx.StaticText(self.sw, -1, 'Room Number')
	self.labels[roomTAG].SetToolTipString('Room where of the instrument location')
	localsizer.Add(self.labels[roomTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[roomTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	staticbox = wx.StaticBox(self.sw, -1, "Local Information")			
	local_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	local_Sizer.Add(localsizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	#-- COLLAPSIBLE PANES ---#
	self.strucpane= wx.CollapsiblePane(self.sw, label="Hardware", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
	self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, self.strucpane)
	self.hardwarePane(self.strucpane.GetPane())
	
        self.illumpane = wx.CollapsiblePane(self.sw, label="Optics", style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, self.illumpane)
        self.opticsPane(self.illumpane.GetPane())

	#---------------Layout with sizers---------------
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	self.swsizer.Add(titlesizer)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attribute_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(local_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(self.strucpane, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)
	self.swsizer.Add(self.illumpane, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)
	
        self.sw.SetSizer(self.swsizer)
        self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
	self.updateProgressBar()

    def OnPaneChanged(self, evt=None):
        self.sw.SetSizer(self.swsizer)
        self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

    def hardwarePane(self, pane):
	''' This pane makes the microscope stand (backbone of the microscope)'''	
	
	meta = ExperimentSettings.getInstance()
	self.pane = pane	
	
	#--- Stand ---#	
	staticbox = wx.StaticBox(self.pane, -1, "Stand")
	standSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	microstandTAG = self.tag_stump+'|Stand|%s'%str(self.tab_number)
	microstand = meta.get_field(microstandTAG, [])
	
	stand_choices=['Wide Field','Laser Scanning Microscopy', 'Laser Scanning Confocal', 'Spinning Disk Confocal', 'Slit Scan Confocal', 'Multi Photon Microscopy', 'Structured Illumination','Single Molecule Imaging', 'Total Internal Reflection', 'Fluorescence Lifetime', 'Spectral Imaging', 'Fluorescence Correlation Spectroscopy', 'Near FieldScanning Optical Microscopy', 'Second Harmonic Generation Imaging', 'Timelapse', 'Unknown', 'Other']
	self.settings_controls[microstandTAG+'|0']= wx.ListBox(self.pane, -1, wx.DefaultPosition, (150,30), stand_choices, wx.LB_SINGLE)
	if len(microstand) > 0:
	    self.settings_controls[microstandTAG+'|0'].Append(microstand[0])
	    self.settings_controls[microstandTAG+'|0'].SetStringSelection(microstand[0])
	self.settings_controls[microstandTAG+'|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData) 
	self.labels[microstandTAG+'|0'] = wx.StaticText(self.pane, -1, 'Type')
	self.labels[microstandTAG+'|0'].SetToolTipString('Type of microscope e.g. Inverted, Confocal...') 
	multctrlSizer.Add(self.labels[microstandTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[microstandTAG+'|0'], 0, wx.EXPAND)	
	
	make_choices=['Zeiss','Olympus','Nikon', 'MDS','GE', 'Unknown', 'Other']
	self.settings_controls[microstandTAG+'|1']= wx.ListBox(self.pane, -1, wx.DefaultPosition, (150,30), make_choices, wx.LB_SINGLE)
	if len(microstand) > 1:
	    self.settings_controls[microstandTAG+'|1'].Append(microstand[1])
	    self.settings_controls[microstandTAG+'|1'].SetStringSelection(microstand[1])
	self.settings_controls[microstandTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	self.labels[microstandTAG+'|1'] =  wx.StaticText(self.pane, -1, 'Make')
	self.labels[microstandTAG+'|1'].SetToolTipString('Manufacturer of microscope') 
	multctrlSizer.Add(self.labels[microstandTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[microstandTAG+'|1'], 0, wx.EXPAND)		
	
	self.settings_controls[microstandTAG+'|2']= wx.TextCtrl(self.pane, value='') 
	if len(microstand) > 2:
	    self.settings_controls[microstandTAG+'|2'].SetValue(microstand[2])
	self.settings_controls[microstandTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[microstandTAG+'|2'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[microstandTAG+'|2'].SetToolTipString('Model of the microscope') 
	multctrlSizer.Add(self.labels[microstandTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[microstandTAG+'|2'], 0, wx.EXPAND)
		
	self.settings_controls[microstandTAG+'|3']= wx.Choice(self.pane, -1, choices=['', 'Upright', 'Inverted'])
	if len(microstand) > 3:
	    self.settings_controls[microstandTAG+'|3'].SetStringSelection(microstand[3])
	self.settings_controls[microstandTAG+'|3'].Bind(wx.EVT_CHOICE, self.OnSavingData) 
	self.labels[microstandTAG+'|3'] = wx.StaticText(self.pane, -1, 'Orientation')
	self.labels[microstandTAG+'|3'].SetToolTipString('Orientation of the microscope in relation to the sample') 
	multctrlSizer.Add(self.labels[microstandTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[microstandTAG+'|3'], 0, wx.EXPAND)	
	
	self.settings_controls[microstandTAG+'|4']= wx.SpinCtrl(self.pane, -1, "", (30, 50))
	self.settings_controls[microstandTAG+'|4'].SetRange(0,20)
	if len(microstand) > 4:
	    self.settings_controls[microstandTAG+'|4'].SetValue(int(microstand[4]))
	self.settings_controls[microstandTAG+'|4'].Bind(wx.EVT_SPINCTRL, self.OnSavingData)
	self.labels[microstandTAG+'|4'] = wx.StaticText(self.pane, -1, 'Number of Lamps')
	self.labels[microstandTAG+'|4'].SetToolTipString('Number of lamps used in the microscope') 
	multctrlSizer.Add(self.labels[microstandTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[microstandTAG+'|4'], 0, wx.EXPAND) 	     
	
	self.settings_controls[microstandTAG+'|5']= wx.SpinCtrl(self.pane, -1, "", (30, 50))
	self.settings_controls[microstandTAG+'|5'].SetRange(0,20)
	if len(microstand) > 5:
	    self.settings_controls[microstandTAG+'|5'].SetValue(int(microstand[5]))
	self.settings_controls[microstandTAG+'|5'].Bind(wx.EVT_SPINCTRL, self.OnSavingData)
	self.labels[microstandTAG+'|5'] = wx.StaticText(self.pane, -1, 'Number of Detectors')
	self.labels[microstandTAG+'|5'].SetToolTipString('Number of detectors used in the microscope') 
	multctrlSizer.Add(self.labels[microstandTAG+'|5'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[microstandTAG+'|5'], 0, wx.EXPAND)    	

	standSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	#-- Condenser --#
	staticbox = wx.StaticBox(self.pane, -1, "Condenser")
	condensSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	condensorTAG = self.tag_stump+'|Condenser|'+str(self.tab_number)
	condensor = meta.get_field(condensorTAG, [])

	self.settings_controls[condensorTAG+'|0']= wx.Choice(self.pane, -1, choices=['','White Light', 'Fluorescence'])
	if len(condensor) > 0:
	    self.settings_controls[condensorTAG+'|0'].SetStringSelection(condensor[0])
	self.settings_controls[condensorTAG+'|0'].Bind(wx.EVT_CHOICE, self.OnSavingData) 
	self.labels[condensorTAG+'|0'] = wx.StaticText(self.pane, -1, 'Type')
	self.labels[condensorTAG+'|0'].SetToolTipString('Type of condenser') 
	multctrlSizer.Add(self.labels[condensorTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[condensorTAG+'|0'], 0, wx.EXPAND)

	self.settings_controls[condensorTAG+'|1'] = wx.TextCtrl(self.pane, value='') 
	if len(condensor)> 1:
	    self.settings_controls[condensorTAG+'|1'].SetValue(condensor[1])
	self.settings_controls[condensorTAG+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[condensorTAG+'|1'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[condensorTAG+'|1'].SetToolTipString('Manufacturer of condensor source')
	multctrlSizer.Add(self.labels[condensorTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[condensorTAG+'|1'], 0, wx.EXPAND)
	
	self.settings_controls[condensorTAG+'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(condensor)> 2:
	    self.settings_controls[condensorTAG+'|2'].SetValue(condensor[2])
	self.settings_controls[condensorTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[condensorTAG+'|2'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[condensorTAG+'|2'].SetToolTipString('Model of condensor source')
	multctrlSizer.Add(self.labels[condensorTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[condensorTAG+'|2'], 0, wx.EXPAND)

	condensSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	

	#-- Stage --#
	staticbox = wx.StaticBox(self.pane, -1, "Stage")
	stageSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	stageTAG = self.tag_stump+'|Stage|'+str(self.tab_number)
	stage = meta.get_field(stageTAG, [])

	self.settings_controls[stageTAG+'|0']= wx.Choice(self.pane, -1, choices=['','Manual', 'Motorized'])
	if len(stage) > 0:
	    self.settings_controls[stageTAG+'|0'].SetStringSelection(stage[0])
	self.settings_controls[stageTAG+'|0'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[stageTAG+'|0'] = wx.StaticText(self.pane, -1, 'Type')
	self.labels[stageTAG+'|0'].SetToolTipString('Type of stage') 
	multctrlSizer.Add(self.labels[stageTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[stageTAG+'|0'], 0, wx.EXPAND)

	self.settings_controls[stageTAG+'|1'] = wx.TextCtrl(self.pane, value='') 
	if len(stage)> 1:
	    self.settings_controls[stageTAG+'|1'].SetValue(stage[1])
	self.settings_controls[stageTAG+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[stageTAG+'|1'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[stageTAG+'|1'].SetToolTipString('Manufacturer of stage source')
	multctrlSizer.Add(self.labels[stageTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[stageTAG+'|1'], 0, wx.EXPAND)
	
	self.settings_controls[stageTAG+'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(stage)> 2:
	    self.settings_controls[stageTAG+'|2'].SetValue(stage[2])
	self.settings_controls[stageTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[stageTAG+'|2'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[stageTAG+'|2'].SetToolTipString('Model of stage source')
	multctrlSizer.Add(self.labels[stageTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[stageTAG+'|2'], 0, wx.EXPAND)
	
	self.settings_controls[stageTAG+'|3']= wx.Choice(self.pane, -1, choices=['Yes', 'No'])
	if len(stage) > 3:
	    self.settings_controls[stageTAG+'|3'].SetStringSelection(stage[3])
	self.settings_controls[stageTAG+'|3'].Bind(wx.EVT_CHOICE, self.onEnabling) 
	self.labels[stageTAG+'|3'] = wx.StaticText(self.pane, -1, 'Sample Holder')
	self.labels[stageTAG+'|3'].SetToolTipString('Holder for the samples') 
	multctrlSizer.Add(self.labels[stageTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[stageTAG+'|3'], 0, wx.EXPAND)	
	
	self.settings_controls[stageTAG+'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(stage)> 4:
	    self.settings_controls[stageTAG+'|4'].SetValue(stage[4])
	self.settings_controls[stageTAG+'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[stageTAG+'|4'].Disable()
	self.labels[stageTAG+'|4'] = wx.StaticText(self.pane, -1, 'Holder Code')
	self.labels[stageTAG+'|4'].SetToolTipString('Sample holder code')
	multctrlSizer.Add(self.labels[stageTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[stageTAG+'|4'], 0, wx.EXPAND)	

	stageSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	#-- Incubator --#
	staticbox = wx.StaticBox(self.pane, -1, "Incubator")
	incubatorSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	incbatorTAG = self.tag_stump+'|Incubator|'+str(self.tab_number)
	incubator = meta.get_field(incbatorTAG, [])

	self.settings_controls[incbatorTAG+'|0'] = wx.TextCtrl(self.pane, value='') 
	if len(incubator)> 0:
	    self.settings_controls[incbatorTAG+'|0'].SetValue(incubator[0])
	self.settings_controls[incbatorTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[incbatorTAG+'|0'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[incbatorTAG+'|0'].SetToolTipString('Manufacturer of incubator source')
	multctrlSizer.Add(self.labels[incbatorTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[incbatorTAG+'|0'], 0, wx.EXPAND)
	
	self.settings_controls[incbatorTAG+'|1'] = wx.TextCtrl(self.pane, value='') 	
	if len(incubator)> 1:
	    self.settings_controls[incbatorTAG+'|1'].SetValue(incubator[1])
	self.settings_controls[incbatorTAG+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[incbatorTAG+'|1'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[incbatorTAG+'|1'].SetToolTipString('Model of incubator source')
	multctrlSizer.Add(self.labels[incbatorTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[incbatorTAG+'|1'], 0, wx.EXPAND)
	
	self.settings_controls[incbatorTAG+'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(incubator)> 2:
	    self.settings_controls[incbatorTAG+'|2'].SetValue(incubator[2])
	self.settings_controls[incbatorTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[incbatorTAG+'|2'] = wx.StaticText(self.pane, -1, 'Temperature(C)')
	self.labels[incbatorTAG+'|2'].SetToolTipString('Incubation temperature')
	multctrlSizer.Add(self.labels[incbatorTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[incbatorTAG+'|2'], 0, wx.EXPAND)
	
	self.settings_controls[incbatorTAG+'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(incubator)> 3:
	    self.settings_controls[incbatorTAG+'|3'].SetValue(incubator[3])
	self.settings_controls[incbatorTAG+'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[incbatorTAG+'|3'] = wx.StaticText(self.pane, -1, 'CO2%')
	self.labels[incbatorTAG+'|3'].SetToolTipString('Percentages of Carbondioxide')
	multctrlSizer.Add(self.labels[incbatorTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[incbatorTAG+'|3'], 0, wx.EXPAND)	

	self.settings_controls[incbatorTAG+'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(incubator)> 4:
	    self.settings_controls[incbatorTAG+'|4'].SetValue(incubator[4])
	self.settings_controls[incbatorTAG+'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[incbatorTAG+'|4'] = wx.StaticText(self.pane, -1, 'Humidity')
	self.labels[incbatorTAG+'|4'].SetToolTipString('Humidity within the incubator')
	multctrlSizer.Add(self.labels[incbatorTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[incbatorTAG+'|4'], 0, wx.EXPAND)	
	
	self.settings_controls[incbatorTAG+'|5'] = wx.TextCtrl(self.pane, value='') 	
	if len(incubator)> 5:
	    self.settings_controls[incbatorTAG+'|5'].SetValue(incubator[5])
	self.settings_controls[incbatorTAG+'|5'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[incbatorTAG+'|5'] = wx.StaticText(self.pane, -1, 'Pressure')
	self.labels[incbatorTAG+'|5'].SetToolTipString('Pressure within the incubator')
	multctrlSizer.Add(self.labels[incbatorTAG+'|5'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[incbatorTAG+'|5'], 0, wx.EXPAND)	
	
	incubatorSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	#--- Layout ---#	
	hardwareSizer = wx.BoxSizer(wx.VERTICAL)
	hardwareSizer.Add(standSizer, 0, wx.EXPAND|wx.ALL, 5)
	hardwareSizer.Add(condensSizer, 0, wx.EXPAND|wx.ALL, 5)
	hardwareSizer.Add(stageSizer, 0, wx.EXPAND|wx.ALL, 5)
	hardwareSizer.Add(incubatorSizer, 0, wx.EXPAND|wx.ALL, 5)

	self.pane.SetSizer(hardwareSizer, 0)

    def opticsPane(self, pane):
	''' This pane makes the Illumination pane of the microscope. Each component of the illum pane can have mulitple components
	which can again has multiple attributes'''
	
	meta = ExperimentSettings.getInstance()
	self.pane = pane
	
	self.exTsld = 300
	self.exBsld = 800	
	
	#-- Light Source --#
	staticbox = wx.StaticBox(self.pane, -1, "Light")
	lightSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	lightsrcTAG = self.tag_stump+'|LightSource|'+str(self.tab_number)
	lightsrc = meta.get_field(lightsrcTAG, [])
	
	self.settings_controls[lightsrcTAG+'|0']=  wx.Choice(self.pane, -1,  choices=['Transmitted','Epifluorescence','Oblique','Non Linear'])
	if len(lightsrc)> 0:
	    self.settings_controls[lightsrcTAG+'|0'].SetStringSelection(lightsrc[0])
	self.settings_controls[lightsrcTAG+'|0'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[lightsrcTAG+'|0'] = wx.StaticText(self.pane, -1, 'Type')
	self.labels[lightsrcTAG+'|0'].SetToolTipString('Type of the light source') 
	multctrlSizer.Add(self.labels[lightsrcTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|0'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|1']= wx.Choice(self.pane, -1, choices=['Laser', 'Filament', 'Arc', 'Light Emitting Diode'])
	if len(lightsrc) > 1:
	    self.settings_controls[lightsrcTAG+'|1'].SetStringSelection(lightsrc[1])
	self.settings_controls[lightsrcTAG+'|1'].Bind(wx.EVT_CHOICE, self.OnSavingData) 
	self.labels[lightsrcTAG+'|1'] = wx.StaticText(self.pane, -1, 'Source')
	self.labels[lightsrcTAG+'|1'].SetToolTipString('Type of the light source') 
	multctrlSizer.Add(self.labels[lightsrcTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|1'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|2'] = wx.TextCtrl(self.pane, value='') 
	if len(lightsrc)> 2:
	    self.settings_controls[lightsrcTAG+'|2'].SetValue(lightsrc[2])
	self.settings_controls[lightsrcTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lightsrcTAG+'|2'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[lightsrcTAG+'|2'].SetToolTipString('Manufacturer of light source')
	multctrlSizer.Add(self.labels[lightsrcTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|2'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(lightsrc)> 3:
	    self.settings_controls[lightsrcTAG+'|3'].SetValue(lightsrc[3])
	self.settings_controls[lightsrcTAG+'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lightsrcTAG+'|3'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[lightsrcTAG+'|3'].SetToolTipString('Model of light source')
	multctrlSizer.Add(self.labels[lightsrcTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|3'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(lightsrc)> 4:
	    self.settings_controls[lightsrcTAG+'|4'].SetValue(lightsrc[4])
	self.settings_controls[lightsrcTAG+'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lightsrcTAG+'|4'] = wx.StaticText(self.pane, -1, 'Measured Power (User)')
	self.labels[lightsrcTAG+'|4'].SetToolTipString('Power of light source')
	multctrlSizer.Add(self.labels[lightsrcTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|4'], 0, wx.EXPAND)	
	
	self.settings_controls[lightsrcTAG+'|5'] = wx.TextCtrl(self.pane, value='') 	
	if len(lightsrc)> 5:
	    self.settings_controls[lightsrcTAG+'|5'].SetValue(lightsrc[5])
	self.settings_controls[lightsrcTAG+'|5'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lightsrcTAG+'|5'] = wx.StaticText(self.pane, -1, 'Measured Power (Instrument)')
	self.labels[lightsrcTAG+'|5'].SetToolTipString('Measured power of light source')
	multctrlSizer.Add(self.labels[lightsrcTAG+'|5'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|5'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|6']= wx.Choice(self.pane, -1, choices=['Yes', 'No'])
	if len(lightsrc) > 6:
	    self.settings_controls[lightsrcTAG+'|6'].SetStringSelection(lightsrc[6])
	self.settings_controls[lightsrcTAG+'|6'].Bind(wx.EVT_CHOICE, self.onEnabling)
	self.labels[lightsrcTAG+'|6'] = wx.StaticText(self.pane, -1, 'Shutter Used')
	self.labels[lightsrcTAG+'|6'].SetToolTipString('Shutter used') 
	multctrlSizer.Add(self.labels[lightsrcTAG+'|6'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|6'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|7']= wx.Choice(self.pane, -1, choices=['Internal', 'External'])
	if len(lightsrc) > 7:
	    self.settings_controls[lightsrcTAG+'|7'].SetStringSelection(lightsrc[7])
	self.settings_controls[lightsrcTAG+'|7'].Bind(wx.EVT_CHOICE, self.onEnabling)
	self.settings_controls[lightsrcTAG+'|7'].Disable()
	self.labels[lightsrcTAG+'|7'] = wx.StaticText(self.pane, -1, 'Shutter Type')
	self.labels[lightsrcTAG+'|7'].SetToolTipString('Shutter used') 
	multctrlSizer.Add(self.labels[lightsrcTAG+'|7'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|7'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|8'] = wx.TextCtrl(self.pane, value='') 
	if len(lightsrc)> 8:
	    self.settings_controls[lightsrcTAG+'|8'].SetValue(lightsrc[8])
	self.settings_controls[lightsrcTAG+'|8'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[lightsrcTAG+'|8'].Disable()
	self.labels[lightsrcTAG+'|8'] = wx.StaticText(self.pane, -1, 'Ext Shutter Make')
	self.labels[lightsrcTAG+'|8'].SetToolTipString('Manufacturer of light source')
	multctrlSizer.Add(self.labels[lightsrcTAG+'|8'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|8'], 0, wx.EXPAND)
	
	self.settings_controls[lightsrcTAG+'|9'] = wx.TextCtrl(self.pane, value='') 	
	if len(lightsrc)> 9:
	    self.settings_controls[lightsrcTAG+'|9'].SetValue(lightsrc[9])
	self.settings_controls[lightsrcTAG+'|9'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[lightsrcTAG+'|9'].Disable()
	self.labels[lightsrcTAG+'|9'] = wx.StaticText(self.pane, -1, 'Ext Shutter Model') 
	self.labels[lightsrcTAG+'|9'].SetToolTipString('Model of light source')
	multctrlSizer.Add(self.labels[lightsrcTAG+'|9'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lightsrcTAG+'|9'], 0, wx.EXPAND)	
	
	lightSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)
	
	#-- Excitation Filter --#
	staticbox = wx.StaticBox(self.pane, -1, " Excitation Filter")
	extfilterSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	extfltTAG = self.tag_stump+'|ExtFilter|'+str(self.tab_number)
	extfilter = meta.get_field(extfltTAG, [])
	
	self.startNM, self.endNM = 300, 1000
	if len(extfilter)> 1:
	    self.startNM = int(extfilter[0])
	    self.endNM = int(extfilter[1])

	multctrlSizer.Add(wx.StaticText(self.pane, -1, 'Wavelength\n(nm)'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

	self.exTsld = self.settings_controls[extfltTAG +'|0'] = wx.Slider(self.pane, -1, self.startNM, 300, 1000, wx.DefaultPosition, (100, -1), wx.SL_LABELS)
	self.exBsld = self.settings_controls[extfltTAG +'|1'] = wx.Slider(self.pane, -1, self.endNM, 300, 1000, wx.DefaultPosition, (100, -1), style = wx.SL_LABELS|wx.SL_TOP)
	
	self.fltrspectrum = FilterSpectrum(self.pane)

	self.pane.Bind(wx.EVT_SLIDER, self.OnSavingData)
	
	spctrmSizer = wx.BoxSizer(wx.VERTICAL)
	spctrmSizer.Add(self.settings_controls[extfltTAG +'|0'],0)
	spctrmSizer.Add(self.fltrspectrum, 0)
	spctrmSizer.Add(self.settings_controls[extfltTAG +'|1'],0)   
	
	multctrlSizer.Add(spctrmSizer, 0)
	
	self.settings_controls[extfltTAG +'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(extfilter)> 2:
	    self.settings_controls[extfltTAG +'|2'].SetValue(extfilter[2])
	self.settings_controls[extfltTAG +'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[extfltTAG +'|2'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[extfltTAG +'|2'].SetToolTipString('Make of filter')
	multctrlSizer.Add(self.labels[extfltTAG +'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[extfltTAG +'|2'], 0, wx.EXPAND)	
	
	self.settings_controls[extfltTAG +'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(extfilter)> 3:
	    self.settings_controls[extfltTAG +'|3'].SetValue(extfilter[3])
	self.settings_controls[extfltTAG +'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[extfltTAG +'|3'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[extfltTAG +'|3'].SetToolTipString('Model of filter')
	multctrlSizer.Add(self.labels[extfltTAG +'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[extfltTAG +'|3'], 0, wx.EXPAND)
	
	extfilterSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	#-- Dichroic Mirror --#
	staticbox = wx.StaticBox(self.pane, -1, "Dichroic Mirror")
	mirrorSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	mirrorTAG = self.tag_stump+'|Mirror|'+str(self.tab_number)
	mirror = meta.get_field(mirrorTAG, [])
	self.startNM, self.endNM = 300, 1000
	if len(mirror)> 1:
	    self.startNM = int(mirror[0])
	    self.endNM = int(mirror[1])

	multctrlSizer.Add(wx.StaticText(self.pane, -1, 'Wavelength\n(nm)'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

	self.settings_controls[mirrorTAG +'|0'] = wx.Slider(self.pane, -1, self.startNM, 300, 1000, wx.DefaultPosition, (100, -1), wx.SL_LABELS)
	self.settings_controls[mirrorTAG +'|1'] = wx.Slider(self.pane, -1, self.endNM, 300, 1000, wx.DefaultPosition, (100, -1), style = wx.SL_LABELS|wx.SL_TOP)
	
	self.pane.fltTsld = self.settings_controls[mirrorTAG +'|0']
	self.pane.fltBsld = self.settings_controls[mirrorTAG +'|1']
	
	self.fltrspectrum = FilterSpectrum(self.pane)

	self.pane.Bind(wx.EVT_SLIDER, self.OnSavingData)
	
	spctrmSizer = wx.BoxSizer(wx.VERTICAL)
	spctrmSizer.Add(self.pane.fltTsld,0)
	spctrmSizer.Add(self.fltrspectrum, 0)
	spctrmSizer.Add(self.pane.fltBsld,0)   
	
	multctrlSizer.Add(spctrmSizer, 0)
	
	self.settings_controls[mirrorTAG+'|2']= wx.Choice(self.pane, -1, choices=['Transmitted', 'Reflected'])
	if len(lightsrc) > 2:
	    self.settings_controls[mirrorTAG+'|2'].SetStringSelection(lightsrc[2])
	self.settings_controls[mirrorTAG+'|2'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[mirrorTAG+'|2'] = wx.StaticText(self.pane, -1, 'Mode')
	self.labels[mirrorTAG+'|2'].SetToolTipString('Mirror mode') 
	multctrlSizer.Add(self.labels[mirrorTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG+'|2'], 0, wx.EXPAND)	
	
	self.settings_controls[mirrorTAG +'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(mirror)> 3:
	    self.settings_controls[mirrorTAG +'|3'].SetValue(mirror[3])
	self.settings_controls[mirrorTAG +'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mirrorTAG+'|3'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[mirrorTAG+'|3'].SetToolTipString('Make of mirror')
	multctrlSizer.Add(self.labels[mirrorTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG +'|3'], 0, wx.EXPAND)	
	
	self.settings_controls[mirrorTAG +'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(mirror)> 4:
	    self.settings_controls[mirrorTAG +'|4'].SetValue(mirror[4])
	self.settings_controls[mirrorTAG +'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mirrorTAG+'|4'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[mirrorTAG+'|4'].SetToolTipString('Model of mirror')
	multctrlSizer.Add(self.labels[mirrorTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG +'|4'], 0, wx.EXPAND)
	
	self.settings_controls[mirrorTAG+'|5']= wx.Choice(self.pane, -1, choices=['Yes', 'No'])
	if len(lightsrc) > 5:
	    self.settings_controls[mirrorTAG+'|5'].SetStringSelection(lightsrc[5])
	self.settings_controls[mirrorTAG+'|5'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[mirrorTAG+'|5'] = wx.StaticText(self.pane, -1, 'Modification')
	self.labels[mirrorTAG+'|5'].SetToolTipString('Modification done') 
	multctrlSizer.Add(self.labels[mirrorTAG+'|5'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG+'|5'], 0, wx.EXPAND)		
	
	mirrorSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	#-- Split Mirror --#
	staticbox = wx.StaticBox(self.pane, -1, "Split Mirror")
	splitterSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	mirrorTAG = self.tag_stump+'|SplitMirror|'+str(self.tab_number)
	mirror = meta.get_field(mirrorTAG, [])
	startNM = 300
	if len(mirror)> 0:
	    startNM = int(mirror[0])

	multctrlSizer.Add(wx.StaticText(self.pane, -1, 'Wavelength\n(nm)'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	self.settings_controls[mirrorTAG +'|0'] = wx.Slider(self.pane, -1, startNM, 300, 1000, wx.DefaultPosition, (100, -1), wx.SL_LABELS)	
	self.pane.fltTsld = self.settings_controls[mirrorTAG +'|0']
	self.fltrspectrum = FilterSpectrum(self.pane)

	self.pane.Bind(wx.EVT_SLIDER, self.OnSavingData)
	
	spctrmSizer = wx.BoxSizer(wx.VERTICAL)
	spctrmSizer.Add(self.pane.fltTsld,0)
	spctrmSizer.Add(self.fltrspectrum, 0)  
	
	multctrlSizer.Add(spctrmSizer, 0)
	
	self.settings_controls[mirrorTAG +'|1'] = wx.TextCtrl(self.pane, value='') 	
	if len(mirror)> 1:
	    self.settings_controls[mirrorTAG +'|1'].SetValue(mirror[1])
	self.settings_controls[mirrorTAG +'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mirrorTAG+'|1'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[mirrorTAG+'|1'].SetToolTipString('Make of mirror')
	multctrlSizer.Add(self.labels[mirrorTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG +'|1'], 0, wx.EXPAND)	
	
	self.settings_controls[mirrorTAG +'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(mirror)> 2:
	    self.settings_controls[mirrorTAG +'|2'].SetValue(mirror[2])
	self.settings_controls[mirrorTAG +'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mirrorTAG+'|2'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[mirrorTAG+'|2'].SetToolTipString('Model of mirror')
	multctrlSizer.Add(self.labels[mirrorTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG +'|2'], 0, wx.EXPAND)
	
	self.settings_controls[mirrorTAG +'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(mirror)> 3:
	    self.settings_controls[mirrorTAG +'|3'].SetValue(mirror[3])
	self.settings_controls[mirrorTAG +'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mirrorTAG+'|3'] = wx.StaticText(self.pane, -1, 'Left Component')
	self.labels[mirrorTAG+'|3'].SetToolTipString('e.g. Pump')
	multctrlSizer.Add(self.labels[mirrorTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG +'|3'], 0, wx.EXPAND)	

	self.settings_controls[mirrorTAG +'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(mirror)> 4:
	    self.settings_controls[mirrorTAG +'|4'].SetValue(mirror[4])
	self.settings_controls[mirrorTAG +'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mirrorTAG+'|4'] = wx.StaticText(self.pane, -1, 'Right Component')
	self.labels[mirrorTAG+'|4'].SetToolTipString('e.g. Stoking')
	multctrlSizer.Add(self.labels[mirrorTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[mirrorTAG +'|4'], 0, wx.EXPAND)
	
	splitterSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)
	
	
	#-- Emission Filter --#
	staticbox = wx.StaticBox(self.pane, -1, " Emission Filter")
	emsfilterSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	emsfltTAG = self.tag_stump+'|EmsFilter|'+str(self.tab_number)
	emsfilter = meta.get_field(emsfltTAG, [])
	self.startNM, self.endNM = 300, 1000
	if len(emsfilter)> 1:
	    self.startNM = int(emsfilter[0])
	    self.endNM = int(emsfilter[1])

	multctrlSizer.Add(wx.StaticText(self.pane, -1, 'Wavelength\n(nm)'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

	self.settings_controls[emsfltTAG +'|0'] = wx.Slider(self.pane, -1, self.startNM, 300, 1000, wx.DefaultPosition, (100, -1), wx.SL_LABELS)
	self.settings_controls[emsfltTAG +'|1'] = wx.Slider(self.pane, -1, self.endNM, 300, 1000, wx.DefaultPosition, (100, -1), style = wx.SL_LABELS|wx.SL_TOP)
	
	self.pane.fltTsld = self.settings_controls[emsfltTAG +'|0']
	self.pane.fltBsld = self.settings_controls[emsfltTAG +'|1']
	
	self.fltrspectrum = FilterSpectrum(self.pane)

	self.pane.Bind(wx.EVT_SLIDER, self.OnSavingData)
	
	spctrmSizer = wx.BoxSizer(wx.VERTICAL)
	spctrmSizer.Add(self.pane.fltTsld,0)
	spctrmSizer.Add(self.fltrspectrum, 0)
	spctrmSizer.Add(self.pane.fltBsld,0)   
	
	multctrlSizer.Add(spctrmSizer, 0)
	
	self.settings_controls[emsfltTAG +'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(emsfilter)> 2:
	    self.settings_controls[emsfltTAG +'|2'].SetValue(emsfilter[2])
	self.settings_controls[emsfltTAG +'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[emsfltTAG +'|2'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[emsfltTAG +'|2'].SetToolTipString('Make of filter')
	multctrlSizer.Add(self.labels[emsfltTAG +'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[emsfltTAG +'|2'], 0, wx.EXPAND)	
	
	self.settings_controls[emsfltTAG +'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(emsfilter)> 3:
	    self.settings_controls[emsfltTAG +'|3'].SetValue(emsfilter[3])
	self.settings_controls[emsfltTAG +'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[emsfltTAG +'|3'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[emsfltTAG +'|3'].SetToolTipString('Model of filter')
	multctrlSizer.Add(self.labels[emsfltTAG +'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[emsfltTAG +'|3'], 0, wx.EXPAND)
	
	emsfilterSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)
	
	
	#-- Lens --#
	staticbox = wx.StaticBox(self.pane, -1, "Lens")
	lensSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)

	lensTAG = self.tag_stump+'|Lens|'+str(self.tab_number)
	lens = meta.get_field(lensTAG, [])
	
	self.settings_controls[lensTAG+'|0'] = wx.TextCtrl(self.pane, value='') 
	if len(lens)> 0:
	    self.settings_controls[lensTAG+'|0'].SetValue(lens[0])
	self.settings_controls[lensTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lensTAG+'|0'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[lensTAG+'|0'].SetToolTipString('Manufacturer of lens')
	multctrlSizer.Add(self.labels[lensTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|0'], 0, wx.EXPAND)
	
	self.settings_controls[lensTAG+'|1'] = wx.TextCtrl(self.pane, value='') 	
	if len(lens)> 1:
	    self.settings_controls[lensTAG+'|1'].SetValue(lens[1])
	self.settings_controls[lensTAG+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lensTAG+'|1'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[lensTAG+'|1'].SetToolTipString('Model of lens')
	multctrlSizer.Add(self.labels[lensTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|1'], 0, wx.EXPAND)
	
	self.settings_controls[lensTAG+'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(lens)> 2:
	    self.settings_controls[lensTAG+'|2'].SetValue(lens[2])
	self.settings_controls[lensTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lensTAG+'|2'] = wx.StaticText(self.pane, -1, 'Objective Magnification')
	self.labels[lensTAG+'|2'].SetToolTipString('Objective Magnification')
	multctrlSizer.Add(self.labels[lensTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|2'], 0, wx.EXPAND)
	
	self.settings_controls[lensTAG+'|3'] = wx.TextCtrl(self.pane, value='') 	
	if len(lens)> 3:
	    self.settings_controls[lensTAG+'|3'].SetValue(lens[3])
	self.settings_controls[lensTAG+'|3'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lensTAG+'|3'] = wx.StaticText(self.pane, -1, 'Objective NA')
	self.labels[lensTAG+'|3'].SetToolTipString('nominal aperture')
	multctrlSizer.Add(self.labels[lensTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|3'], 0, wx.EXPAND)	
	
	self.settings_controls[lensTAG+'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(lens)> 4:
	    self.settings_controls[lensTAG+'|4'].SetValue(lens[4])
	self.settings_controls[lensTAG+'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[lensTAG+'|4'] = wx.StaticText(self.pane, -1, 'Calibrated Magnification')
	self.labels[lensTAG+'|4'].SetToolTipString('Calibrated Magnification')
	multctrlSizer.Add(self.labels[lensTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|4'], 0, wx.EXPAND)	
	
	immersion_choices=['Oil', 'Water', 'Water Dipping', 'Air', 'Multi', 'Glycerol', 'Unknown','Other']
	self.settings_controls[lensTAG+'|5']= wx.ListBox(self.pane, -1, wx.DefaultPosition, (50,30), immersion_choices, wx.LB_SINGLE)
	if len(lens) > 5:
	    self.settings_controls[lensTAG+'|5'].Append(lens[5])
	    self.settings_controls[lensTAG+'|5'].SetStringSelection(lens[5])
	self.settings_controls[lensTAG+'|5'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	self.labels[lensTAG+'|5'] = wx.StaticText(self.pane, -1, 'Immersion')
	self.labels[lensTAG+'|5'].SetToolTipString('Immersion') 
	multctrlSizer.Add(self.labels[lensTAG+'|5'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|5'], 0, wx.EXPAND)
	
	self.settings_controls[lensTAG+'|6']= wx.Choice(self.pane, -1, choices=['Yes', 'No'])
	if len(lens) > 6:
	    self.settings_controls[lensTAG+'|6'].SetStringSelection(lens[6])
	self.settings_controls[lensTAG+'|6'].Bind(wx.EVT_CHOICE, self.onEnabling)
	self.labels[lensTAG+'|6'] = wx.StaticText(self.pane, -1, 'Correction Collar')
	self.labels[lensTAG+'|6'].SetToolTipString('Correction Collar') 
	multctrlSizer.Add(self.labels[lensTAG+'|6'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|6'], 0, wx.EXPAND)
	
	self.settings_controls[lensTAG+'|7']= wx.TextCtrl(self.pane, value='')
	if len(lens) > 7:
	    self.settings_controls[lensTAG+'|7'].SetValue(lens[7])
	self.settings_controls[lensTAG+'|7'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[lensTAG+'|7'].Disable()
	self.labels[lensTAG+'|7'] = wx.StaticText(self.pane, -1, 'Correction Value')
	self.labels[lensTAG+'|7'].SetToolTipString('Correction value') 
	multctrlSizer.Add(self.labels[lensTAG+'|7'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|7'], 0, wx.EXPAND) 	
	
	self.settings_controls[lensTAG+'|8']= wx.Choice(self.pane, -1, choices=['UV', 'PlanApo', 'PlanFluor', 'SuperFluor', 'VioletCorrected', 'Unknown'])
	if len(lens) > 8:
	    self.settings_controls[lensTAG+'|8'].SetStringSelection(lens[8])
	self.settings_controls[lensTAG+'|8'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.settings_controls[lensTAG+'|8'].Disable()
	self.labels[lensTAG+'|8'] = wx.StaticText(self.pane, -1, 'Correction Type')
	self.labels[lensTAG+'|8'].SetToolTipString('Correction type') 
	multctrlSizer.Add(self.labels[lensTAG+'|8'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[lensTAG+'|8'], 0, wx.EXPAND)	
		
	lensSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	
	#-- Detector --#
	staticbox = wx.StaticBox(self.pane, -1, "Detector")
	detectorSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	multctrlSizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	detectorTAG = self.tag_stump+'|Detector|'+str(self.tab_number)
	detector = meta.get_field(detectorTAG, [])
	
	detector_choices =['CCD', 'Intensified-CCD', 'Analog-Video', 'Spectroscopy', 'Life-time-imaging', 'Correlation-Spectroscopy', 'FTIR', 'EM-CCD', 'APD', 'CMOS', 'Unknown', 'Other']
	self.settings_controls[detectorTAG+'|0']= wx.ListBox(self.pane, -1, wx.DefaultPosition, (120,30), detector_choices, wx.LB_SINGLE)
	if len(detector) > 0:
	    self.settings_controls[detectorTAG+'|0'].Append(detector[0])
	    self.settings_controls[detectorTAG+'|0'].SetStringSelection(detector[0])
	self.settings_controls[detectorTAG+'|0'].Bind(wx.EVT_LISTBOX, self.OnSavingData) 
	self.labels[detectorTAG+'|0'] = wx.StaticText(self.pane, -1, 'Type')
	self.labels[detectorTAG+'|0'].SetToolTipString('Type of detector') 
	multctrlSizer.Add(self.labels[detectorTAG+'|0'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|0'], 0, wx.EXPAND)
	multctrlSizer.Add(wx.StaticText(self.pane, -1, ''), 0)
	
	self.settings_controls[detectorTAG+'|1'] = wx.TextCtrl(self.pane, value='') 
	if len(detector)> 1:
	    self.settings_controls[detectorTAG+'|1'].SetValue(detector[1])
	self.settings_controls[detectorTAG+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[detectorTAG+'|1'] = wx.StaticText(self.pane, -1, 'Make')
	self.labels[detectorTAG+'|1'].SetToolTipString('Manufacturer of detector')
	multctrlSizer.Add(self.labels[detectorTAG+'|1'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|1'], 0, wx.EXPAND)
	multctrlSizer.Add(wx.StaticText(self.pane, -1, ''), 0)
	
	self.settings_controls[detectorTAG+'|2'] = wx.TextCtrl(self.pane, value='') 	
	if len(detector)> 2:
	    self.settings_controls[detectorTAG+'|2'].SetValue(detector[2])
	self.settings_controls[detectorTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[detectorTAG+'|2'] = wx.StaticText(self.pane, -1, 'Model')
	self.labels[detectorTAG+'|2'].SetToolTipString('Model of light source')
	multctrlSizer.Add(self.labels[detectorTAG+'|2'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|2'], 0, wx.EXPAND)
	multctrlSizer.Add(wx.StaticText(self.pane, -1, ''), 0)
	
	self.settings_controls[detectorTAG+'|3']= wx.Choice(self.pane, -1, choices=['1','2','4','8','16'])
	if len(detector) > 3:
	    self.settings_controls[detectorTAG+'|3'].SetStringSelection(detector[3])
	self.settings_controls[detectorTAG+'|3'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[detectorTAG+'|3'] = wx.StaticText(self.pane, -1, 'Binning')
	self.labels[detectorTAG+'|3'].SetToolTipString('Binning') 
	multctrlSizer.Add(self.labels[detectorTAG+'|3'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|3'], 0, wx.EXPAND)
	multctrlSizer.Add(wx.StaticText(self.pane, -1, ''), 0)
		
	self.settings_controls[detectorTAG+'|4'] = wx.TextCtrl(self.pane, value='') 	
	if len(detector)> 4:
	    self.settings_controls[detectorTAG+'|4'].SetValue(detector[4])
	self.settings_controls[detectorTAG+'|4'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[detectorTAG+'|5']= wx.Choice(self.pane, -1, choices=['microsecond','millisecond','second','minute'])
	if len(detector) > 5:
	    self.settings_controls[detectorTAG+'|5'].SetStringSelection(detector[5])
	self.settings_controls[detectorTAG+'|5'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[detectorTAG+'|4'] = wx.StaticText(self.pane, -1, 'Exposure Time')
	self.labels[detectorTAG+'|4'].SetToolTipString('Exposure Time (Value & Unit)')
	multctrlSizer.Add(self.labels[detectorTAG+'|4'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|4'], 0, wx.EXPAND)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|5'], 0, wx.EXPAND)
	
	self.settings_controls[detectorTAG+'|6'] = wx.TextCtrl(self.pane, value='') 	
	if len(detector)> 6:
	    self.settings_controls[detectorTAG+'|6'].SetValue(detector[6])
	self.settings_controls[detectorTAG+'|6'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[detectorTAG+'|7']= wx.Choice(self.pane, -1, choices=['microvolt','millivolt','volt'])
	if len(detector) > 7:
	    self.settings_controls[detectorTAG+'|7'].SetStringSelection(detector[7])
	self.settings_controls[detectorTAG+'|7'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[detectorTAG+'|5'] = wx.StaticText(self.pane, -1, 'Gain')
	self.labels[detectorTAG+'|5'].SetToolTipString('Gain in volts') 	
	multctrlSizer.Add(self.labels[detectorTAG+'|5'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|6'], 0, wx.EXPAND)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|7'], 0, wx.EXPAND)
	
	
	self.settings_controls[detectorTAG+'|8'] = wx.TextCtrl(self.pane, value='') 	
	if len(detector)> 8:
	    self.settings_controls[detectorTAG+'|8'].SetValue(detector[8])
	self.settings_controls[detectorTAG+'|8'].Bind(wx.EVT_TEXT, self.OnSavingData)	
	self.settings_controls[detectorTAG+'|9']= wx.Choice(self.pane, -1, choices=['microvolt','millivolt','volt'])
	if len(detector) > 9:
	    self.settings_controls[detectorTAG+'|9'].SetStringSelection(detector[9])
	self.settings_controls[detectorTAG+'|9'].Bind(wx.EVT_CHOICE, self.OnSavingData)
	self.labels[detectorTAG+'|6'] = wx.StaticText(self.pane, -1, 'Offset')
	self.labels[detectorTAG+'|6'].SetToolTipString('Offset in volts')
	multctrlSizer.Add(self.labels[detectorTAG+'|6'], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|8'], 0, wx.EXPAND)
	multctrlSizer.Add(self.settings_controls[detectorTAG+'|9'], 0, wx.EXPAND)	
	
	detectorSizer.Add(multctrlSizer, 1, wx.EXPAND|wx.ALL, 5)	
	
	# --- Layout and Sizers ---#
	opticSizer = wx.BoxSizer(wx.VERTICAL)
	opticSizer.Add(lightSizer, 0, wx.EXPAND|wx.ALL, 5)
	opticSizer.Add(extfilterSizer, 0, wx.EXPAND|wx.ALL, 5)
	opticSizer.Add(mirrorSizer, 0, wx.EXPAND|wx.ALL, 5)
	opticSizer.Add(splitterSizer, 0, wx.EXPAND|wx.ALL, 5)
	opticSizer.Add(emsfilterSizer, 0, wx.EXPAND|wx.ALL, 5)
	opticSizer.Add(lensSizer, 0, wx.EXPAND|wx.ALL, 5)
	opticSizer.Add(detectorSizer, 0, wx.EXPAND|wx.ALL, 5)
	
	self.pane.SetSizer(opticSizer, 0)
	

    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags) 
		
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
		    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)
	# update the progress bar (only for Microscope)    
	self.updateProgressBar()

	
    def onEnabling(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]	

	if self.settings_controls[self.tag_stump+'|LightSource|%s|%s'%(str(self.tab_number), '6')].GetStringSelection() == 'Yes':
	    self.settings_controls[self.tag_stump+'|LightSource|%s|%s'%(str(self.tab_number), '7')].Enable()
	if self.settings_controls[self.tag_stump+'|LightSource|%s|%s'%(str(self.tab_number), '7')].GetStringSelection() == 'External':
	    self.settings_controls[self.tag_stump+'|LightSource|%s|%s'%(str(self.tab_number), '8')].Enable()
	    self.settings_controls[self.tag_stump+'|LightSource|%s|%s'%(str(self.tab_number), '9')].Enable()
	if self.settings_controls[self.tag_stump+'|Lens|%s|%s'%(str(self.tab_number), '6')].GetStringSelection() == 'Yes':
	    self.settings_controls[self.tag_stump+'|Lens|%s|%s'%(str(self.tab_number), '7')].Enable()
	    self.settings_controls[self.tag_stump+'|Lens|%s|%s'%(str(self.tab_number), '8')].Enable()
	if self.settings_controls[self.tag_stump+'|Stage|%s|%s'%(str(self.tab_number), '3')].GetStringSelection() == 'Yes':
	    self.settings_controls[self.tag_stump+'|Stage|%s|%s'%(str(self.tab_number), '4')].Enable()	
	    
	meta.saveData(ctrl, tag, self.settings_controls)   
		
	self.updateProgressBar()	
    
    def updateProgressBar(self):
	filledCount = 0
	
	for tag, ctrl in self.settings_controls.items():
	    if isinstance(ctrl, wx.Choice) or isinstance(ctrl, wx.ListBox):
		if ctrl.GetStringSelection():
		    filledCount += 1	    
	    elif isinstance(ctrl, wx.Slider):
		if tag.endswith('0') and ctrl.GetValue() > 300:
		    filledCount += 1
		if tag.endswith('1') and ctrl.GetValue() < 700:
		    filledCount += 1
	    else:
		if ctrl.GetValue():
		    filledCount += 1
		    
	progress = 100*(filledCount/float(len(self.settings_controls)))
	self.gauge.SetValue(int(progress))
	self.progpercent.SetLabel(str(int(progress))+' %')


class FilterSpectrum(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,  size=(100, 30), style=wx.SUNKEN_BORDER)

        self.parent = parent
	self.meta = ExperimentSettings.getInstance()
	self.startNM = 300
	self.endNM = 800

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnPaint(self, event):

        dc = wx.PaintDC(self)
	
	# get the component WL of the just previous one
	nmRange =  self.meta.partition(range(self.startNM, self.endNM+1), 5)
	
        #fltTsldVal = self.parent.exTsld.GetValue()
	#fltTsldMinVal = self.parent.exTsld.GetMin()
        #fltBsldVal = self.parent.exBsld.GetValue()
	#fltBsldMaxVal = self.parent.exBsld.GetMax()
	
	#fltTsldMove = (fltTsldVal-fltTsldMinVal)*100/(fltBsldMaxVal-fltTsldMinVal)  # 100 pxl is the physical size of the spectra panel
	#fltBsldMove = (fltBsldVal-fltTsldMinVal)*100/(fltBsldMaxVal-fltTsldMinVal)
	        
        # Draw the specturm according to the spectral range
        dc.GradientFillLinear((0, 0, 20, 30), self.meta.nmToRGB(nmRange[0]), self.meta.nmToRGB(nmRange[1]), wx.EAST)
        dc.GradientFillLinear((20, 0, 20, 30), self.meta.nmToRGB(nmRange[1]), self.meta.nmToRGB(nmRange[2]), wx.EAST)
        dc.GradientFillLinear((40, 0, 20, 30), self.meta.nmToRGB(nmRange[2]), self.meta.nmToRGB(nmRange[3]), wx.EAST)
        dc.GradientFillLinear((60, 0, 20, 30), self.meta.nmToRGB(nmRange[3]), self.meta.nmToRGB(nmRange[4]), wx.EAST)
        dc.GradientFillLinear((80, 0, 20, 30), self.meta.nmToRGB(nmRange[4]), self.meta.nmToRGB(nmRange[5]), wx.EAST)
        
        # Draw the slider on the spectrum to depict the selected range within the specta
	#dc = wx.PaintDC(self)
	#dc.SetPen(wx.Pen(self.GetBackgroundColour()))
	#dc.SetBrush(wx.Brush(self.GetBackgroundColour()))
	#dc.DrawRectangle(0, 0, fltTsldMove, 30)
	#dc.DrawRectangle(fltBsldMove, 0, 100, 30) 

       
    def OnSize(self, event):
        self.Refresh()	

########################################################################        
################## FLOW CYTOMETER SETTING PANEL         ####################
########################################################################
class FlowcytometerSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Instrument|Flowcytometer'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = FlowcytometerPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = FlowcytometerPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = FlowcytometerPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)     
 
 
class FlowcytometerPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	 
	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	
	# TAG
	self.tab_number = tab_number	# tab or instance number
	self.tag_stump = tag_stump                  # first two parts of tag (type|event) e.g Instrument|Centrifuge
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Manufacturer|'+str(self.tab_number)]        # mandatory fields 
 
	self.top_panel = wx.ScrolledWindow(self)
	self.bot_panel = wx.ScrolledWindow(self)	
  
	self.top_fgs = wx.BoxSizer(wx.VERTICAL)
	self.bot_fgs = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)

	# Title
	text = wx.StaticText(self.top_panel, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.top_panel, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.top_panel, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)    	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.top_panel, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.top_panel, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	self.labels[self.nameTAG] = wx.StaticText(self.top_panel, -1, 'Settings Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for the settings')
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL) 
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0, wx.EXPAND)
	
	mfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
	choices=['Beckman','BD-Biosciences', 'Other']
	self.settings_controls[mfgTAG] = wx.ListBox(self.top_panel, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if meta.get_field(mfgTAG) is not None:
	    self.settings_controls[mfgTAG].Append(meta.get_field(mfgTAG))
	    self.settings_controls[mfgTAG].SetStringSelection(meta.get_field(mfgTAG))	    
	self.settings_controls[mfgTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	self.labels[mfgTAG] = wx.StaticText(self.top_panel, -1, 'Manufacturer')
	self.labels[mfgTAG].SetToolTipString('Manufacturer name')
	attributesizer.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[mfgTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.top_panel, -1, ''), 0)
	
	modelTAG = self.tag_stump+'|Model|'+str(self.tab_number)
	self.settings_controls[modelTAG] = wx.TextCtrl(self.top_panel, value=meta.get_field(modelTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[modelTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[modelTAG] = wx.StaticText(self.top_panel , -1,  'Model')
	self.labels[modelTAG].SetToolTipString('Model number')
	attributesizer.Add(self.labels[modelTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[modelTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.top_panel, -1, ''), 0)	
	
	staticbox = wx.StaticBox(self.top_panel, -1, "Instrument Information")			
	attribute_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	attribute_Sizer.Add(attributesizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )		

	# ==== Local  ====
	localsizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	nickTAG = self.tag_stump+'|NickName|'+str(self.tab_number)
	self.settings_controls[nickTAG] = wx.TextCtrl(self.top_panel, name='Nick Name' ,  value=meta.get_field(nickTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[nickTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[nickTAG] = wx.StaticText(self.top_panel, -1, 'Nick Name')
	self.labels[nickTAG].SetToolTipString('Nick Name of the instrument')
	localsizer.Add(self.labels[nickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[nickTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.top_panel, -1, ''), 0)

	srlTAG = self.tag_stump+'|SerialNo|'+str(self.tab_number)
	self.settings_controls[srlTAG] = wx.TextCtrl(self.top_panel, name='Serial Number' ,  value=meta.get_field(srlTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[srlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[srlTAG] = wx.StaticText(self.top_panel, -1, 'Serial Number')
	self.labels[srlTAG].SetToolTipString('Serial Number')
	localsizer.Add(self.labels[srlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[srlTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.top_panel, -1, ''), 0)

	adrsTAG = self.tag_stump+'|Address|'+str(self.tab_number)
	self.settings_controls[adrsTAG] = wx.TextCtrl(self.top_panel, name='Address' ,  value=meta.get_field(adrsTAG, default=''), size=(-1, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.settings_controls[adrsTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[adrsTAG] = wx.StaticText(self.top_panel, -1, 'Address')
	self.labels[adrsTAG].SetToolTipString('Address where of the instrument location')
	localsizer.Add(self.labels[adrsTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[adrsTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.top_panel, -1, ''), 0)	
	
	roomTAG = self.tag_stump+'|Room|'+str(self.tab_number)
	self.settings_controls[roomTAG] = wx.TextCtrl(self.top_panel, name='Room' ,  value=meta.get_field(roomTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[roomTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[roomTAG] = wx.StaticText(self.top_panel, -1, 'Room Number')
	self.labels[roomTAG].SetToolTipString('Room where of the instrument location')
	localsizer.Add(self.labels[roomTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[roomTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.top_panel, -1, ''), 0)
	
	staticbox = wx.StaticBox(self.top_panel, -1, "Local Information")			
	local_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	local_Sizer.Add(localsizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	# Add Channel	
	self.addCh = wx.Button(self.top_panel, 1, 'Add Channel +')
	self.addCh.Bind(wx.EVT_BUTTON, self.onAddChnnel) 	

	# Show previously encoded channels in case of loading ch settings	
	self.showChannels()
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
        
	#---------------Layout with sizers---------------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(self.addCh, 0, wx.ALL, 5)
	swsizer.Add(attribute_Sizer, 0 , wx.EXPAND|wx.ALL, 5)
	swsizer.Add(local_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.top_panel.SetSizer(swsizer)
	self.bot_panel.SetSizer(self.bot_fgs)
	self.top_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	self.bot_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.top_panel, 1, wx.EXPAND|wx.ALL, 5)
	self.Sizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
	self.Sizer.Add(self.bot_panel, 1, wx.EXPAND|wx.ALL, 10)	          

    def onAddChnnel(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags): 
	    self.dlg = ChannelBuilder(self.bot_panel, -1, 'Channel Builder')
	    
	    if self.dlg.ShowModal() == wx.ID_OK:
		if self.dlg.componentCount != len(self.dlg.componentList):
		    dial = wx.MessageDialog(None, 'Last component was not configured\nPlease again add %s ch.'%self.dlg.select_chName.GetStringSelection(), 'Error', wx.OK | wx.ICON_ERROR)
		    dial.ShowModal() 
		    return	
		# All are OK
		lightpath = []
		for comp in self.dlg.componentList:
		    lightpath.append(self.dlg.componentList[comp])
		chName = self.dlg.select_chName.GetStringSelection()
		tag = self.tag_stump+'|%s|%s' %(chName, str(self.tab_number))
		value = lightpath
		self.drawChannel(chName, value)
		meta.set_field(tag, value)
    
    def showChannels(self):
	meta = ExperimentSettings.getInstance()	
			    
	#-- Show previously encoded channels --#
	chs = [tag.split('|')[2] for tag in meta.get_field_tags(self.tag_stump+'', str(self.tab_number))
                           if not tag.startswith(self.tag_stump+'|Manufacturer') 
	                   if not tag.startswith(self.tag_stump+'|Model')
	                   if not tag.startswith(self.tag_stump+'|Name')
	                   if not tag.startswith(self.tag_stump+'|AttachFiles')
	                   if not tag.startswith(self.tag_stump+'|NickName')
	                   if not tag.startswith(self.tag_stump+'|SerialNo')
	                   if not tag.startswith(self.tag_stump+'|Address')
	                   if not tag.startswith(self.tag_stump+'|Room')
	                   
	                   ]
	if chs:
	    for ch in sorted(chs):
		self.drawChannel(ch, meta.get_field((self.tag_stump+'|%s|%s') %(ch, str(self.tab_number))))
	    
    
    def drawChannel(self, chName, lightpath):
	#ch_sizer = wx.BoxSizer(wx.HORIZONTAL)
	ch_sizer = wx.FlexGridSizer(rows=1, hgap=5, vgap=5)  
	# Add the channel name
	ch_sizer.Add(wx.StaticText(self.bot_panel, -1, chName), 0, wx.ALIGN_CENTER_VERTICAL)
	# Add the components
	for component in lightpath:
	    compName = component[0]
	    nmRange = component[1]
	    
	    if compName.startswith('LSR'):
		staticbox = wx.StaticBox(self.bot_panel, -1, "Excitation Laser")
		laserNM = int(compName.split('LSR')[1])
		self.laser = wx.TextCtrl(self.bot_panel, -1, str(laserNM), style=wx.TE_READONLY)
		self.laser.SetBackgroundColour(meta.nmToRGB(laserNM))
		laserSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
		laserSizer.Add(self.laser, 0) 	    
		ch_sizer.Add(laserSizer,  0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
	    
	    if compName.startswith('DMR') or compName.startswith('FLT') or compName.startswith('SLT'):
		staticbox = wx.StaticBox(self.bot_panel, -1, compName)
		self.startNM, self.endNM = meta.getNM(nmRange)
		self.spectralRange =  meta.partition(range(self.startNM, self.endNM+1), 5)
		self.spectrum = DrawSpectrum(self.bot_panel, self.startNM, self.endNM)
		mirrorSizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
		mirrorSizer.Add(self.spectrum, 0)
		ch_sizer.Add(mirrorSizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
		
	    if compName.startswith('DYE'):
		staticbox = wx.StaticBox(self.bot_panel, -1, 'DYE')
		dye = compName.split('_')[1]
		emLow, emHgh = meta.getNM(nmRange)
		dyeList = meta.setDyeList(emLow, emHgh)
		if dye not in dyeList:
		    dyeList.append(dye) 
		dyeList.append('Add Dye by double click')
		self.dyeListBox = wx.ListBox(self.bot_panel, -1, wx.DefaultPosition, (150, 50), dyeList, wx.LB_SINGLE)
		self.dyeListBox.SetStringSelection(dye)
		self.dyeListBox.Bind(wx.EVT_LISTBOX, partial(self.onEditDye, ch = chName, compNo = lightpath.index(component), opticalpath = lightpath))
		self.dyeListBox.Bind(wx.EVT_LISTBOX_DCLICK, partial(self.onMyDyeSelect, ch = chName, compNo = lightpath.index(component), opticalpath = lightpath))
		dye_sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
		dye_sizer.Add(self.dyeListBox, 0)               
		ch_sizer.Add(dye_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND) 	    		
		
	    if compName.startswith('DTC'):
		staticbox = wx.StaticBox(self.bot_panel, -1, "Detector")
		volt = int(compName.split('DTC')[1])		
		self.detector = wx.SpinCtrl(self.bot_panel, -1, "", (30, 50))
		self.detector.SetRange(1,1000)
		self.detector.SetValue(volt)
		self.detector.Bind(wx.EVT_SPINCTRL, partial(self.onEditDetector, ch = chName, compNo = lightpath.index(component), opticalpath = lightpath))
		detector_sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
		detector_sizer.Add(self.detector, 0)
		ch_sizer.Add(detector_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
	
	
	##set the delete button at the end
	self.delete_button = wx.Button(self.bot_panel, wx.ID_DELETE)
	self.delete_button.Bind(wx.EVT_BUTTON, partial(self.onDeleteCh, cn = chName))
	ch_sizer.Add(self.delete_button, 0, wx.ALIGN_CENTER_VERTICAL)
	
	#-- Sizers --#
	#self.top_panel.SetSizer(self.top_fgs)
	self.bot_fgs.Add(ch_sizer, 0, wx.ALL, 5)
	self.bot_panel.SetSizer(self.bot_fgs)
        self.bot_panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

	
    def onEditDye(self, event, ch, compNo, opticalpath):
	meta = ExperimentSettings.getInstance() 
	ctrl = event.GetEventObject()
		
	opticalpath[compNo][0] = 'DYE'+'_'+ctrl.GetStringSelection()
	tag = self.tag_stump+'|%s|%s' %(ch, str(self.tab_number))
	meta.remove_field(tag)
	meta.set_field(tag, opticalpath)
    
    def onMyDyeSelect(self, event, ch, compNo, opticalpath):
	meta = ExperimentSettings.getInstance()
	ctrl = event.GetEventObject()
	
	emLow, emHgh = meta.getNM(opticalpath[compNo][1])
	dye = wx.GetTextFromUser('Enter Dye name within the emission range '+str(emLow)+' - '+str(emHgh), 'Customized Dye')
	if dye != '':
	    ctrl.Delete(ctrl.GetSelection())
	    ctrl.Append(dye)
	    ctrl.SetStringSelection(dye)
	    
	    opticalpath[compNo][0] = 'DYE'+'_'+dye
	    tag = self.tag_stump+'|%s|%s' %(ch, str(self.tab_number))
	    meta.remove_field(tag)
	    meta.set_field(tag, opticalpath)
	    
    def onEditDetector(self, event, ch, compNo, opticalpath):
	meta = ExperimentSettings.getInstance() 
	ctrl = event.GetEventObject()

	opticalpath[compNo][0] = 'DTC%s' %str(ctrl.GetValue())
		
	tag = self.tag_stump+'|%s|%s' %(ch, str(self.tab_number))
	meta.remove_field(tag)
	meta.set_field(tag, opticalpath)	
		    
    def onDeleteCh(self, event, cn):
	meta = ExperimentSettings.getInstance()
	meta.remove_field(self.tag_stump+'|%s|%s'%(cn, self.tab_number))
	self.bot_fgs.Clear(deleteWindows=True)
	self.showChannels()
	    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)

    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags) 		

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)



#########################################################################        
###################     Draw Spectrum on panel size 100,30 pxl  #########
######################################################################### 
class DrawSpectrum(wx.Panel):
    def __init__(self, parent, startNM, endNM):
        wx.Panel.__init__(self, parent,  size=(100, 30), style=wx.SUNKEN_BORDER)

        self.parent = parent	
	
	self.startNM = startNM
	self.endNM = endNM
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnPaint(self, event): 
	
	meta = ExperimentSettings.getInstance()  
	
	spectralRange =  meta.partition(range(self.startNM, self.endNM+1), 5)
	
	dc = wx.PaintDC(self)	
	dc.GradientFillLinear((0, 0, 30, 30), meta.nmToRGB(spectralRange[0]), meta.nmToRGB(spectralRange[1]), wx.EAST)
	dc.GradientFillLinear((30, 0, 30, 30), meta.nmToRGB(spectralRange[1]), meta.nmToRGB(spectralRange[2]), wx.EAST)
	dc.GradientFillLinear((60, 0, 30, 30), meta.nmToRGB(spectralRange[2]), meta.nmToRGB(spectralRange[3]), wx.EAST)
	dc.GradientFillLinear((90, 0, 30, 30), meta.nmToRGB(spectralRange[3]), meta.nmToRGB(spectralRange[4]), wx.EAST)
	dc.GradientFillLinear((120, 0, 30, 30), meta.nmToRGB(spectralRange[4]), meta.nmToRGB(spectralRange[5]), wx.EAST)
	dc.EndDrawing()	
	
    def OnSize(self, event):
	self.Refresh()

#########################################################################        
###################     PLATE SETTING PANEL          ####################
#########################################################################
class PlateSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """   
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'ExptVessel|Plate'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	stack_ids = meta.get_stack_ids(self.protocol)
	
	for stack_id in sorted(stack_ids):
	    panel = PlatePanel(self.notebook, int(stack_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(stack_id), True)
		
	# Buttons
	self.createTabBtn = wx.Button(self, label="Create Instance")
	self.createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(self.createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	stack_ids = meta.get_stack_ids(self.protocol)
	if stack_ids:
            stack_id =  max(map(int, stack_ids))+1
        else:
            stack_id = 1	    
	
	panel = PlatePanel(self.notebook, stack_id)
	self.notebook.AddPage(panel, 'Instance No: %s'%stack_id, True) 
	#Prevent users from clicking the 'Create Instance' button
	self.createTabBtn.Disable()

##---- Plate Configuration Panel --------#         
class PlatePanel(wx.Panel):
    '''
    Panel that displays the instance
    '''
    def __init__(self, parent, tab_number):

	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()

	self.tag_stump = 'ExptVessel|Plate'	
	self.tab_number = tab_number

	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	self.sw = wx.ScrolledWindow(self)

	fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	
	new_stack = True
	stack_ids = meta.get_stack_ids(self.tag_stump)
	rep_vessel_instance = None
	for stack_id in stack_ids:
	    if stack_id == self.tab_number:
		rep_vessel_instance = meta.get_rep_vessel_instance(self.tag_stump, stack_id) #Since all vessels for a given stack have same specifications, so single instance will be used to fill the information
	if rep_vessel_instance is not None:
	    new_stack = False
	    
	self.mandatory_tags = [self.tag_stump+'|Number|%s'%rep_vessel_instance, self.tag_stump+'|StackName|%s'%rep_vessel_instance, self.tag_stump+'|Design|%s'%rep_vessel_instance]
        # Heading
	text = wx.StaticText(self.sw, -1, 'Plate Specifications')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(text, 0)
	titlesizer.Add((10,-1))
	# CREATE button
	self.createBtn = wx.Button(self.sw, -1, label="Put Stack on Bench")
	self.createBtn.Bind(wx.EVT_BUTTON, self.onCreateStack)
	if new_stack is False:
	    self.createBtn.Disable()        
	titlesizer.Add(self.createBtn, 0, wx.EXPAND) 	
	
        # Vessel number
	numberTAG = self.tag_stump+'|Number|%s'%rep_vessel_instance
        self.vessnum = wx.Choice(self.sw, -1,  choices= map(str, range(1,51)), style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.vessnum.Enable() 
        else:
            self.vessnum.SetStringSelection(meta.get_field(numberTAG))
            self.vessnum.Disable()  
	self.labels[numberTAG] = wx.StaticText(self.sw, -1, 'Number of Plate in Stack')
	fgs.Add(self.labels[numberTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.vessnum, 0, wx.EXPAND)                
        # Stack name
	nameTAG = self.tag_stump+'|StackName|%s'%rep_vessel_instance
        self.stkname= wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.stkname.Enable()
        else:
            self.stkname.SetValue(meta.get_field(nameTAG))
            self.stkname.Disable()
	self.labels[nameTAG] = wx.StaticText(self.sw, -1, 'Stack Name')
        fgs.Add(self.labels[nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.stkname, 0, wx.EXPAND) 
	#--Design--# **** This is different as it include different plate formats *****
	designTAG = self.tag_stump+'|Design|%s'%rep_vessel_instance
	self.vessdesign = wx.Choice(self.sw, -1, choices=WELL_NAMES_ORDERED, name='PlateDesign')
	for i, format in enumerate([WELL_NAMES[name] for name in WELL_NAMES_ORDERED]):
		self.vessdesign.SetClientData(i, format)
	if new_stack is True:
	    self.vessdesign.Enable()            
	else:
	    self.vessdesign.SetStringSelection(meta.get_field(designTAG))
	    self.vessdesign.Disable() 
	self.labels[designTAG] = wx.StaticText(self.sw, -1, 'Plate Design')
	fgs.Add(self.labels[designTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessdesign, 0, wx.EXPAND)	
	# Manufacturer
	mfgTAG = self.tag_stump+'|Manufacturer|%s'%rep_vessel_instance
	self.vessmfg = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessmfg.Enable()
	else:
	    self.vessmfg.SetValue(meta.get_field(mfgTAG, default=''))
	    self.vessmfg.Disable()
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer') 
	fgs.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessmfg, 0, wx.EXPAND) 
	# Catalogue Number
	catnoTAG = self.tag_stump+'|CatalogueNo|%s'%rep_vessel_instance
	self.vesscat = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesscat.Enable()
	else:
	    self.vesscat.SetValue(meta.get_field(catnoTAG, default=''))
	    self.vesscat.Disable()
	self.labels[catnoTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	fgs.Add(self.labels[catnoTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscat, 0, wx.EXPAND) 	
	# Shape
	shapeTAG = self.tag_stump+'|Shape|%s'%rep_vessel_instance
	self.vessshape = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessshape.Enable()
	else:
	    self.vessshape.SetValue(meta.get_field(shapeTAG, default=''))
	    self.vessshape.Disable()
	self.labels[shapeTAG] = wx.StaticText(self.sw, -1, 'Shape')
	fgs.Add(self.labels[shapeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessshape, 0, wx.EXPAND)		
	# Size
	sizeTAG = self.tag_stump+'|Size|%s'%rep_vessel_instance
	self.vesssize = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesssize.Enable()
	else:
	    self.vesssize.SetValue(meta.get_field(sizeTAG))
	    self.vesssize.Disable()
	self.labels[sizeTAG] = wx.StaticText(self.sw, -1, 'Size (mm x mm)')
	fgs.Add(self.labels[sizeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesssize, 0, wx.EXPAND)
        # Coating
	coatTAG = self.tag_stump+'|Coat|%s'%rep_vessel_instance
	choices=['None','Collagen IV','Gelatin','Poly-L-Lysine','Poly-D-Lysine', 'Fibronectin', 'Laminin','Poly-D-Lysine + Laminin', 'Poly-L-Ornithine+Laminin', 'Other']
	self.vesscoat = wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if new_stack is True:
	    self.vesscoat.Enable()
	else:	
	    self.vesscoat.Append(meta.get_field(coatTAG))
	    self.vesscoat.SetStringSelection(meta.get_field(coatTAG))
	    self.vesscoat.Disable()
	self.vesscoat.Bind(wx.EVT_LISTBOX, self.onSelectOther)
	self.labels[coatTAG] = wx.StaticText(self.sw, -1, 'Coating')
	fgs.Add(self.labels[coatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscoat, 0, wx.EXPAND)
	# Other Information
	otherTAG = self.tag_stump+'|OtherInfo|%s'%rep_vessel_instance
	self.vessother = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.vessother.SetInitialSize((-1,100))
	if new_stack is True:
	    self.vessother.Enable()
	else:
	    self.vessother.SetValue(meta.get_field(otherTAG, default=''))
	    self.vessother.Disable()
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other Information')
	fgs.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessother, 0, wx.EXPAND) 	   
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		

	#---  Layout with sizers  -------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(fgs)
	self.sw.SetSizer(swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
    def onSelectOther(self, event):
	if self.vesscoat.GetStringSelection() == 'Other':
	    other = wx.GetTextFromUser('Insert Other', 'Other')
	    self.vesscoat.Append(other)
	    self.vesscoat.SetStringSelection(other)	
    
    def onCreateStack(self, event):
	# Checks 
	if not self.vessnum.GetStringSelection():
	    dial = wx.MessageDialog(None, 'Please select the number of vessels', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	if not self.stkname.GetValue():
	    dial = wx.MessageDialog(None, 'Please select the Stack Name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	if not self.vessdesign.GetStringSelection():
	    dial = wx.MessageDialog(None, 'Please select the vessel design', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return	
	
	# if all checks are passed
	self.createBtn.Disable()
	
        vess_list = meta.get_field_instances(self.tag_stump)
        if vess_list:
            max_id =  max(map(int, vess_list))+1
        else:
            max_id = 1
	    
        for v_id in range(max_id, max_id+int(self.vessnum.GetStringSelection())):
            id = 'Plate%s'%(v_id)
            plate_design = self.vessdesign.GetClientData(self.vessdesign.GetSelection())  
            if id not in PlateDesign.get_plate_ids():
                PlateDesign.add_plate('Plate', str(v_id), plate_design, self.stkname.GetValue())
            else:
                PlateDesign.set_plate_format(id, plate_design)
        
            meta.set_field(self.tag_stump+'|StackNo|%s'%str(v_id),    self.tab_number, notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Number|%s'%str(v_id),     self.vessnum.GetStringSelection(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|StackName|%s'%str(v_id),  self.stkname.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Design|%s'%str(v_id),     self.vessdesign.GetStringSelection(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Manufacturer|%s'%str(v_id),  self.vessmfg.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|CatalogueNo|%s'%str(v_id),  self.vesscat.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Shape|%s'%str(v_id),       self.vessshape.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Size|%s'%str(v_id),       self.vesssize.GetValue(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Coat|%s'%str(v_id),       self.vesscoat.GetStringSelection(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|OtherInfo|%s'%str(v_id),  self.vessother.GetValue())
        
	#make all input fields disable
        self.vessnum.Disable()
	self.stkname.Disable()
	self.vessdesign.Disable()
	self.vessmfg.Disable()
	self.vesscat.Disable()
	self.vessshape.Disable()
	self.vesssize.Disable()
	self.vesscoat.Disable()
	self.vessother.Disable()
	#Enable to create new instance
	self.GrandParent.createTabBtn.Enable()
	
#########################################################################        
###################     DISH SETTING PANEL          ####################
#########################################################################	    
class DishSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """   
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'ExptVessel|Dish'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	stack_ids = meta.get_stack_ids(self.protocol)
	
	for stack_id in sorted(stack_ids):
	    panel = DishPanel(self.notebook, int(stack_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(stack_id), True)
		
	# Buttons
	self.createTabBtn = wx.Button(self, label="Create Instance")
	self.createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(self.createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	stack_ids = meta.get_stack_ids(self.protocol)
	if stack_ids:
            stack_id =  max(map(int, stack_ids))+1
        else:
            stack_id = 1	    
	
	panel = DishPanel(self.notebook, stack_id)
	self.notebook.AddPage(panel, 'Instance No: %s'%stack_id, True) 
	#Prevent users from clicking the 'Create Instance' button
	self.createTabBtn.Disable()	

##---------- Dish Config Panel----------------##
class DishPanel(wx.Panel):
    '''
    Panel that displays the instance
    '''
    def __init__(self, parent, tab_number):

	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	self.sw = wx.ScrolledWindow(self)

	self.tab_number = tab_number
	fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	
	self.tag_stump = 'ExptVessel|Dish'
	
	new_stack = True
	stack_ids = meta.get_stack_ids(self.tag_stump)
	rep_vessel_instance = None
	for stack_id in stack_ids:
	    if stack_id == self.tab_number:
		rep_vessel_instance = meta.get_rep_vessel_instance(self.tag_stump, stack_id) #Since all vessels for a given stack have same specifications, so single instance will be used to fill the information
	if rep_vessel_instance is not None:
	    new_stack = False
	    
	self.mandatory_tags = [self.tag_stump+'|Number|%s'%rep_vessel_instance, self.tag_stump+'|StackName|%s'%rep_vessel_instance]

        # Heading
	text = wx.StaticText(self.sw, -1, 'Dish Specifications')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(text, 0)
	titlesizer.Add((10,-1))
	# CREATE button
	self.createBtn = wx.Button(self.sw, -1, label="Put Stack on Bench")
	self.createBtn.Bind(wx.EVT_BUTTON, self.onCreateStack)
	if new_stack is False:
	    self.createBtn.Disable()        
	titlesizer.Add(self.createBtn, 0, wx.EXPAND) 	
	
        # Vessel number
	numberTAG = self.tag_stump+'|Number|%s'%rep_vessel_instance
        self.vessnum = wx.Choice(self.sw, -1,  choices= map(str, range(1,51)), style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.vessnum.Enable() 
        else:
            self.vessnum.SetStringSelection(meta.get_field(numberTAG))
            self.vessnum.Disable()   
	self.labels[numberTAG] = wx.StaticText(self.sw, -1, 'Number of Dish in Stack')
	fgs.Add(self.labels[numberTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.vessnum, 0, wx.EXPAND)                
        # Group name
	nameTAG = self.tag_stump+'|StackName|%s'%rep_vessel_instance
        self.stkname= wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.stkname.Enable()
        else:
            self.stkname.SetValue(meta.get_field(nameTAG))
            self.stkname.Disable()
	self.labels[nameTAG] = wx.StaticText(self.sw, -1, 'Stack Name')
        fgs.Add(self.labels[nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.stkname, 0, wx.EXPAND) 
	# Manufacturer
	mfgTAG = self.tag_stump+'|Manufacturer|%s'%rep_vessel_instance
	self.vessmfg = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessmfg.Enable()
	else:
	    self.vessmfg.SetValue(meta.get_field(mfgTAG, default=''))
	    self.vessmfg.Disable()
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	fgs.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessmfg, 0, wx.EXPAND) 
	# Catalogue Number
	catnoTAG = self.tag_stump+'|CatalogueNo|%s'%rep_vessel_instance
	self.vesscat = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesscat.Enable()
	else:
	    self.vesscat.SetValue(meta.get_field(catnoTAG, default=''))
	    self.vesscat.Disable()
	self.labels[catnoTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	fgs.Add(self.labels[catnoTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscat, 0, wx.EXPAND) 	
	# Size
	sizeTAG = self.tag_stump+'|Size|%s'%rep_vessel_instance
	self.vesssize = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesssize.Enable()
	else:
	    self.vesssize.SetValue(meta.get_field(sizeTAG, default=''))
	    self.vesssize.Disable()
	self.labels[sizeTAG] = wx.StaticText(self.sw, -1, 'Size (mm)')
	fgs.Add(self.labels[sizeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesssize, 0, wx.EXPAND)
        # Coating
	coatTAG = self.tag_stump+'|Coat|%s'%rep_vessel_instance
	choices=['None','Collagen IV','Gelatin','Poly-L-Lysine','Poly-D-Lysine', 'Fibronectin', 'Laminin','Poly-D-Lysine + Laminin', 'Poly-L-Ornithine+Laminin', 'Other']
	self.vesscoat = wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if new_stack is True:
	    self.vesscoat.Enable()
	else:	
	    self.vesscoat.Append(meta.get_field(self.tag_stump+'|Coat|%s'%rep_vessel_instance, default=''))
	    self.vesscoat.SetStringSelection(meta.get_field(coatTAG))
	    self.vesscoat.Disable()
	self.vesscoat.Bind(wx.EVT_LISTBOX, self.onSelectOther)
	self.labels[coatTAG] = wx.StaticText(self.sw, -1, 'Coating')
	fgs.Add(self.labels[coatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscoat, 0, wx.EXPAND)
	# Other Information
	otherTAG = self.tag_stump+'|OtherInfo|%s'%rep_vessel_instance
	self.vessother = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.vessother.SetInitialSize((-1,100))
	if new_stack is True:
	    self.vessother.Enable()
	else:
	    self.vessother.SetValue(meta.get_field(otherTAG, default=''))
	    self.vessother.Disable()
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other Information')
	fgs.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessother, 0, wx.EXPAND) 	

	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)

	#---  Layout with sizers  -------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(fgs)
	self.sw.SetSizer(swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
    def onSelectOther(self, event):
	if self.vesscoat.GetStringSelection() == 'Other':
	    other = wx.GetTextFromUser('Insert Other', 'Other')
	    self.vesscoat.Append(other)
	    self.vesscoat.SetStringSelection(other)	
    
    def onCreateStack(self, event):
	# Checks 
	if not self.vessnum.GetStringSelection():
	    dial = wx.MessageDialog(None, 'Please select the number of vessels', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	if not self.stkname.GetValue():
	    dial = wx.MessageDialog(None, 'Please select the Stack Name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	#vess_design = self.vessdesign.GetStringSelection()
	#if vess_design is None:
	    #dial = wx.MessageDialog(None, 'Please select the vessel design', 'Error', wx.OK | wx.ICON_ERROR)
	    #dial.ShowModal()  
	    #return	
	self.createBtn.Disable()
	
        vess_list = meta.get_field_instances(self.tag_stump)
        if vess_list:
            max_id =  max(map(int, vess_list))+1
        else:
            max_id = 1
	    
        for v_id in range(max_id, max_id+int(self.vessnum.GetStringSelection())):
            id = 'Dish%s'%(v_id)
            plate_design = (1,1)  # since flask is alwasys a sigle entity resembling to 1x1 well plate format   
            if id not in PlateDesign.get_plate_ids():
                PlateDesign.add_plate('Dish', str(v_id), plate_design, self.stkname.GetValue())
            else:
                PlateDesign.set_plate_format(id, plate_design)
        
            meta.set_field(self.tag_stump+'|StackNo|%s'%str(v_id),    self.tab_number, notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Number|%s'%str(v_id),     self.vessnum.GetStringSelection(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|StackName|%s'%str(v_id),  self.stkname.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Manufacturer|%s'%str(v_id),  self.vessmfg.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|CatalogueNo|%s'%str(v_id),  self.vesscat.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Size|%s'%str(v_id),       self.vesssize.GetValue(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Coat|%s'%str(v_id),       self.vesscoat.GetStringSelection(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|OtherInfo|%s'%str(v_id),  self.vessother.GetValue())
        
	#make all input fields disable
        self.vessnum.Disable()
	self.stkname.Disable()
	self.vessmfg.Disable()
	self.vesscat.Disable()
	self.vesssize.Disable()
	self.vesscoat.Disable()
	self.vessother.Disable()
	#Enable to create new instance
	self.GrandParent.createTabBtn.Enable()
	
#########################################################################        
###################     DISH SETTING PANEL          ####################
#########################################################################	    
class CoverslipSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """   
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'ExptVessel|Coverslip'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	stack_ids = meta.get_stack_ids(self.protocol)
	
	for stack_id in sorted(stack_ids):
	    panel = CoverslipPanel(self.notebook, int(stack_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(stack_id), True)
		
	# Buttons
	self.createTabBtn = wx.Button(self, label="Create Instance")
	self.createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(self.createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	stack_ids = meta.get_stack_ids(self.protocol)
	if stack_ids:
            stack_id =  max(map(int, stack_ids))+1
        else:
            stack_id = 1	    
	
	panel = CoverslipPanel(self.notebook, stack_id)
	self.notebook.AddPage(panel, 'Instance No: %s'%stack_id, True) 
	#Prevent users from clicking the 'Create Instance' button
	self.createTabBtn.Disable()	

##---------- Coverslip Instance Panel----------------##
class CoverslipPanel(wx.Panel):
    '''
    Panel that displays the instance
    '''
    def __init__(self, parent, tab_number):

	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	self.sw = wx.ScrolledWindow(self)

	self.tab_number = tab_number
	fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	
	self.tag_stump = 'ExptVessel|Coverslip'
	
	new_stack = True
	stack_ids = meta.get_stack_ids(self.tag_stump)
	rep_vessel_instance = None
	for stack_id in stack_ids:
	    if stack_id == self.tab_number:
		rep_vessel_instance = meta.get_rep_vessel_instance(self.tag_stump, stack_id) #Since all vessels for a given stack have same specifications, so single instance will be used to fill the information
	if rep_vessel_instance is not None:
	    new_stack = False
	    
	self.mandatory_tags = [self.tag_stump+'|Number|%s'%rep_vessel_instance, self.tag_stump+'|StackName|%s'%rep_vessel_instance]	

        # Heading
	text = wx.StaticText(self.sw, -1, 'Coverslip Specifications')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(text, 0)
	titlesizer.Add((10,-1))
	# CREATE button
	self.createBtn = wx.Button(self.sw, -1, label="Put Stack on Bench")
	self.createBtn.Bind(wx.EVT_BUTTON, self.onCreateStack)
	if new_stack is False:
	    self.createBtn.Disable()        
	titlesizer.Add(self.createBtn, 0, wx.EXPAND) 	
	
        # Vessel number
	numberTAG = self.tag_stump+'|Number|%s'%rep_vessel_instance
        self.vessnum = wx.Choice(self.sw, -1,  choices= map(str, range(1,51)), style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.vessnum.Enable() 
        else:
            self.vessnum.SetStringSelection(meta.get_field(numberTAG))
            self.vessnum.Disable() 
	self.labels[numberTAG] = wx.StaticText(self.sw, -1, 'Number of Coverslip in Stack')
	fgs.Add(self.labels[numberTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.vessnum, 0, wx.EXPAND)                
        # Group name
	nameTAG = self.tag_stump+'|StackName|%s'%rep_vessel_instance	
        self.stkname= wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.stkname.Enable()
        else:
            self.stkname.SetValue(meta.get_field(nameTAG))
            self.stkname.Disable()
	self.labels[nameTAG] = wx.StaticText(self.sw, -1, 'Stack Name')
        fgs.Add(self.labels[nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.stkname, 0, wx.EXPAND) 
	# Manufacturer
	mfgTAG = self.tag_stump+'|Manufacturer|%s'%rep_vessel_instance
	self.vessmfg = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessmfg.Enable()
	else:
	    self.vessmfg.SetValue(meta.get_field(mfgTAG, default=''))
	    self.vessmfg.Disable()
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	fgs.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessmfg, 0, wx.EXPAND) 
	# Catalogue Number
	catnoTAG = self.tag_stump+'|CatalogueNo|%s'%rep_vessel_instance
	self.vesscat = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesscat.Enable()
	else:
	    self.vesscat.SetValue(meta.get_field(catnoTAG, default=''))
	    self.vesscat.Disable()
	self.labels[catnoTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	fgs.Add(self.labels[catnoTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscat, 0, wx.EXPAND) 	
	# Size
	sizeTAG = self.tag_stump+'|Size|%s'%rep_vessel_instance
	self.vesssize = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesssize.Enable()
	else:
	    self.vesssize.SetValue(meta.get_field(sizeTAG, default=''))
	    self.vesssize.Disable()
	self.labels[sizeTAG] = wx.StaticText(self.sw, -1, 'Size (mm x mm)')
	fgs.Add(self.labels[sizeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesssize, 0, wx.EXPAND)
	# Thickness
	thickTAG = self.tag_stump+'|Thickness|%s'%rep_vessel_instance
	self.vessthick = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessthick.Enable()
	else:
	    self.vessthick.SetValue(meta.get_field(thickTAG, default=''))
	    self.vessthick.Disable()
	self.labels[thickTAG] = wx.StaticText(self.sw, -1, 'Thickness') 
	fgs.Add(self.labels[thickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessthick, 0, wx.EXPAND)	
        # Coating
	coatTAG = self.tag_stump+'|Coat|%s'%rep_vessel_instance
	choices=['None','Collagen IV','Gelatin','Poly-L-Lysine','Poly-D-Lysine', 'Fibronectin', 'Laminin','Poly-D-Lysine + Laminin', 'Poly-L-Ornithine+Laminin', 'Other']
	self.vesscoat = wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if new_stack is True:
	    self.vesscoat.Enable()
	else:	
	    self.vesscoat.Append(meta.get_field(coatTAG))
	    self.vesscoat.SetStringSelection(meta.get_field(coatTAG))
	    self.vesscoat.Disable()
	self.vesscoat.Bind(wx.EVT_LISTBOX, self.onSelectOther)
	self.labels[coatTAG] = wx.StaticText(self.sw, -1, 'Coating')
	fgs.Add(self.labels[coatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscoat, 0, wx.EXPAND)
	# Other Information
	otherTAG = self.tag_stump+'|OtherInfo|%s'%rep_vessel_instance
	self.vessother = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.vessother.SetInitialSize((-1,100))
	if new_stack is True:
	    self.vessother.Enable()
	else:
	    self.vessother.SetValue(meta.get_field(otherTAG, default=''))
	    self.vessother.Disable()
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other Information')
	fgs.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessother, 0, wx.EXPAND) 	            
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	

	#---  Layout with sizers  -------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(fgs)
	self.sw.SetSizer(swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
    def onSelectOther(self, event):
	if self.vesscoat.GetStringSelection() == 'Other':
	    other = wx.GetTextFromUser('Insert Other', 'Other')
	    self.vesscoat.Append(other)
	    self.vesscoat.SetStringSelection(other)	
    
    def onCreateStack(self, event):
	# Checks 
	if not self.vessnum.GetStringSelection:
	    dial = wx.MessageDialog(None, 'Please select the number of vessels', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	if not self.stkname.GetValue():
	    dial = wx.MessageDialog(None, 'Please select the Stack Name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	#vess_design = self.vessdesign.GetStringSelection()
	#if vess_design is None:
	    #dial = wx.MessageDialog(None, 'Please select the vessel design', 'Error', wx.OK | wx.ICON_ERROR)
	    #dial.ShowModal()  
	    #return	
	self.createBtn.Disable()
	
        vess_list = meta.get_field_instances(self.tag_stump)
        if vess_list:
            max_id =  max(map(int, vess_list))+1
        else:
            max_id = 1
	    
        for v_id in range(max_id, max_id+int(self.vessnum.GetStringSelection())):
            id = 'Coverslip%s'%(v_id)
            plate_design = (1,1)  # since flask is alwasys a sigle entity resembling to 1x1 well plate format   
            if id not in PlateDesign.get_plate_ids():
                PlateDesign.add_plate('Coverslip', str(v_id), plate_design, self.stkname.GetValue())
            else:
                PlateDesign.set_plate_format(id, plate_design)
        
            meta.set_field(self.tag_stump+'|StackNo|%s'%str(v_id),    self.tab_number, notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Number|%s'%str(v_id),     self.vessnum.GetStringSelection(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|StackName|%s'%str(v_id),  self.stkname.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Manufacturer|%s'%str(v_id),  self.vessmfg.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|CatalogueNo|%s'%str(v_id),  self.vesscat.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Size|%s'%str(v_id),       self.vesssize.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Thickness|%s'%str(v_id),       self.vessthick.GetValue(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Coat|%s'%str(v_id),       self.vesscoat.GetStringSelection(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|OtherInfo|%s'%str(v_id),  self.vessother.GetValue())
        
	#make all input fields disable
        self.vessnum.Disable()
	self.stkname.Disable()
	self.vessmfg.Disable()
	self.vesscat.Disable()
	self.vesssize.Disable()
	self.vessthick.Disable()
	self.vesscoat.Disable()
	self.vessother.Disable()
	#Enable to create new instance
	self.GrandParent.createTabBtn.Enable()
	
#########################################################################        
###################     FLASK SETTING PANEL          ####################
#########################################################################	    
class FlaskSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """   
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'ExptVessel|Flask'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	stack_ids = meta.get_stack_ids(self.protocol)
	
	for stack_id in sorted(stack_ids):
	    panel = FlaskPanel(self.notebook, int(stack_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(stack_id), True)
		
	# Buttons
	self.createTabBtn = wx.Button(self, label="Create Instance")
	self.createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(self.createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	stack_ids = meta.get_stack_ids(self.protocol)
	if stack_ids:
            stack_id =  max(map(int, stack_ids))+1
        else:
            stack_id = 1	    
	
	panel = FlaskPanel(self.notebook, stack_id)
	self.notebook.AddPage(panel, 'Instance No: %s'%stack_id, True) 
	#Prevent users from clicking the 'Create Instance' button
	self.createTabBtn.Disable()

##---------- Flask Config Panel----------------##
class FlaskPanel(wx.Panel):
    '''
    Panel that displays the instance
    '''
    def __init__(self, parent, tab_number):

	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	self.sw = wx.ScrolledWindow(self)

	self.tab_number = tab_number
	fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	
	self.tag_stump = 'ExptVessel|Flask'
	
	new_stack = True
	stack_ids = meta.get_stack_ids(self.tag_stump)
	rep_vessel_instance = None
	for stack_id in stack_ids:
	    if stack_id == self.tab_number:
		rep_vessel_instance = meta.get_rep_vessel_instance(self.tag_stump, stack_id) #Since all vessels for a given stack have same specifications, so single instance will be used to fill the information
	if rep_vessel_instance is not None:
	    new_stack = False
	
	self.mandatory_tags = [self.tag_stump+'|Number|%s'%rep_vessel_instance, self.tag_stump+'|StackName|%s'%rep_vessel_instance]

        # Heading
	text = wx.StaticText(self.sw, -1, 'Flask Specifications')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(text, 0)
	titlesizer.Add((10,-1))
	# CREATE button
	self.createBtn = wx.Button(self.sw, -1, label="Put Stack on Bench")
	self.createBtn.Bind(wx.EVT_BUTTON, self.onCreateStack)
	if new_stack is False:
	    self.createBtn.Disable()        
	titlesizer.Add(self.createBtn, 0, wx.EXPAND) 	
	
        # Vessel number
	numberTAG = self.tag_stump+'|Number|%s'%rep_vessel_instance
        self.vessnum = wx.Choice(self.sw, -1,  choices= map(str, range(1,51)), style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.vessnum.Enable() 
        else:
            self.vessnum.SetStringSelection(meta.get_field(numberTAG))
            self.vessnum.Disable()    
	self.labels[numberTAG] = wx.StaticText(self.sw, -1, 'Number of Flask in Stack')
	fgs.Add(self.labels[numberTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.vessnum, 0, wx.EXPAND)                
        # Group name
	nameTAG = self.tag_stump+'|StackName|%s'%rep_vessel_instance
        self.stkname= wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.stkname.Enable()
        else:
            self.stkname.SetValue(meta.get_field(nameTAG))
            self.stkname.Disable()
	self.labels[nameTAG] = wx.StaticText(self.sw, -1, 'Stack Name')
        fgs.Add(self.labels[nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.stkname, 0, wx.EXPAND) 
	# Manufacturer
	mfgTAG = self.tag_stump+'|Manufacturer|%s'%rep_vessel_instance
	self.vessmfg = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessmfg.Enable()
	else:
	    self.vessmfg.SetValue(meta.get_field(mfgTAG, default=''))
	    self.vessmfg.Disable()
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	fgs.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessmfg, 0, wx.EXPAND) 
	# Catalogue Number
	catnoTAG = self.tag_stump+'|CatalogueNo|%s'%rep_vessel_instance
	self.vesscat = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesscat.Enable()
	else:
	    self.vesscat.SetValue(meta.get_field(catnoTAG, default=''))
	    self.vesscat.Disable()
	self.labels[catnoTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	fgs.Add(self.labels[catnoTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscat, 0, wx.EXPAND) 	
	# Size
	sizeTAG = self.tag_stump+'|Size|%s'%rep_vessel_instance
	self.vesssize = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesssize.Enable()
	else:
	    self.vesssize.SetValue(meta.get_field(sizeTAG, default=''))
	    self.vesssize.Disable()
	self.labels[sizeTAG] = wx.StaticText(self.sw, -1, 'Size (cm2)')
	fgs.Add(self.labels[sizeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesssize, 0, wx.EXPAND)
        # Coating
	coatTAG = self.tag_stump+'|Coat|%s'%rep_vessel_instance
	choices=['None','Collagen IV','Gelatin','Poly-L-Lysine','Poly-D-Lysine', 'Fibronectin', 'Laminin','Poly-D-Lysine + Laminin', 'Poly-L-Ornithine+Laminin', 'Other']
	self.vesscoat = wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if new_stack is True:
	    self.vesscoat.Enable()
	else:	
	    self.vesscoat.Append(meta.get_field(coatTAG))
	    self.vesscoat.SetStringSelection(meta.get_field(coatTAG))
	    self.vesscoat.Disable()
	self.vesscoat.Bind(wx.EVT_LISTBOX, self.onSelectOther)
	self.labels[coatTAG] = wx.StaticText(self.sw, -1, 'Coating')
	fgs.Add(self.labels[coatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscoat, 0, wx.EXPAND)
	# Other Information
	otherTAG = self.tag_stump+'|OtherInfo|%s'%rep_vessel_instance
	self.vessother = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.vessother.SetInitialSize((-1,100))
	if new_stack is True:
	    self.vessother.Enable()
	else:
	    self.vessother.SetValue(meta.get_field(otherTAG, default=''))
	    self.vessother.Disable()
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other Information')
	fgs.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessother, 0, wx.EXPAND) 	            
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		

	#---  Layout with sizers  -------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(fgs)
	self.sw.SetSizer(swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
    def onSelectOther(self, event):
	if self.vesscoat.GetStringSelection() == 'Other':
	    other = wx.GetTextFromUser('Insert Other', 'Other')
	    self.vesscoat.Append(other)
	    self.vesscoat.SetStringSelection(other)	
    
    def onCreateStack(self, event):
	# Checks 
	if not self.vessnum.GetStringSelection():
	    dial = wx.MessageDialog(None, 'Please select the number of vessels', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	if not self.stkname.GetValue():
	    dial = wx.MessageDialog(None, 'Please select the Stack Name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return

	self.createBtn.Disable()
	
        vess_list = meta.get_field_instances(self.tag_stump)
        if vess_list:
            max_id =  max(map(int, vess_list))+1
        else:
            max_id = 1
	    
        for v_id in range(max_id, max_id+int(self.vessnum.GetStringSelection())):
            id = 'Flask%s'%(v_id)
            plate_design = (1,1)  # since flask is alwasys a sigle entity resembling to 1x1 well plate format   
            if id not in PlateDesign.get_plate_ids():
                PlateDesign.add_plate('Flask', str(v_id), plate_design, self.stkname.GetValue())
            else:
                PlateDesign.set_plate_format(id, plate_design)
        
            meta.set_field(self.tag_stump+'|StackNo|%s'%str(v_id),    self.tab_number, notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Number|%s'%str(v_id),     self.vessnum.GetStringSelection(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|StackName|%s'%str(v_id),  self.stkname.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Manufacturer|%s'%str(v_id),  self.vessmfg.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|CatalogueNo|%s'%str(v_id),  self.vesscat.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Size|%s'%str(v_id),       self.vesssize.GetValue(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Coat|%s'%str(v_id),       self.vesscoat.GetStringSelection(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|OtherInfo|%s'%str(v_id),  self.vessother.GetValue())
        
	#make all input fields disable
        self.vessnum.Disable()
	self.stkname.Disable()
	self.vessmfg.Disable()
	self.vesscat.Disable()
	self.vesssize.Disable()
	self.vesscoat.Disable()
	self.vessother.Disable()
	#Enable to create new instance
	self.GrandParent.createTabBtn.Enable()
	
	
#########################################################################        
###################     TUBE SETTING PANEL          ####################
#########################################################################	    
class TubeSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """   
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'ExptVessel|Tube'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	stack_ids = meta.get_stack_ids(self.protocol)
	
	for stack_id in sorted(stack_ids):
	    panel = TubePanel(self.notebook, int(stack_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(stack_id), True)
		
	# Buttons
	self.createTabBtn = wx.Button(self, label="Create Instance")
	self.createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(self.createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	stack_ids = meta.get_stack_ids(self.protocol)
	if stack_ids:
            stack_id =  max(map(int, stack_ids))+1
        else:
            stack_id = 1	    
	
	panel = TubePanel(self.notebook, stack_id)
	self.notebook.AddPage(panel, 'Instance No: %s'%stack_id, True)  
	#Prevent users from clicking the 'Create Instance' button
	self.createTabBtn.Disable()	

##---------- Tube Instance Panel----------------##
class TubePanel(wx.Panel):
    '''
    Panel that displays the instance
    '''
    def __init__(self, parent, tab_number):

	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	self.sw = wx.ScrolledWindow(self)

	self.tab_number = tab_number
	fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
	
	self.tag_stump = 'ExptVessel|Tube'
	
	new_stack = True
	stack_ids = meta.get_stack_ids(self.tag_stump)
	rep_vessel_instance = None
	for stack_id in stack_ids:
	    if stack_id == self.tab_number:
		rep_vessel_instance = meta.get_rep_vessel_instance(self.tag_stump, stack_id) #Since all vessels for a given stack have same specifications, so single instance will be used to fill the information
	if rep_vessel_instance is not None:
	    new_stack = False

	self.mandatory_tags = [self.tag_stump+'|Number|%s'%rep_vessel_instance, self.tag_stump+'|StackName|%s'%rep_vessel_instance]
	
        # Heading
	text = wx.StaticText(self.sw, -1, 'Tube Specifications')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(text, 0)
	titlesizer.Add((10,-1))
	# CREATE button
	self.createBtn = wx.Button(self.sw, -1, label="Put Stack on Bench")
	self.createBtn.Bind(wx.EVT_BUTTON, self.onCreateStack)
	if new_stack is False:
	    self.createBtn.Disable()        
	titlesizer.Add(self.createBtn, 0, wx.EXPAND) 	
	
        # Vessel number
	numberTAG = self.tag_stump+'|Number|%s'%rep_vessel_instance
        self.vessnum = wx.Choice(self.sw, -1,  choices= map(str, range(1,51)), style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.vessnum.Enable() 
        else:
            self.vessnum.SetStringSelection(meta.get_field(numberTAG))
            self.vessnum.Disable()  
	self.labels[numberTAG] = wx.StaticText(self.sw, -1, 'Number of Tube in Stack')
	fgs.Add(self.labels[numberTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.vessnum, 0, wx.EXPAND)                
        # Group name
	nameTAG = self.tag_stump+'|StackName|%s'%rep_vessel_instance
        self.stkname= wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
        if new_stack is True:
            self.stkname.Enable()
        else:
            self.stkname.SetValue(meta.get_field(nameTAG))
            self.stkname.Disable()
	self.labels[nameTAG] = wx.StaticText(self.sw, -1, 'Stack Name')
        fgs.Add(self.labels[nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.stkname, 0, wx.EXPAND) 
	# Manufacturer
	mfgTAG = self.tag_stump+'|Manufacturer|%s'%rep_vessel_instance
	self.vessmfg = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vessmfg.Enable()
	else:
	    self.vessmfg.SetValue(meta.get_field(mfgTAG, default=''))
	    self.vessmfg.Disable()
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	fgs.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessmfg, 0, wx.EXPAND) 
	# Catalogue Number
	catnoTAG = self.tag_stump+'|CatalogueNo|%s'%rep_vessel_instance
	self.vesscat = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesscat.Enable()
	else:
	    self.vesscat.SetValue(meta.get_field(catnoTAG, default=''))
	    self.vesscat.Disable()
	self.labels[catnoTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	fgs.Add(self.labels[catnoTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscat, 0, wx.EXPAND) 	
	# Size
	sizeTAG = self.tag_stump+'|Size|%s'%rep_vessel_instance
	self.vesssize = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_PROCESS_ENTER)
	if new_stack is True:
	    self.vesssize.Enable()
	else:
	    self.vesssize.SetValue(meta.get_field(sizeTAG, default=''))
	    self.vesssize.Disable()
	self.labels[sizeTAG] = wx.StaticText(self.sw, -1, 'Size (cm2)')
	fgs.Add(self.labels[sizeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesssize, 0, wx.EXPAND)
        # Coating
	coatTAG = self.tag_stump+'|Coat|%s'%rep_vessel_instance
	choices=['None','Collagen IV','Gelatin','Poly-L-Lysine','Poly-D-Lysine', 'Fibronectin', 'Laminin','Poly-D-Lysine + Laminin', 'Poly-L-Ornithine+Laminin', 'Other']
	self.vesscoat = wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if new_stack is True:
	    self.vesscoat.Enable()
	else:	
	    self.vesscoat.Append(meta.get_field(coatTAG))
	    self.vesscoat.SetStringSelection(meta.get_field(coatTAG))
	    self.vesscoat.Disable()
	self.vesscoat.Bind(wx.EVT_LISTBOX, self.onSelectOther)
	self.labels[coatTAG] = wx.StaticText(self.sw, -1, 'Coating')
	fgs.Add(self.labels[coatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vesscoat, 0, wx.EXPAND)
	# Other Information
	otherTAG = self.tag_stump+'|OtherInfo|%s'%rep_vessel_instance
	self.vessother = wx.TextCtrl(self.sw, -1, value='', style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.vessother.SetInitialSize((-1,100))
	if new_stack is True:
	    self.vessother.Enable()
	else:
	    self.vessother.SetValue(meta.get_field(otherTAG, default=''))
	    self.vessother.Disable()
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other Information')
	fgs.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.vessother, 0, wx.EXPAND) 	
        
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	                           

	#---  Layout with sizers  -------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(fgs)
	self.sw.SetSizer(swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)
	
    def onSelectOther(self, event):
	if self.vesscoat.GetStringSelection() == 'Other':
	    other = wx.GetTextFromUser('Insert Other', 'Other')
	    self.vesscoat.Append(other)
	    self.vesscoat.SetStringSelection(other)	
    
    def onCreateStack(self, event):
	# Checks 
	if not self.vessnum.GetStringSelection():
	    dial = wx.MessageDialog(None, 'Please select the number of vessels', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	if not self.stkname.GetValue():
	    dial = wx.MessageDialog(None, 'Please select the Stack Name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	#vess_design = self.vessdesign.GetStringSelection()
	#if vess_design is None:
	    #dial = wx.MessageDialog(None, 'Please select the vessel design', 'Error', wx.OK | wx.ICON_ERROR)
	    #dial.ShowModal()  
	    #return	
	self.createBtn.Disable()
	
        vess_list = meta.get_field_instances(self.tag_stump)
        if vess_list:
            max_id =  max(map(int, vess_list))+1
        else:
            max_id = 1
	    
        for v_id in range(max_id, max_id+int(self.vessnum.GetStringSelection())):
            id = 'Tube%s'%(v_id)
            plate_design = (1,1)  # since flask is alwasys a sigle entity resembling to 1x1 well plate format   
            if id not in PlateDesign.get_plate_ids():
                PlateDesign.add_plate('Tube', str(v_id), plate_design, self.stkname.GetValue())
            else:
                PlateDesign.set_plate_format(id, plate_design)
        
            meta.set_field(self.tag_stump+'|StackNo|%s'%str(v_id),    self.tab_number, notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Number|%s'%str(v_id),     self.vessnum.GetStringSelection(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|StackName|%s'%str(v_id),  self.stkname.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Manufacturer|%s'%str(v_id),  self.vessmfg.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|CatalogueNo|%s'%str(v_id),  self.vesscat.GetValue(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|Size|%s'%str(v_id),       self.vesssize.GetValue(), notify_subscribers =False)
            meta.set_field(self.tag_stump+'|Coat|%s'%str(v_id),       self.vesscoat.GetStringSelection(), notify_subscribers =False)
	    meta.set_field(self.tag_stump+'|OtherInfo|%s'%str(v_id),  self.vessother.GetValue())
        
	#make all input fields disable
        self.vessnum.Disable()
	self.stkname.Disable()
	self.vessmfg.Disable()
	self.vesscat.Disable()
	self.vesssize.Disable()
	self.vesscoat.Disable()
	self.vessother.Disable()
	#Enable to create new instance
	self.GrandParent.createTabBtn.Enable()
         
########################################################################        
################## CELL SEEDING PANEL #########################
########################################################################
class CellSeedSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Transfer|Seed'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = CellSeedPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)       

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):	
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = CellSeedPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    
class CellSeedPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.celllineTAG = 'Sample|CellLine'
	self.mandatory_tags = [self.tag_stump+'|CellLineInstance|'+str(self.tab_number)]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	
	# Process
	self.token = 'Step'
	staticbox = wx.StaticBox(self.sw, -1, self.token)
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl',50, -1, '']),
		                              ('Description', ['TextCtrl', 100, -1, '']),
		                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
		                              ('Temp\n(C)', ['TextCtrl', 30, -1, '']),
		                              ('Tips', ['TextCtrl', 50, -1, ''])
		                            ])				
	self.procedure = RowBuilder(self.sw, self.protocol, self.token, COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	self.procedure.Disable()
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
        self.selectinstTAG = self.tag_stump+'|CellLineInstance|'+str(self.tab_number)
	self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value='', style=wx.TE_READONLY)  
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
	showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
	if meta.get_field(self.selectinstTAG) is not None: # seeded from the stock flask
	    self.settings_controls[self.selectinstTAG].SetValue(meta.get_cellLine_Name(self.tab_number, 'S'))
	    pic=wx.StaticBitmap(self.sw)
	    pic.SetBitmap(icons.stock.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    titlesizer.Add(pic)
	    titlesizer.AddSpacer((5,-1))	
	    titlesizer.Add(text, 0)
	    showInstBut.Enable()
	    self.procedure.Enable()
	elif meta.get_field(self.tag_stump+'|HarvestInstance|'+str(self.tab_number)) is not None:  # harvest-seed action
	    self.settings_controls[self.selectinstTAG].SetValue(meta.get_cellLine_Name(str(self.tab_number), 'HS'))
	    pic=wx.StaticBitmap(self.sw)
	    pic.SetBitmap(icons.seed.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    titlesizer.Add(pic)
	    titlesizer.AddSpacer((5,-1))	
	    titlesizer.Add(text, 0)		    
	    showInstBut.Disable()
	    self.procedure.Enable()
	else:
	    pic=wx.StaticBitmap(self.sw)
	    pic.SetBitmap(icons.stock.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    titlesizer.Add(pic)
	    titlesizer.AddSpacer((5,-1))	
	    titlesizer.Add(text, 0)
	    showInstBut.Enable()
	    self.procedure.Disable()	    
	self.settings_controls[self.selectinstTAG].SetToolTipString('Cell Line used')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Cell Line')
	attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
	attributesizer.Add(showInstBut, 0, wx.EXPAND)	
	
	seeddensityTAG = self.tag_stump+'|SeedingDensity|'+str(self.tab_number)
	seeddensity = meta.get_field(seeddensityTAG, [])
	self.settings_controls[seeddensityTAG+'|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(seeddensity) > 0:
	    self.settings_controls[seeddensityTAG+'|0'].SetValue(seeddensity[0])
	self.settings_controls[seeddensityTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[seeddensityTAG] = wx.StaticText(self.sw, -1, 'Density')
	attributesizer.Add(self.labels[seeddensityTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[seeddensityTAG+'|0'], 0, wx.EXPAND)
	unit_choices =['nM2', 'uM2', 'mM2','Other']
	self.settings_controls[seeddensityTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(seeddensity) > 1:
	    self.settings_controls[seeddensityTAG+'|1'].Append(seeddensity[1])
	    self.settings_controls[seeddensityTAG+'|1'].SetStringSelection(seeddensity[1])
	self.settings_controls[seeddensityTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	attributesizer.Add(self.settings_controls[seeddensityTAG+'|1'], 0, wx.EXPAND)	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event):     
        # link with the instrument instance
        attributes = meta.get_attribute_list(self.celllineTAG)       
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%exp.get_tag_event(self.celllineTAG), 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, self.celllineTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(meta.get_field(self.celllineTAG+'|Name|'+str(instance)))
		meta.set_field(self.selectinstTAG, str(instance))
		meta.setLabelColour(self.mandatory_tags, self.labels)
		self.procedure.Enable()
        dia.Destroy()   
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)




########################################################################        
################## CELL HARVEST PANEL #########################
########################################################################
class CellHarvestSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'Transfer|Harvest'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.protocol)):
	    panel = CellHarvestPanel(self.notebook, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)       

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.protocol)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return   	    
	
	panel = CellHarvestPanel(self.notebook, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)

class CellHarvestPanel(wx.Panel):
    def __init__(self, parent, page_counter):

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.page_counter = page_counter

        # Attach the scrolling option with the panel
        self.sw = wx.ScrolledWindow(self)
        # Attach a flexi sizer for the text controler and labels
        fgs = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	#------- Heading ---#
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.harvest.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	text = wx.StaticText(self.sw, -1, 'Harvest')
	font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	text.SetFont(font)
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)	

        cell_Line_instances = meta.get_field_instances('Sample|CellLine|Name|')
        cell_Line_choices = []
        for cell_Line_instance in cell_Line_instances:
            cell_Line_choices.append(meta.get_field('Sample|CellLine|Name|'+cell_Line_instance)+'_'+cell_Line_instance)
  
        #-- Cell Line selection ---#
        celllineselcTAG = 'Transfer|Harvest|CellLineInstance|'+str(self.page_counter)
        self.settings_controls[celllineselcTAG] = wx.Choice(self.sw, -1,  choices=cell_Line_choices)
        if meta.get_field(celllineselcTAG) is not None:
            self.settings_controls[celllineselcTAG].SetStringSelection(meta.get_field(celllineselcTAG))
        self.settings_controls[celllineselcTAG].Bind(wx.EVT_CHOICE, self.OnSavingData)
        self.settings_controls[celllineselcTAG].SetToolTipString('Cell Line used for harvesting')
        fgs.Add(wx.StaticText(self.sw, -1, 'Select Cell Line'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.settings_controls[celllineselcTAG], 0, wx.EXPAND)
	fgs.Add(wx.StaticText(self.sw, -1, ''), 0)

        # Harvesting Density
	harvestdensityTAG = 'Transfer|Harvest|HarvestingDensity|'+str(self.page_counter)
	harvestdensity = meta.get_field(harvestdensityTAG, [])
	self.settings_controls[harvestdensityTAG+'|0'] = wx.lib.masked.NumCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(harvestdensity) > 0:
	    self.settings_controls[harvestdensityTAG+'|0'].SetValue(harvestdensity[0])
	self.settings_controls[harvestdensityTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	fgs.Add(wx.StaticText(self.sw, -1, 'Density'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.settings_controls[harvestdensityTAG+'|0'], 0, wx.EXPAND)
	unit_choices =['nM2', 'uM2', 'mM2','Other']
	self.settings_controls[harvestdensityTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(harvestdensity) > 1:
	    self.settings_controls[harvestdensityTAG+'|1'].Append(harvestdensity[1])
	    self.settings_controls[harvestdensityTAG+'|1'].SetStringSelection(harvestdensity[1])
	self.settings_controls[harvestdensityTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	fgs.Add(self.settings_controls[harvestdensityTAG+'|1'], 0, wx.EXPAND)	

        #  Medium Addatives
        medaddTAG = 'Transfer|Harvest|MediumAddatives|'+str(self.page_counter)
        self.settings_controls[medaddTAG] = wx.TextCtrl(self.sw, value=meta.get_field(medaddTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[medaddTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[medaddTAG].SetToolTipString(meta.get_field(medaddTAG, default='Any medium addatives used with concentration, Glutamine'))
        fgs.Add(wx.StaticText(self.sw, -1, 'Medium Addatives'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs.Add(self.settings_controls[medaddTAG], 0, wx.EXPAND)
	fgs.Add(wx.StaticText(self.sw, -1, ''), 0)

        
        #---------------Layout with sizers---------------
	swsizer = wx.BoxSizer(wx.VERTICAL)
	swsizer.Add(titlesizer)
	swsizer.Add((-1,10))
	swsizer.Add(fgs)
	self.sw.SetSizer(swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)
	
	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND|wx.ALL, 5)

    def OnSavingData(self, event):
        ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	meta.saveData(ctrl, tag, self.settings_controls)



########################################################################        
################## CHEMICAL SETTING PANEL ###########################
########################################################################	    
class ChemicalSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Perturbation|Chemical'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = ChemicalAgentPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Library")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = ChemicalAgentPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)

    
    def onLoadTab(self, event):	
	dlg = wx.DirDialog(None, "Select the file containing library...",
                                    style=wx.DD_DEFAULT_STYLE)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    dirname = dlg.GetPath()
	    for file_path in glob.glob( os.path.join(dirname, '*.txt') ):
		##Check for empty file
		if os.stat(file_path)[6] == 0:
		    continue
		##Check for Settings Type
		if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		    continue
		next_tab_num = meta.get_new_protocol_id(self.tag_stump)	    
		if self.notebook.GetPageCount()+1 != int(next_tab_num):
		    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
		    dlg.ShowModal()
		    return 			
		meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
		panel = ChemicalAgentPanel(self.notebook, self.tag_stump, next_tab_num)
		self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
	
	

class ChemicalAgentPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Name|'+str(self.tab_number), self.tag_stump+'|PerturbConc|'+str(self.tab_number)]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+' Perturbation')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.treat.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	save_bmp = icons.save.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse.")	
	#self.save_btn = wx.Button(self.sw, -1, "Save Instance")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(self.save_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	# Additives
	staticbox = wx.StaticBox(self.sw, -1, "Additives")
	additivesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Additive', COLUMN_DETAILS, self.mandatory_tags)
	additivesizer.Add(self.additive, 0, wx.ALL, 5)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
        self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
        self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''), style=wx.TE_PROCESS_ENTER)
        self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Name')
	self.labels[self.nameTAG].SetToolTipString('Name of the Chemical agent used')
        attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	perturbconcTAG = self.tag_stump+'|PerturbConc|'+str(self.tab_number)
	conc = meta.get_field(perturbconcTAG, [])
	self.settings_controls[perturbconcTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(conc) > 0:
	    self.settings_controls[perturbconcTAG+'|0'].SetValue(conc[0])
	self.settings_controls[perturbconcTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[perturbconcTAG] = wx.StaticText(self.sw, -1, 'Perturbing Conc.')
	self.labels[perturbconcTAG].SetToolTipString('Concentration of chemical applied as VALUE-UNIT, if your unit is not available in the list please click Other')
	attributesizer.Add(self.labels[perturbconcTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[perturbconcTAG+'|0'], 0, wx.EXPAND)
	unit_choices =['uM', 'nM', 'mM', 'mg/L', 'uL/L', '%w/v', '%v/v','Other']
	self.settings_controls[perturbconcTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(conc) > 1:
	    self.settings_controls[perturbconcTAG+'|1'].Append(conc[1])
	    self.settings_controls[perturbconcTAG+'|1'].SetStringSelection(conc[1])
	self.settings_controls[perturbconcTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	attributesizer.Add(self.settings_controls[perturbconcTAG+'|1'], 0, wx.EXPAND)	

	stockconcTAG = self.tag_stump+'|StockConc|'+str(self.tab_number)
	conc = meta.get_field(stockconcTAG, [])
	self.settings_controls[stockconcTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(conc) > 0:
	    self.settings_controls[stockconcTAG+'|0'].SetValue(conc[0])
	self.settings_controls[stockconcTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[stockconcTAG] = wx.StaticText(self.sw, -1, 'Stock Conc.')
	self.labels[stockconcTAG].SetToolTipString('Stock concentration as VALUE-UNIT, if your unit is not available in the list please click Other')
	attributesizer.Add(self.labels[stockconcTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[stockconcTAG+'|0'], 0, wx.EXPAND)
	unit_choices =['uM', 'nM', 'mM', 'mg/L', 'uL/L', '%w/v', '%v/v','Other']
	self.settings_controls[stockconcTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(conc) > 1:
	    self.settings_controls[stockconcTAG+'|1'].Append(conc[1])
	    self.settings_controls[stockconcTAG+'|1'].SetStringSelection(conc[1])
	self.settings_controls[stockconcTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	attributesizer.Add(self.settings_controls[stockconcTAG+'|1'], 0, wx.EXPAND)	

        chemmfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
        self.settings_controls[chemmfgTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemmfgTAG, default=''), style=wx.TE_PROCESS_ENTER)
        self.settings_controls[chemmfgTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[chemmfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	self.labels[chemmfgTAG].SetToolTipString('Name of the Chemical agent Manufacturer')
        attributesizer.Add(self.labels[chemmfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemmfgTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        chemcatTAG = self.tag_stump+'|CatNum|'+str(self.tab_number)
        self.settings_controls[chemcatTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemcatTAG, default=''))
        self.settings_controls[chemcatTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[chemcatTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	self.labels[chemcatTAG].SetToolTipString('Name of the Chemical agent Catalogue Number')
        attributesizer.Add(self.labels[chemcatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemcatTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	storageTAG = self.tag_stump+'|Storage|'+str(self.tab_number)
	self.settings_controls[storageTAG] = wx.TextCtrl(self.sw, value=meta.get_field(storageTAG, default=''))
	self.settings_controls[storageTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[storageTAG] = wx.StaticText(self.sw, -1, 'Storage Info.')
	self.labels[storageTAG].SetToolTipString('Local storage information regarding the stock.')
	attributesizer.Add(self.labels[storageTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[storageTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	chemothTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[chemothTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemothTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[chemothTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[chemothTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[chemothTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[chemothTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemothTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	

	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(additivesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)     
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)    
	    



########################################################################        
################## BIOLOGICAL SETTING PANEL ###########################
########################################################################	    
class BiologicalSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Perturbation|Biological'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = BiologicalAgentPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	
	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = BiologicalAgentPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)


class BiologicalAgentPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+' Perturbation')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.dna.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	# RNAi sequence 
	staticbox = wx.StaticBox(self.sw, -1, "RNAi Sequence")
	rnaisizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Accession No.', ['TextCtrl', 70, -1, '']),
	                              ('Manufacturer', ['TextCtrl', 50, -1, '']),
	                              ('URL link.', ['TextCtrl', 70, -1, '']),
	                              ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.rnai = RowBuilder(self.sw, self.protocol, 'RNAi', COLUMN_DETAILS, self.mandatory_tags)
	rnaisizer.Add(self.rnai, 0, wx.ALL, 5)
	
	# Target sequence
	staticbox = wx.StaticBox(self.sw, -1, "Target Sequence")
	targetsizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Accession No.', ['TextCtrl', 70, -1, '']),
	                              ('Manufacturer', ['TextCtrl', 50, -1, '']),
                                      ('URL link.', ['TextCtrl', 70, -1, '']),
                                      ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.target = RowBuilder(self.sw, self.protocol, 'Target', COLUMN_DETAILS, self.mandatory_tags)
	targetsizer.Add(self.target, 0, wx.ALL, 5)	
	
	# Additives
	staticbox = wx.StaticBox(self.sw, -1, "Additives")
	additivesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Additive', COLUMN_DETAILS, self.mandatory_tags)
	additivesizer.Add(self.additive, 0, wx.ALL, 5)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	 

	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(rnaisizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(targetsizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(additivesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
			
    def OnSavingSettings(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags) is None:
	    dial = wx.MessageDialog(None, 'Please provide a chemical name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
				
	filename = meta.get_field(self.tag_stump+'|ChemName|%s'%str(self.tab_number))+'.txt'
	dlg = wx.FileDialog(None, message='Saving ...', 
                            defaultDir=os.getcwd(), defaultFile=filename, 
                            wildcard='.txt', 
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
	if dlg.ShowModal() == wx.ID_OK:
	    dirname=dlg.GetDirectory()
	    filename=dlg.GetFilename()
	    self.file_path = os.path.join(dirname, filename)
	    meta.save_settings(self.file_path, self.protocol)     
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)    
	    
########################################################################        
################## BIOLOGICAL SETTING PANEL ###########################
########################################################################	    
class PhysicalSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Perturbation|Physical'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = PhysicalAgentPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	
	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = PhysicalAgentPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)


class PhysicalAgentPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+' Perturbation')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.physical.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	# Material 
	staticbox = wx.StaticBox(self.sw, -1, "Material")
	materialsizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Manufacturer', ['TextCtrl', 70, -1, '']),
	                              ('Model', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.material = RowBuilder(self.sw, self.protocol, 'Material', COLUMN_DETAILS, self.mandatory_tags)
	materialsizer.Add(self.material, 0, wx.ALL, 5)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	 

	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(materialsizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
			
    def OnSavingSettings(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags) is None:
	    dial = wx.MessageDialog(None, 'Please provide a chemical name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
				
	filename = meta.get_field(self.tag_stump+'|ChemName|%s'%str(self.tab_number))+'.txt'
	dlg = wx.FileDialog(None, message='Saving ...', 
                            defaultDir=os.getcwd(), defaultFile=filename, 
                            wildcard='.txt', 
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
	if dlg.ShowModal() == wx.ID_OK:
	    dirname=dlg.GetDirectory()
	    filename=dlg.GetFilename()
	    self.file_path = os.path.join(dirname, filename)
	    meta.save_settings(self.file_path, self.protocol)     
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)    
	    
########################################################################        
################## ANTIBODY SETTING PANEL    ###########################
########################################################################
class ImmunoSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Labeling|Immuno'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = ImmunoPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = ImmunoPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = ImmunoPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)   


class ImmunoPanel(wx.Panel):    
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+'fluroscence Labeling')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.antibody.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	# Antibodies
	staticbox = wx.StaticBox(self.sw, -1, "Antibody")
	antibodysizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	self.antibody_columns = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Manufacturer', ['TextCtrl', 70, -1, '']),
                                      ('Catalogue No.', ['TextCtrl', 70, -1, '']),
                                      ('Species', ['ListBox', -1, 20, ['Homo Sapiens', 'Mus Musculus', 'Rattus Norvegicus', 'Other']]),
	                              ('Target', ['TextCtrl', 100, -1, '']),
	                              ('Tag', ['TextCtrl', 70, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Antibody', self.antibody_columns, self.mandatory_tags)
	antibodysizer.Add(self.additive, 0, wx.ALL, 5)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)
	
	self.urlTAG = self.tag_stump+'|URL|'+str(self.tab_number)
	self.settings_controls[self.urlTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(self.urlTAG, default=''))
	self.settings_controls[self.urlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[self.urlTAG] = wx.StaticText(self.sw, -1, 'Ref. URL')
	self.labels[self.urlTAG].SetToolTipString('Reference protocol URL')
	url_bmp = icons.url.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.goURLBtn = wx.BitmapButton(self.sw, -1, url_bmp)
	self.goURLBtn.SetToolTipString("Open webpage in browser")
	self.goURLBtn.Bind(wx.EVT_BUTTON, self.goURL)
	attributesizer.Add(self.labels[self.urlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.urlTAG], 0, wx.EXPAND)
	attributesizer.Add(self.goURLBtn, 0)	
	
	otherTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[otherTAG] = wx.TextCtrl(self.sw, value=meta.get_field(otherTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[otherTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[otherTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[otherTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(antibodysizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)

    def goURL(self, event):
	try:
	    webbrowser.open(self.settings_controls[self.urlTAG].GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return  
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)     
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls) 
	    
	    
########################################################################        
################## GENETIC REPORTER (PRIMER) SETTING PANEL #############
########################################################################
class GeneticSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Labeling|Genetic'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = GeneticPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = GeneticPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = GeneticPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True) 

class GeneticPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+' Reporter Labeling')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.primer.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	# Sequence
	staticbox = wx.StaticBox(self.sw, -1, "Sequence")
	sequencesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Accession No.', ['TextCtrl', 70, -1, '']),
	                              ('GC%', ['TextCtrl', 50, -1, '']),
                                      ('Sequence', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Sequence', COLUMN_DETAILS, self.mandatory_tags)
	sequencesizer.Add(self.additive, 0, wx.ALL, 5)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)
	
	self.urlTAG = self.tag_stump+'|URL|'+str(self.tab_number)
	self.settings_controls[self.urlTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(self.urlTAG, default=''))
	self.settings_controls[self.urlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[self.urlTAG] = wx.StaticText(self.sw, -1, 'Ref. URL')
	self.labels[self.urlTAG].SetToolTipString('Reference protocol URL')
	url_bmp = icons.url.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.goURLBtn = wx.BitmapButton(self.sw, -1, url_bmp)
	self.goURLBtn.SetToolTipString("Open webpage in browser")
	self.goURLBtn.Bind(wx.EVT_BUTTON, self.goURL)
	attributesizer.Add(self.labels[self.urlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.urlTAG], 0, wx.EXPAND)
	attributesizer.Add(self.goURLBtn, 0)	
	
	otherTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[otherTAG] = wx.TextCtrl(self.sw, value=meta.get_field(otherTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[otherTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[otherTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[otherTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(sequencesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)

    def goURL(self, event):
	try:
	    webbrowser.open(self.settings_controls[self.urlTAG].GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return  
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)      
	    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)     

            
########################################################################        
################## DYE SETTING PANEL      ###########################
########################################################################
class DyeSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Labeling|Dye'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = DyePanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = DyePanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = DyePanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)   
	    
	
class DyePanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|DyeName|'+str(self.tab_number), self.tag_stump+'|LabellingConc|'+str(self.tab_number)]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+' Labeling')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.stain.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	# Additives
	staticbox = wx.StaticBox(self.sw, -1, "Additives")
	additivesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Additive', COLUMN_DETAILS, self.mandatory_tags)
	additivesizer.Add(self.additive, 0, wx.ALL, 5)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse.")	
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)
	
	self.urlTAG = self.tag_stump+'|URL|'+str(self.tab_number)
	self.settings_controls[self.urlTAG] = wx.TextCtrl(self.sw,  value=meta.get_field(self.urlTAG, default=''))
	self.settings_controls[self.urlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[self.urlTAG] = wx.StaticText(self.sw, -1, 'Ref. URL')
	self.labels[self.urlTAG].SetToolTipString('Reference protocol URL')
	url_bmp = icons.url.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.goURLBtn = wx.BitmapButton(self.sw, -1, url_bmp)
	self.goURLBtn.SetToolTipString("Open webpage in browser.")	
	self.goURLBtn.Bind(wx.EVT_BUTTON, self.goURL)
	attributesizer.Add(self.labels[self.urlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.urlTAG], 0, wx.EXPAND)
	attributesizer.Add(self.goURLBtn, 0)	
	
	chemnamTAG = self.tag_stump+'|DyeName|'+str(self.tab_number)
        self.settings_controls[chemnamTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemnamTAG, default=''), style=wx.TE_PROCESS_ENTER)
        self.settings_controls[chemnamTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[chemnamTAG] = wx.StaticText(self.sw, -1, 'Name')
	self.labels[chemnamTAG].SetToolTipString('Name of the Chemical agent used')
        attributesizer.Add(self.labels[chemnamTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemnamTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	perturbconcTAG = self.tag_stump+'|LabellingConc|'+str(self.tab_number)
	conc = meta.get_field(perturbconcTAG, [])
	self.settings_controls[perturbconcTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(conc) > 0:
	    self.settings_controls[perturbconcTAG+'|0'].SetValue(conc[0])
	self.settings_controls[perturbconcTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[perturbconcTAG] = wx.StaticText(self.sw, -1, 'Labelling Conc.')
	self.labels[perturbconcTAG].SetToolTipString('Concentration of dye applied as VALUE-UNIT, if your unit is not available in the list please click Other')
	attributesizer.Add(self.labels[perturbconcTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[perturbconcTAG+'|0'], 0, wx.EXPAND)
	unit_choices =['uM', 'nM', 'mM', 'mg/L', 'uL/L', '%w/v', '%v/v','Other']
	self.settings_controls[perturbconcTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(conc) > 1:
	    self.settings_controls[perturbconcTAG+'|1'].Append(conc[1])
	    self.settings_controls[perturbconcTAG+'|1'].SetStringSelection(conc[1])
	self.settings_controls[perturbconcTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	attributesizer.Add(self.settings_controls[perturbconcTAG+'|1'], 0, wx.EXPAND)	

	stockconcTAG = self.tag_stump+'|StockConc|'+str(self.tab_number)
	conc = meta.get_field(stockconcTAG, [])
	self.settings_controls[stockconcTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER)
	if len(conc) > 0:
	    self.settings_controls[stockconcTAG+'|0'].SetValue(conc[0])
	self.settings_controls[stockconcTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[stockconcTAG] = wx.StaticText(self.sw, -1, 'Stock Conc.')
	self.labels[stockconcTAG].SetToolTipString('Stock concentration as VALUE-UNIT, if your unit is not available in the list please click Other')
	attributesizer.Add(self.labels[stockconcTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[stockconcTAG+'|0'], 0, wx.EXPAND)
	unit_choices =['uM', 'nM', 'mM', 'mg/L', 'uL/L', '%w/v', '%v/v','Other']
	self.settings_controls[stockconcTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (50,20), unit_choices, wx.LB_SINGLE)
	if len(conc) > 1:
	    self.settings_controls[stockconcTAG+'|1'].Append(conc[1])
	    self.settings_controls[stockconcTAG+'|1'].SetStringSelection(conc[1])
	self.settings_controls[stockconcTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	attributesizer.Add(self.settings_controls[stockconcTAG+'|1'], 0, wx.EXPAND)	

        chemmfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
        self.settings_controls[chemmfgTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemmfgTAG, default=''), style=wx.TE_PROCESS_ENTER)
        self.settings_controls[chemmfgTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[chemmfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	self.labels[chemmfgTAG].SetToolTipString('Name of the Chemical agent Manufacturer')
        attributesizer.Add(self.labels[chemmfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemmfgTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        chemcatTAG = self.tag_stump+'|CatNum|'+str(self.tab_number)
        self.settings_controls[chemcatTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemcatTAG, default=''))
        self.settings_controls[chemcatTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[chemcatTAG] = wx.StaticText(self.sw, -1, 'Catalogue Number')
	self.labels[chemcatTAG].SetToolTipString('Name of the Chemical agent Catalogue Number')
        attributesizer.Add(self.labels[chemcatTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemcatTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	storageTAG = self.tag_stump+'|Storage|'+str(self.tab_number)
	self.settings_controls[storageTAG] = wx.TextCtrl(self.sw, value=meta.get_field(storageTAG, default=''))
	self.settings_controls[storageTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[storageTAG] = wx.StaticText(self.sw, -1, 'Storage Info.')
	self.labels[storageTAG].SetToolTipString('Local storage information regarding the stock.')
	attributesizer.Add(self.labels[storageTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[storageTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	chemothTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[chemothTAG] = wx.TextCtrl(self.sw, value=meta.get_field(chemothTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[chemothTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[chemothTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[chemothTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[chemothTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[chemothTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(additivesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)

    def goURL(self, event):
	try:
	    webbrowser.open(self.settings_controls[self.urlTAG].GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return  
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
	
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)     
	    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls) 

        
######################################################       
#### DRYING SETTING PANEL     ########################
######################################################          
class DryingSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'InstProcess|Drying'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = DryingPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = DryingPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = DryingPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)   

class DryingPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Oven'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
	
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.drying.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
		
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.settings_controls[self.nameTAG].SetToolTipString('Type a unique name for identifying the setting:\n%s'%meta.get_field(self.nameTAG))
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	self.labels[self.nameTAG] = wx.StaticText(self.sw , -1,  'Settings Name')
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND) 
	attributesizer.Add(self.save_btn, 0)
	
        #-- Instance selection ---#
        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)        
        link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[self.selectinstTAG].SetToolTipString('Oven used for data acquisition')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Oven')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND) 
        attributesizer.Add(showInstBut, 0)
	
	#Gas Composition
	staticbox = wx.StaticBox(self.sw, -1, "Gas Composition")
	gascompsizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
                                    ('Composition', ['TextCtrl', 200, -1, ''])
                                    ])	
	gas_compose = RowBuilder(self.sw, self.protocol, 'Gas', COLUMN_DETAILS, self.mandatory_tags)
	gascompsizer.Add(gas_compose, 0, wx.ALL, 5)
	
	#Temp Profile
	staticbox = wx.StaticBox(self.sw, -1, "Temperature Gradient")
	tempprofilesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Temp\n(C)', ['TextCtrl', 50, -1, '']), 
                                    ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	temp_profile = RowBuilder(self.sw, self.protocol, 'Temperature', COLUMN_DETAILS, self.mandatory_tags)	
	tempprofilesizer.Add(temp_profile, 0, wx.ALL, 5)	
	
	#Humidity Profile
	staticbox = wx.StaticBox(self.sw, -1, "Humidity Gradient")
	humiditysizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Humidity', ['TextCtrl', 50, -1, '']), 
	                              ('Unit', ['TextCtrl', 50, -1, '']), 
	                              ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	humidity_profile = RowBuilder(self.sw, self.protocol, 'Humidity', COLUMN_DETAILS, self.mandatory_tags)	
	humiditysizer.Add(humidity_profile, 0, wx.ALL, 5)
	
	#Pressure Profile
	staticbox = wx.StaticBox(self.sw, -1, "Pressure Gradient")
	pressuresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Pressure', ['TextCtrl', 50, -1, '']), 
                                      ('Unit', ['TextCtrl', 50, -1, '']), 
                                      ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	pressure_profile = RowBuilder(self.sw, self.protocol, 'Pressure', COLUMN_DETAILS, self.mandatory_tags)	
	pressuresizer.Add(pressure_profile, 0, wx.ALL, 5)	
		
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
                                    ('Description', ['TextCtrl', 200, -1, '']),
                                    ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                    ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(gascompsizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(tempprofilesizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(humiditysizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(pressuresizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer,0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
	
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags) 	
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
    

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)



######################################################       
#### INCUBATION SETTING PANEL     ########################
######################################################          
class IncubationSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'InstProcess|Incubation'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = IncubationPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = IncubationPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = IncubationPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)   

class IncubationPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Incubator'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.incubator.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
		
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.settings_controls[self.nameTAG].SetToolTipString('Type a unique name for identifying the setting:\n%s'%meta.get_field(self.nameTAG))
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	self.labels[self.nameTAG] = wx.StaticText(self.sw , -1,  'Settings Name')
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND) 
	attributesizer.Add(self.save_btn, 0)
	
        #-- Instance selection ---#
        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)        
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[self.selectinstTAG].SetToolTipString('Incubator used..')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Incubator')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
        attributesizer.Add(showInstBut, 0)	
	
	#Gas Composition
	staticbox = wx.StaticBox(self.sw, -1, "Gas Composition")
	gascompsizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
                                    ('Composition', ['TextCtrl', 200, -1, ''])
                                    ])	
	gas_compose = RowBuilder(self.sw, self.protocol, 'Gas', COLUMN_DETAILS, self.mandatory_tags)
	gascompsizer.Add(gas_compose, 0, wx.ALL, 5)
	
	#Temp Profile
	staticbox = wx.StaticBox(self.sw, -1, "Temperature Gradient")
	tempprofilesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Temp\n(C)', ['TextCtrl', 50, -1, '']), 
                                    ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	temp_profile = RowBuilder(self.sw, self.protocol, 'Temperature', COLUMN_DETAILS, self.mandatory_tags)	
	tempprofilesizer.Add(temp_profile, 0, wx.ALL, 5)	
	
	#Humidity Profile
	staticbox = wx.StaticBox(self.sw, -1, "Humidity Gradient")
	humiditysizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Humidity', ['TextCtrl', 50, -1, '']), 
	                              ('Unit', ['TextCtrl', 50, -1, '']), 
	                              ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	humidity_profile = RowBuilder(self.sw, self.protocol, 'Humidity', COLUMN_DETAILS, self.mandatory_tags)	
	humiditysizer.Add(humidity_profile, 0, wx.ALL, 5)
	
	#Pressure Profile
	staticbox = wx.StaticBox(self.sw, -1, "Pressure Gradient")
	pressuresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Pressure', ['TextCtrl', 50, -1, '']), 
                                      ('Unit', ['TextCtrl', 50, -1, '']), 
                                      ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	pressure_profile = RowBuilder(self.sw, self.protocol, 'Pressure', COLUMN_DETAILS, self.mandatory_tags)	
	pressuresizer.Add(pressure_profile, 0, wx.ALL, 5)	
		
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
                                    ('Description', ['TextCtrl', 200, -1, '']),
                                    ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                    ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
	                            ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(gascompsizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(tempprofilesizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(humiditysizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(pressuresizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer,0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
	
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)     
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)  

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)

########################################################################        
################## CULTURE INITIATION SETTING PANEL        #############
########################################################################
class InitiationSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'AddProcess|Initiation'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = InitiationPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = InitiationPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = InitiationPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True) 

class InitiationPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	
        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, 'Culture %s'%exp.get_tag_event(tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.initiation.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	
	# Additives
	staticbox = wx.StaticBox(self.sw, -1, "Additives")
	additivesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Additive', COLUMN_DETAILS, self.mandatory_tags)
	additivesizer.Add(self.additive, 0, wx.ALL, 5)
		
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)	
	
	otherTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[otherTAG] = wx.TextCtrl(self.sw, value=meta.get_field(otherTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[otherTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[otherTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[otherTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(additivesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)

    def goURL(self, event):
	try:
	    webbrowser.open(self.settings_controls[self.urlTAG].GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return  
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list) 
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)      
	    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)
	    
########################################################################        
################## ADD MEDIUM SETTING PANEL                #############
########################################################################
class AddMediumSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'AddProcess|Medium'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = AddMediumPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = AddMediumPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = AddMediumPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True) 

class AddMediumPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	
        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump)+' Addition')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.medium.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	
	# Additives
	staticbox = wx.StaticBox(self.sw, -1, "Additives")
	additivesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
                                      ('Conc.', ['TextCtrl', 50, -1, '']),
                                      ('Description', ['TextCtrl', 200, -1, ''])
                                    ])		
	self.additive = RowBuilder(self.sw, self.protocol, 'Additive', COLUMN_DETAILS, self.mandatory_tags)
	additivesizer.Add(self.additive, 0, wx.ALL, 5)
		
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)	
	
	otherTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[otherTAG] = wx.TextCtrl(self.sw, value=meta.get_field(otherTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[otherTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[otherTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[otherTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(additivesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)

    def goURL(self, event):
	try:
	    webbrowser.open(self.settings_controls[self.urlTAG].GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return  
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list) 
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)      
	    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)     


########################################################################        
################## STORAGE SETTING PANEL                #############
########################################################################
class StorageSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'AddProcess|Storage'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = StoragePanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = StoragePanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = StoragePanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True) 

class StoragePanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	
        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.storage.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	
	#Storage	
	self.staticbox = wx.StaticBox(self.sw, -1, "Storage")
	self.staticbox_sizer = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
	
	self.ctypeSizer = wx.FlexGridSizer(cols=3, hgap=15, vgap=5)
	self.cool_box = wx.RadioButton(self.sw, -1, "CoolBox", style = wx.RB_GROUP )
	self.freezer = wx.RadioButton(self.sw, -1, "Freezer" )
	self.cool_box.SetValue(0)
	self.freezer.SetValue(0)
	self.ctypeSizer.Add(self.cool_box, 0)
	self.ctypeSizer.Add(self.freezer, 0)
	self.ctypeSizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	self.staticbox_sizer.Add(self.ctypeSizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
	self.staticbox_sizer.Add((-1,10))
    
	if meta.get_field(self.tag_stump+'|Type|'+str(self.tab_number)) is not None: 	
	    if meta.get_field(self.tag_stump+'|Type|'+str(self.tab_number)) == 'CoolBox':
		self.onShowCoolBox(event=meta.get_field(self.tag_stump+'|Type|'+str(self.tab_number)))
	    if meta.get_field(self.tag_stump+'|Type|'+str(self.tab_number)) == 'Freeze':
		self.onShowFreeze(event=meta.get_field(self.tag_stump+'|Type|'+str(self.tab_number)))
	else:	    
	    #self.cool_box.Bind(wx.EVT_RADIOBUTTON,self.onShowCoolBox)
	    self.freezer.Bind(wx.EVT_RADIOBUTTON, self.onShowFreeze)	

	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)	
	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(self.staticbox_sizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def onShowFreeze(self, event):
	self.freezer.SetValue(1)
	self.freezer.Enable(0)	
	self.cool_box.Enable(0)	
	
	meta.set_field(self.tag_stump+'|Type|'+str(self.tab_number), 'Freeze')	    
	fgs = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	# make
	# model
	# dimension
	# capacity
	# Refrigerant
	# Sample Location rack # block # 
	freeze_sizer = wx.BoxSizer(wx.VERTICAL)

	makeTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
	self.settings_controls[makeTAG] = wx.TextCtrl(self.sw, value=meta.get_field(makeTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[makeTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[makeTAG].SetToolTipString('Manufacturer of freeze')
	fgs.Add(wx.StaticText(self.sw, -1, 'Manufacturer'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.settings_controls[makeTAG], 0, wx.EXPAND)
	fgs.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	modelTAG = self.tag_stump+'|Model|'+str(self.tab_number)
	self.settings_controls[modelTAG] = wx.TextCtrl(self.sw, value=meta.get_field(modelTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[modelTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.settings_controls[makeTAG].SetToolTipString('Model number')
	fgs.Add(wx.StaticText(self.sw, -1, 'Model'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.settings_controls[modelTAG], 0, wx.EXPAND)
	fgs.Add(wx.StaticText(self.sw, -1, ''), 0)	

	dimensionTAG = self.tag_stump+'|Dimension|'+str(self.tab_number)
	dimn = meta.get_field(dimensionTAG, [])
	dimn_sizer = wx.BoxSizer(wx.HORIZONTAL)
	self.settings_controls[dimensionTAG+'|0'] = wx.TextCtrl(self.sw, size=(30,-1), style=wx.TE_PROCESS_ENTER)
	if len(dimn) > 0:
	    self.settings_controls[dimensionTAG+'|0'].SetValue(dimn[0])
	self.settings_controls[dimensionTAG+'|1'] = wx.TextCtrl(self.sw, size=(30,-1), style=wx.TE_PROCESS_ENTER)
	if len(dimn) > 1:
	    self.settings_controls[dimensionTAG+'|1'].SetValue(dimn[1])
	self.settings_controls[dimensionTAG+'|2'] = wx.TextCtrl(self.sw, size=(30,-1), style=wx.TE_PROCESS_ENTER)
	if len(dimn) > 2:
	    self.settings_controls[dimensionTAG+'|2'].SetValue(dimn[2])
	    
	dimn_sizer.Add(wx.StaticText(self.sw, -1, 'W'), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)    
	dimn_sizer.Add(self.settings_controls[dimensionTAG+'|0'], 0, wx.EXPAND)
	dimn_sizer.Add(wx.StaticText(self.sw, -1, 'H'), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
	dimn_sizer.Add(self.settings_controls[dimensionTAG+'|1'], 0, wx.EXPAND)
	dimn_sizer.Add(wx.StaticText(self.sw, -1, 'D'), 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
	dimn_sizer.Add(self.settings_controls[dimensionTAG+'|2'], 0, wx.EXPAND)

	fgs.Add(wx.StaticText(self.sw, -1, 'Dimension (cm)'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(dimn_sizer, 0, wx.EXPAND)
	fgs.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	self.settings_controls[dimensionTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[dimensionTAG+'|1'].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[dimensionTAG+'|2'].Bind(wx.EVT_TEXT, self.OnSavingData)
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Sample Placement")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Sample', ['TextCtrl', 100, -1, '']),
                                      ('Rack No.', ['TextCtrl', 30, -1, '']),
                                      ('Location', ['TextCtrl', 30, -1, '']),
                                      ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Placement', COLUMN_DETAILS, self.mandatory_tags)
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)
		
	    
	#--- Sizers -------
	freeze_sizer.Add(fgs, 0)
	freeze_sizer.Add(proceduresizer, 0)
	self.staticbox_sizer.Add(freeze_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0) 
	self.sw.FitInside()

    def goURL(self, event):
	try:
	    webbrowser.open(self.settings_controls[self.urlTAG].GetValue())
	except:
	    dial = wx.MessageDialog(None, 'Unable to launch internet browser', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return  
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list) 
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)      
	    
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)     

########################################################################        
################## WASH SETTING PANEL                      #############
########################################################################
class WashSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'AddProcess|Wash'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = WashPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = WashPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = WashPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True) 

class WashPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	
        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = []
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title & Save button
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.wash.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
			
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),
	                              ('Description', ['TextCtrl', 200, -1, '']),
	                              ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
	                              ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Attributes
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''))
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.labels[self.nameTAG] = wx.StaticText(self.sw, -1, 'Protocol Name')
	self.labels[self.nameTAG].SetToolTipString('Type a unique name for identifying the protocol')
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND)
	attributesizer.Add(self.save_btn, 0)	
	
	otherTAG = self.tag_stump+'|Other|'+str(self.tab_number)
        self.settings_controls[otherTAG] = wx.TextCtrl(self.sw, value=meta.get_field(otherTAG, default=''), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.settings_controls[otherTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[otherTAG] = wx.StaticText(self.sw, -1, 'Other informaiton')
	self.labels[otherTAG].SetToolTipString('Other relevant information')
        attributesizer.Add(self.labels[otherTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[otherTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
			
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)     
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)  


########################################################################        
################## INCUBATOR SETTING PANEL    ###########################
########################################################################            
class IncubatorSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Instrument|Incubator'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = IncubatorPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)   

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = IncubatorPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    

	
        
class IncubatorPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	 
	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	
	# TAG
	self.tab_number = tab_number	# tab or instance number
	self.tag_stump = tag_stump                  # first two parts of tag (type|event) e.g Instrument|Centrifuge
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Manufacturer|'+str(self.tab_number)]        # mandatory fields 
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)	
	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	mfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
	self.settings_controls[mfgTAG] = wx.TextCtrl(self.sw, name='Manufacturer' ,  value=meta.get_field(mfgTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[mfgTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	self.labels[mfgTAG].SetToolTipString('Manufacturer name')
	attributesizer.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[mfgTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	modelTAG = self.tag_stump+'|Model|'+str(self.tab_number)
	self.settings_controls[modelTAG] = wx.TextCtrl(self.sw, value=meta.get_field(modelTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[modelTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[modelTAG] = wx.StaticText(self.sw , -1,  'Model number')
	self.labels[modelTAG].SetToolTipString('Model number')
	attributesizer.Add(self.labels[modelTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[modelTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	capacityTAG = self.tag_stump+'|Capacity|'+str(self.tab_number)
	self.settings_controls[capacityTAG] = wx.TextCtrl(self.sw, value=meta.get_field(capacityTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[capacityTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[capacityTAG] = wx.StaticText(self.sw , -1,  'Capacity')
	self.labels[capacityTAG].SetToolTipString('Capacity (L) of the incubator')
	attributesizer.Add(self.labels[capacityTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[capacityTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	

	staticbox = wx.StaticBox(self.sw, -1, "Instrument Information")			
	attribute_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	attribute_Sizer.Add(attributesizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )		

	# ==== Local  ====
	localsizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	nickTAG = self.tag_stump+'|NickName|'+str(self.tab_number)
	self.settings_controls[nickTAG] = wx.TextCtrl(self.sw, name='Nick Name' ,  value=meta.get_field(nickTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[nickTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[nickTAG] = wx.StaticText(self.sw, -1, 'Nick Name')
	self.labels[nickTAG].SetToolTipString('Nick Name of the instrument')
	localsizer.Add(self.labels[nickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[nickTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	srlTAG = self.tag_stump+'|SerialNo|'+str(self.tab_number)
	self.settings_controls[srlTAG] = wx.TextCtrl(self.sw, name='Serial Number' ,  value=meta.get_field(srlTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[srlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[srlTAG] = wx.StaticText(self.sw, -1, 'Serial Number')
	self.labels[srlTAG].SetToolTipString('Serial Number')
	localsizer.Add(self.labels[srlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[srlTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	adrsTAG = self.tag_stump+'|Address|'+str(self.tab_number)
	self.settings_controls[adrsTAG] = wx.TextCtrl(self.sw, name='Address' ,  value=meta.get_field(adrsTAG, default=''), size=(-1, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.settings_controls[adrsTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[adrsTAG] = wx.StaticText(self.sw, -1, 'Address')
	self.labels[adrsTAG].SetToolTipString('Address where of the instrument location')
	localsizer.Add(self.labels[adrsTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[adrsTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	roomTAG = self.tag_stump+'|Room|'+str(self.tab_number)
	self.settings_controls[roomTAG] = wx.TextCtrl(self.sw, name='Room' ,  value=meta.get_field(roomTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[roomTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[roomTAG] = wx.StaticText(self.sw, -1, 'Room Number')
	self.labels[roomTAG].SetToolTipString('Room where of the instrument location')
	localsizer.Add(self.labels[roomTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[roomTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	staticbox = wx.StaticBox(self.sw, -1, "Local Information")			
	local_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	local_Sizer.Add(localsizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)
		
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attribute_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(local_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer) 
	
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)  
	    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
		
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)

########################################################################        
################## RHEOMETER SETTING PANEL    ###########################
########################################################################            
class RheometerSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Instrument|Rheometer'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = RheometerPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)
      

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = RheometerPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    

        
class RheometerPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	 
	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	
	# TAG
	self.tab_number = tab_number	# tab or instance number
	self.tag_stump = tag_stump                  # first two parts of tag (type|event) e.g Instrument|Centrifuge
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Manufacturer|'+str(self.tab_number)]        # mandatory fields 
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	mfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
	self.settings_controls[mfgTAG] = wx.TextCtrl(self.sw, name='Manufacturer' ,  value=meta.get_field(mfgTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[mfgTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	self.labels[mfgTAG].SetToolTipString('Manufacturer name')
	attributesizer.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[mfgTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	modelTAG = self.tag_stump+'|Model|'+str(self.tab_number)
	self.settings_controls[modelTAG] = wx.TextCtrl(self.sw, value=meta.get_field(modelTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[modelTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[modelTAG] = wx.StaticText(self.sw , -1,  'Model')
	self.labels[modelTAG].SetToolTipString('Model number')
	attributesizer.Add(self.labels[modelTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[modelTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	capacityTAG = self.tag_stump+'|Capacity|'+str(self.tab_number)
	self.settings_controls[capacityTAG] = wx.TextCtrl(self.sw, value=meta.get_field(capacityTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[capacityTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[capacityTAG] = wx.StaticText(self.sw , -1,  'Capacity')
	self.labels[capacityTAG].SetToolTipString('Capacity (L) of the oven')
	attributesizer.Add(self.labels[capacityTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[capacityTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	

	staticbox = wx.StaticBox(self.sw, -1, "Instrument Information")			
	attribute_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	attribute_Sizer.Add(attributesizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )		

	# ==== Local  ====
	localsizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	nickTAG = self.tag_stump+'|NickName|'+str(self.tab_number)
	self.settings_controls[nickTAG] = wx.TextCtrl(self.sw, name='Nick Name' ,  value=meta.get_field(nickTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[nickTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[nickTAG] = wx.StaticText(self.sw, -1, 'Nick Name')
	self.labels[nickTAG].SetToolTipString('Nick Name of the instrument')
	localsizer.Add(self.labels[nickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[nickTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	srlTAG = self.tag_stump+'|SerialNo|'+str(self.tab_number)
	self.settings_controls[srlTAG] = wx.TextCtrl(self.sw, name='Serial Number' ,  value=meta.get_field(srlTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[srlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[srlTAG] = wx.StaticText(self.sw, -1, 'Serial Number')
	self.labels[srlTAG].SetToolTipString('Serial Number')
	localsizer.Add(self.labels[srlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[srlTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	adrsTAG = self.tag_stump+'|Address|'+str(self.tab_number)
	self.settings_controls[adrsTAG] = wx.TextCtrl(self.sw, name='Address' ,  value=meta.get_field(adrsTAG, default=''), size=(-1, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.settings_controls[adrsTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[adrsTAG] = wx.StaticText(self.sw, -1, 'Address')
	self.labels[adrsTAG].SetToolTipString('Address where of the instrument location')
	localsizer.Add(self.labels[adrsTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[adrsTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	roomTAG = self.tag_stump+'|Room|'+str(self.tab_number)
	self.settings_controls[roomTAG] = wx.TextCtrl(self.sw, name='Room' ,  value=meta.get_field(roomTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[roomTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[roomTAG] = wx.StaticText(self.sw, -1, 'Room Number')
	self.labels[roomTAG].SetToolTipString('Room where of the instrument location')
	localsizer.Add(self.labels[roomTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[roomTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	staticbox = wx.StaticBox(self.sw, -1, "Local Information")			
	local_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	local_Sizer.Add(localsizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)
	#Geometry	
	self.geometry_staticbox = wx.StaticBox(self.sw, -1, "Geometry")
	self.geometrysizer = wx.StaticBoxSizer(self.geometry_staticbox, wx.VERTICAL)
	
	self.ctypeSizer = wx.FlexGridSizer(cols=3, hgap=15, vgap=5)
	self.par_plate = wx.RadioButton(self.sw, -1, "Parallel", style = wx.RB_GROUP )
	self.cone_plate = wx.RadioButton(self.sw, -1, "Cone" )
	self.par_plate.SetValue(0)
	self.cone_plate.SetValue(0)
	self.ctypeSizer.Add(self.par_plate, 0)
	self.ctypeSizer.Add(self.cone_plate, 0)
	self.ctypeSizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	self.geometrysizer.Add(self.ctypeSizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
	self.geometrysizer.Add((-1,10))
    
	if meta.get_field(self.tag_stump+'|GeometryType|'+str(self.tab_number)) is not None: 	
	    self.onShowGeometry(event=meta.get_field(self.tag_stump+'|GeometryType|'+str(self.tab_number)))
	else:	    
	    self.par_plate.Bind(wx.EVT_RADIOBUTTON, self.onShowGeometry)
	    self.cone_plate.Bind(wx.EVT_RADIOBUTTON, self.onShowGeometry)	
	    
	#Gas	
	staticbox = wx.StaticBox(self.sw, -1, "Gas")
	self.gassizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
	                            ('Composition', ['TextCtrl', 200, -1, ''])
	                            ])	
	gas_supply = RowBuilder(self.sw, self.protocol, 'Gas', COLUMN_DETAILS, self.mandatory_tags)
	self.gassizer.Add(gas_supply, 1, wx.EXPAND|wx.ALL, 5)

	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attribute_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(local_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(self.geometrysizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(self.gassizer,0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer) 
	
    def onShowGeometry(self, event):
	if isinstance(event, str):
	    plate_type = event
	else:
	    plate_button = event.GetEventObject()
	    plate_type = plate_button.GetLabel()
	    
	fgs = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	    
	diaTAG = self.tag_stump+'|GeometryDiameter|'+str(self.tab_number)
	dia = meta.get_field(diaTAG, [])
	self.settings_controls[diaTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT)
	if len(dia) > 0:
	    self.settings_controls[diaTAG+'|0'].SetValue(dia[0])
	self.settings_controls[diaTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	unit_choices =['mm', 'cm', 'uM','Other']
	self.settings_controls[diaTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (-1,20), unit_choices, wx.LB_SINGLE)
	if len(dia) > 1:
	    self.settings_controls[diaTAG+'|1'].Append(dia[1])
	    self.settings_controls[diaTAG+'|1'].SetStringSelection(dia[1])
	self.settings_controls[diaTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	fgs.Add(wx.StaticText(self.sw, -1, 'Diameter'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.settings_controls[diaTAG+'|0'], 0, wx.EXPAND)	    
	fgs.Add(self.settings_controls[diaTAG+'|1'], 0, wx.EXPAND)	
	
	materialTAG = self.tag_stump+'|GeometryMaterial|'+str(self.tab_number)
	material_choices =['Aluminium', 'Stainless Steel', 'Acrylic', 'Other']
	self.settings_controls[materialTAG]= wx.ListBox(self.sw, -1, wx.DefaultPosition, (-1,30), material_choices, wx.LB_SINGLE)
	if meta.get_field(materialTAG) is not None:
	    self.settings_controls[materialTAG].Append(meta.get_field(materialTAG))
	    self.settings_controls[materialTAG].SetStringSelection(meta.get_field(materialTAG))
	self.settings_controls[materialTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)   
	self.settings_controls[materialTAG].SetToolTipString('Material type')
	fgs.Add(wx.StaticText(self.sw, -1, 'Material'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	fgs.Add(self.settings_controls[materialTAG], 0, wx.EXPAND)
	fgs.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	if plate_type == 'Parallel':
	    self.par_plate.SetValue(1)
	    meta.set_field(self.tag_stump+'|GeometryType|'+str(self.tab_number), 'Parallel')	

	    gapTAG = self.tag_stump+'|GeometryGap|'+str(self.tab_number)
	    gap = meta.get_field(gapTAG, [])
	    self.settings_controls[gapTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT)
	    if len(gap) > 0:
		self.settings_controls[gapTAG+'|0'].SetValue(gap[0])
	    self.settings_controls[gapTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    unit_choices =['radians', 'degree', 'Other']
	    self.settings_controls[gapTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (-1,20), unit_choices, wx.LB_SINGLE)
	    if len(gap) > 1:
		self.settings_controls[gapTAG+'|1'].Append(gap[1])
		self.settings_controls[gapTAG+'|1'].SetStringSelection(gap[1])
	    self.settings_controls[gapTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    fgs.Add(wx.StaticText(self.sw, -1, 'Gap'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    fgs.Add(self.settings_controls[gapTAG+'|0'], 0, wx.EXPAND)	    
	    fgs.Add(self.settings_controls[gapTAG+'|1'], 0, wx.EXPAND)
	    
	if plate_type == 'Cone':
	    self.cone_plate.SetValue(1)
	    meta.set_field(self.tag_stump+'|GeometryType|'+str(self.tab_number), 'Cone')	
	    
	    angelTAG = self.tag_stump+'|GeometryAngel|'+str(self.tab_number)
	    angel = meta.get_field(angelTAG, [])
	    self.settings_controls[angelTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT)
	    if len(angel) > 0:
		self.settings_controls[angelTAG+'|0'].SetValue(angel[0])
	    self.settings_controls[angelTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    unit_choices =['radiant', 'degree', 'Other']
	    self.settings_controls[angelTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (-1,20), unit_choices, wx.LB_SINGLE)
	    if len(angel) > 1:
		self.settings_controls[angelTAG+'|1'].Append(angel[1])
		self.settings_controls[angelTAG+'|1'].SetStringSelection(angel[1])
	    self.settings_controls[angelTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    fgs.Add(wx.StaticText(self.sw, -1, 'Angel'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    fgs.Add(self.settings_controls[angelTAG+'|0'], 0, wx.EXPAND)	    
	    fgs.Add(self.settings_controls[angelTAG+'|1'], 0, wx.EXPAND)	 
	    
	    trctTAG = self.tag_stump+'|GeometryTurncate|'+str(self.tab_number)
	    trct = meta.get_field(trctTAG, [])
	    self.settings_controls[trctTAG+'|0'] = wx.TextCtrl(self.sw, size=(20,-1), style=wx.TE_PROCESS_ENTER|wx.TE_RIGHT)
	    if len(trct) > 0:
		self.settings_controls[trctTAG+'|0'].SetValue(trct[0])
	    self.settings_controls[trctTAG+'|0'].Bind(wx.EVT_TEXT, self.OnSavingData)
	    unit_choices =['uM', 'mm', 'cm', 'Other']
	    self.settings_controls[trctTAG+'|1'] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (-1,20), unit_choices, wx.LB_SINGLE)
	    if len(trct) > 1:
		self.settings_controls[trctTAG+'|1'].Append(trct[1])
		self.settings_controls[trctTAG+'|1'].SetStringSelection(trct[1])
	    self.settings_controls[trctTAG+'|1'].Bind(wx.EVT_LISTBOX, self.OnSavingData)
	    fgs.Add(wx.StaticText(self.sw, -1, 'Turncation'), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	    fgs.Add(self.settings_controls[trctTAG+'|0'], 0, wx.EXPAND)	    
	    fgs.Add(self.settings_controls[trctTAG+'|1'], 0, wx.EXPAND)	    
	    
	self.par_plate.Enable(0)
	self.cone_plate.Enable(0)	
	    
	#--- Sizers -------
	self.geometrysizer.Add(fgs, 0, wx.ALIGN_LEFT|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0) 
	self.sw.FitInside()

    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)  
	    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
		
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)

########################################################################        
#### RHEOLOGICAL MANIPULATION SETTING PANEL     ########################
########################################################################            
class RheoManipulationSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag = 'InstProcess|RheoManipulation'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag)):
	    panel = RheoManipulationPanel(self.notebook, self.tag, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)       

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag)
	panel = RheoManipulationPanel(self.notebook, self.tag, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)

class RheoManipulationPanel(wx.Panel):
    def __init__(self, parent, tag, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Rheometer'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, 'Rheological Manipulation')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.rheometer.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())		
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
        #-- Instance selection ---#
        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)           
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind(wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Rheometer')
        self.labels[self.selectinstTAG].SetToolTipString('Rheometer used for data acquisition')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
        attributesizer.Add(showInstBut, 0, wx.EXPAND)	
	
	#Gel Composition
	staticbox = wx.StaticBox(self.sw, -1, "Gel Composition")
	gelcompsizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Component', ['TextCtrl', 100, -1, '']), 
                                    ('Volume', ['TextCtrl', 50, -1, '']),
                                    ('Concentration', ['TextCtrl', 50, -1, ''])
                                    ])	
	gel_compose = RowBuilder(self.sw, self.protocol, 'GelComposition', COLUMN_DETAILS, self.mandatory_tags)
	gelcompsizer.Add(gel_compose, 0, wx.ALL, 5)
	
	# Gel Profile
	staticbox = wx.StaticBox(self.sw, -1, "Gel Profile")
	gelprofilesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('Temp\n(C)', ['TextCtrl', 50, -1, '']), 
                                    ('Duration\n(Min)', ['TextCtrl', 50, -1, '']),
                                    ])	
	gel_profile = RowBuilder(self.sw, self.protocol, 'GelProfile', COLUMN_DETAILS, self.mandatory_tags)	
	gelprofilesizer.Add(gel_profile, 0, wx.ALL, 5)	
		
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
                                    ('Description', ['TextCtrl', 200, -1, '']),
                                    ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                    ('Oscillation\nAmplitude\n(%)', ['TextCtrl', 30, -1, '']),
                                    ('Oscillation\nFrequency\n(Hz)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)			
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(gelcompsizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(gelprofilesizer,0,wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer,0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)

    def OnSavingData(self, event):
        ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	meta.saveData(ctrl, tag, self.settings_controls)


########################################################################        
################## RHEOLOGY SETTING PANEL    ###########################
########################################################################            
class RHESettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag = 'DataAcquis|RHE'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag)):
	    panel = RHEPanel(self.notebook, self.tag, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)       

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag)
	panel = RHEPanel(self.notebook, self.tag, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)

class RHEPanel(wx.Panel):
    def __init__(self, parent, tag, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag = tag
	self.protocol = self.tag+'|'+str(self.tab_number)
	self.instrument_used = 'Rheometer'
	self.mandatory_tags = [self.tag+'|%sInstance|%s' %(self.instrument_used, str(self.tab_number))]
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, 'Rheological Measurement')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.rhe.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)	
	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)	
        #-- Instance selection ---#
        self.selectinstTAG = self.tag+'|%sInstance|%s' %(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)            
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Rheometer')
        self.labels[self.selectinstTAG].SetToolTipString('Rheometer used for data acquisition')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
        attributesizer.Add(showInstBut, 0)
	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']), 
                                    ('Description', ['TextCtrl', 200, -1, '']),
                                    ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                    ('Oscillation\nAmplitude\n(%)', ['TextCtrl', 30, -1, '']),
                                    ('Oscillation\nFrequency\n(Hz)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)	
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer, 0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
	
    def OnShowFileContainer(self, event):
	    dia = FileListDialog(self, self.tag, selection_mode = False)
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.drop_target.filelist
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
		    self.propfiles.SetStrings(f_list)    

    def OnSavingData(self, event):
        ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	meta.saveData(ctrl, tag, self.settings_controls)
        
########################################################################        
################## CENTRIFUGE SETTING PANEL    ###########################
########################################################################            
class CentrifugeSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Instrument|Centrifuge'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = CentrifugePanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)   

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = CentrifugePanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    
	
        
class CentrifugePanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	 
	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	
	# TAG
	self.tab_number = tab_number	# tab or instance number
	self.tag_stump = tag_stump                  # first two parts of tag (type|event) e.g Instrument|Centrifuge
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Manufacturer|'+str(self.tab_number)]        # mandatory fields 
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)	
	# Attributes	
	
	# ==== Instrument  ====
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	mfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
	self.settings_controls[mfgTAG] = wx.TextCtrl(self.sw, name='Manufacturer' ,  value=meta.get_field(mfgTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[mfgTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	self.labels[mfgTAG].SetToolTipString('Manufacturer name')
	attributesizer.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[mfgTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	modelTAG = self.tag_stump+'|Model|'+str(self.tab_number)
	self.settings_controls[modelTAG] = wx.TextCtrl(self.sw, value=meta.get_field(modelTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[modelTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[modelTAG] = wx.StaticText(self.sw , -1,  'Model')
	self.labels[modelTAG].SetToolTipString('Model number of the Centrifuge')
	attributesizer.Add(self.labels[modelTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[modelTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	typeTAG = self.tag_stump+'|Type|'+str(self.tab_number)
	choices = ['Ultracentrifuges', 'Haematocrit', 'Gas centrifuges', 'Other']
	self.settings_controls[typeTAG] = wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), choices, wx.LB_SINGLE)
	if meta.get_field(typeTAG) is not None:
	    self.settings_controls[typeTAG].Append(meta.get_field(typeTAG))
	    self.settings_controls[typeTAG].SetStringSelection(meta.get_field(typeTAG))
	self.settings_controls[typeTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)	    
	self.labels[typeTAG] = wx.StaticText(self.sw , -1,  'Type')
	self.labels[typeTAG].SetToolTipString('Type of the Centrifuge')
	attributesizer.Add(self.labels[typeTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[typeTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	staticbox = wx.StaticBox(self.sw, -1, "Instrument Information")			
	attribute_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	attribute_Sizer.Add(attributesizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )		

	# ==== Local  ====
	localsizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	nickTAG = self.tag_stump+'|NickName|'+str(self.tab_number)
	self.settings_controls[nickTAG] = wx.TextCtrl(self.sw, name='Nick Name' ,  value=meta.get_field(nickTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[nickTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[nickTAG] = wx.StaticText(self.sw, -1, 'Nick Name')
	self.labels[nickTAG].SetToolTipString('Nick Name of the instrument')
	localsizer.Add(self.labels[nickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[nickTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	srlTAG = self.tag_stump+'|SerialNo|'+str(self.tab_number)
	self.settings_controls[srlTAG] = wx.TextCtrl(self.sw, name='Serial Number' ,  value=meta.get_field(srlTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[srlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[srlTAG] = wx.StaticText(self.sw, -1, 'Serial Number')
	self.labels[srlTAG].SetToolTipString('Serial Number')
	localsizer.Add(self.labels[srlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[srlTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	adrsTAG = self.tag_stump+'|Address|'+str(self.tab_number)
	self.settings_controls[adrsTAG] = wx.TextCtrl(self.sw, name='Address' ,  value=meta.get_field(adrsTAG, default=''), size=(-1, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.settings_controls[adrsTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[adrsTAG] = wx.StaticText(self.sw, -1, 'Address')
	self.labels[adrsTAG].SetToolTipString('Address where of the instrument location')
	localsizer.Add(self.labels[adrsTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[adrsTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	roomTAG = self.tag_stump+'|Room|'+str(self.tab_number)
	self.settings_controls[roomTAG] = wx.TextCtrl(self.sw, name='Room' ,  value=meta.get_field(roomTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[roomTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[roomTAG] = wx.StaticText(self.sw, -1, 'Room Number')
	self.labels[roomTAG].SetToolTipString('Room where of the instrument location')
	localsizer.Add(self.labels[roomTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[roomTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	staticbox = wx.StaticBox(self.sw, -1, "Local Information")			
	local_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	local_Sizer.Add(localsizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)
		
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attribute_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(local_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer) 
	
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)  
	    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
		
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)
	


######################################################       
#### CENTRIFUGATION SETTING PANEL     ########################
######################################################          
class CentrifugationSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'InstProcess|Centrifugation'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = CentrifugationPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)    
	loadTabBtn = wx.Button(self, label="Load Instance")
	loadTabBtn.Bind(wx.EVT_BUTTON, self.onLoadTab)  	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	btnSizer.Add(loadTabBtn, 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = CentrifugationPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 
    def onLoadTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not load the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 
	
	dlg = wx.FileDialog(None, "Select the file containing settings...",
                                    defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
	# read the supp protocol file and setup a new tab
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    file_path = os.path.join(dirname, filename)
	    #Check for empty file
	    if os.stat(file_path)[6] == 0:
		dial = wx.MessageDialog(None, 'Settings file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return	
	    #Check for Settings Type:	
	    if open(file_path).readline().rstrip() != exp.get_tag_event(self.tag_stump):
		dial = wx.MessageDialog(None, 'The file is not %s settings!!'%exp.get_tag_event(self.tag_stump), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return		    
	    
	    meta.load_settings(file_path, self.tag_stump+'|%s'%str(next_tab_num))  
	    panel = CentrifugationPanel(self.notebook, self.tag_stump, next_tab_num)
	    self.notebook.AddPage(panel, 'Instance No: %s'%str(next_tab_num), True)   

class CentrifugationPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Centrifuge'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.spin.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic, 0)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
		
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
	
	self.nameTAG = self.tag_stump+'|Name|'+str(self.tab_number)
	self.settings_controls[self.nameTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.nameTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[self.nameTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.settings_controls[self.nameTAG].SetInitialSize((250,20))
	self.settings_controls[self.nameTAG].SetToolTipString('Type a unique name for identifying the setting:\n%s'%meta.get_field(self.nameTAG))
	save_bmp = icons.save.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	self.save_btn = wx.BitmapButton(self.sw, -1, save_bmp)
	self.save_btn.SetToolTipString("Save instance for future reuse")
	self.save_btn.Bind(wx.EVT_BUTTON, self.OnSavingSettings)
	self.labels[self.nameTAG] = wx.StaticText(self.sw , -1,  'Settings Name')
	attributesizer.Add(self.labels[self.nameTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[self.nameTAG], 0, wx.EXPAND) 
	attributesizer.Add(self.save_btn, 0) 
	
        #-- Instance selection ---#
        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)        
        link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[self.selectinstTAG].SetToolTipString('Oven used for data acquisition')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Centrifuge')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND) 
        attributesizer.Add(showInstBut, 0) 
	
	#RPM profile
	staticbox = wx.StaticBox(self.sw, -1, "RPM Profile")
	rpmprofilesizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	COLUMN_DETAILS = OrderedDict([('RPM', ['TextCtrl', 50, -1, '']), 
                                    ('Duration\n(Min)', ['TextCtrl', 50, -1, ''])
                                    ])	
	rpm_profile = RowBuilder(self.sw, self.protocol, 'RPM', COLUMN_DETAILS, self.mandatory_tags)	
	rpmprofilesizer.Add(rpm_profile, 0, wx.ALL, 5)	
	# Procedure
	staticbox = wx.StaticBox(self.sw, -1, "Procedure")
	proceduresizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
	COLUMN_DETAILS = OrderedDict([('Name', ['TextCtrl', 100, -1, '']),('Description', ['TextCtrl', 200, -1, '']),
                                    ('RPM\n/Sec', ['TextCtrl', 30, -1, '']),
                                    ('Duration\n(Min)', ['TextCtrl', 30, -1, '']),
                                    ('Temp\n(C)', ['TextCtrl', 30, -1, ''])
                                    ])		
	self.procedure = RowBuilder(self.sw, self.protocol, 'Step', COLUMN_DETAILS, self.mandatory_tags)
	self.procedure.SetBackgroundColour('#99CC99')
	proceduresizer.Add(self.procedure, 0, wx.ALL, 5)	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(rpmprofilesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(proceduresizer,0,wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
	
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)   

    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)     

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)

########################################################################        
################## CENTRIFUGE SETTING PANEL    ###########################
########################################################################            
class OvenSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'Instrument|Oven'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = OvenPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)        

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = OvenPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    

	
        
class OvenPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):
	 
	self.settings_controls = {}
	self.labels = {}
	meta = ExperimentSettings.getInstance()
	
	wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
	
	# TAG
	self.tab_number = tab_number	# tab or instance number
	self.tag_stump = tag_stump                  # first two parts of tag (type|event) e.g Instrument|Centrifuge
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.mandatory_tags = [self.tag_stump+'|Manufacturer|'+str(self.tab_number)]        # mandatory fields 
	
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, exp.get_tag_event(self.tag_stump))
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	self.attfileTAG = self.tag_stump+'|AttachFiles|%s'%str(self.tab_number)	
	attach_bmp = icons.clip.Scale(16.0, 16.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	attach_btn = wx.BitmapButton(self.sw, -1, attach_bmp)
	attach_btn.SetToolTipString("Attach file links.")
	self.attach_file_num = wx.StaticText(self.sw, -1, '(%s)' %str(len(meta.get_field(self.attfileTAG, default=[]))))
	attach_btn.Bind (wx.EVT_BUTTON, self.OnAttachPropFile)	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)		
	titlesizer.Add(text, 0)
	titlesizer.AddSpacer((10,-1))
	titlesizer.Add(attach_btn, 0)
	titlesizer.AddSpacer((5,-1))
	titlesizer.Add(self.attach_file_num)
	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	mfgTAG = self.tag_stump+'|Manufacturer|'+str(self.tab_number)
	self.settings_controls[mfgTAG] = wx.TextCtrl(self.sw, name='Manufacturer' ,  value=meta.get_field(mfgTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[mfgTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[mfgTAG] = wx.StaticText(self.sw, -1, 'Manufacturer')
	self.labels[mfgTAG].SetToolTipString('Manufacturer name')
	attributesizer.Add(self.labels[mfgTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[mfgTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	modelTAG = self.tag_stump+'|Model|'+str(self.tab_number)
	self.settings_controls[modelTAG] = wx.TextCtrl(self.sw, value=meta.get_field(modelTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[modelTAG].Bind(wx.EVT_TEXT,self.OnSavingData)
	self.labels[modelTAG] = wx.StaticText(self.sw , -1,  'Model')
	self.labels[modelTAG].SetToolTipString('Model number')
	attributesizer.Add(self.labels[modelTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[modelTAG], 0, wx.EXPAND)
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	staticbox = wx.StaticBox(self.sw, -1, "Instrument Information")			
	attribute_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	attribute_Sizer.Add(attributesizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )		

	# ==== Local  ====
	localsizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

	nickTAG = self.tag_stump+'|NickName|'+str(self.tab_number)
	self.settings_controls[nickTAG] = wx.TextCtrl(self.sw, name='Nick Name' ,  value=meta.get_field(nickTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[nickTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[nickTAG] = wx.StaticText(self.sw, -1, 'Nick Name')
	self.labels[nickTAG].SetToolTipString('Nick Name of the instrument')
	localsizer.Add(self.labels[nickTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[nickTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	srlTAG = self.tag_stump+'|SerialNo|'+str(self.tab_number)
	self.settings_controls[srlTAG] = wx.TextCtrl(self.sw, name='Serial Number' ,  value=meta.get_field(srlTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[srlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[srlTAG] = wx.StaticText(self.sw, -1, 'Serial Number')
	self.labels[srlTAG].SetToolTipString('Serial Number')
	localsizer.Add(self.labels[srlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[srlTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)

	adrsTAG = self.tag_stump+'|Address|'+str(self.tab_number)
	self.settings_controls[adrsTAG] = wx.TextCtrl(self.sw, name='Address' ,  value=meta.get_field(adrsTAG, default=''), size=(-1, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
	self.settings_controls[adrsTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[adrsTAG] = wx.StaticText(self.sw, -1, 'Address')
	self.labels[adrsTAG].SetToolTipString('Address where of the instrument location')
	localsizer.Add(self.labels[adrsTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[adrsTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
	roomTAG = self.tag_stump+'|Room|'+str(self.tab_number)
	self.settings_controls[roomTAG] = wx.TextCtrl(self.sw, name='Room' ,  value=meta.get_field(roomTAG, default=''), style=wx.TE_PROCESS_ENTER)
	self.settings_controls[roomTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[roomTAG] = wx.StaticText(self.sw, -1, 'Room Number')
	self.labels[roomTAG].SetToolTipString('Room where of the instrument location')
	localsizer.Add(self.labels[roomTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	localsizer.Add(self.settings_controls[roomTAG], 0, wx.EXPAND)
	localsizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	staticbox = wx.StaticBox(self.sw, -1, "Local Information")			
	local_Sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)	
	local_Sizer.Add(localsizer,  0, wx.ALIGN_LEFT|wx.ALL, 5 )	
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)
		
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attribute_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.swsizer.Add(local_Sizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer) 
	
    def OnSavingSettings(self, event):
	meta.saving_settings(self.protocol, self.nameTAG, self.mandatory_tags)  
	    
    def OnAttachPropFile(self, event):
	if meta.checkMandatoryTags(self.mandatory_tags):	
	    dia = FileListDialog(self, self.attfileTAG, meta.get_field(self.attfileTAG, []), None)		
	    if dia.ShowModal()== wx.ID_OK:
		f_list = dia.file_list
		self.attach_file_num.SetLabel('(%s)'%str(len(f_list)))
		if f_list:
		    meta.set_field(self.attfileTAG, f_list)
		
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)



########################################################################        
################## TIMELAPSE SETTING PANEL    ##########################
########################################################################
class TLMSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'DataAcquis|TLM'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = TLMPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = TLMPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 

class TLMPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Microscope'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, 'Timelapse Image Format')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.tlm.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)

	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)            
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[self.selectinstTAG].SetToolTipString('Microscope channel used..')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Channel')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
        attributesizer.Add(showInstBut, 0)	
	
	tlmfrmtTAG = self.tag_stump+'|Format|'+str(self.tab_number)
	format_choices =['tiff', 'jpeg', 'stk', 'Other']
	self.settings_controls[tlmfrmtTAG]= wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), format_choices, wx.LB_SINGLE)
	if meta.get_field(tlmfrmtTAG) is not None:
	    self.settings_controls[tlmfrmtTAG].Append(meta.get_field(tlmfrmtTAG))
	    self.settings_controls[tlmfrmtTAG].SetStringSelection(meta.get_field(tlmfrmtTAG))
	self.settings_controls[tlmfrmtTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)   
	self.labels[tlmfrmtTAG] = wx.StaticText(self.sw, -1, 'Image Format')
	self.labels[tlmfrmtTAG].SetToolTipString('Image Format')
	attributesizer.Add(self.labels[tlmfrmtTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[tlmfrmtTAG], 0, wx.EXPAND)	
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	
	
        tlmintTAG = self.tag_stump+'|TimeInterval|'+str(self.tab_number)
        self.settings_controls[tlmintTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmintTAG, default=''))
        self.settings_controls[tlmintTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmintTAG] = wx.StaticText(self.sw, -1, 'Time Interval (min)')
	self.labels[tlmintTAG].SetToolTipString('Time interval image was acquired')
	attributesizer.Add(self.labels[tlmintTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
        attributesizer.Add(self.settings_controls[tlmintTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmfrmTAG = self.tag_stump+'|FrameNumber|'+str(self.tab_number)
        self.settings_controls[tlmfrmTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmfrmTAG, default=''))
        self.settings_controls[tlmfrmTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmfrmTAG] = wx.StaticText(self.sw, -1, 'Total Frame/Pane Number')
	self.labels[tlmfrmTAG].SetToolTipString('Total Frame/Pane Number')
	attributesizer.Add(self.labels[tlmfrmTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[tlmfrmTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmstkTAG = self.tag_stump+'|StackProcess|'+str(self.tab_number)
        self.settings_controls[tlmstkTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmstkTAG, default=''))
        self.settings_controls[tlmstkTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmstkTAG] = wx.StaticText(self.sw, -1, 'Stacking Process')
	self.labels[tlmstkTAG].SetToolTipString('Stacking Process')
	attributesizer.Add(self.labels[tlmstkTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
        attributesizer.Add(self.settings_controls[tlmstkTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmpxlTAG = self.tag_stump+'|PixelSize|'+str(self.tab_number)
        self.settings_controls[tlmpxlTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmpxlTAG, default=''))
        self.settings_controls[tlmpxlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmpxlTAG] = wx.StaticText(self.sw, -1, 'Pixel Size')
	self.labels[tlmpxlTAG].SetToolTipString('Pixel Size')
	attributesizer.Add(self.labels[tlmpxlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
        attributesizer.Add(self.settings_controls[tlmpxlTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmpxcnvTAG = self.tag_stump+'|PixelConvert|'+str(self.tab_number)
        self.settings_controls[tlmpxcnvTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmpxcnvTAG, default=''))
        self.settings_controls[tlmpxcnvTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[tlmpxcnvTAG] = wx.StaticText(self.sw, -1, 'Pixel Conversion') 
	self.labels[tlmpxcnvTAG].SetToolTipString('Pixel Conversion')
	attributesizer.Add(self.labels[tlmpxcnvTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
        attributesizer.Add(self.settings_controls[tlmpxcnvTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmsoftTAG = self.tag_stump+'|Software|'+str(self.tab_number)
        self.settings_controls[tlmsoftTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmsoftTAG, default=''))
        self.settings_controls[tlmsoftTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmsoftTAG] = wx.StaticText(self.sw, -1, 'Software Name and Version')
	self.labels[tlmsoftTAG].SetToolTipString(' Software')
	attributesizer.Add(self.labels[tlmsoftTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[tlmsoftTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
  
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)


########################################################################        
################## STATIC IMAGE SETTING PANEL    #######################
########################################################################
class HCSSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'DataAcquis|HCS'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = HCSPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = HCSPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 

class HCSPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Microscope'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, 'Static Image Format')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.hcs.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)

	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)        
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[self.selectinstTAG].SetToolTipString('Microscope channel used..')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Channel')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
        attributesizer.Add(showInstBut, 0)	
	
	tlmfrmtTAG = self.tag_stump+'|Format|'+str(self.tab_number)
	format_choices =['tiff', 'jpeg', 'stk', 'Other']
	self.settings_controls[tlmfrmtTAG]= wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), format_choices, wx.LB_SINGLE)
	if meta.get_field(tlmfrmtTAG) is not None:
	    self.settings_controls[tlmfrmtTAG].Append(meta.get_field(tlmfrmtTAG))
	    self.settings_controls[tlmfrmtTAG].SetStringSelection(meta.get_field(tlmfrmtTAG))
	self.settings_controls[tlmfrmtTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)   
	self.labels[tlmfrmtTAG] = wx.StaticText(self.sw, -1, 'Image Format')
	self.labels[tlmfrmtTAG].SetToolTipString('Image Format')
	attributesizer.Add(self.labels[tlmfrmtTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[tlmfrmtTAG], 0, wx.EXPAND)	
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	

        tlmpxlTAG = self.tag_stump+'|PixelSize|'+str(self.tab_number)
        self.settings_controls[tlmpxlTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmpxlTAG, default=''))
        self.settings_controls[tlmpxlTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmpxlTAG] = wx.StaticText(self.sw, -1, 'Pixel Size')
	self.labels[tlmpxlTAG].SetToolTipString('Pixel Size')
	attributesizer.Add(self.labels[tlmpxlTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
        attributesizer.Add(self.settings_controls[tlmpxlTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmpxcnvTAG = self.tag_stump+'|PixelConvert|'+str(self.tab_number)
        self.settings_controls[tlmpxcnvTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmpxcnvTAG, default=''))
        self.settings_controls[tlmpxcnvTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
	self.labels[tlmpxcnvTAG] = wx.StaticText(self.sw, -1, 'Pixel Conversion') 
	self.labels[tlmpxcnvTAG].SetToolTipString('Pixel Conversion')
	attributesizer.Add(self.labels[tlmpxcnvTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)	
        attributesizer.Add(self.settings_controls[tlmpxcnvTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)

        tlmsoftTAG = self.tag_stump+'|Software|'+str(self.tab_number)
        self.settings_controls[tlmsoftTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmsoftTAG, default=''))
        self.settings_controls[tlmsoftTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmsoftTAG] = wx.StaticText(self.sw, -1, 'Software Name and Version')
	self.labels[tlmsoftTAG].SetToolTipString(' Software')
	attributesizer.Add(self.labels[tlmsoftTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[tlmsoftTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
   

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)


########################################################################        
################## FLOW SETTING PANEL            #######################
########################################################################
class FCSSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.tag_stump = 'DataAcquis|FCS'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.tag_stump)):
	    panel = FCSPanel(self.notebook, self.tag_stump, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)      	

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.tag_stump)
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	
	panel = FCSPanel(self.notebook, self.tag_stump, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)    
 

class FCSPanel(wx.Panel):
    def __init__(self, parent, tag_stump, tab_number):

        self.settings_controls = {}
	self.labels = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.tab_number = tab_number
	self.tag_stump = tag_stump
	self.protocol = self.tag_stump+'|'+str(self.tab_number)
	self.instrument_used = 'Flowcytometer'
	self.mandatory_tags = [self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))]
		
	# Panel
	self.sw = wx.ScrolledWindow(self)
	self.swsizer = wx.BoxSizer(wx.VERTICAL)
	
	# Title
	text = wx.StaticText(self.sw, -1, 'FCS File Format')
	font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
	text.SetFont(font)
	pic=wx.StaticBitmap(self.sw)
	pic.SetBitmap(icons.fcs.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())	
	titlesizer = wx.BoxSizer(wx.HORIZONTAL)	
	titlesizer.Add(pic)
	titlesizer.AddSpacer((5,-1))	
	titlesizer.Add(text, 0)

	# Attributes	
	attributesizer = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)

        self.selectinstTAG = self.tag_stump+'|%sInstance|%s'%(self.instrument_used, str(self.tab_number))
        self.settings_controls[self.selectinstTAG] = wx.TextCtrl(self.sw, value=meta.get_field(self.selectinstTAG, default=''), style=wx.TE_READONLY)        
	link_bmp = icons.link.Scale(20.0, 20.0, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	showInstBut = wx.BitmapButton(self.sw, -1, link_bmp)
	showInstBut.SetToolTipString("Show choices")
        showInstBut.Bind (wx.EVT_BUTTON, self.ShowInstrumentInstances)
        self.settings_controls[self.selectinstTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.settings_controls[self.selectinstTAG].SetToolTipString('Flowcytometer used..')
	self.labels[self.selectinstTAG] = wx.StaticText(self.sw, -1, 'Select Flowcytometer')
        attributesizer.Add(self.labels[self.selectinstTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[self.selectinstTAG], 0, wx.EXPAND)
        attributesizer.Add(showInstBut, 0)	
	
	tlmfrmtTAG = self.tag_stump+'|Format|'+str(self.tab_number)
	format_choices =['fcs1.0', 'fcs2.0', 'fcs3.0', 'Other']
	self.settings_controls[tlmfrmtTAG]= wx.ListBox(self.sw, -1, wx.DefaultPosition, (120,30), format_choices, wx.LB_SINGLE)
	if meta.get_field(tlmfrmtTAG) is not None:
	    self.settings_controls[tlmfrmtTAG].Append(meta.get_field(tlmfrmtTAG))
	    self.settings_controls[tlmfrmtTAG].SetStringSelection(meta.get_field(tlmfrmtTAG))
	self.settings_controls[tlmfrmtTAG].Bind(wx.EVT_LISTBOX, self.OnSavingData)   
	self.labels[tlmfrmtTAG] = wx.StaticText(self.sw, -1, 'File Format')
	self.labels[tlmfrmtTAG].SetToolTipString('File Format')
	attributesizer.Add(self.labels[tlmfrmtTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
	attributesizer.Add(self.settings_controls[tlmfrmtTAG], 0, wx.EXPAND)	
	attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)	

        tlmsoftTAG = self.tag_stump+'|Software|'+str(self.tab_number)
        self.settings_controls[tlmsoftTAG] = wx.TextCtrl(self.sw, value=meta.get_field(tlmsoftTAG, default=''))
        self.settings_controls[tlmsoftTAG].Bind(wx.EVT_TEXT, self.OnSavingData)
        self.labels[tlmsoftTAG] = wx.StaticText(self.sw, -1, 'Software Name and Version')
	self.labels[tlmsoftTAG].SetToolTipString(' Software')
	attributesizer.Add(self.labels[tlmsoftTAG], 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        attributesizer.Add(self.settings_controls[tlmsoftTAG], 0, wx.EXPAND)
        attributesizer.Add(wx.StaticText(self.sw, -1, ''), 0)
	
	# Set Mandatory Label colour
	meta.setLabelColour(self.mandatory_tags, self.labels)		
	
        #--- Layout ----
	self.swsizer.Add(titlesizer,0,wx.ALL, 5)
	self.swsizer.Add((-1,10))
	self.swsizer.Add(attributesizer, 0, wx.EXPAND|wx.ALL, 5)
	self.sw.SetSizer(self.swsizer)
	self.sw.SetScrollbars(20, 20, self.Size[0]+10, self.Size[1]+10, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.sw, 1, wx.EXPAND)
	self.SetSizer(self.Sizer)
    
    def ShowInstrumentInstances(self, event): 
	instrumentTAG = 'Instrument|%s'%self.instrument_used
        attributes = meta.get_attribute_list(instrumentTAG) 
        #check whether there is at least one attributes
        if not attributes:
            dial = wx.MessageDialog(None, 'No %s instance exists!!'%self.instrument_used, 'Error', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()  
            return
        #show the popup table 
        dia = InstanceListDialog(self, instrumentTAG, selection_mode = False)
        if dia.ShowModal() == wx.ID_OK:
            if dia.listctrl.get_selected_instances() != []:
                instance = dia.listctrl.get_selected_instances()[0]
                self.settings_controls[self.selectinstTAG].SetValue(str(instance))
        dia.Destroy()
   

    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if exp.get_tag_stump(tag, 4) in self.mandatory_tags:
	    meta.saveData(ctrl, tag, self.settings_controls)
	    meta.setLabelColour(self.mandatory_tags, self.labels)	    
	elif meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)


########################################################################        
################## NoteSettingPanel             #########################
########################################################################
class NoteSettingPanel(wx.Panel):
    """
    Panel that holds parameter input panel and the buttons for more additional panel
    """
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()
		
	self.protocol = 'Notes'	

        self.notebook = fnb.FlatNotebook(self, -1, style=fnb.FNB_NO_X_BUTTON | fnb.FNB_VC8)
	self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, meta.onTabClosing)

	for instance_id in sorted(meta.get_field_instances(self.protocol)):
	    panel = NotePanel(self.notebook, int(instance_id))
	    self.notebook.AddPage(panel, 'Instance No: %s'%(instance_id), True)
		
	# Buttons
	createTabBtn = wx.Button(self, label="Create Instance")
	createTabBtn.Bind(wx.EVT_BUTTON, self.onCreateTab)

	# Sizers
	mainsizer = wx.BoxSizer(wx.VERTICAL)
	btnSizer = wx.BoxSizer(wx.HORIZONTAL)
	mainsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
	btnSizer.Add(createTabBtn  , 0, wx.ALL, 5)
	mainsizer.Add(btnSizer)
	self.SetSizer(mainsizer)
	self.Layout()
	
    def onCreateTab(self, event):
	next_tab_num = meta.get_new_protocol_id(self.protocol)	
	if self.notebook.GetPageCount()+1 != int(next_tab_num):
	    dlg = wx.MessageDialog(None, 'Can not create the next instance\nPlease fill information in Instance No: %s'%next_tab_num, 'Creating Instance..', wx.OK| wx.ICON_STOP)
	    dlg.ShowModal()
	    return 	    
	
	panel = NotePanel(self.notebook, next_tab_num)
	self.notebook.AddPage(panel, 'Instance No: %s'%next_tab_num, True)
    


class NotePanel(wx.Panel):
    def __init__(self, parent, page_counter):

        self.settings_controls = {}
        meta = ExperimentSettings.getInstance()

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.page_counter = page_counter
        self.panel = wx.Panel(self)
 
        self.titlesizer = wx.BoxSizer(wx.HORIZONTAL)
	self.top_fgs = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)	
	self.bot_fgs = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
		
	self.noteSelect = wx.Choice(self.panel, -1,  choices=['Text', 'Rest', 'Hint', 'URL', 'MultiMedia', 'File'])
	self.note_label = wx.StaticText(self.panel, -1, 'Note type')
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
	self.panel.SetSizer(self.mainSizer)
	#self.panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 5)		
	
	if meta.get_field_tags('Notes|', str(self.page_counter)):
	    self.noteTAG = meta.get_field_tags('Notes|', str(self.page_counter))[0]
	    self.noteType = exp.get_tag_event(self.noteTAG)
	    self.noteSelect.SetStringSelection(self.noteType)
	    self.noteSelect.Disable()
	    self.createNotePad()	

	

    def onCreateNotepad(self, event):
	ctrl = event.GetEventObject()
	self.noteType = ctrl.GetStringSelection()
	self.createNotePad()
    
    def createNotePad(self):	
	
	self.note_label.Hide()
	self.noteSelect.Hide()	
	
	if self.noteType=='Text':
	    self.noteDescrip = wx.TextCtrl(self.panel,  value=meta.get_field('Notes|%s|Description|%s' %(self.noteType, str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.noteDescrip.Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.noteDescrip.SetInitialSize((250, 300))
	
	    pic=wx.StaticBitmap(self.panel)
	    pic.SetBitmap(icons.critical.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    text = wx.StaticText(self.panel, -1, 'Critical Note')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)

	    self.titlesizer.Add(pic)
	    self.titlesizer.Add(text, 0) 
	    self.bot_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.bot_fgs.Add(wx.StaticText(self.panel, -1, ''), 0)
	    
	if self.noteType=='Hint':
	    self.noteDescrip = wx.TextCtrl(self.panel,  value=meta.get_field('Notes|%s|Description|%s' %(self.noteType, str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.noteDescrip.Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.noteDescrip.SetInitialSize((250, 300))
	
	    pic=wx.StaticBitmap(self.panel)
	    pic.SetBitmap(icons.hint.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    text = wx.StaticText(self.panel, -1, 'Hint')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)

	    self.titlesizer.Add(pic)
	    self.titlesizer.Add(text, 0) 
	    self.bot_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.bot_fgs.Add(wx.StaticText(self.panel, -1, ''), 0)	
	    
	if self.noteType=='Rest':
	    self.noteDescrip = wx.TextCtrl(self.panel,  value=meta.get_field('Notes|%s|Description|%s' %(self.noteType, str(self.page_counter)), default=''), style=wx.TE_MULTILINE)
	    self.noteDescrip.Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.noteDescrip.SetInitialSize((250, 300))
	
	    pic=wx.StaticBitmap(self.panel)
	    pic.SetBitmap(icons.rest.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    text = wx.StaticText(self.panel, -1, 'Rest')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)

	    self.titlesizer.Add(pic)
	    self.titlesizer.Add(text, 0) 
	    self.bot_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.bot_fgs.Add(wx.StaticText(self.panel, -1, ''), 0)	
	

	if self.noteType == 'URL':
	    self.noteDescrip = wx.TextCtrl(self.panel,  value=meta.get_field('Notes|%s|Description|%s' %(self.noteType, str(self.page_counter)), default='http://www.jove.com/'))
	    self.noteDescrip.Bind(wx.EVT_TEXT, self.OnSavingData)
	    self.noteDescrip.SetInitialSize((250, 20))
	    
	    goURLBtn = wx.Button(self.panel, -1, 'Go to URL')
	    goURLBtn.Bind(wx.EVT_BUTTON, self.goURL)
	
	    pic=wx.StaticBitmap(self.panel)
	    pic.SetBitmap(icons.url.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    text = wx.StaticText(self.panel, -1, 'URL')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)

	    self.titlesizer.Add(pic)
	    self.titlesizer.Add(text, 0) 
	    self.top_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.top_fgs.Add(goURLBtn, 0)	    
	    
	if self.noteType == 'MultiMedia':
	    self.mediaTAG = 'Notes|%s|Description|%s' %(self.noteType, str(self.page_counter))
	    self.noteDescrip = wx.TextCtrl(self.panel, value=meta.get_field(self.mediaTAG, default=''))
	    self.noteDescrip.Bind(wx.EVT_TEXT, self.OnSavingData)	    
	    self.browseBtn = wx.Button(self.panel, -1, 'Load Media File')
	    self.browseBtn.Bind(wx.EVT_BUTTON, self.loadFile)
	    self.mediaplayer = MediaPlayer(self.panel)
	    
	    pic=wx.StaticBitmap(self.panel)
	    pic.SetBitmap(icons.video.Scale(ICON_SIZE, ICON_SIZE, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap())
	    text = wx.StaticText(self.panel, -1, 'MultiMedia')
	    font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
	    text.SetFont(font)	    
	    
	    if meta.get_field('Notes|%s|Description|%s' %(self.noteType, str(self.page_counter))) is not None:	
		self.mediaplayer.mc.Load(meta.get_field('Notes|%s|Description|%s' %(self.noteType, str(self.page_counter))))		
    
	    self.titlesizer.Add(pic)
	    self.titlesizer.Add(text, 0) 
	    self.top_fgs.Add(self.noteDescrip, 0,  wx.EXPAND)
	    self.top_fgs.Add(self.browseBtn, 0)	    	
	    self.bot_fgs.Add(self.mediaplayer, 0)

	self.panel.SetSizer(self.mainSizer)
	self.panel.Refresh()
	#self.panel.SetScrollbars(20, 20, self.Size[0]+20, self.Size[1]+20, 0, 0)

	self.Sizer = wx.BoxSizer(wx.VERTICAL)
	self.Sizer.Add(self.panel, 0, wx.EXPAND|wx.ALL, 5)
	self.SetSizer(self.Sizer)
	self.Layout()
	
    def loadFile(self, event):
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

    def OnSavingData(self, event):	
        meta = ExperimentSettings.getInstance()    
        self.noteTAG = 'Notes|%s|Description|%s' %(self.noteType, str(self.page_counter))
        meta.set_field(self.noteTAG, self.noteDescrip.GetValue())

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

    #def onPlay(self):
        #self.mc.Play()

        
if __name__ == '__main__':
    app = wx.App(False)
    
    frame = wx.Frame(None, title='ProtocolNavigator', size=(650, 650))
    p = ExperimentSettingsWindow(frame)

    frame.SetMenuBar(wx.MenuBar())
    fileMenu = wx.Menu()
    saveSettingsMenuItem = fileMenu.Append(-1, 'Save settings\tCtrl+S', help='')
    loadSettingsMenuItem = fileMenu.Append(-1, 'Load settings\tCtrl+O', help='')
    #frame.Bind(wx.EVT_MENU, on_save_settings, saveSettingsMenuItem)
    #frame.Bind(wx.EVT_MENU, on_load_settings, loadSettingsMenuItem) 
    frame.GetMenuBar().Append(fileMenu, 'File')


    frame.Show()
    app.MainLoop()