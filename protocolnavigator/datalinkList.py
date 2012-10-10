import wx
import sys
import wx.lib.mixins.listctrl as listmix
from experimentsettings import *

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class DataLinkListDialog(wx.Dialog):
    def __init__(self, parent, well_ids, ancestor_tags):
        wx.Dialog.__init__(self, parent, -1, size=(500,450), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.listctrl = InstanceListCtrl(self, well_ids, ancestor_tags)
        
        outputs = ('Export Selected', 'Export All', 'Show in ImageJ')
        self.output_options = wx.RadioBox(self, -1, "Output Choices", choices=outputs)
        
        
        self.ok_btn = wx.Button(self, wx.ID_OK)
        self.close_btn = wx.Button(self, wx.ID_CANCEL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL) 
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.listctrl, 1, wx.EXPAND)
        hbox2.Add(self.output_options, 1)
        hbox3.Add(self.ok_btn, 1)
        hbox3.AddSpacer((10,-1))
        hbox3.Add(self.close_btn, 1)
        vbox.Add(hbox1, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        vbox.Add(hbox2, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        vbox.Add(hbox3, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        self.SetSizer(vbox)
        self.Center()
 
        
class InstanceListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin, listmix.TextEditMixin):
    def __init__(self, parent, well_ids, ancestor_tags):
        '''
        tag_prefix -- the tag whose instances to list in this list control
        '''
        meta = ExperimentSettings.getInstance()
        
        wx.ListCtrl.__init__(self, parent, -1, size=(-1,270), style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SORT_ASCENDING|wx.LC_HRULES)
        
        
        # get all data acquisition tags
        self.data_acquis_well = {}
        self.select_data_acquis_well = {}
        row = 1
        for tag in meta.global_settings:
            if len(tag.split('|')) == 6:
                for url in meta.get_field(tag):
                    self.data_acquis_well[row] = (get_tag_well(tag), str(get_tag_timepoint(tag)), url)
                    row += 1
                

        self.InsertColumn(0, 'Location')
        self.InsertColumn(1, 'Time')
        self.InsertColumn(2, 'Data URL')
        self.InsertColumn(3, 'Data Provenance')
          
        items = self.data_acquis_well.items()
       
        for key, data in items:                
            index = self.InsertStringItem(sys.maxint, data[0])
            self.SetStringItem(index, 1, format_time_string(data[1]), wx.LIST_FORMAT_CENTER)
            self.SetStringItem(index, 2, data[2], wx.LIST_FORMAT_RIGHT)
            self.SetItemData(index, key) 
            
            r = 1
            for well in well_ids:
                if str(well) == str(data[0]):
                    provenance_description = self.decode_tags(ancestor_tags)
                    self.SetStringItem(index, 3, provenance_description, wx.LIST_FORMAT_RIGHT)
                    self.select_data_acquis_well[r] = (data[0], data[1], data[2], provenance_description)
                    self.Select(index)
                    r +=1
        
    def get_selected_urls(self):
        i = -1
        selections = []
        while 1:
            i = self.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if i == -1:
                break
            selections.append([self.GetItem(i, col).GetText() for col in range(self.GetColumnCount())])
        return selections        
        
    def get_all_urls(self):
        selections = []
        for row in range(self.GetItemCount()):
            selections.append([self.GetItem(row, col).GetText() for col in range(self.GetColumnCount())])
        return selections
    
    def decode_tags(self, tags):
        description = ''        
        for tag in tags:
            description += '@%s hr %s %s was done; '%(format_time_string(get_tag_timepoint(tag)), get_tag_event(tag), get_tag_type(tag))
        return description
                    
                    
