
import StimToolLib, os, random, operator, shutil, psutil
from psychopy import visual, core, event, data, gui

#data mover: move files generated during a session.  This way they can be generated locally (more reliable) and then copied onto network storage.

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.output = None

event_types = {'RESPONSE':1, 
    'TASK_END':StimToolLib.TASK_END}
    
def error_try_again(txt):
    error_msg = gui.Dlg(title="ERROR")
    error_msg.addText(txt)
    error_msg.addField('Try again?', choices=['yes', 'no'], initial='yes')
    error_msg.show()
    thisInfo = error_msg.data
    if thisInfo[0] == 'yes':
        return True
    return False
    
def move_one(source, destination):
    #move all files in a source folder to a destination folder
    if not os.path.exists(destination):
        while True:
            try:
                os.makedirs(destination)
                break
            except:
                if not error_try_again('Had trouble making destination: ' + destination + ' Check network connectivity and permissions.'):
                    return
    if source == 'output_dir':
        source = g.session_params['output_dir']
    while True:
        try:
            all_files = os.listdir(source)
            break
        except:
            if not error_try_again('Had trouble finding ' + source + ' Check network connectivity and that the files/folders exist.'):
                return
    for f in all_files:
        full_path = os.path.join(source, f)
        while True:
            #keep retrying individual files if they fail--unless the user decides not to
            try:
                shutil.move(full_path, destination)
                break
            except:
                if not error_try_again('Had trouble moving ' + source + ' to ' + destination + '. Check network connectivity and that the files/folders exist.'):
                    break
    
def check_processes_running():
    #make sure all processes in the check_not_running list are not running
    #this is so you can force the user to close programs that may be using some of the output files that need to be moved
    all_processes = psutil.pids()
    for i in all_processes:
        try:
            this_process = psutil.Process(i)
        except: #happens when a process exits
            pass
        print(this_process.name())
        if this_process.name() in g.run_params['check_not_running']:
            try:
                StimToolLib.error_popup('Plese close "' + this_process.name() + '" so that all output files can be moved successfully.')
            except StimToolLib.QuitException as q:
                return True
    return False
            
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/DM.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    #except Exception as e:
    #    StimToolLib.error_popup('UNKNOWN ERROR MOVING FILES: ' + str(e) + '\nMake sure the data files for this session get moved to the appropriate location')
    if g.win:
        g.win.close()
    #StimToolLib.task_end(g)
    return g.status
        
def run_try():  
    
    myDlg = gui.Dlg(title="Data Mover")
    #question_lists = [f for f in os.listdir(os.path.join(os.path.dirname(__file__))) if f.endswith('.schedule')] 
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg.addField('Movement Params', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #StimToolLib.general_setup(g)
    g.clock = core.Clock()
    start_time = data.getDateStr()
    g.session_params['screen_x'] = 500  #just draw a square in the middle--so error popups still show up and it's easier to close programs if necessary
    g.session_params['screen_y'] = 500

    StimToolLib.general_setup(g) #create a window and show a message so people don't just hit the stop button before files are moved
    g.mouse.setVisible(True) #show the mouse, so it's easier to click in the dialogue box
    g.msg = visual.TextStim(g.win,text="Moving files, please wait...",units='pix',pos=[0,0],color=[1,1,1],height=30,wrapWidth=int(1600))
    g.msg.draw()
    g.win.flip()
    
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    #g.prefix = StimToolLib.generate_prefix(g)
    #fileName = os.path.join(g.prefix + '.csv')
    
    check_again = True
    while check_again: #make sure all of the processes listed in the .params file are not running
        check_again = check_processes_running()
    
    #g.prefix = 'R-' + g.session_params['SID'] + '-Admin_' + str(g.session_params['raID']) + '-run_1' + '-' +  start_time 
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    #g.output= open(fileName, 'w')
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    #g.output.write('Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ",Event Codes:," + str(sorted_events) + '\n')
    #g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    #StimToolLib.task_start(StimToolLib.DATA_MOVER_CODE, g) #send message that this task is starting
    
    instruct_onset = g.clock.getTime()
    StimToolLib.close_output() #close stdout and stderr output files so they can be moved
    input_file = open(schedule_file, 'r')
    g.trial = 0
    for line in input_file.readlines()[1:]: #discard the header
        l = line.split()
        q_start = g.clock.getTime()
        move_one(l[0], os.path.join(l[1], start_time))
        now = g.clock.getTime()
        g.trial = g.trial + 1
        
    
    
    

  
 


