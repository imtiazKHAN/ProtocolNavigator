import re
import wx
import os
import icons
from singleton import Singleton
from utils import *
from timeline import Timeline


VERSION = 'ProtocolNavigator_v1.07.01'
# TODO: Updating PlateDesign could be done entirely within 
#       set_field and remove_field.
#
# TODO: Add backwards compatiblize and file versioning.
#

def format_time_string(timepoint):
    '''formats the given time as a string
    '''
    hours = int(timepoint) / 60
    mins = int(timepoint) - 60 * hours
    return '%s:%02d'%(hours, mins)

def get_matchstring_for_subtag(pos, subtag):
    '''matches a subtag at a specific position.
    '''
    return '([^\|]+\|){%s}%s.*'%(pos, subtag)

def get_tag_stump(tag, n_subtags=3):
    return '|'.join(tag.split('|')[:n_subtags])

def get_tag_type(tag):
    return tag.split('|')[0]

def get_tag_event(tag):
    return tag.split('|')[1]

def get_tag_attribute(tag):
    return tag.split('|')[2]

def get_tag_instance(tag):
    return tag.split('|')[3]

def get_tag_timepoint(tag):
    return int(tag.split('|')[4])

def get_tag_well(tag):
    '''Returns the well subtag from image tags of the form:
    DataAcquis|<type>|Images|<inst>|<timepoint>|<well> = [channel_urls, ...]
    '''
    return tag.split('|')[5]

def get_tag_protocol(tag):
    '''returns the tag prefix and instance that define a unique protocol
    eg: get_tag_protocol("CT|Seed|Density|1") ==> "CT|Seed|1"
    '''
    return get_tag_stump(tag,2) + '|' + tag.split('|')[3]


class ExperimentSettings(Singleton):
    
    global_settings = {}
    timeline        = Timeline('TEST_STOCK')
    subscribers     = {}
    #curr_dir =  os.path.dirname(os.path.abspath(__file__))
    #save_file_path = curr_dir+'\\temporary_experiment.txt'    # first assign it to the temp directory
    save_file_path = None
   
   
    def __init__(self):
        pass
    
    def set_field(self, tag, value, notify_subscribers=True):
        self.global_settings[tag] = value
        if re.match(get_matchstring_for_subtag(2, 'Well'), tag):
            self.update_timeline(tag)
        if notify_subscribers:
            self.notify_subscribers(tag)
        print 'SET FIELD: %s = %s'%(tag, value)
        
    def get_field(self, tag, default=None):
        return self.global_settings.get(tag, default)

    def remove_field(self, tag, notify_subscribers=True):
        '''completely removes the specified tag from the metadata (if it exists)
        '''
        #if self.get_field(tag) is not None:
        self.global_settings.pop(tag)
        if re.match(get_matchstring_for_subtag(2, 'Well'), tag):
            self.update_timeline(tag)

        if notify_subscribers:
            self.notify_subscribers(tag)
        print 'DEL FIELD: %s'%(tag)
    
    def remove_harvest_seed_tags(self, h_inst, s_inst):
	'''removes all associated tags with coupled harvest seed tags e.g density, steps etc'''
	h_attrs = self.get_attribute_list_by_instance('Transfer|Harvest', h_inst)
	s_attrs = self.get_attribute_list_by_instance('Transfer|Seed', s_inst)
	if h_attrs:
	    for h_attr in h_attrs:
		self.remove_field('Transfer|Harvest|%s|%s'%(h_attr, h_inst), notify_subscribers =False)
	if s_attrs:
	    for s_attr in s_attrs:
		self.remove_field('Transfer|Seed|%s|%s'%(s_attr, s_inst), notify_subscribers =False)    
		
    def remove_associated_dataacquis_tag(self, wells):
	'''removes all image tags associated with this timepoint and wells  e.g. DataAcquis|*|Images|*|timepoint|[(Plate_Well), ()]'''
	image_tags = self.get_matching_tags('DataAcquis|*|Images|*|*|%s'%str(wells))
	if image_tags:
	    for i_tag in image_tags:
		self.remove_field(i_tag)
	    
    def remove_timeline_attachments(self, timepoint):
	'''removes all notes and attachment from the timeline at the given timepoint'''
	note_tags = self.get_matching_tags('Notes|*|%s|*'%timepoint)
	attach_tags = self.get_matching_tags('Attachments|*|%s|*'%timepoint)
	if note_tags:
	    for n_tag in note_tags:
		self.remove_field(n_tag)
	if attach_tags:
	    for a_tag in attach_tags:
		self.remove_field(a_tag)	

    
    def get_action_tags(self):
        '''returns all existing TEMPORAL tags as list'''
        return [tag for tag in self.global_settings 
                if tag.split('|')[0] in ('Transfer', 'Perturbation', 
                                    'Labeling', 'AddProcess', 'DataAcquis', 'InstProcess', 'Notes')]

    def get_field_instances(self, tag_prefix):
        '''returns a list of unique instance ids for each tag beginning with 
        tag_prefix'''
        ids = set([get_tag_instance(tag) for tag in self.global_settings
                   if tag.startswith(tag_prefix)])
        return list(ids)
    
    def get_attribute_list(self, tag_prefix):
        '''returns a list of attributes name for each tag beginning with 
        tag_prefix'''
        ids = set([get_tag_attribute(tag) for tag in self.global_settings
                   if tag.startswith(tag_prefix)])
        return list(ids)
    
    def get_attribute_list_by_instance(self, tag_prefix, instance=None):
        '''returns a list of all attributes beginning with tag_prefix. If instance
        is passed in, only attributes of the given instance will be returned'''
        ids = set([get_tag_attribute(tag) for tag in self.global_settings
                           if ((tag_prefix is None or tag.startswith(tag_prefix)) and 
                               (instance is None or get_tag_instance(tag) == instance))])
        return list(ids)   
        
        #tags = []
        #for tag in self.global_settings:
            #if ((tag_prefix is None or tag.startswith(tag_prefix)) and 
                #(instance is None or get_tag_instance(tag) == instance)):
                #tag += [tag]
                #ids= set([get_tag_attribute(tag)])
        #return list(ids)
        
    
    def get_attribute_dict(self, protocol):
        '''returns a dict mapping attribute names to their values for a given
        protocol.
        eg: get_attribute_dict('Transfer|Seed|1') -->
               {'SeedingDensity': 12, 'MediumUsed': 'agar', 
                'MediumAddatives': 'None', 'Trypsinization': True}
        '''
        d = {}
        for tag in self.get_matching_tags('|*|'.join(protocol.rsplit('|',1))):
            if (get_tag_attribute(tag) not in ('Wells', 'EventTimepoint', 'Images', 'OriginWells')):
                d[get_tag_attribute(tag)] = self.global_settings[tag]
        return d
    
    def get_eventtype_list(self, tag_prefix):
        '''returns a list of attributes name for each tag beginning with 
        tag_prefix'''
        ids = set([tag.split('|')[1] for tag in self.global_settings
                   if tag.startswith(tag_prefix)])
        return list(ids)
    
    def get_eventclass_list(self, tag_prefix):
        '''returns a list of event class name for each tag beginning with 
        tag_prefix'''
        ids = set([tag.split('|')[0] for tag in self.global_settings
                   if tag.startswith(tag_prefix)])
        return list(ids)

    def get_field_tags(self, tag_prefix=None, instance=None):
        '''returns a list of all tags beginning with tag_prefix. If instance
        is passed in, only tags of the given instance will be returned'''
        tags = []
        for tag in self.global_settings:
            if ((tag_prefix is None or tag.startswith(tag_prefix)) and 
                (instance is None or get_tag_instance(tag) == instance)):
                tags += [tag]
        return tags
    
    def get_matching_tags(self, matchstring):
        '''returns a list of all tags matching matchstring
        matchstring -- a string that matches the tags you want
        eg: Transfer|*
        '''
        tags = []
        for tag in self.global_settings:
            match = True
            for m, subtag in map(None, matchstring.split('|'), tag.split('|')):
                if m != subtag and m not in ('*', None):
                    match = False
                    break
            if match:
                tags += [tag]

        return tags
    
    def get_protocol_instances(self, prefix):
        '''returns a list of protocol instance names for tags 
        matching the given prefix.
        '''
        return list(set([get_tag_instance(tag) 
                         for tag in self.get_field_tags(prefix)]))
    
    def get_new_protocol_id(self, prefix):
        '''returns an id string that hasn't been used for the given tag prefix
        prefix -- eg: Transfer|Seed
        '''
        instances = self.get_protocol_instances(prefix)
        for i in xrange(1, 100000):
            if str(i) not in instances:
                return str(i)
	    
    def get_instance_by_field_value(self, prefix, field_value):
	'''returns instance number given tag prefix and field value
	'''
	return get_tag_instance([tag for tag, value in self.global_settings.iteritems() if value == field_value][0])
    
    def get_stack_ids(self, prefix):
	'''returns the stack ids for a given type of vessels prefix  e.g. ExptVessel|Tube'''
	return set([self.get_field(prefix+'|StackNo|%s'%instance)
	           for instance in sorted(self.get_field_instances(prefix))])
    
    def get_rep_vessel_instance(self, prefix, stack_id):
	''' returns instance number of the vessel for this stack, since all vessels of a given stack has identical settings
	    one instance represents others'''
	for instance in sorted(self.get_field_instances(prefix)):
	    if self.get_field(prefix+'|StackNo|%s'%(instance)) == stack_id:
		return instance   
	
    def clear(self):
        self.global_settings = {}
        PlateDesign.clear()
        #
        # TODO:
        #
        self.timeline = Timeline('TEST_STOCK')
        for matchstring, callbacks in self.subscribers.items():
            for callback in callbacks:
                callback(None)
		
    def onTabClosing(self, event):
	event.Veto()
	dlg = wx.MessageDialog(None, 'Can not delete instance', 'Deleting..', wx.OK| wx.ICON_STOP)
	dlg.ShowModal()
	return    
        
    def get_timeline(self):
        return self.timeline
    
    def does_tag_exists(self, tag_prefix, instnace=None):
	for tag in self.global_settings:
	    if ((tag_prefix is None or tag.startswith(tag_prefix)) and (instnace is None or get_tag_instance(tag) == instnace)):
		return True  
	    else:
		return False	
	
	    
    def is_supp_protocol_filled(self, tag_prefix, instance=None):
	'''tag_prefix is always type|event e.g. AddProcess|Wash
	'''
	for tag in self.global_settings:
	    if ((tag_prefix is None or tag.startswith(tag_prefix)) and (instance is None or get_tag_instance(tag) == instance)):
		if (self.get_field(tag_prefix+'|ProtocolName|%s'%instance) is None) or (self.get_field(tag_prefix+'|Step1|%s'%instance) == ['', '', '']):
		    return False
		else:
		    return True
		

    def update_timeline(self, welltag):
        '''Updates the experiment metadata timeline event associated with the
        action and wells in welltag (eg: 'ExpNum|AddProcess|Spin|Wells|1|1')
        '''
        platewell_ids = self.get_field(welltag, [])
        if platewell_ids == []:
            self.timeline.delete_event(welltag)
        else:
            event = self.timeline.get_event(welltag)
            if event is not None:
                event.set_well_ids(platewell_ids)
            else:
                self.timeline.add_event(welltag, platewell_ids)
		
    def save_file_dialogue(self):
	exp_date = self.get_field('Overview|Project|ExptDate')
	exp_num = self.get_field('Overview|Project|ExptNum')
	exp_title = self.get_field('Overview|Project|Title')
	if self.save_file_path:
	    self.save_to_file()
	    #import ntpath
	    #filename = os.path.splitext(ntpath.basename(self.save_file_path))[0]
	else:
	    filename = 'new_experiment.txt'
	    if None not in [exp_date, exp_num, exp_title]:
		day, month, year = exp_date.split('/')
		filename = '%s%s%s_%s_%s.txt'%(year, month, day , exp_num, exp_title)
	    dlg = wx.FileDialog(None, message='Saving experimental protocol...', 
	                        defaultDir=os.getcwd(), defaultFile=filename, 
	                        wildcard='.txt', 
	                        style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
	    if dlg.ShowModal() == wx.ID_OK:
		self.save_file_path = dlg.GetPath()
		self.save_to_file()
	
    def save_as_file_dialogue(self):
	exp_date = self.get_field('Overview|Project|ExptDate')
	exp_num = self.get_field('Overview|Project|ExptNum')
	exp_title = self.get_field('Overview|Project|Title')
	if self.save_file_path:
	    import ntpath
	    filename = os.path.splitext(ntpath.basename(self.save_file_path))[0]
	else:
	    filename = 'new_experiment.txt'
	    if None not in [exp_date, exp_num, exp_title]:
		day, month, year = exp_date.split('/')
		filename = '%s%s%s_%s_%s.txt'%(year, month, day , exp_num, exp_title)
	dlg = wx.FileDialog(None, message='Saving experimental protocol...', 
                            defaultDir=os.getcwd(), defaultFile=filename, 
                            wildcard='.txt', 
                            style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
	if dlg.ShowModal() == wx.ID_OK:
	    self.save_file_path = dlg.GetPath()
	    self.save_to_file()
	    
    def save_to_file(self):
	if self.save_file_path:
	    try:
		f = open(self.save_file_path, 'w')
		f.write(VERSION+'\n')
		for field, value in sorted(self.global_settings.items()):
		    f.write('%s = %s\n'%(field, repr(value)))
		f.close()	
	    except IOError:
		import wx
		dial = wx.MessageDialog(None, 'No permission to create temporary experimental file in current directory\nPlease save file in separate directory.', 'Error', wx.OK | wx.ICON_ERROR)
		if dial.ShowModal() == wx.ID_OK:
		    self.save_as_file_dialogue()	

    def saveData(self, ctrl, tag, settings_controls):
	if isinstance(ctrl, wx.ListBox) and ctrl.GetStringSelection() == 'Other':
	    other = wx.GetTextFromUser('Insert Other', 'Other')
	    ctrl.Append(other)
	    ctrl.SetStringSelection(other)	
	    
	if len(tag.split('|'))>4:
	    # get the relevant controls for this tag eg, duration, temp controls for this step
	    subtags = []
	    info = []
	    for subtag in [t for t, c in settings_controls.items()]:
		if get_tag_stump(tag, 4) == get_tag_stump(subtag, 4):
		    subtags.append(subtag)
	    for i in range(0, len(subtags)):
		info.append('')
	    for st in subtags:
		if isinstance(settings_controls[st], wx.Choice) or isinstance(settings_controls[st], wx.ListBox):
		    info[int(st.split('|')[4])]=settings_controls[st].GetStringSelection()	
		    #settings_controls[st].SetToolTipString(settings_controls[st].GetStringSelection())
		else:
		    info[int(st.split('|')[4])]=settings_controls[st].GetValue()
		    #settings_controls[st].SetToolTipString(settings_controls[st].GetValue())
	    self.set_field(get_tag_stump(tag, 4), info)  # get the core tag like AddProcess|Spin|Step|<instance> = [duration, description, temp]
	else:
	    if isinstance(ctrl, wx.Choice) or isinstance(ctrl, wx.ListBox):
		self.set_field(tag, ctrl.GetStringSelection())
		#ctrl.SetToolTipString(ctrl.GetStringSelection())
		
	    elif isinstance(ctrl, wx.DatePickerCtrl):
		date = ctrl.GetValue()
		self.set_field(tag, '%02d/%02d/%4d'%(date.Day, date.Month+1, date.Year))
	    else:
		user_input = ctrl.GetValue()
		self.set_field(tag, user_input)	
		#ctrl.SetToolTipString(ctrl.GetValue())
		
    def saving_settings(self, protocol, tag, m_tags):
	import wx
	if not self.get_field(tag):
	    dial = wx.MessageDialog(None, 'Please provide a settings/protocol name', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return	
	if self.checkMandatoryTags(m_tags):
	    filename = self.get_field(tag)+'.txt'
	    dlg = wx.FileDialog(None, message='Saving ...', 
	                        defaultDir=os.getcwd(), defaultFile=filename, 
	                        wildcard='.txt', 
	                        style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
	    if dlg.ShowModal() == wx.ID_OK:
		dirname=dlg.GetDirectory()
		filename=dlg.GetFilename()
		file_path = os.path.join(dirname, filename)
		self.save_settings(file_path, protocol)     
	
    def save_settings(self, file, protocol):
	'''
	saves settings in text file. the settings may include instrument settings, supp protocol, stock flask
	Format:    attr = value          where value may be text, int, list, etc.
	'''
	instance = get_tag_attribute(protocol)
	tag_stump = get_tag_stump(protocol, 2)
	setting_type = get_tag_event(protocol)
	f = open(file,'w')
	f.write(setting_type+'\n')
	attributes = list(set(self.get_attribute_list_by_instance(tag_stump, instance)))
	if 'Wells' in attributes: attributes.remove('Wells')
	for attr in attributes:
	    value = self.get_field(tag_stump+'|%s|%s' %(attr, instance))
	    if attr.endswith('Instance'):
		f.write('Dependency%s = %s\n'%(attr, repr(value))) # to get the ...Instance which will be overwritten 
		for d_attr, d_val in self.get_attribute_dict('%s|%s' %(DEPENDENCY[get_tag_event(protocol)], value)).iteritems():
		    f.write('Dependency%s = %s\n'%(d_attr, repr(d_val)))	
	    else:
		f.write('%s = %s\n'%(attr, repr(value)))
	f.close()	    		

    def load_from_file(self, file, menuitem):
        # Populate the tag structure
        self.clear()
        f = open(file, 'r')
	lines = [line.strip() for line in f]
	if not lines.pop(0).startswith('ProtocolNavigator'):
	    import wx
	    dial = wx.MessageDialog(None, 'Selected file is not a ProtocolNavigator file', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return
	
        for line in lines:
            tag, value = line.split('=', 1)
            tag = tag.strip()
            self.set_field(tag, eval(value), notify_subscribers=False)
        f.close()
	# Disable the open file menu
	menuitem.Enable(False)
	# index the file path
        self.save_file_path = file
	#import ntpath
	#self.temp_file_path = os.path.dirname(os.path.abspath(file))+os.path.splitext(ntpath.basename(self.save_file_path))[0]+'_temp.txt'
		
        # Populate PlateDesign
        PlateDesign.clear()
        for vessel_type in ('Plate', 'Flask', 'Dish', 'Coverslip', 'Tube'):
            prefix = 'ExptVessel|%s'%(vessel_type)
            for inst in self.get_field_instances(prefix):
                d = self.get_attribute_dict(prefix+'|'+inst)
                shape = d.get('Design', None)
                if shape is None:
                    shape = (1,1)
                group = d.get('StackName', None)
                PlateDesign.add_plate(vessel_type, inst, shape, group)
            
        # Update everything
        for tag in self.global_settings:
            self.notify_subscribers(tag)            

        # Update the bench time-slider
        # TODO: this is crappy
        try:
            import wx
            bench = wx.GetApp().get_bench()
            bench.set_time_interval(0, self.get_timeline().get_max_timepoint())
        except:return
	



    def load_supp_protocol_file(self, file, protocol):	
	instance = get_tag_attribute(protocol)
	tag_stump = get_tag_stump(protocol, 2)	
	
	lines = [line.strip() for line in open(file)]
	if not lines:
	    import wx
	    dial = wx.MessageDialog(None, 'Sub-process file is empty!!', 'Error', wx.OK | wx.ICON_ERROR)
	    dial.ShowModal()  
	    return	

	for line in lines:
	    #line.rstrip('\n')
	    line_info = line.split('|')
	    attr = line_info.pop(0)

	    if len(line_info)>1:
		self.set_field(tag_stump+'|%s|%s'%(attr, instance), line_info)
	    else:
		self.set_field(tag_stump+'|%s|%s'%(attr, instance), line_info[0])
    
    def load_settings(self, file, protocol):
	instance = get_tag_attribute(protocol)
	tag_stump = get_tag_stump(protocol, 2)	
	f = open(file, 'r')
	lines = [line.strip() for line in f]
	event = lines.pop(0) # takes out the first line or the header where all setting type microscope/spin etc are written	
	attributes = {}
	for line in lines:
	    attr, value = line.split('=', 1)
	    attributes[attr.strip()] = value
	# set all dependency attributes e.g. Centifugation depends on Centrifuge
	dependecny_attrs = [s for s in attributes if 'Dependency' in s]
	if dependecny_attrs:
	    d_inst = self.get_new_protocol_id(DEPENDENCY[event])
	    for d_attr in dependecny_attrs:
		if d_attr.endswith('Instance'):
		    tag = tag_stump+'|%s|%s'%(d_attr.split('Dependency')[1], instance)
		    self.set_field(tag, d_inst, notify_subscribers=False)
		    self.notify_subscribers(tag)
		    del attributes[d_attr]
		else:
		    tag = DEPENDENCY[event]+'|%s|%s'%(d_attr.split('Dependency')[1], d_inst)
		    self.set_field(tag, eval(attributes[d_attr]), notify_subscribers=False)
		    self.notify_subscribers(tag)
		    del attributes[d_attr]
	# set rest of the attributes
	for attr in attributes:
	    tag = tag_stump+'|%s|%s'%(attr, instance)
	    self.set_field(tag, eval(attributes[attr]), notify_subscribers=False)
	    self.notify_subscribers(tag)
	    f.close()	    
		
	
	    
	    
	#for line in lines:
	    #attr, value = line.split('=', 1)
	    #attr = attr.strip()
	    #tag = tag_stump+'|%s|%s'%(attr, instance)
	    #self.set_field(tag, eval(value), notify_subscribers=False)
	    #self.notify_subscribers(tag)
	    #f.close()
	
    def add_subscriber(self, callback, match_string):
        '''callback -- the function to be called
        match_string -- a regular expression string matching the tags you want 
                        to be notified of changes to
        '''
        self.subscribers[match_string] = self.subscribers.get(match_string, []) + [callback]
        
    def remove_subscriber(self, callback):
        '''unsubscribe the given callback function.
        This MUST be called before a callback function is deleted.
        '''
        for k, v in self.subscribers:
            if v == callback:
                self.subscribers.pop(k)
            
    def notify_subscribers(self, tag):
        for matchstring, callbacks in self.subscribers.items():
            if re.match(matchstring, tag):
		#self.save_to_temp_file()  # update info to the temp file
                for callback in callbacks:
                    callback(tag)
                    
    def getNM(self, nm):
        return int(nm.split('-')[0]), int(nm.split('-')[1])
    
    def belongsTo(self, value, rangeStart, rangeEnd):
                if value >= rangeStart and value <= rangeEnd:
                        return True
                return False    
            
    def partition(self, lst, n):
        division = len(lst) / float(n)   
        rlist = [lst[int(round(division * i)): int(round(division * (i + 1)))] [-1] for i in xrange(n) ]  
        rlist.insert(0, lst[0])
        return rlist	
    
    def stringSplitByNumbers(self, x):
	r = re.compile('(\d+)')
	l = r.split(x)
	return [int(y) if y.isdigit() else y for y in l]     
    
    def nmToRGB(self, w):
        # colour
        if w >= 380 and w < 440:
            R = -(w - 440.) / (440. - 350.)
            G = 0.0
            B = 1.0
        elif w >= 440 and w < 490:
            R = 0.0
            G = (w - 440.) / (490. - 440.)
            B = 1.0
        elif w >= 490 and w < 510:
            R = 0.0
            G = 1.0
            B = -(w - 510.) / (510. - 490.)
        elif w >= 510 and w < 580:
            R = (w - 510.) / (580. - 510.)
            G = 1.0
            B = 0.0
        elif w >= 580 and w < 645:
            R = 1.0
            G = -(w - 645.) / (645. - 580.)
            B = 0.0
        elif w >= 645 and w <= 780:
            R = 1.0
            G = 0.0
            B = 0.0
        else:
            R = 0.0
            G = 0.0
            B = 0.0
        
        # intensity correction
        if w >= 380 and w < 420:
            SSS = 0.3 + 0.7*(w - 350) / (420 - 350)
        elif w >= 420 and w <= 700:
            SSS = 1.0
        elif w > 700 and w <= 780:
            SSS = 0.3 + 0.7*(780 - w) / (780 - 700)
        else:
            SSS = 0.0
        SSS *= 255  
        
        return [int(SSS*R), int(SSS*G), int(SSS*B)]    
    
    def decode_ch_component(self, component):
        '''this method decofify the components of the light path for a given channel
        'LSR488' --> Laser 488nm, 'DMR567LP' ---> Long pass Dichroic Mirror 567nm etc.. 
        '''
        description = ''
        
        if component.startswith('LSR'):
            nm = re.sub('\D', '', component)
            description = nm+' nm Excitation laser ' 
        if component.startswith('DMR'):
            nm = re.sub('\D', '', component)
            if component.endswith('LP'):
                description = nm+' nm Long Pass Dichroic Mirror'
            if component.endswith('SP'):
                description = nm+' nm Short Pass Dichroic Mirror'            
        if component.startswith('FLT'):
	    if component.endswith('LP'):
		description = re.sub('\D', '', component)+' nm Long Pass Filter'
	    if component.endswith('SP'):
		description = re.sub('\D', '', component)+' nm Short Pass Filter'
	    if component.endswith('BP'):
		description = (component.split('FLT')[1]).split('BP')[0]+' nm Band pass Filter' # this needs to be adjusted
	if component.startswith('SLT'):
	    ratio = component.split('SLT')[1]
	    description = re.sub('/', ':', ratio)+' Beam Splitter'
        if component.startswith('DYE'):
            dye = component.split('_')[1]
            description = 'Dye used: %s' %dye
        if component.startswith('DTC'):
            volt = re.sub('\D', '', component)
            description = 'PMT voltage %s volts' %volt           
            
        return description
    
    def setDyeList(self, emLow, emHgh):
	'''This method sets the list of dye for a given spectrum range'''
	dyeList = []
	for dye in FLUOR_SPECTRUM: 
	    dyeLowNM, dyeHghNM = self.getNM(FLUOR_SPECTRUM[dye][1])
	    for wl in range(emLow, emHgh+1):
		if wl in range(dyeLowNM, dyeHghNM+1):
		    dyeList.append(dye)
	#self.dyeListBox.Clear()	
	return sorted(list(set(dyeList)))  
	
    def get_seeded_sample(self, platewell_id):
	'''this method returns sample or cell line information for the selected well
	'''
	timeline = self.get_timeline()
	timepoints = timeline.get_unique_timepoints()
	events_by_timepoint = timeline.get_events_by_timepoint()   
	
	seeding_instances = []
	for i, timepoint in enumerate(timepoints):
	    for ev in events_by_timepoint[timepoint]:
		for well_id in ev.get_well_ids():
		    if well_id == platewell_id and ev.get_welltag().startswith('Transfer|Seed'):
			seeding_instances.append(ev.get_welltag())
			
	return seeding_instances
    #----------------------------------------------------------------------
    def get_sampleInstance(self, seed_tag):
	'''This method returns the stock culutre or sample instance for a given seeding tag Transfer|Seed|Wells|<instance>
	'''
	instance = get_tag_instance(seed_tag)
	# if seed from stock culture
	if self.global_settings.has_key('Transfer|Seed|CellLineInstance|%s'%instance):
	    return self.get_field('Transfer|Seed|CellLineInstance|%s'%instance)
	elif self.global_settings.has_key('Transfer|Seed|HarvestInstance|%s'%instance):
	    return self.get_field('Transfer|Harvest|CellLineInstance|%s'
	                          %str(self.get_field('Transfer|Seed|HarvestInstance|%s'%instance)))  
	    
    #----------------------------------------------------------------------
    def getStateRGB(self, trackTags):
	"""This method returns the colour of the node given the history of the ancestor nodes events"""
	currRGB = (255, 255, 255, 100)
	for tag in trackTags:
	    event = get_tag_event(tag)
	    if event.startswith('Notes') or event.startswith('DataAcquis'): # since these are measurements or notes
		continue
	    currRGB = (int((currRGB[0]+EVENT_RGB[event][0])/2), int((currRGB[1]+EVENT_RGB[event][1])/2), int((currRGB[2]+EVENT_RGB[event][2])/2), 100)
	return currRGB
    #----------------------------------------------------------------------
    def getEventRGB(self, tag):
	"""get all event tags for the passed node and returns the colour associated with the last event** Need to change**"""
	#currRGB = (255, 255, 255, 100)	
	#if nodeTags:
	    #tag = nodeTags.pop()
	event = get_tag_event(tag)
	if not event.startswith('Notes') or not event.startswith('DataAcquis'): # since these are measurements or notes
	    return (EVENT_RGB[event][0], EVENT_RGB[event][1], EVENT_RGB[event][2], 100)
	else:
	    return (255, 255, 255, 100)
    #----------------------------------------------------------------------
    def getEventIcon(self, icon_size, act):
	"""get the associated icon for the given action/event"""
	if act == 'Seed':
	    icon = icons.seed.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act == 'CellLine':
	    icon = icons.stock.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Harvest':
	    icon = icons.harvest.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	    
	elif act =='Chemical':
	    icon = icons.treat.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	elif act =='Biological':
	    icon = icons.dna.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Physical':
	    icon = icons.physical.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	    
	elif act =='Dye':
	    icon = icons.stain.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	elif act =='Immuno':
	    icon = icons.antibody.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Genetic':
	    icon = icons.primer.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	    
	elif act =='Centrifugation':
	    icon = icons.spin.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	elif act =='Wash':
	    icon = icons.wash.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Drying':
	    icon = icons.drying.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Medium':
	    icon = icons.medium.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Initiation':
	    icon = icons.initiation.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='Storage':
	    icon = icons.storage.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	elif act =='Incubation':
	    icon = icons.incubator.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	elif act =='RheoManipulation':
	    icon = icons.rheometer.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 	
	    
	elif act =='HCS':
	    icon = icons.hcs.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='FCS':
	    icon = icons.fcs.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='TLM':
	    icon = icons.tlm.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	elif act =='RHE':
	    icon = icons.rhe.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()	
	
	#elif act =='Hint':
	    #icon = icons.hint.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	#elif act =='Text':
	    #icon = icons.critical.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap() 
	#elif act =='Rest':
	    #icon = icons.rest.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()   
	#elif act =='URL':
	    #icon = icons.url.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()   
	#elif act =='MultiMedia':
	    #icon = icons.video.Scale(icon_size, icon_size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
	    
	return icon
    
    #----------------------------------------------------------------------
    def get_Row_Numbers(self, protocol, token):
	"""This method returs TAGS with similar elements 
	eg. 'AddProcess|Rheology|Gas1|1' 'AddProcess|Rheology|Gas2|1'  etc"""
	
	tag_stump = get_tag_stump(protocol, 2)
	instance = get_tag_attribute(protocol)	
	
	return sorted(self.get_attribute_list_by_instance(tag_stump+'|%s'%token, instance), key = self.stringSplitByNumbers)
    #----------------------------------------------------------------------
    def setLabelColour(self, tags, labels):
	"""Change mandatory label colour Red-->Green when filled"""
	for tag in tags:
	    if self.get_field(tag):
		labels[tag].SetForegroundColour(('#006600'))
		labels[tag].Refresh()
	    else:
		labels[tag].SetForegroundColour(wx.RED)
		labels[tag].Refresh()    
    #----------------------------------------------------------------------
    def checkMandatoryTags(self, tags):
	"""Checks whether the mandatory fields/tags being filled"""
	for tag in tags:
	    if not self.get_field(tag):	
		import wx
		dial = wx.MessageDialog(None, 'Please fill %s mandatory field' %get_tag_attribute(tag), 'Error', wx.OK | wx.ICON_ERROR)
		dial.ShowModal()   
		return
	return True	
    #----------------------------------------------------------------------
    def alphanumeric_sort(self, lst):
	"""sort alphanumeric strings in a list e.g. [Plate1, Plate11, Tube2]"""
	re_natural = re.compile('[0-9]+|[^0-9]+')
	return [(1, int(c)) if c.isdigit() else (0, c.lower()) for c in re_natural.findall(lst)] + [lst] 	
    #----------------------------------------------------------------------
    def last_seed_instance(self, instance):
	"""finds the last seeding instance that is associated with a harvest instance"""
	for inst in list(reversed(range(int(instance)))):
	    if 'Transfer|Seed|HarvestInstance|%s'%str(inst) is not None:
		return str(inst)
	    
    #----------------------------------------------------------------------
    def get_cellLine_Name(self, inst, mode):
	"""returns cell Line name given the seeding/harvesting (mode) instance that is realted with a harvest instance
	   if mode is None, it refers to Harvest_Seed type of seeding instance"""
	if mode is 'H':
	    return self.get_field('Sample|CellLine|Name|%s'
                        %str(self.get_field('Transfer|Harvest|CellLineInstance|%s'%str(inst))))
	if mode is 'S':
	    return self.get_field('Sample|CellLine|Name|%s'
                        %str(self.get_field('Transfer|Seed|CellLineInstance|%s'%str(inst))))
	if mode is 'HS':
	    return self.get_field('Sample|CellLine|Name|%s'
                        %str(self.get_field('Transfer|Harvest|CellLineInstance|%s'
                        %str(self.get_field('Transfer|Seed|HarvestInstance|%s'
                        %str(inst))))))
	
	    
EVENT_RGB ={
    'Seed': (255,255,0,100),
    'Harvest': (227,205,41,100),
    'Chemical': (255,51,102,100),
    'Biological': (102,102,255,100),
    'Physical': (107, 112, 255, 100),
    'Dye': (27,188,224,100),
    'Immuno': (27,224,43,100),
    'Genetic': (27,224,181,100),
    'Centrifugation': (224,27,198,100),
    'Incubation': (224,27,224,100),
    'RheoManipulation': (224, 27, 244, 100),
    'Wash': (175,27,224,100),
    'Initiation': (175,27,224,100),
    'Storage': (175,27,224,100),
    'Drying': (168,27224,100),
    'Medium': (122,27,224,100),
    'TLM': (224,194,27,100),
    'HCS': (224,178,27,100),
    'FCS': (224,142,27,100),
    'RHE': (224, 27, 244, 100),
    'Text': (224,103,27,100),
    'Hint': (224,86,27,100),
    'Rest': (224,73,27,100),
    'URL': (224,53,27,100),
    'MultiMedia': (224,40,27,100),
    

}

	
DEPENDENCY = { 
    'Instrument':'InstProcess',
    'Centrifugation':'Instrument|Centrifuge', 
    'Incubation':'Instrument|Incubator',
    'Drying':'Instrument|Oven',
    'RheoManipulation':'Instrument|Rheometer',
    }
            
        


ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# Plate formats
FLASK = (1, 1)
#P1    = (1,1)
#P2    = (1,2)
#P4    = (1,4)
P6    = (2, 3)
#P8    = (2,4)
P12   = (3,4)
P24   = (4, 6)
P48   = (6, 8)
P96   = (8, 12)
P384  = (16, 24)
P1536 = (32, 48)
P5600 = (40, 140)

WELL_NAMES = {
              #'1-Well-(1x1)'       : P1,
              #'2-Well-(1x2)'       : P2,
              #'4-Well-(1x4)'       : P4,
              '6-Well-(2x3)'       : P6,
              #'8-Well-(2x4)'       : P8,
              '12-Well-(3x4)'      : P12, 
              '24-Well-(4x6)'      : P24, 
              '48-Well-(6x8)'      : P48,
              '96-Well-(8x12)'     : P96, 
              '384-Well-(16x24)'   : P384, 
              '1536-Well-(32x48)'  : P1536, 
              '5600-Well-(40x140)' : P5600,
              }

WELL_NAMES_ORDERED = [
                      #'1-Well-(1x1)',
                      #'2-Well-(1x2)',
                      #'4-Well-(1x4)',
                      '6-Well-(2x3)',
                      #'8-Well-(2x4)',
                      '12-Well-(3x4)',
                      '24-Well-(4x6)',
                      '48-Well-(6x8)',
                      '96-Well-(8x12)',
                      '384-Well-(16x24)',
                      '1536-Well-(32x48)',
                      '5600-Well-(40x140)']
#TO DO: make this table comprehensive
FLUOR_SPECTRUM = {
                   'Brilliant Violet 421': ['397-417','411-431'],
                   'BD Horizon V450': ['394-414','438-458'],
                   'AmCyan': ['447-467','481-501'],
                   'PE': ['486-506','568-588'],
                   'BD Horizon PE-CF594': ['486-506','602-622'],
                   'PerCP': ['472-492','667-687'],
                   'PerCP-Cy': ['472-492','685-705'],
                   'Alexa Fluor 647': ['640-660','658-678'],
                   'Alexa Fluor 700': ['686-706','709-729'],
                   'APC-H7': ['640-660','775-795'],
                   'Alexa 488' : ['450-560', '510-550'],
                   'PE-Texas Red' : ['550-625', '600-650'],
                   'FITC' : ['475-510','515-545'],
                   'Pacific Blue' : ['390-410','440-460'],
                   'PE-Cy5' : ['500-650','650-700'],
                   'PE-Cy7' : ['470-550','680-785'],
                   'APC' : ['600-670','640-670'],
                   'APC-Cy' : ['650-730', '740-800'],
                   'APC-Cy7' : ['620-680', '750-800'],
                   'BD Horizon V450' : ['380-404', '410-448'],
                   'BD Horizon V500' : ['390-450', '460-500'],
             }

ATTRIBUTE_THESAURUS = {
    'Immuno': ['Immunological', ]
    
    
    }
class Vessel(object):
    def __init__(self, vessel_type, instance, shape, group, **kwargs):
        self.instance    = instance
        self.group       = group
        self.vessel_type = vessel_type
        if type(shape) == tuple:
            self.shape = shape
        else:
            self.shape = WELL_NAMES[shape]
##        meta.set_field('ExptVessel|%(vessel_type)|Design|%(instance)'%(locals), shape)
##        meta.set_field('ExptVessel|%(vessel_type)|StackName|%(instance)'%(locals), group)
        for k,v in kwargs:
            self.set_attribute(k, v)
        
##    def __del__(self):
##        for tag in meta.get_matching_tags('ExptVessel|%(vessel_type)|*|%(instance)'%(self.__dict__)):
##            meta.remove_field(tag)
            
    def set_attribute(self, att, value):
        self.__dict__[att] = value
##        meta.set_field('ExptVessel|%s|*|%s'%(att, self.instance), value)
        
    @property
    def vessel_id(self):
        return '%(vessel_type)s%(instance)s'%(self.__dict__)    


class PlateDesign:
    '''Maps plate_ids to plate formats.
    Provides methods for getting well information for different plate formats.
    '''
    
    plates = {}
    
    @classmethod
    def clear(self):
        self.plates = {}
        
    @classmethod
    def add_plate(self, vessel_type, instance, shape, group, **kwargs):
        '''Add a new plate with the specified format
        '''
        v = Vessel(vessel_type, instance, shape, group, **kwargs)
        self.plates[v.vessel_id] = v
        
    @classmethod
    def set_plate_format(self, plate_id, shape):
        self.plates[plate_id].shape = shape
        
    @classmethod
    def get_plate_ids(self):
        return self.plates.keys()
    
    @classmethod
    def get_plate_id(self, vessel_type, instance):
        for vessel in self.plates.values():
            if vessel.instance == instance and vessel.vessel_type == vessel_type:
                return vessel.vessel_id
            
    @classmethod
    def get_plate_group(self, vessel_id):
        return self.plates[vessel_id].group
    
    @classmethod
    def get_vessel(self, vessel_id):
        return self.plates[vessel_id]

    @classmethod
    def get_plate_format(self, plate_id):
        '''returns the plate_format for a given plate_id
        '''
        return self.plates[plate_id].shape
    
    @classmethod
    def get_all_platewell_ids(self):
        '''returns a list of every platewell_id across all plates
        '''
        return [(plate_id, well_id) 
                for plate_id in self.plates
                for well_id in self.get_well_ids(self.get_plate_format(plate_id))
                ]

    @classmethod
    def get_well_ids(self, plate_format):
        '''plate_format - a valid plate format. eg: P96 or (8,12)
        '''
        return ['%s%02d'%(ch, num) 
                for ch in ALPHABET[:plate_format[0]] 
                for num in range(1,plate_format[1]+1)]
    
    @classmethod
    def get_col_labels(self, plate_format):
        return ['%02d'%(num) for num in range(1,plate_format[1]+1)]

    @classmethod
    def get_row_labels(self, plate_format):
        return list(ALPHABET[:plate_format[0]])
    
    @classmethod
    def get_well_id_at_pos(self, plate_format, (row, col)):
        assert 0 <= row < plate_format[0], 'invalid row %s'%(row)
        assert 0 <= col < plate_format[1], 'invalid col %s'%(col)
        cols = plate_format[1]
        return PlateDesign.get_well_ids(plate_format)[cols*row + col]

    @classmethod
    def get_pos_for_wellid(self, plate_format, wellid):
        '''returns the x,y position of the given well
        eg: get_pos_for_wellid(P96, 'A02') --> (0,1)
        '''
        if type(wellid) is tuple:
            wellid = wellid[-1]
        row = ALPHABET.index(wellid[0])
        col = int(wellid[1:]) - 1
        assert row < plate_format[0] and col < plate_format[1], 'Invalid wellid (%s) for plate format (%s)'%(wellid, plate_format)
        return (row, col)