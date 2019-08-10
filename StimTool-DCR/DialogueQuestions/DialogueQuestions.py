
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

event_types = {'RESPONSE':1, 
    'TASK_END':StimToolLib.TASK_END}
    
    
    
def get_one_response(question, force_numerical):
    while True:
        myDlg = gui.Dlg(title='Question')
        myDlg.addText(question)
        myDlg.addField('Response')
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            raise StimToolLib.QuitException()
        retval = thisInfo[0]
        if force_numerical:
            try:
                float(retval) #just test to see if it can be cast as a float--still return the actual string input by the user
            except ValueError:
                continue
        break
    return retval
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/DQ.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
        
def run_try():  
    
    myDlg = gui.Dlg(title="Dialogue Questions")
    #question_lists = [f for f in os.listdir(os.path.join(os.path.dirname(__file__))) if f.endswith('.schedule')] 
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg.addField('Question List', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #StimToolLib.general_setup(g)
    g.clock = core.Clock()
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
    StimToolLib.task_start(StimToolLib.DIALOGUE_QUESTIONS_CODE, g) #send message that this task is starting
    
    instruct_onset = g.clock.getTime()
    
    input_file = open(schedule_file, 'r')
    g.trial = 0
    for line in input_file.readlines()[1:]: #discard the header
        l = line.split(',')
        q_start = g.clock.getTime()
        resp = get_one_response(l[0], l[1]=='True')
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, 'NA', event_types['RESPONSE'], now, now - q_start, resp, l[0], g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.trial = g.trial + 1
        
    
    
    
    

  
 


