from bench import Bench
from metadatainput import ExperimentSettingsWindow
from lineagepanel import LineageFrame
from experimentsettings import ExperimentSettings
from instancelist import *
from stepwiseprinter import PrintProtocol
from utils import *
from wx.html import HtmlEasyPrinting, HtmlWindow
import snapshotPrinter
import wx
import os


class ProtocolNavigator(wx.App):
    '''The ProtocolNavigator Application
    This launches the main UI, and keeps track of the session.
    '''
    def OnInit(self):

        self.settings_frame = wx.Frame(None, title='ProtocolNavigator', 
                                  size=(900, 720), pos=(50,10))
        self.settings_frame.Sizer = wx.BoxSizer()
     
        self.lr_splitter = wx.SplitterWindow(self.settings_frame)
        self.settings_frame.Sizer.Add(self.lr_splitter, 1, wx.EXPAND)
        self.ud_splitter = wx.SplitterWindow(self.lr_splitter, style=wx.NO_BORDER|wx.SP_3DSASH)
        self.exptsetting_frame = ExperimentSettingsWindow(self.ud_splitter)
        self.settings_frame.SetMenuBar(wx.MenuBar())
        fileMenu = wx.Menu()
        
        saveSettingsMenuItem = fileMenu.Append(-1, 'Save Protocol\tCtrl+S', help='')
        loadSettingsMenuItem = fileMenu.Append(-1, 'Load Protocol\tCtrl+O', help='')
        printExperimentMenuItem = fileMenu.Append(-1, 'Print Protocol\tCtrl+P', help='')
        #self.settings_frame.Bind(wx.EVT_MENU, self.on_new_experiment, newExperimentMenuItem)
       
        self.settings_frame.Bind(wx.EVT_MENU, self.on_save_settings, saveSettingsMenuItem)
        self.settings_frame.Bind(wx.EVT_MENU, self.on_load_settings, loadSettingsMenuItem)
        self.settings_frame.Bind(wx.EVT_MENU, self.on_print_protocol, printExperimentMenuItem)
        self.settings_frame.GetMenuBar().Append(fileMenu, 'File')
        
        self.settings_frame.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        
        self.bench_frame = Bench(self, self.ud_splitter)
        self.ud_splitter.SplitHorizontally(self.exptsetting_frame, self.bench_frame)
	self.ud_splitter.SetSashGravity(0.4)
        
        self.lineage_frame = LineageFrame(self.lr_splitter)
        self.lr_splitter.SplitVertically(self.ud_splitter, self.lineage_frame)
	self.lr_splitter.SetSashGravity(0.5)
        
        if hasattr(sys, 'frozen'):
            path = os.path.split(os.path.abspath(sys.argv[0]))[0]
            path = os.path.join(path, 'icons')
        else:
            path = os.path.join(os.path.split(__file__)[0], "icons")
        icon = wx.EmptyIcon()
        if sys.platform.startswith('win'):
            icon_image = icons.protocol_navigator32x32
        else:
            icon_image = icons.protocol_navigator128x128
        icon.CopyFromBitmap(wx.BitmapFromImage(icon_image))
        self.settings_frame.SetIcon(icon)
        self.settings_frame.Layout()
        self.settings_frame.Show()
         
        return True
 
    def get_exptsettings(self):
        return self.exptsetting_frame
    
    def get_bench(self):
        return self.bench_frame
    
    def get_lineage(self):
        return self.lineage_frame
    
    def get_settings(self):
        return self.lineage_frame
    
    def on_new_experiment(self, evt):
        '''clears the existing Experiment settings
        '''
        return ExperimentSettings.getInstance().clear()

    def on_save_settings(self, evt):
        # for saving the experimental file, the text file may have the following nomenclature
        # Date(YYYY_MM_DD)_ExperimenterNumber_Experimenter Name_ first 20 words from the aim
    
        meta = ExperimentSettings.getInstance()
        
        #-- Get Experimental Date/number ---#
        exp_date = meta.get_field('Overview|Project|ExptDate')
        exp_num = meta.get_field('Overview|Project|ExptNum')
        exp_title = meta.get_field('Overview|Project|Title')
        if None not in [exp_date, exp_num, exp_title]:
            day, month, year = exp_date.split('/')
            filename = '%s%s%s_%s_%s.txt'%(year, month, day , exp_num, exp_title)
        else:
            filename = 'new_experiment.txt'
        
        dlg = wx.FileDialog(None, message='Saving experimental metadata...', 
                            defaultDir=os.getcwd(), defaultFile=filename, 
                            wildcard='.txt', 
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            os.chdir(os.path.split(dlg.GetPath())[0])
            ExperimentSettings.getInstance().save_to_file(dlg.GetPath())
    
            
    def on_load_settings(self, evt):
        dlg = wx.FileDialog(None, "Select the file containing your ProtocolNavigator workspace...",
                            defaultDir=os.getcwd(), style=wx.OPEN|wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            ExperimentSettings.getInstance().load_from_file(dlg.GetPath())
    
    def on_print_protocol(self, event):
        """ Takes a screenshot of the lineage panel pos & size (rect). 
            and then reformat the encoded experiment in natural laguage
            and print both together in a single file"""

        rect = self.lineage_frame.GetRect()
        
        PrintProtocol(rect)
        
    def onCloseWindow(self, event):
        if ExperimentSettings.global_settings:
            dlg = wx.MessageDialog(None,
                   "Do you want to save changes before exiting ProtocolNavigator?", "Confirm Exit", 
                   wx.YES|wx.NO|wx.CANCEL|wx.ICON_EXCLAMATION)
           
	    try:
		selection = dlg.ShowModal()
		if  selection == wx.ID_YES:
		    self.on_save_settings(self)
		    event.Skip()
		elif selection == wx.ID_NO:
		    event.Skip()	
		elif selection == wx.ID_CANCEL:
		    event.Veto()
	    finally:
		dlg.Destroy()
	else:
	    event.Skip()
		
if __name__ == '__main__':
    app = ProtocolNavigator(redirect=False)
    # Load a settings file if passed in args
    if len(sys.argv) > 1:
        ExperimentSettings.getInstance().load_from_file(sys.argv[1])
    app.MainLoop()
