import wx
import sys
import wx.lib.mixins.listctrl as listmix
import icons
from experimentsettings import *
from wx.lib.agw import ultimatelistctrl as ULC

########################################################################        
########       Popup Dialog showing all instances of settings       ####
########################################################################            
class DataLinkListDialog(wx.Dialog):
    def __init__(self, parent, well_ids, time_point, ancestor_tags):
        wx.Dialog.__init__(self, parent, -1, size=(500,650), title='Data Links', style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.ultimateList = ULC.UltimateListCtrl(self, agwStyle = ULC.ULC_REPORT|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)       
        
        meta = ExperimentSettings.getInstance()

        ## get all data acquisition tags
        self.data_acquis_well = {}
        #self.select_data_acquis_well = {}
        self.data_metadata = {}
        
        for tag in meta.global_settings:
            if len(tag.split('|')) == 6:
                for dm in meta.get_field(tag):
                    pw = (tag.split('|')[5]).strip('[]')
                    self.data_metadata[dm] = pw+'_'+str(get_tag_timepoint(tag))  # dictionary [data_metadata tuple] = plate_well 

        self.ultimateList.InsertColumn(0, 'Where')
        self.ultimateList.InsertColumn(1, 'When')
        self.ultimateList.InsertColumn(2, 'Provenance')
        self.ultimateList.InsertColumn(3, 'Data')
        self.ultimateList.InsertColumn(4, 'Metadata')
        self.ultimateList.SetColumnWidth(2, 250)
        
        for dm, pw_t in self.data_metadata.iteritems():
            pw = pw_t.split('_')[0]
            t = pw_t.split('_')[1]
            d = dm[0]
            m = dm[1]
            index = self.ultimateList.InsertStringItem(sys.maxint, pw)
            self.ultimateList.SetStringItem(index, 1, format_time_string(t), wx.LIST_FORMAT_CENTER)
            self.ultimateList.SetStringItem(index, 3, d , wx.LIST_FORMAT_RIGHT)
            self.ultimateList.SetStringItem(index, 4, m, wx.LIST_FORMAT_RIGHT)
   
            for well in well_ids:
                if str(well)+'_'+str(time_point) == pw_t: 
                    provenance_description = self.decode_tags(ancestor_tags)  # better to provide ancestor tags for all rows 
                    self.ultimateList.SetStringItem(index, 2, provenance_description, wx.LIST_FORMAT_RIGHT)
                    self.ultimateList.Select(index)
                    
        outputs = ('Export Selected', 'Export All', 'Show in ImageJ')
        self.output_options = wx.RadioBox(self, -1, "Output Choices", choices=outputs)
        
        self.ok_btn = wx.Button(self, wx.ID_OK)
        self.close_btn = wx.Button(self, wx.ID_CANCEL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL) 
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.ultimateList, 1, wx.EXPAND)
        hbox2.Add(self.output_options, 1, wx.ALIGN_LEFT)
        hbox3.Add(self.ok_btn, 1)
        hbox3.AddSpacer((10,-1))
        hbox3.Add(self.close_btn, 1)
        vbox.Add(hbox1, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        vbox.Add(hbox2, 0, wx.ALL|wx.EXPAND, 5)
        vbox.Add(hbox3, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        self.SetSizer(vbox)
        self.Center()
 
    def get_selected_urls(self):
        i = -1
        selections = []
        while 1:
            i = self.ultimateList.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if i == -1:
                break
            selections.append([self.ultimateList.GetItem(i, col).GetText() for col in range(self.ultimateList.GetColumnCount())])
        return selections        
        
    def get_all_urls(self):
        selections = []
        for row in range(self.ultimateList.GetItemCount()):
            selections.append([self.ultimateList.GetItem(row, col).GetText() for col in range(self.ultimateList.GetColumnCount())])
        return selections
    
    def decode_tags(self, tags):
        description = ''        
        for tag in tags:
            description += '@%s hr %s %s was done; '%(format_time_string(get_tag_timepoint(tag)), get_tag_event(tag), get_tag_type(tag))
        return description
                    
                    
