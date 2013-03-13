import os
import wx
import sys
import re
import icons
import experimentsettings as exp
from timeline import Timeline
from wx.html import HtmlEasyPrinting, HtmlWindow
from experimentsettings import ExperimentSettings

meta = exp.ExperimentSettings.getInstance()
 

      
class PrintProtocol(wx.Frame):
 
    ##----------------------------------------------------------------------
    def __init__(self, screen, **kwargs):
        wx.Frame.__init__(self, None, size=(700,800))
        
        self.screen =  screen
 
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.printer = HtmlEasyPrinting(name='Printing', parentWindow=None)
 
        self.html = HtmlWindow(self.panel)
        self.html.SetRelatedFrame(self, self.GetTitle())
	
 
        #if not os.path.exists('screenshot.htm'):
        self.formatProtocolInfo()
        self.html.LoadPage('screenshot.htm')
        
        # adjust widths for Linux (figured out by John Torres 
        # http://article.gmane.org/gmane.comp.python.wxpython/67327)
        if sys.platform == 'linux2':
            client_x, client_y = self.ClientToScreen((0, 0))
            border_width = client_x - self.screen.x
            title_bar_height = client_y - self.screen.y
            self.screen.width += (border_width * 2)
            self.screen.height += title_bar_height + border_width
 
        #Create a DC for the whole screen area
        dcScreen = wx.ScreenDC()
 
        #Create a Bitmap that will hold the screenshot image later on
        bmp = wx.EmptyBitmap(self.screen.width, self.screen.height)
 
        #Create a memory DC that will be used for actually taking the screenshot
        memDC = wx.MemoryDC()
 
        #Tell the memory DC to use our Bitmap
        memDC.SelectObject(bmp)
 
        #Blit (in this case copy) the actual screen on the memory DC and thus the Bitmap
        memDC.Blit( 0, #Copy to this X coordinate
                    0, #Copy to this Y coordinate
                    self.screen.width, #Copy this width
                    self.screen.height, #Copy this height
                    dcScreen, #From where do we copy?
                    self.screen.x, #What's the X offset in the original DC?
                    self.screen.y  #What's the Y offset in the original DC?
                    )
 
        #Select the Bitmap out of the memory DC by selecting a new uninitialized Bitmap
        memDC.SelectObject(wx.NullBitmap)
 
        img = bmp.ConvertToImage()
        fileName = "myImage.png"
        img.SaveFile(fileName, wx.BITMAP_TYPE_PNG)
 
        self.sendToPrinter()
        
        
    def formatProtocolInfo(self):
        ''' this method format the information of the annoted protocols 
        ready for printing'''
        meta = exp.ExperimentSettings.getInstance()
        
        self.printfile = file('screenshot.htm', 'w')
      
        timeline = meta.get_timeline()
	timepoints = timeline.get_unique_timepoints()
        self.events_by_timepoint = timeline.get_events_by_timepoint()
        
        #---- Overview ---#
        protocol_info =  self.decode_event_description('Overview|Project|1') #this 1 is psedo to make it coherent with other instance based tabs
        self.printfile.write('<html><head><title>Experiment Protocol</title></head><br/><body><h1>'+protocol_info.get('Title', '')+'</h1><h3>1. Experiment Overview</h3>')
	self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
	if 'Aims' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Aims: </b>'+protocol_info['Aims']+'</font></code></td></tr>')
	if 'Fund' in protocol_info:	
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Funding Code: </b>'+protocol_info['Fund']+'</font></code></td></tr>')
	if 'Keywords' in protocol_info:	
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Keywords: </b>'+protocol_info['Keywords']+'</font></code></td></tr>')
	if 'ExptNum' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Experiment Number: </b>'+protocol_info['ExptNum']+'</font></code></td></tr>')
	if 'ExptDate' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Experiment start Date: </b>'+protocol_info['ExptDate']+'</font></code></td></tr>')
	if 'Publications' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Publications: </b>'+protocol_info['Publications']+'</font></code></td></tr>')
	if 'Experimenter' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Experimenter: </b>'+protocol_info['Experimenter']+'</font></code></td></tr>')
	if 'Institution' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Institution: </b>'+protocol_info['Institution']+'</font></code></td></tr>')
	if 'Department' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Department: </b>'+protocol_info['Department']+'</font></code></td></tr>')
	if 'Address' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Address: </b>'+protocol_info['Address']+'</font></code></td></tr>')
	if 'Status' in protocol_info:
	    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Status: </b>'+protocol_info['Status']+'</font></code></td></tr>')
	self.printfile.write('</table>')
        #---- Sample ----#
	cellline = meta.get_field_instances('Sample|CellLine')
	self.printfile.write('<h3>2. Sample (Cell Line)</h3>')	
	if cellline:
	    for instance in cellline:
		protocol_info = self.decode_event_description('Sample|CellLine|%s'%instance)
		self.printfile.write('<code><font size="1"><b>' +protocol_info['Name']+ ' cell line (Authority ' +protocol_info.get('Authority', '')+ ' , Catalogue No: '+protocol_info.get('CatalogueNo', '')+ ') was used. This will be referred as Cell Line Instance ' +str(instance)+ '</b></font></code>')		
		self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		if 'Depositors' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Depositors: </b>'+protocol_info['Depositors']+'</font></code></td></tr>')
		if 'Biosafety' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Biosafety: </b>'+protocol_info['Biosafety']+'</font></code></td></tr>')
		if 'Shipment' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Shipment: </b>'+protocol_info['Shipment']+'</font></code></td></tr>')
		if 'Permit' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Permit: </b>'+protocol_info['Permit']+'</font></code></td></tr>')	
		if 'GrowthProperty' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Growth Property: </b>'+protocol_info['GrowthProperty']+'</font></code></td></tr>')
		if 'Organism' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Organism: </b>'+protocol_info['Organism']+'</font></code></td></tr>')		    
		if 'Morphology' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Morphology: </b>'+protocol_info['Morphology']+'</font></code></td></tr>')		    
		if 'Organ' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Organ: </b>'+protocol_info['Organ']+'</font></code></td></tr>')		    
		if 'Disease' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Disease: </b>'+protocol_info['Disease']+'</font></code></td></tr>')		    
		if 'Products' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Products: </b>'+protocol_info['Products']+'</font></code></td></tr>')		    
		if 'Applications' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Applications: </b>'+protocol_info['Applications']+'</font></code></td></tr>')		    
		if '' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Receptors: </b>'+protocol_info['Receptors']+'</font></code></td></tr>')		    
		if 'Antigen' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Antigen: </b>'+protocol_info['Antigen']+'</font></code></td></tr>')		    
		if 'DNA' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>DNA: </b>'+protocol_info['DNA']+'</font></code></td></tr>')		    
		if '' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Cytogenetic: </b>'+protocol_info['Cytogenetic']+'</font></code></td></tr>')		    
		if 'Isoenzymes' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Isoenzymes: </b>'+protocol_info['Isoenzymes']+'</font></code></td></tr>')		    
		if 'Age' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Age: </b>'+protocol_info['Age']+'</font></code></td></tr>')		    
		if 'Gender' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Gender: </b>'+protocol_info['Gender']+'</font></code></td></tr>')		    
		if 'Ethnicity' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Ethnicity: </b>'+protocol_info['Ethnicity']+'</font></code></td></tr>')		    
		if 'Comments' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Comments: </b>'+protocol_info['Comments']+'</font></code></td></tr>')		    
		if 'Publications' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Publications: </b>'+protocol_info['Publications']+'</font></code></td></tr>')		    
		if 'RelProduct' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Related Products: </b>'+protocol_info['RelProduct']+'</font></code></td></tr>')		    
		if 'OrgPassageNo' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Orginal Passage No: </b>'+protocol_info['OrgPassageNo']+'</font></code></td></tr>')		    
		if 'Preservation' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Preservation: </b>'+protocol_info['Preservation']+'</font></code></td></tr>')		    
		if 'GrowthMedium' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Growth Medium: </b>'+protocol_info['GrowthMedium']+'</font></code></td></tr>')		    
		
		if 'Passage' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="2"><b>Maintenance History</b></font></code></td></tr>')
		    for pass_info in protocol_info['Passage']:
			self.printfile.write('<tr><td align="left"><code><font size="1">'+pass_info+'</font></code></td></tr>')
		self.printfile.write('</table><br />')
		    
	else:
	    self.printfile.write('<code>No cell line was used for this experiment</code>')
          	
        #---- Instrument Secion ---#
        self.printfile.write('<h3>3. Instrument Settings</h3>')
	
	microscopes = meta.get_field_instances('Instrument|Microscope')
	flowcytometers = meta.get_field_instances('Instrument|Flowcytometer')
	centrifuges = meta.get_field_instances('Instrument|Centrifuge')
	incubators = meta.get_field_instances('Instrument|Incubator')
	ovens = meta.get_field_instances('Instrument|Oven')
	rheometers = meta.get_field_instances('Instrument|Rheometer')
		
	if microscopes:
	    for instance in microscopes:
		protocol_info = self.decode_event_description('Instrument|Microscope|%s'%instance)
		self.printfile.write('<code><font size="1"><b>'+protocol_info.get('Name', 'Not Specified')+' Channel settings</b></font></code>')
		# TODO: For different components the attributes of the components needs to be written
		self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1">Hardware</font></code></th></tr>')
		if 'Stand' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Stand: </b>'+' '.join(map(str,protocol_info['Stand']))+'</font></code></td></tr>')
		if 'Condenser' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Condenser: </b>'+' '.join(map(str,protocol_info['Condenser']))+'</font></code></td></tr>')		
		if 'Stage' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Stage: </b>'+' '.join(map(str,protocol_info['Stage']))+'</font></code></td></tr>')		
		if 'Incubator' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Incubator: </b>'+' '.join(map(str,protocol_info['Incubator']))+'</font></code></td></tr>')		
		self.printfile.write('</table>')
	
		self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1">Optics</font></code></th></tr>')
		if 'LightSource' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>LightSource: </b>'+' '.join(map(str,protocol_info['LightSource']))+'</font></code></td></tr>')
		if 'ExtFilter' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Excitation Filter: </b>'+' '.join(map(str,protocol_info['ExtFilter']))+'</font></code></td></tr>')		
		if 'Mirror' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Mirror: </b>'+' '.join(map(str,protocol_info['Mirror']))+'</font></code></td></tr>')		
		if 'SplitMirror' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>SplitMirror: </b>'+' '.join(map(str,protocol_info['SplitMirror']))+'</font></code></td></tr>')		
		if 'EmsFilter' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Emission Filter: </b>'+' '.join(map(str,protocol_info['EmsFilter']))+'</font></code></td></tr>')		
		if 'Lens' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Lens: </b>'+' '.join(map(str,protocol_info['Lens']))+'</font></code></td></tr>')		
		if 'Detector' in protocol_info:
		    self.printfile.write('<tr><td align="left"><code><font size="1"><b>Detector: </b>'+' '.join(map(str,protocol_info['Detector']))+'</font></code></td></tr>')		
		self.printfile.write('</table>')			
			
	if flowcytometers:
	    for instance in flowcytometers:
		protocol_info = self.decode_event_description('Instrument|Flowcytometer|%s'%instance)
		self.printfile.write('<br /><table border="1"><tr><th colspan="2" align="center"><i>'+protocol_info['Name']+ ' Flowcytometer (%s %s) was used. This will be referred as instance %s' %(protocol_info.get('Manufacturer', ''), protocol_info.get('Model', ''), str(instance))+'</i></th></tr>')		
		for ch, components in protocol_info.iteritems():
		    if ch not in ['Name', 'Manufacturer', 'Model']:
			self.printfile.write('<tr><code><td width=10% align="center"><font size="2"><b>'+ch+'</b></font></code></td>')
			self.printfile.write('<code><td width=90% align="left"><font size="1">')
			for component in components[:-1]: 
			    self.printfile.write(meta.decode_ch_component(component[0])+' >>')
			self.printfile.write(meta.decode_ch_component(components[-1][0])+'</font></td></code></tr>')			
		self.printfile.write('</table><p></p>')
		
	if centrifuges:
	    for instance in centrifuges:
		protocol_info = self.decode_event_description('Instrument|Centrifuge|%s'%instance)	
		
	if incubators:
	    for instance in incubators:
		protocol_info = self.decode_event_description('Instrument|Incubator|%s'%instance)

	if ovens:
	    for instance in ovens:
		protocol_info = self.decode_event_description('Instrument|Oven|%s'%instance)

	if rheometers:
	    for instance in rheometers:
		protocol_info = self.decode_event_description('Instrument|Rheometer|%s'%instance)
		
        #---- Material and Method Secion ---#
        self.printfile.write('<h3>4. Materials and Methods</h3>')  
        for i, timepoint in enumerate(timepoints):
	    for protocol in self.ordered_list(list(set([exp.get_tag_protocol(ev.get_welltag()) for ev in self.events_by_timepoint[timepoint]]))):
            #for protocol in set([exp.get_tag_protocol(ev.get_welltag()) for ev in self.events_by_timepoint[timepoint]]):
		
		self.printfile.write('<tr>')
		
		instance = exp.get_tag_attribute(protocol)
		# protocol info includes the description of the attributes for each of the protocol e.g. Perturbation|Chemical|1 is passed
		protocol_info = self.decode_event_description(protocol)
		# spatial info includes plate well inforamtion for this event well tag e.g. Perturbation|Bio|Wells|1|793
		####spatial_info = self.decode_event_location(ev.get_welltag())  ##THIS THING DOES NOT WORK WHEN SAME EVENT AT SAME TIME POINT HAPPENS
		welltag = exp.get_tag_stump(protocol, 2)+'|Wells|%s|%s'%(instance, str(timepoint)) 
		spatial_info = self.decode_event_location(welltag)
		
		## -- write the description and location of the event --#
                #if (exp.get_tag_event(protocol) == 'Seed') and (meta.get_field('Transfer|Seed|CellLineInstance|%s'%instance) is not None):  
                    #self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         #'</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Seeding from Stock Culture</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
                    #self.printfile.write('<code><font size="1">'+protocol_info[0]+'</font></code><br />')
		    #self.printlocation(spatial_info)
			
                #if exp.get_tag_event(protocol) == 'Harvest': 
                    #self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         #'</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Cell Transfer (Harvest->Seed)</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i)+' & '+str(i+1)+'</font></th></tr></table>')
		    ##self.printfile.write('<code>'+protocol_info[0]+'</code><br />')
		    #self.printCellTransfer(instance, timepoint)
		
		if exp.get_tag_event(protocol) == 'Seed':
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                        '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Seeding from Stock Culture</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Cell Line' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Cell Line']+' were seeded')
		    if 'Seeding Density' in protocol_info:
			self.printfile.write(' with a density of '+protocol_info['Seeding Density'])
		    self.printfile.write('</font></code></td></tr>')			   
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)		    
		
		#Chemical perturbation
		if exp.get_tag_event(protocol) == 'Chemical': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Chemical Perturbation</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Name' in protocol_info:	
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Chemical Name </b>'+protocol_info['Name']+'</font></code></td></tr>')
		    if 'PerturbConc' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Perturbing Concentration </b>'+' '.join(protocol_info['PerturbConc'])+'</font></code></td></tr>')	
		    if 'StockConc' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Stock Concentration </b>'+' '.join(protocol_info['StockConc'])+'</font></code></td></tr>')	
		    if 'Manufacturer' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Manufacturer </b>'+protocol_info['Manufacturer']+'</font></code></td></tr>')	
		    if 'CatNum' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Catalogue Number </b>'+protocol_info['CatNum']+'</font></code></td></tr>')	
		    if 'Storage' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Storage </b>'+protocol_info['Storage']+'</font></code></td></tr>')			
		    if 'Other' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Other Information </b>'+protocol_info['Other']+'</font></code></td></tr>')
		    if 'Additive' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Additive </b></font></code></td></tr>')
			for row in protocol_info['Additive']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	    
		    if 'Step' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure </b></font></code></td></tr>')
			for row in protocol_info['Step']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'URL' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Related website </b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['URL']+'</font></code></td></tr>')
		    if 'AttachFiles' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Attached Files </b></font></code></td></tr>')
			for row in protocol_info['AttachFiles']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')						    
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)		

		#Biological perturbation
		if exp.get_tag_event(protocol) == 'Biological': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Biological Perturbation</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'RNAi' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>RNAi Used</b></font></code></td></tr>')
			for row in protocol_info['RNAi']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'Target' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Target</b></font></code></td></tr>')
			for row in protocol_info['Target']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')		    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)			    
			    
		#Physical perturbation
		if exp.get_tag_event(protocol) == 'Physical': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Physical Perturbation</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Material' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Material Used</b></font></code></td></tr>')
			for row in protocol_info['Material']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)	
		    
		#Chemical Dye Labeling
		if exp.get_tag_event(protocol) == 'Dye': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Dye Labeling</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')
		    if 'Dye Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Dye Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Dye Name']+'</font></code></td></tr>')
		    if 'Dye Concentration' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Dye Concentration</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Dye Concentration']+'</font></code></td></tr>')
		    if 'Labeling Concentration' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Labeling Concentration</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Labeling Concentration']+'</font></code></td></tr>')	
		    if 'Stock Concentration' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Stock Concentration</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Stock Concentration']+'</font></code></td></tr>')	
		    if 'Manufacturer' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Manufacturer</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Manufacturer']+'</font></code></td></tr>')	
		    if 'Catalogue Number' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Catalogue Number</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Catalogue Number']+'</font></code></td></tr>')	
		    if 'Storage' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Storage</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Storage']+'</font></code></td></tr>')			
		    if 'Other Information' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Other Information</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Other Information']+'</font></code></td></tr>')
		    if 'Additive' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Additive</b></font></code></td></tr>')
			for row in protocol_info['Additive']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'URL' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Related website</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['URL']+'</font></code></td></tr>')
		    if 'Attached Files' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Attached Files</b></font></code></td></tr>')
			for row in protocol_info['Attached Files']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')						    
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)
		
		#Immunofluorescence Labeling		
		if exp.get_tag_event(protocol) == 'Immuno': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Immunofluroscence Labeling</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Other Information' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Other Information</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Other Information']+'</font></code></td></tr>')
		    if 'Antibody' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Antibody</b></font></code></td></tr>')
			for row in protocol_info['Antibody']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'URL' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Related website</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['URL']+'</font></code></td></tr>')
		    if 'Attached Files' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Attached Files</b></font></code></td></tr>')
			for row in protocol_info['Attached Files']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')						    
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)		
		
		#Genetic		
		if exp.get_tag_event(protocol) == 'Genetic': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Genetic Labeling</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Other Information' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Other Information</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Other Information']+'</font></code></td></tr>')
		    if 'Sequence' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Sequence</b></font></code></td></tr>')
			for row in protocol_info['Sequence']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'URL' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Related website</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['URL']+'</font></code></td></tr>')
		    if 'Attached Files' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Attached Files</b></font></code></td></tr>')
			for row in protocol_info['Attached Files']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')						    
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)			
		
		# Add Meidum   
		if exp.get_tag_event(protocol) == 'Medium': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Add Medium</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Other Information' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Other Information</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Other Information']+'</font></code></td></tr>')
		    if 'Additive' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Additive</b></font></code></td></tr>')
			for row in protocol_info['Additive']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'URL' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['URL']+'</font></code></td></tr>')
		    if 'Attached Files' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Attached Files</b></font></code></td></tr>')
			for row in protocol_info['Attached Files']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')						    
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)	
		
		# Wash    
		if exp.get_tag_event(protocol) == 'Wash': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Washing </th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')			
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Other Information' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Other Information</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Other Information']+'</font></code></td></tr>')						    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)		
		
		# Centrifugation    
		if exp.get_tag_event(protocol) == 'Centrifugation': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Centrifugation</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">Centrifuge instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'RPM' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>RPM Profile</b></font></code></td></tr>')
			for row in protocol_info['RPM']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')			    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)			    

		# Drying
		if exp.get_tag_event(protocol) == 'Drying': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Drying</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">Oven instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'Gas Composition' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Gas Composition</b></font></code></td></tr>')
			for row in protocol_info['Gas Composition']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')			    
		    if 'Temperature Gradient' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Temperature Gradient</b></font></code></td></tr>')
			for row in protocol_info['Temperature Gradient']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'Humidity Gradient' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Humidity Gradient</b></font></code></td></tr>')
			for row in protocol_info['Humidity Gradient']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')
		    if 'Pressure Gradient' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Pressure Gradient</b></font></code></td></tr>')
			for row in protocol_info['Pressure Gradient']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')		    
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')		
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)		
		
		# Incubation
		if exp.get_tag_event(protocol) == 'Incubation': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Incubation</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">Incubator instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'Gas Composition' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Gas Composition</b></font></code></td></tr>')
			for row in protocol_info['Gas Composition']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')			    
		    if 'Temperature Gradient' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Temperature Gradient</b></font></code></td></tr>')
			for row in protocol_info['Temperature Gradient']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'Humidity Gradient' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Humidity Gradient</b></font></code></td></tr>')
			for row in protocol_info['Humidity Gradient']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')		
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)	
		
		# Rheological Manipulation
		if exp.get_tag_event(protocol) == 'RheoManipulation': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Rheological Manipulation</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')
		    if 'Protocol Name' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Protocol Name</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">'+protocol_info['Protocol Name']+'</font></code></td></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used</b></font></code></td></tr>')
			self.printfile.write('<tr><td align="left"><code><font size="1">Rheometer instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'Gel Composition' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Gel Composition</b></font></code></td></tr>')
			for row in protocol_info['Gel Composition']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')			    
		    if 'Gel Profile' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Gel Profile</b></font></code></td></tr>')
			for row in protocol_info['Gel Profile']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')	
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')		
		    self.printfile.write('</table>')		
		    self.printlocation(spatial_info)
		
		if exp.get_tag_event(protocol) == 'FCS': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                         '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Flow Data</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used: </b>Flowcytometer instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'File Format' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>File Format: </b>'+protocol_info['File Format']+'</font></code></td></tr>')
		    if 'Software' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Software: </b>'+protocol_info['Software']+'</font></code></td></tr>')				
		    self.printfile.write('</table>')
		    self.printLoacationandURL(spatial_info, instance,timepoint, 'FCS')
		           
                if exp.get_tag_event(protocol) == 'HCS': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                        '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Static Image Data</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used: </b>Microscope instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'File Format' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>File Format: </b>'+protocol_info['File Format']+'</font></code></td></tr>')
		    if 'Pixel Size' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Pixel Size: </b>'+protocol_info['Pixel Size']+'</font></code></td></tr>')
		    if 'Pixel Convertion' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Pixel Convertion: </b>'+protocol_info['Pixel Convertion']+'</font></code></td></tr>')
		    if 'Software' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Software: </b>'+protocol_info['Software']+'</font></code></td></tr>')				
		    self.printfile.write('</table>')
		    self.printLoacationandURL(spatial_info, instance,timepoint, 'HCS')

		if exp.get_tag_event(protocol) == 'TLM': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                        '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Timelapse Image Data</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used: </b>Microscope instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'File Format' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>File Format: </b>'+protocol_info['File Format']+'</font></code></td></tr>')
		    if 'Time Interval' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Time Interval: </b>'+protocol_info['Time Interval']+'</font></code></td></tr>')
		    if 'Frame Number' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Frame Number: </b>'+protocol_info['Frame Number']+'</font></code></td></tr>')
		    if 'Stack Process' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Stack Process: </b>'+protocol_info['Stack Process']+'</font></code></td></tr>')
		    if 'Pixel Size' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Pixel Size: </b>'+protocol_info['Pixel Size']+'</font></code></td></tr>')
		    if 'Pixel Convertion' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Pixel Convertion: </b>'+protocol_info['Pixel Convertion']+'</font></code></td></tr>')
		    if 'Software' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Software: </b>'+protocol_info['Software']+'</font></code></td></tr>')				
		    self.printfile.write('</table>')
		    self.printLoacationandURL(spatial_info, instance,timepoint, 'TLM')		    

		if exp.get_tag_event(protocol) == 'RHE': 
		    self.printfile.write('<br /><table border="0"><tr><th align="left" width="20%" BGCOLOR=#CCCCCC><b>'+exp.format_time_string(timepoint)+
		                        '</b><i> hr</i></th><th align="center" width="65%" BGCOLOR=#CCCCCC>Rheometer Data</th><th align="right" width="15%" BGCOLOR=#CCCCCC><font size=-2>Step '+str(i+1)+'</font></th></tr></table>')
		    self.printfile.write('<br /><table border="0"><tr><th align="left"><code><font size="1"></font></code></th></tr>')	
		    if 'Instrument Instance' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Instrument Used: </b>Rheometer instance '+protocol_info['Instrument Instance']+' was used for this purpose</font></code></td></tr>')				
		    if 'Procedure' in protocol_info:
			self.printfile.write('<tr><td align="left"><code><font size="1"><b>Procedure</b></font></code></td></tr>')
			for row in protocol_info['Procedure']:
			    self.printfile.write('<tr><td align="left"><code><font size="1">'+row+'</font></code></td></tr>')
				
                #if exp.get_tag_event(protocol) == 'Text': # to implement if there are events at the same timepoint write those event first then the critical point
                    #self.printfile.write('<code><font size="1" color="#FF0000">Critical point: '+meta.get_field('Notes|Text|Description|%s'%instance)+'</font></code><br />')                
		
		#if exp.get_tag_event(protocol) == 'Hint': 
		    #self.printfile.write('<code><font size="1" color="#990000">Hint: '+meta.get_field('Notes|Hint|Description|%s'%instance)+'</font></code><br />')                		
		
		#if exp.get_tag_event(protocol) == 'Rest': 
		    #self.printfile.write('<code><font size="1" color="#CC9933">Rest: '+meta.get_field('Notes|Rest|Description|%s'%instance)+'</font></code><br />') 
		
		#if exp.get_tag_event(protocol) == 'URL': 
		    #self.printfile.write('<code><font size="1" color="#666600">URL: To find out more information please visit '+meta.get_field('Notes|URL|Description|%s'%instance)+'</font></code><br />')
		    
		#if exp.get_tag_event(protocol) == 'MultiMedia': 
		    #self.printfile.write('<code><font size="1" color="#99CC33">MultiMedia: For more information please watch the media file: '+meta.get_field('Notes|MultiMedia|Description|%s'%instance)+'</font></code><br />')
		    
            self.printfile.write('</tr>')
            #self.printfile.write('<br />')   
	self.printfile.write('</table>')      
        
        #---- Protocol Map ---#             
        self.printfile.write('<br />'.join(['<h3>5. Methodology Map</h3>',                                 
                             '<br/><br/>',                     
                             '<center><img src=myImage.png width=500 height=600></center>',
                             '</body></html>']))
                                                     
        self.printfile.close()  

    #----------------------------------------------------------------------
    def sendToPrinter(self):
        """"""
        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintFile(self.html.GetOpenedPage())    
    
    def decode_event_description(self, protocol):
	meta = ExperimentSettings.getInstance()
	instance = exp.get_tag_attribute(protocol)
	tag_stump = exp.get_tag_stump(protocol, 2)
	metadata = {}
	
        if exp.get_tag_type(protocol) == 'Overview':
	    for attr in meta.get_attribute_list(tag_stump):
		metadata[attr] = meta.get_field(tag_stump+'|'+attr)
	    return metadata
	
	if exp.get_tag_event(protocol) == 'CellLine':
	    passages = []
	    for attr in meta.get_attribute_list_by_instance(tag_stump, instance):
		if attr.startswith('Passage'):
		    passages.append(attr)
		else:
		    metadata[attr] = meta.get_field(tag_stump+'|'+attr+'|'+instance)
	    if passages:
		passage_info = []
		for passage in sorted(passages, key=meta.stringSplitByNumbers):
		    passage_info.append('%s was done by %s'%(passage, self.get_passage_admin_info(meta.get_field('Sample|CellLine|%s|%s'%(passage,instance)))))
		metadata['Passage'] = passage_info
	    return metadata         
	
	if exp.get_tag_event(protocol) == 'Microscope':	   
	    for attr in meta.get_attribute_list(tag_stump):
		if attr.startswith('Name'):
		    metadata[attr] = meta.get_field(tag_stump+'|'+attr+'|'+instance)
		else:
		    metadata[attr] = [f for f in meta.get_field(tag_stump+'|'+attr+'|'+instance)] 
	    return metadata
	
	if exp.get_tag_event(protocol) in ('Flowcytometer', 'Centrifuge', 'Incubator', 'Oven', 'Rheometer'):
	    for attr in meta.get_attribute_list(tag_stump):
		metadata[attr] = meta.get_field(tag_stump+'|'+attr+'|'+instance)
	    return metadata
		
	if exp.get_tag_event(protocol) == 'Seed':
	    if meta.get_field('Transfer|Seed|CellLineInstance|%s'%instance) is not None:                    
		metadata['Cell Line']= meta.get_field('Sample|CellLine|Name|%s'%meta.get_field('Transfer|Seed|CellLineInstance|%s'%instance))	  
	    if meta.get_field('Transfer|Seed|SeedingDensity|%s'%instance) is not None: 
		metadata['Seeding Density']= '%s %s' %(meta.get_field('Transfer|Seed|SeedingDensity|%s'%instance)[0], meta.get_field('Transfer|Seed|SeedingDensity|%s'%instance)[1]) 	    
	    if meta.get_field('Transfer|Seed|Step1|%s'%instance) is not None: # At least one step/additive is present
		metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	
	    return metadata
	
	if exp.get_tag_event(protocol) in ('Seed', 'Chemical', 'Biological', 'Physical', 'Dye', 'Immuno', 'Genetic', 'Medium', 'Wash', 'Storage', 'Initiation',
	                                   'Centrifugation', 'Incubation', 'RheoManipulation', 'Drying',	                                   
	                                   'TLM', 'HCS','FCS', 'RHE', 'Text', 'Hint', 'Rest', 'URL', 'MultiMedia'):
	    for attr in meta.get_attribute_list_by_instance(tag_stump, instance):
		if attr.endswith('1'):
		    metadata[attr[:-1]] = self.decode_subprocess(protocol, attr[:-1])
		elif attr.startswith('AttachFiles'):
		    metadata['AttachFiles'] = [f for f in meta.get_field(tag_stump+'|AttachFiles|%s'%instance)] 
		elif attr.startswith('URL'):
		    metadata['URL'] = ' %s'%meta.get_field(tag_stump+'|URL|%s'%instance)		
		else:
		    metadata[attr] = meta.get_field(tag_stump+'|'+attr+'|'+instance)	
	    return metadata

        #if exp.get_tag_event(protocol) == 'Biological':	
	    #for attr in meta.get_attribute_list_by_instance(tag_stump, instance):
		#if attr.startswith('RNAi1'):
		    #metadata['RNAi'] = self.decode_subprocess(protocol, 'RNAi')
		#elif attr.startswith('Target1'):
		    #metadata['Target'] = self.decode_subprocess(protocol, 'Target')
		#elif attr.startswith('Target1'):
		    #metadata['Target'] = self.decode_subprocess(protocol, 'Target')		
		#elif attr.startswith('AttachFiles'):
		    #metadata['AttachFiles'] = [f for f in meta.get_field(tag_stump+'|AttachFiles|%s'%instance)] 
		#elif attr.startswith('URL'):
		    #metadata['URL'] = ' %s'%meta.get_field(tag_stump+'|URL|%s'%instance)		
		#else:
		    #metadata[attr] = meta.get_field(tag_stump+'|'+attr+'|'+instance)	
	    #return metadata	  
	
	    #if meta.get_field('Perturbation|Biological|RNAi1|%s'%instance) is not None:
		#metadata['RNAi']  = self.decode_subprocess(protocol, 'RNAi')	    
	    #if meta.get_field('Perturbation|Biological|Target1|%s'%instance) is not None:
		#metadata['Target'] = self.decode_subprocess(protocol, 'Target')		    
	    #if meta.get_field('Perturbation|Biological|Additive1|%s'%instance) is not None:
		#metadata['Additive'] = self.decode_subprocess(protocol, 'Additive')	
	    #if meta.get_field('Perturbation|Biological|Step1|%s'%instance) is not None:
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')		    
            #return metadata
	
	#if exp.get_tag_event(protocol) == 'Physical':	    
	    #if meta.get_field('Perturbation|Physical|Material1|%s'%instance) is not None:
		#metadata['Material'] = self.decode_subprocess(protocol, 'Material')	    
	    #if meta.get_field('Perturbation|Physical|Step1|%s'%instance) is not None:
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')		    
	    #return metadata	
	
	#if exp.get_tag_event(protocol) == 'Dye':
	    #if meta.get_field('Labeling|Dye|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('Labeling|Dye|Name|%s'%instance)
	    #if meta.get_field('Labeling|Dye|DyeName|%s'%instance) is not None:                    
		#metadata['Dye Name'] = meta.get_field('Labeling|Dye|DyeName|%s'%instance)
	    #if meta.get_field('Labeling|Dye|Manufacturer|%s'%instance) is not None:
		#metadata['Dye Concentration'] = '%s,%s' %(meta.get_field('Labeling|Dye|Manufacturer|%s'%instance, default=''), meta.get_field('Labeling|Dye|CatNum|%s'%instance, default=''))
	    #if meta.get_field('Labeling|Dye|LabelingConc|%s'%instance) is not None: 
		#metadata['Labeling Concentration']= ' at a concentration of %s %s' %(meta.get_field('Labeling|Dye|LabelingConc|%s'%instance)[0], meta.get_field('Labeling|Dye|LabelingConc|%s'%instance)[1]) 
	    #if meta.get_field('Labeling|Dye|StockConc|%s'%instance) is not None:    
		#metadata['Stock Concentration']= '%s %s' %(meta.get_field('Labeling|Dye|StockConc|%s'%instance)[0], meta.get_field('Labeling|Dye|StockConc|%s'%instance)[1])
	    #if meta.get_field('Labeling|Dye|Manufacturer|%s'%instance) is not None: 
		#metadata['Manufacturer'] = meta.get_field('Labeling|Dye|Manufacturer|%s'%instance)
	    #if meta.get_field('Labeling|Dye|CatNum|%s'%instance) is not None: 
		#metadata['Catalogue Number'] = meta.get_field('Labeling|Dye|CatNum|%s'%instance)
	    #if meta.get_field('Labeling|Dye|Storage|%s'%instance) is not None: 
		#metadata['Storage'] = meta.get_field('Labeling|Dye|Storage|%s'%instance) 
	    #if meta.get_field('Labeling|Dye|Other|%s'%instance) is not None: 
		#metadata['Other Information'] = meta.get_field('Labeling|Dye|Other|%s'%instance) 	
	    #if meta.get_field('Labeling|Dye|AttachFiles|%s'%instance) is not None:
		#metadata['Attached Files'] = [f for f in meta.get_field('Labeling|Dye|AttachFiles|%s'%instance)]   	    
	    #if meta.get_field('Labeling|Dye|URL|%s'%instance) is not None: 
		#metadata['URL'] = ' %s'%meta.get_field('Labeling|Dye|URL|%s'%instance)	    
	    #if meta.get_field('Labeling|Dye|Additive1|%s'%instance) is not None: 
		#metadata['Additive'] = self.decode_subprocess(protocol, 'Additive')
	    #if meta.get_field('Labeling|Dye|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	
	    #return metadata	
	
	#if exp.get_tag_event(protocol) == 'Immuno':
	    #if meta.get_field('Labeling|Immuno|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('Labeling|Immuno|Name|%s'%instance)
	    #if meta.get_field('Labeling|Immuno|Other|%s'%instance) is not None: 
		#metadata['Other Information'] = meta.get_field('Labeling|Immuno|Other|%s'%instance) 	
	    #if meta.get_field('Labeling|Immuno|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('Labeling|Immuno|AttachFiles|%s'%instance)]    	    
	    #if meta.get_field('Labeling|Immuno|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('Labeling|Immuno|URL|%s'%instance)	    
	    #if meta.get_field('Labeling|Immuno|Antibody1|%s'%instance) is not None: 
		#metadata['Antibody'] = self.decode_subprocess(protocol, 'Antibody')
	    #if meta.get_field('Labeling|Immuno|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	
	    #return metadata	
	
	#if exp.get_tag_event(protocol) == 'Genetic':
	    #if meta.get_field('Labeling|Genetic|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('Labeling|Genetic|Name|%s'%instance)
	    #if meta.get_field('Labeling|Genetic|Other|%s'%instance) is not None: 
		#metadata['Other Information'] = meta.get_field('Labeling|Genetic|Other|%s'%instance) 	
	    #if meta.get_field('Labeling|Genetic|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('Labeling|Genetic|AttachFiles|%s'%instance)]    	    
	    #if meta.get_field('Labeling|Genetic|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('Labeling|Genetic|URL|%s'%instance)	    
	    #if meta.get_field('Labeling|Genetic|Sequence1|%s'%instance) is not None: 
		#metadata['RPM']  = self.decode_subprocess(protocol, 'Sequence')
	    #if meta.get_field('Labeling|Genetic|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	    
	    #return metadata  	    

	#if exp.get_tag_event(protocol) == 'Medium':
	    #if meta.get_field('AddProcess|Medium|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('AddProcess|Medium|Name|%s'%instance)
	    #if meta.get_field('AddProcess|Medium|Other|%s'%instance) is not None: 
		#metadata['Other Information'] = meta.get_field('AddProcess|Medium|Other|%s'%instance) 	
	    #if meta.get_field('AddProcess|Medium|AttachFiles|%s'%instance) is not None:
		#metadata['Attached Files'] = [f for f in meta.get_field('AddProcess|Medium|AttachFiles|%s'%instance)]    	    
	    #if meta.get_field('AddProcess|Medium|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('AddProcess|Medium|URL|%s'%instance)	    
	    #if meta.get_field('AddProcess|Medium|Additive1|%s'%instance) is not None: 
		#metadata['Additive'] = self.decode_subprocess(protocol, 'Additive')
	    #if meta.get_field('AddProcess|Medium|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	
	    #return metadata	
			
	#if exp.get_tag_event(protocol) == 'Wash':
	    #if meta.get_field('AddProcess|Wash|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('AddProcess|Wash|Name|%s'%instance)
	    #if meta.get_field('AddProcess|Wash|Other|%s'%instance) is not None: 
		#metadata['Other Information'] = meta.get_field('AddProcess|Wash|Other|%s'%instance) 	
	    #if meta.get_field('AddProcess|Wash|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('AddProcess|Wash|AttachFiles|%s'%instance)] 	    
	    #if meta.get_field('AddProcess|Wash|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('AddProcess|Wash|URL|%s'%instance)	    
	    #if meta.get_field('AddProcess|Wash|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	
	    #return metadata 
	
	#if exp.get_tag_event(protocol) == 'Centrifugation':
	    #if meta.get_field('InstProcess|Centrifugation|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('InstProcess|Centrifugation|Name|%s'%instance)
	    #if meta.get_field('InstProcess|Centrifugation|CentrifugeInstance|%s'%instance) is not None: 
		#metadata['Instrument Instance'] = meta.get_field('InstProcess|Centrifugation|CentrifugeInstance|%s'%instance) 	
	    #if meta.get_field('InstProcess|Centrifugation|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('InstProcess|Centrifugation|AttachFiles|%s'%instance)]    	    
	    #if meta.get_field('InstProcess|Centrifugation|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('InstProcess|Centrifugation|URL|%s'%instance)	    
	    #if meta.get_field('InstProcess|Centrifugation|RPM1|%s'%instance) is not None: 
		#metadata['RPM']  = self.decode_subprocess(protocol, 'RPM')
	    #if meta.get_field('InstProcess|Centrifugation|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	    
	    #return metadata             

	#if exp.get_tag_event(protocol) == 'Drying':
	    #if meta.get_field('InstProcess|Drying|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('InstProcess|Drying|Name|%s'%instance)
	    #if meta.get_field('InstProcess|Drying|OvenInstance|%s'%instance) is not None: 
		#metadata['Instrument Instance'] = meta.get_field('InstProcess|Drying|OvenInstance|%s'%instance) 	
	    #if meta.get_field('InstProcess|Drying|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('InstProcess|Drying|AttachFiles|%s'%instance)]
	    #if meta.get_field('InstProcess|Drying|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('InstProcess|Drying|URL|%s'%instance)	    
	    #if meta.get_field('InstProcess|Drying|Gas1|%s'%instance) is not None: 
		#metadata['Gas Gradient'] = self.decode_subprocess(protocol, 'Gas')
	    #if meta.get_field('InstProcess|Drying|Temperature1|%s'%instance) is not None: 
		#metadata['Temperature Gradient'] = self.decode_subprocess(protocol, 'Temperature')	 
	    #if meta.get_field('InstProcess|Drying|Humidity1|%s'%instance) is not None: 
		#metadata['Humidity Gradient'] = self.decode_subprocess(protocol, 'Humidity')
	    #if meta.get_field('InstProcess|Drying|Pressure1|%s'%instance) is not None: 
		#metadata['Pressure Gradient'] = self.decode_subprocess(protocol, 'Pressure')	    
	    #if meta.get_field('InstProcess|Drying|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	    
	    #return metadata   
	
	#if exp.get_tag_event(protocol) == 'Incubation':
	    
	    #if meta.get_field('InstProcess|Incubation|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('InstProcess|Incubation|Name|%s'%instance)
	    #if meta.get_field('InstProcess|Incubation|IncubatorInstance|%s'%instance) is not None: 
		#metadata['Instrument Instance'] = meta.get_field('InstProcess|Incubation|IncubatorInstance|%s'%instance) 	
	    #if meta.get_field('InstProcess|Incubation|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('InstProcess|Incubation|AttachFiles|%s'%instance)]
	    #if meta.get_field('InstProcess|Incubation|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('InstProcess|Incubation|URL|%s'%instance)	    
	    #if meta.get_field('InstProcess|Incubation|Gas1|%s'%instance) is not None: 
		#metadata['Gas Gradient'] = self.decode_subprocess(protocol, 'Gas')
	    #if meta.get_field('InstProcess|Incubation|Temperature1|%s'%instance) is not None: 
		#metadata['Temperature Gradient'] = self.decode_subprocess(protocol, 'Temperature')	 
	    #if meta.get_field('InstProcess|Incubation|Humidity1|%s'%instance) is not None: 
		#metadata['Humidity Gradient'] = self.decode_subprocess(protocol, 'Humidity')
	    #if meta.get_field('InstProcess|Incubation|Pressure1|%s'%instance) is not None: 
		#metadata['Pressure Gradient'] = self.decode_subprocess(protocol, 'Pressure')	    
	    #if meta.get_field('InstProcess|Incubation|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	    
	    #return metadata 
	
	#if exp.get_tag_event(protocol) == 'RheoManipulation':
	    #if meta.get_field('InstProcess|RheoManipulation|Name|%s'%instance) is not None:
		#metadata['Protocol Name'] = meta.get_field('InstProcess|RheoManipulation|Name|%s'%instance)
	    #if meta.get_field('InstProcess|RheoManipulation|RheometerInstance|%s'%instance) is not None: 
		#metadata['Instrument Instance'] = meta.get_field('InstProcess|RheoManipulation|RheometerInstance|%s'%instance) 	
	    #if meta.get_field('InstProcess|RheoManipulation|AttachFiles|%s'%instance) is not None: 
		#metadata['Attached Files'] = [f for f in meta.get_field('InstProcess|RheoManipulation|AttachFiles|%s'%instance)]
	    #if meta.get_field('InstProcess|RheoManipulation|URL|%s'%instance) is not None: 
		#metadata['URL'] = meta.get_field('InstProcess|RheoManipulation|URL|%s'%instance)	    
	    #if meta.get_field('InstProcess|RheoManipulation|GelComposition1|%s'%instance) is not None: 
		#metadata['Gel Composition'] = self.decode_subprocess(protocol, 'GelComposition')
	    #if meta.get_field('InstProcess|RheoManipulation|GelProfile1|%s'%instance) is not None: 
		#metadata['Gel Profile'] = self.decode_subprocess(protocol, 'GelProfile')		    
	    #if meta.get_field('InstProcess|RheoManipulation|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')	    
	    #return metadata    

	#if exp.get_tag_event(protocol) == 'FCS':
	    #if meta.get_field('DataAcquis|FCS|FlowcytometerInstance|%s'%instance) is not None:
		#metadata['Instrument Instance'] = meta.get_field('DataAcquis|FCS|FlowcytometerInstance|%s'%instance)
	    #if meta.get_field('DataAcquis|FCS|Format|%s'%instance) is not None:
		#metadata['File Format'] = meta.get_field('DataAcquis|FCS|Format|%s'%instance)
	    #if meta.get_field('DataAcquis|FCS|Software|%s'%instance) is not None:
		#metadata['Software'] = meta.get_field('DataAcquis|FCS|Software|%s'%instance)
	    #return metadata
	
	#if exp.get_tag_event(protocol) == 'RHE':
	    #if meta.get_field('DataAcquis|RHE|RheometerInstance|%s'%instance) is not None:
		#metadata['Instrument Instance'] = meta.get_field('DataAcquis|RHE|RheometerInstance|%s'%instance)
	    #if meta.get_field('DataAcquis|RHE|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')
	    #return metadata

	#if exp.get_tag_event(protocol) == 'HCS':
	    #if meta.get_field('DataAcquis|HCS|MicroscopeInstance|%s'%instance) is not None:
		#metadata['Instrument Instance'] = meta.get_field('DataAcquis|HCS|MicroscopeInstance|%s'%instance)
	    #if meta.get_field('DataAcquis|HCS|Format|%s'%instance) is not None: 
		#metadata['File Format'] = meta.get_field('DataAcquis|HCS|Format|%s'%instance)
	    #if meta.get_field('DataAcquis|HCS|PixelSize|%s'%instance) is not None: 
		#metadata['Pixel Size'] = meta.get_field('DataAcquis|HCS|PixelSize|%s'%instance)
	    #if meta.get_field('DataAcquis|HCS|PixelConvert|%s'%instance) is not None: 
		#metadata['Pixel Convertion'] = meta.get_field('DataAcquis|HCS|PixelConvert|%s'%instance)
	    #if meta.get_field('DataAcquis|HCS|Software|%s'%instance) is not None:
		#metadata['Software'] = meta.get_field('DataAcquis|HCS|Software|%s'%instance)	    
	    #return metadata

	#if exp.get_tag_event(protocol) == 'TLM':
	    #if meta.get_field('DataAcquis|TLM|MicroscopeInstance|%s'%instance) is not None:
		#metadata['Instrument Instance'] = meta.get_field('DataAcquis|TLM|MicroscopeInstance|%s'%instance)
	    #if meta.get_field('DataAcquis|TLM|Format|%s'%instance) is not None: 
		#metadata['File Format'] = meta.get_field('DataAcquis|TLM|Format|%s'%instance)
	    #if meta.get_field('DataAcquis|TLM|TimeInterval|%s'%instance) is not None: 
		#metadata['Time Interval'] = meta.get_field('DataAcquis|TLM|TimeInterval|%s'%instance)	    
	    #if meta.get_field('DataAcquis|TLM|FrameNumber|%s'%instance) is not None: 
		#metadata['Frame Number'] = meta.get_field('DataAcquis|TLM|FrameNumber|%s'%instance)	    
	    #if meta.get_field('DataAcquis|TLM|StackProcess|%s'%instance) is not None: 
		#metadata['Stack Process'] = meta.get_field('DataAcquis|TLM|StackProcess|%s'%instance)	    	    
	    #if meta.get_field('DataAcquis|TLM|PixelSize|%s'%instance) is not None: 
		#metadata['Pixel Size'] = meta.get_field('DataAcquis|TLM|PixelSize|%s'%instance)
	    #if meta.get_field('DataAcquis|TLM|PixelConvert|%s'%instance) is not None: 
		#metadata['Pixel Convertion'] = meta.get_field('DataAcquis|TLM|PixelConvert|%s'%instance)
	    #if meta.get_field('DataAcquis|TLM|Software|%s'%instance) is not None:
		#metadata['Software'] = meta.get_field('DataAcquis|TLM|Software|%s'%instance)	    
	    #return metadata
        
	#if exp.get_tag_event(protocol) == 'RHE':
	    #if meta.get_field('DataAcquis|RHE|RheometerInstance|%s'%instance) is not None:
		#metadata['Instrument Instance'] = meta.get_field('DataAcquis|RHE|RheometerInstance|%s'%instance) 
	    #if meta.get_field('DataAcquis|RHE|Step1|%s'%instance) is not None: 
		#metadata['Procedure'] = self.decode_subprocess(protocol, 'Step')
	    #return metadata

        # ***********************************   CHANGE ENDS    ******************************#
	



    def decode_event_location(self, plate_well_info):
	d = {}
	for pw in meta.get_field(plate_well_info):
	    plate = pw[0]
	    well = pw[1]
	    
	    if d.get(plate, None) is None:
		d[plate] = [well]
	    else:
		d[plate] += [well]
		
	return d 
    
    def get_passage_admin_info(self, passage):
	for stp in passage:
	    if stp[0] == 'ADMIN':
		return '%s on %s. Cells were splited at a ratio of 1:%s, and the seeding density was %s cells per %s'%(stp[1][0], stp[1][1], stp[1][2], stp[1][3], stp[1][4])
    
    #----------------------------------------------------------------------
    def decode_subprocess(self, protocol, token):
	"""This method organize the steps of a subprocess and format it for printing"""
	tag_stump = exp.get_tag_stump(protocol, 2)
	instance = exp.get_tag_attribute(protocol)
	process_info = []
	rows = meta.get_Row_Numbers(protocol, token)
	
	if rows:    
	    for row in rows:
		# according to token this text needs to be customized
		rowTAG = tag_stump+'|%s|%s' %(row, instance)
		row_info =  meta.get_field(rowTAG)
		text = row+': '
		for e in row_info:
		    text += e+' '
		process_info.append(text)
	return process_info
	
    
    def printlocation(self, spatial_info):
	for plate, wells in spatial_info.iteritems():
	    self.printfile.write('<br /><code><font size="2"><b>'+plate+'</b></font></code>')
	    self.printfile.write('<table border="1">')
	    # TO DO: Resize the print area according to the Plate Format...
	    for row in exp.PlateDesign.get_row_labels(exp.PlateDesign.get_plate_format(plate)):
		self.printfile.write('<tr>')
		for col in exp.PlateDesign.get_col_labels(exp.PlateDesign.get_plate_format(plate)):
		    well = row+col
		    if well in wells:
			self.printfile.write('<code><td BGCOLOR=yellow><font size="1">'+well+'</font></td></code>')
		    else:
			self.printfile.write('<code><td><font size="1">'+well+'</font></td></code>')
		self.printfile.write('</tr>')
	    self.printfile.write('</table><br />')
    
    def printLoacationandURL(self, spatial_info, instance,timepoint, format):
	for plate, wells in spatial_info.iteritems():
	    self.printfile.write('<br /><code><font size="2"><b>'+plate+'</b></font></code>')
	    self.printfile.write('<table border="1">')
	    # TO DO: Resize the print area according to the Plate Format...
	    for row in exp.PlateDesign.get_row_labels(exp.PlateDesign.get_plate_format(plate)):
		self.printfile.write('<tr>')
		for col in exp.PlateDesign.get_col_labels(exp.PlateDesign.get_plate_format(plate)):
		    well = row+col
		    if well in wells:
			self.printfile.write('<code><td BGCOLOR=yellow><font size="1">'+well+'</font></td></code>')
		    else:
			self.printfile.write('<code><td><font size="1">'+well+'</font></td></code>')
		self.printfile.write('</tr>')
	    self.printfile.write('</table><br />')	
	
	    # write the image urls
	    self.printfile.write('<br /><table border="0">')
	    for well in wells:
		pw = []
		pw.append((plate, well))
		self.printfile.write('<tr><code><td width=25% align="left"><font size="1"><b>'+plate+'_'+well+'-> </b></font></code></td>')
		self.printfile.write('<td width=75% align="left">')
		urls = meta.get_field('DataAcquis|%s|Images|%s|%s|%s'%(format, instance,timepoint, str(pw)), [])
		for url in urls:
		    self.printfile.write('<code><font size="1">Data> '+url[0]+'<br />Metadata> '+url[1]+'</font></code><br />')
		self.printfile.write('</td></tr>')
	    self.printfile.write('</table>')	
	    
    def printCellTransfer(self, harvest_inst, timepoint):
	seed_instances = meta.get_protocol_instances('Transfer|Seed|HarvestInstance|')
	for seed_inst in seed_instances:
	    if (meta.get_field('Transfer|Seed|Wells|%s|%s'%(seed_inst, str(timepoint+1))) is not None) and (meta.get_field('Transfer|Seed|HarvestInstance|%s'%seed_inst) == harvest_inst):
		harvest_spatial_info = self.decode_event_location('Transfer|Harvest|Wells|%s|%s'%(harvest_inst, str(timepoint)))
		seed_spatial_info = self.decode_event_location('Transfer|Seed|Wells|%s|%s'%(seed_inst, str(timepoint+1)))
	
	self.printfile.write('<br /><table border="0">')
	self.printfile.write('<tr><td>')
	
	for plate, wells in harvest_spatial_info.iteritems():
	    self.printfile.write('<code><font size="2"><b>'+plate+'</b></font></code>')
	    self.printfile.write('<table border="1">')
	    for row in exp.PlateDesign.get_row_labels(exp.PlateDesign.get_plate_format(plate)):
		self.printfile.write('<tr>')
		for col in exp.PlateDesign.get_col_labels(exp.PlateDesign.get_plate_format(plate)):
		    well = row+col
		    if well in wells:
			self.printfile.write('<code><td BGCOLOR=yellow><font size="1">'+well+'</font></td></code>')
		    else:
			self.printfile.write('<code><td><font size="1">'+well+'</font></td></code>')
		self.printfile.write('</tr>')
	    self.printfile.write('</table>')
	
	self.printfile.write('</td><td> --> </td><td>')

	for plate, wells in seed_spatial_info.iteritems():
	    self.printfile.write('<code><font size="2"><b>'+plate+'</b></font></code><br />')
	    self.printfile.write('<table border="1">')
	    for row in exp.PlateDesign.get_row_labels(exp.PlateDesign.get_plate_format(plate)):
		self.printfile.write('<tr>')
		for col in exp.PlateDesign.get_col_labels(exp.PlateDesign.get_plate_format(plate)):
		    well = row+col
		    if well in wells:
			self.printfile.write('<code><td BGCOLOR=yellow><font size="1">'+well+'</font></td></code>')
		    else:
			self.printfile.write('<code><td><font size="1">'+well+'</font></td></code>')
		self.printfile.write('</tr>')
	    self.printfile.write('</table>')
	self.printfile.write('</td></tr>')	
	self.printfile.write('</table><br />')
    
    def ordered_list(self, event_list):
	notes = []
	for evt in event_list:
	    if evt.startswith('Notes'):
		notes.append(event_list.pop(event_list.index(evt)))
	if notes != []:
	    return event_list+notes
	else:
	    return event_list
		
	
		
    
class wxHTML(HtmlWindow):
    #----------------------------------------------------------------------
    def __init__(self, parent, id):
        html.HtmlWindow.__init__(self, parent, id, style=wx.NO_FULL_REPAINT_ON_RESIZE)
 
 
if __name__ == '__main__':
    app = wx.App(False)
    frame = PrintProtocol()
    #frame.Show()
    app.MainLoop()