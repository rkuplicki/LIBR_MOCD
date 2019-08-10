
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui

#rest module: present crosshairs for a fixed duration

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.title = 'Rest'
        self.output = None

event_types = {'INSTRUCT_ONSET':1, 
    'TASK_ONSET':2,
    'TASK_END':StimToolLib.TASK_END}
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/R.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
        
def run_try():  
    
    
    
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="PB")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    
    StimToolLib.general_setup(g)
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_Rest_Schedule1.csv')
    trial_types,junk,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    duration = durations[0][0] #in this case, we only have a single duration
    
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')
    
    #g.prefix = 'R-' + g.session_params['SID'] + '-Admin_' + str(g.session_params['raID']) + '-run_1' + '-' +  start_time 
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output= open(fileName, 'w')
    sorted_events = sorted(event_types.iteritems(), key=operator.itemgetter(1))
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ",Event Codes:," + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.REST_CODE, g) #send message that this task is starting
    
    instruct_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #StimToolLib.show_title(g.win, g.title)
    #StimToolLib.show_instructions(g.win, g.instructions)
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end, instruct_end - instruct_onset, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.trial = 0
    g.ideal_trial_start = instruct_end
    
    g.x = visual.TextStim(g.win, text="+", units='pix', height=150, color=[1,1,1], pos=[0,0])
    g.x.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    
    

  
 


