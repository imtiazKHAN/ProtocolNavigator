import wx
import re
import experimentsettings as exp
import icons
from experimentsettings import ExperimentSettings
from wx.lib.masked import NumCtrl

meta = exp.ExperimentSettings.getInstance()

class RowBuilder(wx.Panel):
    '''Panel that shows the rows or components which can be added or deleted as required 
    '''
    # panel, 'AddProcess|Rheometer|1', 'Gas', [ColumnHeader, [CtrlType, w, h, value/choices]]
    def __init__(self, parent, protocol, token, col_details, mandatory_tags, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
	
	self.protocol = protocol
	self.token = token
	self.col_details = col_details
	self.col_headers = self.col_details.keys()
	self.mandatory_tags = mandatory_tags
	
	self.tag_stump = exp.get_tag_stump(self.protocol, 2)
	self.instance = exp.get_tag_attribute(self.protocol)
	self.settings_controls = {}
	
	self.showRows()

	  
    def showRows(self):
	# Attach a flexi sizer for the text controler and labels
	self.fgs = wx.FlexGridSizer(rows=15000, cols=len(self.col_headers)+3, hgap=5, vgap=5)    
	#-- Header --#	
	font = wx.Font(6, wx.SWISS, wx.NORMAL, wx.BOLD)
	self.fgs.Add(wx.StaticText(self, -1, ''))
	for t in self.col_headers:
	    header = wx.StaticText(self, -1, t)
	    header.SetFont(font)
	    self.fgs.Add(header, 0, wx.ALIGN_CENTRE)
	self.fgs.Add(wx.StaticText(self, -1, ''))
	self.fgs.Add(wx.StaticText(self, -1, ''))
    
	rows = meta.get_Row_Numbers(self.protocol, self.token)
	    
	if rows:  # fill with previously encoded info about the row
	    for row in rows:
		rowNo = int(row.split(self.token)[1])
		rowTAG = self.tag_stump+'|%s|%s' %(row, self.instance)
		row_info =  meta.get_field(rowTAG)
		# Label
		self.fgs.Add(wx.StaticText(self, -1, self.token+'%s'%str(rowNo)), 0, wx.ALIGN_CENTRE)
		if row_info:
		    for c, h in enumerate(self.col_headers):
			if self.col_details[h][0] is 'TextCtrl':
			    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.TextCtrl(self, size=(self.col_details[h][1], self.col_details[h][2]), value=row_info[c], style=wx.TE_PROCESS_ENTER) 
			    self.settings_controls[rowTAG+'|%s'%str(c)].SetToolTipString(row_info[c])
			    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_TEXT, self.OnSavingData)
			if self.col_details[h][0] is 'NumCtrl':
			    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.lib.masked.NumCtrl(self, size=(self.col_details[h][1], self.col_details[h][2]), value=self.col_details[h][3], style=wx.TE_PROCESS_ENTER) 
			    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_TEXT, self.OnSavingData)
			if self.col_details[h][0] is 'ListBox':
			    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.ListBox(self, size=(self.col_details[h][1], self.col_details[h][2]), choices=self.col_details[h][3], style=wx.LB_SINGLE)			    
			    self.settings_controls[rowTAG+'|%s'%str(c)].SetStringSelection(row_info[c])
			    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_LISTBOX, self.OnSavingData)
			self.fgs.Add(self.settings_controls[rowTAG+'|%s'%str(c)], 0, wx.EXPAND|wx.ALL, 5) 	
		    # Button
		    self.add_btn = wx.Button(self, id=rowNo, label='Add +')
		    self.del_btn = wx.Button(self, id=rowNo, label='Del -')
		    self.add_btn.Bind(wx.EVT_BUTTON, self.OnAddRow) 
		    self.del_btn.row_to_delete = row
		    self.del_btn.Bind(wx.EVT_BUTTON, self.OnDelRow) 		
		    self.fgs.Add(self.add_btn, 0, wx.ALIGN_CENTRE)
		    self.fgs.Add(self.del_btn, 0, wx.ALIGN_CENTRE)		    
		else: # new row
		    for c, h in enumerate(self.col_headers):
			if self.col_details[h][0] is 'TextCtrl':
			    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.TextCtrl(self, size=(self.col_details[h][1], self.col_details[h][2]), value=self.col_details[h][3], style=wx.TE_PROCESS_ENTER) 
			    self.settings_controls[rowTAG+'|%s'%str(c)].SetToolTipString(self.col_details[h][3])
			    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_TEXT, self.OnSavingData)
			if self.col_details[h][0] is 'NumCtrl':
			    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.lib.masked.NumCtrl(self, size=(self.col_details[h][1], self.col_details[h][2]), value=self.col_details[h][3], style=wx.TE_PROCESS_ENTER) 
			    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_TEXT, self.OnSavingData)
			if self.col_details[h][0] is 'ListBox':
			    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.ListBox(self, size=(self.col_details[h][1], self.col_details[h][2]), choices=self.col_details[h][3], style=wx.LB_SINGLE)	
			    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_LISTBOX, self.OnSavingData)			
			self.fgs.Add(self.settings_controls[rowTAG+'|%s'%str(c)], 0, wx.EXPAND|wx.ALL, 5) 	
		    self.add_btn = wx.Button(self, id=rowNo, label='Add +')		
		    self.add_btn.Bind(wx.EVT_BUTTON, self.OnAddRow) 
		    self.fgs.Add(self.add_btn, 0, wx.ALIGN_CENTRE)
		    self.fgs.Add(wx.StaticText(self, -1, ''), 0, wx.ALIGN_CENTRE)		    
		    
	else:# First Row
	    rowTAG = self.tag_stump+'|%s|%s' %(self.token+'1', self.instance)
	    row_info =  meta.get_field(rowTAG)
	    self.fgs.Add(wx.StaticText(self, -1, self.token+'1'), 0, wx.ALIGN_CENTRE)
	    # Appropriate Ctrl on the panel/per row or row
	    for c, h in enumerate(self.col_headers):
		if self.col_details[h][0] is 'TextCtrl':
		    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.TextCtrl(self, size=(self.col_details[h][1], self.col_details[h][2]), value=self.col_details[h][3], style=wx.TE_PROCESS_ENTER) 
		    self.settings_controls[rowTAG+'|%s'%str(c)].SetToolTipString(self.col_details[h][3])
		    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_TEXT, self.OnSavingData)
		if self.col_details[h][0] is 'NumCtrl':
		    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.lib.masked.NumCtrl(self, size=(self.col_details[h][1], self.col_details[h][2]), value=self.col_details[h][3], style=wx.TE_PROCESS_ENTER)  
		    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_TEXT, self.OnSavingData)
		if self.col_details[h][0] is 'ListBox':
		    self.settings_controls[rowTAG+'|%s'%str(c)] = wx.ListBox(self, size=(self.col_details[h][1], self.col_details[h][2]), choices=self.col_details[h][3], style=wx.LB_SINGLE)	
		    self.settings_controls[rowTAG+'|%s'%str(c)].Bind(wx.EVT_LISTBOX, self.OnSavingData)			
		self.fgs.Add(self.settings_controls[rowTAG+'|%s'%str(c)], 0, wx.EXPAND|wx.ALL, 5) 		
	    # Buttons at the end of row
	    self.add_btn = wx.Button(self, id=1, label='Add +')		
	    self.add_btn.Bind(wx.EVT_BUTTON, self.OnAddRow) 
	    self.fgs.Add(self.add_btn, 0, wx.ALIGN_CENTRE)
	    self.fgs.Add(wx.StaticText(self, -1, ''), 0, wx.ALIGN_CENTRE)

	self.SetSizer(self.fgs, wx.EXPAND)
	self.Layout()	
	self.Parent.FitInside()
	
    def OnAddRow(self, event):
	# Check whether the description field has been filled by users
	rows = meta.get_Row_Numbers(self.protocol, self.token)  
	for row in rows:
	    rowTAG = self.tag_stump+'|%s|%s' %(row, self.instance)
	    row_info =  meta.get_field(rowTAG)	    
	    if row_info == []:
		dial = wx.MessageDialog(None, 'Please fill the description in %s !!' %row, 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()  
		return
	    
	ctrl = event.GetEventObject()
	
	# Rearrange the rows numbers in the experimental settings
	temp_rows = {}
	
	for row in rows:
	    rowNo = int(row.split(self.token)[1])

	    if rowNo > ctrl.GetId() and temp_rows[rowNo] is not []:
		temp_rows[rowNo+1] = meta.get_field(self.tag_stump+'|%s|%s' %(row, self.instance))
		meta.remove_field(self.tag_stump+'|%s|%s' %(row, self.instance))
	    else:
		temp_rows[rowNo] = meta.get_field(self.tag_stump+'|%s|%s' %(row, self.instance))
		temp_rows[rowNo+1] = []
		meta.remove_field(self.tag_stump+'|%s|%s' %(row, self.instance))		
	
	for rowNo in sorted(temp_rows.iterkeys()):
	    meta.set_field(self.tag_stump+'|%s|%s' %(self.token+'%s'%str(rowNo),  self.instance),  temp_rows[rowNo])	
	
	#clear the sizer
	self.fgs.Clear(deleteWindows=True)
	#redraw the panel
	self.showRows()
	   

    def OnDelRow(self, event):	
	self.del_btn = event.GetEventObject()
	
	#delete the row from the experimental settings 
	meta.remove_field(self.tag_stump+'|%s|%s' %(self.del_btn.row_to_delete,  self.instance))
	
	# Rearrange the rows numbers in the experimental settings
	rows = meta.get_Row_Numbers(self.protocol, self.token)
	
	temp_rows = {}
	for rowNo in range(len(rows)):
	    temp_rows[rowNo+1] = meta.get_field(self.tag_stump+'|%s|%s' %(rows[rowNo],  self.instance))
	    meta.remove_field(self.tag_stump+'|%s|%s' %(rows[rowNo],  self.instance), notify_subscribers =False)
	
	for rowNo in sorted(temp_rows.iterkeys()):
	    meta.set_field(self.tag_stump+'|%s|%s' %(self.token+'%s'%str(rowNo),  self.instance),  temp_rows[rowNo])
	
	#clear the sizer
	self.fgs.Clear(deleteWindows=True)
	#redraw the panel
	self.showRows()
	
    def OnSavingData(self, event):
	ctrl = event.GetEventObject()
	tag = [t for t, c in self.settings_controls.items() if c==ctrl][0]
	if meta.checkMandatoryTags(self.mandatory_tags):
	    meta.saveData(ctrl, tag, self.settings_controls)