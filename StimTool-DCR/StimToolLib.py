

from psychopy import event, core, visual, gui, sound, monitors, data#, microphone
import csv, os, ctypes, ast, numpy, pyo, sys, logging
from shutil import move

PARALLEL_DELAY = 0.005 #time to wait when sending pulses to the parallel port
TRIAL_START_DELAY = 0.005 #test this experimentally--should be the delay between when the run is signalled to BIOPAC and when the clock is reset
AAC_CODE = 1
BASELINE_CODE = 2
CP_CODE = 3
DP_CODE = 4
IAAT_CODE = 5
COLD_PRESSOR_CODE = 6
HEARTBEAT_CODE = 7
BANDIT_CODE = 8
CHANGEPOINT_CODE = 9
DRIVE_CODE = 10
ER_CODE = 11
FEAR_CONDITIONING_CODE = 12
INTEROCEPTIVE_AWARENESS_CODE = 13
MONETARY_INCENTIVE_DELAY_CODE = 14
QUESTIONNAIRE_CODE = 15
STOP_SIGNAL_CODE = 16
BREATH_HOLD_CODE = 17
REST_CODE = 18
DIALOGUE_QUESTIONS_CODE = 19
FINGER_TAPPING_CODE = 20
DATA_MOVER_CODE = 21
HARIRI_CODE = 22
CUE_REACTIVITY_CODE = 23
GONOGOEMOTIONAL_CODE = 24 #emotional go/nogo
HANDGRIP_STRENGTH_CODE = 25
HANDGRIP_ENDURANCE_CODE = 26
GONOGOAFFECTIVE_CODE = 27
GONOGOBUTTONS_CODE = 28
TASK_END = 99

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.mic = None
        pass
        
#gv = GlobalVars()
def initialize_mic():
    pass
    #microphone.switchOn()
    #gv.mic = microphone.AdvAudioCapture()
class QuitException(Exception):
    def __init__(self):
        pass
def short_wait(): #a very short sleep, added in busy waiting loops to reduce CPU load 
    core.wait(0.001, hogCPUperiod=0)
def error_popup(msg):
    error_msg = gui.Dlg(title="ERROR")
    error_msg.addText(msg)
    error_msg.show()
    raise QuitException()
def general_setup(g):
    #initialize the window, main text stim, and clock
    
    thisMon = monitors.Monitor('', width=g.session_params['monitor_width_cm'], distance=g.session_params['monitor_distance_cm'])
    thisMon.setSizePix([g.session_params['monitor_width_pix'], g.session_params['monitor_height_pix']])
    #g.win = visual.Window(fullscr=False, screen=1,color=(-1,-1,-1), waitBlanking=True, colorSpace='rgb',winType='pyglet', allowGUI=False, size=(g.session_params['screen_x'], g.session_params['screen_y']), monitor=thisMon) 
    g.win = visual.Window(fullscr=False, screen=g.session_params['screen_number'],color=(-1,-1,-1), waitBlanking=True, colorSpace='rgb',winType='pyglet', allowGUI=False, size=(g.session_params['screen_x'], g.session_params['screen_y']), monitor=thisMon) 
    g.msg = visual.TextStim(g.win,text="",units='pix',pos=[0,0],color=[1,1,1],height=30,wrapWidth=int(1600))
    g.mouse = event.Mouse(visible=False) #hide the mouse--prevents loss of focus, also leave the mouse object in g so that it can be shown if the task requires it
    core.wait(1)
    g.clock = core.Clock()
   
def verify_parallel(session_params):
    address = session_params['parallel_port_address']
    while True:
        if check_one_parallel_address(address):
            break #seems to work
        else:
            myDlg = gui.Dlg(title="Parallel Port Address")
            myDlg.addText('The parallel port check failed.  Verify the appropriate address in hardware manager, and enter it below.  You may also want to change this in the appropriate .params file.')
            myDlg.addField('Address', initial='0x' + format(address, '02x'))
            myDlg.show()  # show dialog and wait for OK or Cancel
            thisInfo = myDlg.data
            address = ast.literal_eval(thisInfo[0])
            session_params['parallel_port_address'] = address
                
    
def check_one_parallel_address(address):
    for i in range(256):
        parallel_writer.Out32(address, i)
        read_val = parallel_writer.Inp32(address)
        if not i == read_val:
            return False
    parallel_writer.Out32(address, 0) #reset to 0
    print 'PARALLEL PORT SUCCESS'
    return True
    
    
def write_parallel(port, value):
    parallel_writer.Out32(port, value)# 0x3000, value)
    #wait a short time
    
def task_start(value, g): #g should have a clock (to reset) 
    #this function should be called when the task title screen is shown
    g.clock.reset()
    if g.session_params['signal_parallel']:
        write_parallel(g.session_params['parallel_port_address'], value + 128)
        core.wait(PARALLEL_DELAY)
        write_parallel(g.session_params['parallel_port_address'], 128)
    if g.session_params['record_video']:
        #print pyo.pa_get_input_devices()
        #print pyo.pa_get_default_input()
        #gv.mic.record(10800, filename = g.prefix[0:-4] + 'FACE' + '.wav') #start recording audio--up to 3 hours
        split_string = g.prefix.rsplit('-', 1)
        if len(split_string[1]) == 4: #no number at the end (or a very large one, e.g. 1000)
            first_part = split_string[0] + '-'
            second_part = ''
        else:
            first_part = split_string[0][:-4]
            second_part = '-' + split_string[1]
        vid_prefix = first_part + 'FACE' + second_part
        #vid_prefix = g.prefix[0:16] + 'FACE' + g.prefix[20:len(g.prefix)]
        CD.start_recording(vid_prefix, g.clock)
        #CD.start_recording(g.prefix[0:-4] + 'FACE', g.clock)
    
def task_end(g): #status of the task that just ended--do not show the 'break' screen for an exit code of -1
    if g.session_params['signal_parallel']:
        write_parallel(g.session_params['parallel_port_address'], 0)
    if g.session_params['record_video']:
        #gv.mic.stop() #stop recording audio
        #insert flac command here--or at the very end before copying files?
        #gv.mic.reset() #reset the mic--so we're ready to start another recording
        CD.stop_recording()
    if g.output and not g.output.closed:
        mark_event(g.output, 'NA', 'NA', TASK_END, g.clock.getTime(), 'NA', 'NA', 'NA', False, g.session_params['parallel_port_address'])
        g.output.close()
    #send text message to administrator
    #wait for advance to next task
    if g.win:
        if g.status == 0:
            try:
                show_instructions(g.win, ['Run complete: please wait for instructions.'])
            except QuitException:
                g.status = -1
        g.win.close()

def mark_event(fout, trial, trial_type, event_id, event_time, response_time, response, result, write_to_parallel, address):
    fout.write(str(trial) + ',' + str(trial_type) + ',' + str(event_id) + ',' + str(event_time) + ',' + str(response_time) + ',' + str(response) + ',' + str(result) + '\n') #add response time...
    if write_to_parallel:
        write_parallel(address, int(event_id) + 128 + 64) #mark the event (128 is task on, 64 is event occurring, event_id is the type of event (stored in the least significant 6 bits)
        core.wait(PARALLEL_DELAY) 
        write_parallel(address, 128) #now just set the task on bit, but set all others to 0

def show_slides(slides, win):
    #slides should be a list of images to draw--draw them one after another and wait for keys before continuing
    #meant primarily for instruction slides
    for i in slides:
        i.draw()
        win.flip()
        k = event.waitKeys(keyList = ['return', 'escape'])
        if k[0] == 'escape':
            raise QuitException()

def show_title(win, title):
    #win is the window to draw in, msg is the textStim to use, and instructions is a list of strings to display--one item per screen
    msg = visual.TextStim(win,text=str(title),units='pix',pos=[0,0],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=100,wrapWidth=int(1600)) #text color should be opposite of window color
    msg2 = visual.TextStim(win,text="",units='pix',pos=[0,-450],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=20,wrapWidth=int(1600)) 
    msg2.setText("Press ENTER to continue")
    msg.draw()
    msg2.draw()
    win.flip()
    k = event.waitKeys(keyList = ['return', 'escape'])
    if k[0] == 'escape':
        raise QuitException()
        

def show_instructions(win, instructions):
    #win is the window to draw in, msg is the textStim to use, and instructions is a list of strings to display--one item per screen
    msg = visual.TextStim(win,text="",units='pix',pos=[0,0],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=30,wrapWidth=int(1600)) #text color should be opposite of window color
    msg2 = visual.TextStim(win,text="",units='pix',pos=[0,-450],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=20,wrapWidth=int(1600)) 
    msg2.setText("Press ENTER to continue")
    for i in instructions:
        msg.setText(i)
        msg.draw()
        msg2.draw()
        win.flip()
        k = event.waitKeys(keyList = ['return', 'escape'])
        if k[0] == 'escape':
            raise QuitException()
            
def just_wait(c, end_time):
    #wait until end_time, as measured by the clock c
    #raise an exception if the user hits escape--this should be caught in the main program loop
    while c.getTime() < end_time:
        if event.getKeys(["escape"]):
            raise QuitException()
            #return -1
        short_wait()
        
def check_for_esc():
    if event.getKeys(["escape"]):
        raise QuitException()
        
def wait_scan_start(win):
    #show "In Preparation" in msg in win, wait for a 'z' after the scanner is prepped, then wait for a 't' to start the task
    msg = visual.TextStim(win,text="",units='pix',pos=[0,0],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=30,wrapWidth=int(1600)) #text color should be opposite of window color
    msg.setText('In Preparation')
    msg2 = visual.TextStim(win,text="",units='pix',pos=[0,-200],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=20,wrapWidth=int(1600)) 
    msg2.setText("(Press z after scanner prep)")
    msg.draw()
    msg2.draw()
    win.flip()
    k = event.waitKeys(keyList = ['z', 'escape'])
    if k[0] == 'escape':
        raise QuitException()
    #Wait for scanner pulse
    msg.setText('Task will begin soon')
    msg2.setText('(Waiting for a t to start)')
    msg.draw()
    msg2.draw()
    win.flip()
    k = event.waitKeys(keyList = ['t', 'escape'])
    if k[0] == 'escape':
        raise QuitException()
   
  
def wait_start(win):
    #just display a message and wait for 3 seconds before starting
    msg = visual.TextStim(win,text="",units='pix',pos=[0,0],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1] ,height=30,wrapWidth=int(1600)) #text color should be opposite of window color
    msg.setText('Task will begin soon')
    msg.draw()
    win.flip()
    c = core.Clock()
    just_wait(c, 3)

def run_instructions(instruct_schedule_file, g):
    #instructions from schedule file along with audio
    directory = os.path.dirname(instruct_schedule_file)
    fin = open(instruct_schedule_file, 'r')
    lines = fin.readlines()
    fin.close()
    slides = []
    for i in lines:
        slides.append(i.split(','))
    i = 0
    while i < len(slides):
        i = max(i + do_one_slide(slides[i], directory, g), 0) #do_one_slide may increment or decrement i, depending on whether session_params['right'] or session_params['left'] is pressed--don't let them go back on the first slide

def do_one_slide(slide, directory, g):
    image = visual.ImageStim(g.win, image=os.path.join(directory, slide[0]))
    if slide[1] == 'None':
        s = None
    else:
        if len(slide) == 4: #optional volume parameter
            s = sound.Sound(value = os.path.join(directory, slide[1]), volume=float(slide[3]))
        else:
            s = sound.Sound(value = os.path.join(directory, slide[1]), volume=g.session_params['instruction_volume'])
    advance_time = float(slide[2])
    #if it's -1, don't advance, if it's 0, advance at the end of the sound, if it's positive, advance after that amount of time
    wait_z = False
    if advance_time == -1:
        advance_time = float('inf')
    elif advance_time == 0:
        try:
            advance_time = s.getDuration()
        except AttributeError: #in case there is a None in stead of a sound, just set duration to 0.5
            advance_time = 0.5
    elif advance_time == -2: #wait for a 'z' to advance
        advance_time = float('inf')
        wait_z = True
    
    image.draw()
    g.win.flip()
    k = None #initialize k
    if s:
        s.play()
        advance_time = advance_time - s.getDuration() #since we're waiting for the duration of s, decrease advance_time by that amount--allows for e.g. advance_time of 5s with a sound of 3s->wait 2s after the sound ends
        k = event.waitKeys(keyList = ['z', 'a', 'escape'], maxWait=s.getDuration()) #force the subject to listen to all of the instructions--allow 'z' to skip them or 'a' to force back
    if not k: #if skipped instructions, don't wait to advance afterword
        if g.session_params['allow_instructions_back']: #only allow back if it's specified in the session parameters
            kl = [g.session_params['left'], g.session_params['right'], 'escape', 'z', 'a']
        else:
            kl = [g.session_params['right'], 'escape', 'z', 'a']
        if wait_z: #only advance for a 'z'
            kl = ['z', 'a']
        k = event.waitKeys(keyList = kl, maxWait=advance_time)
    if s: #stop the sound if it's still playing
        s.stop()
    if k == None: #event timeout
        return 1
    if k[0] == 'z':
        retval = 1
    if k[0] == 'a':
        retval = -1
    if k[0] == g.session_params['right']:
        retval = 1
    if k[0] == g.session_params['left']:
        retval = -1
    if k[0] == 'escape':
        raise QuitException()
    return retval
    

def run_instructions_keyselect(instruct_schedule_file, g):
    #instructions from schedule file along with audio
    #this version allows you to specify which key to use to advance the slides--e.g. to make the subject press each response button in order
    directory = os.path.dirname(instruct_schedule_file)
    fin = open(instruct_schedule_file, 'r')
    lines = fin.readlines()
    fin.close()
    slides = []
    for i in lines:
        slides.append(i.split(','))
    i = 0
    while i < len(slides):
        i = max(i + do_one_slide_keyselect(slides[i], directory, g), 0) #do_one_slide may increment or decrement i, depending on whether session_params['right'] or session_params['left'] is pressed--don't let them go back on the first slide

def do_one_slide_keyselect(slide, directory, g):
    image = visual.ImageStim(g.win, image=os.path.join(directory, slide[0]))
    if slide[1] == 'None':
        s = None
    else:
        if len(slide) == 4 and slide[3] != 'None': #optional volume parameter
            s = sound.Sound(value = os.path.join(directory, slide[1]), volume=float(slide[3]))
        else:
            s = sound.Sound(value = os.path.join(directory, slide[1]), volume=g.session_params['instruction_volume'])
    if len(slide) == 5 and slide[4].strip() != 'None': #must have volume parameter to have keyselect--not the cleanest way to do this. The volume parameter can be None though, meaning use the session_param
        advance_key = slide[4].strip() #remove newline
    else:
        advance_key = g.session_params['right']
    advance_time = float(slide[2])
    #if it's -1, don't advance, if it's 0, advance at the end of the sound, if it's positive, advance after that amount of time
    wait_z = False
    if advance_time == -1:
        advance_time = float('inf')
    elif advance_time == 0:
        try:
            advance_time = s.getDuration()
        except AttributeError: #in case there is a None in stead of a sound, just set duration to 0.5
            advance_time = 0.5
    elif advance_time == -2: #wait for a 'z' to advance
        advance_time = float('inf')
        wait_z = True
    
    image.draw()
    g.win.flip()
    k = None #initialize k
    if s:
        s.play()
        advance_time = advance_time - s.getDuration() #since we're waiting for the duration of s, decrease advance_time by that amount--allows for e.g. advance_time of 5s with a sound of 3s->wait 2s after the sound ends
        k = event.waitKeys(keyList = ['z', 'a', 'escape'], maxWait=s.getDuration()) #force the subject to listen to all of the instructions--allow 'z' to skip them or 'a' to force back
    if not k: #if skipped instructions, don't wait to advance afterword
        if g.session_params['allow_instructions_back']: #only allow back if it's specified in the session parameters
            kl = [g.session_params['left'], advance_key, 'escape', 'z', 'a']
        else:
            kl = [advance_key, 'escape', 'z', 'a']
        if wait_z: #only advance for a 'z'
            kl = ['z', 'a']
        print advance_key
        k = event.waitKeys(keyList = kl, maxWait=advance_time)
    if s: #stop the sound if it's still playing
        s.stop()
    if k == None: #event timeout
        return 1
    if k[0] == 'z':
        retval = 1
    if k[0] == 'a':
        retval = -1
    if k[0] == g.session_params['left']:
        retval = -1
    if k[0] == advance_key:
        retval = 1
    if k[0] == 'escape':
        raise QuitException()
    return retval

    
    
def read_trial_structure(schedule_file, win, msg):
    #This function will read a .csv file and parse each line, reading images into memory as necessary
    #Each line should have three commas separating four different groups of values--but any of these might be empty
    #The values should be: TrialTypes, Stimuli, Durations, ExtraArgs
    #Within each group of values, different entries should be separated by spaces, allowing an arbitrary number of stimuli or durations for each trial.
    #This may be useful if you have multiple ITIs within a trial.
    #TrialTypes is whatever coding the particular experiment uses.  These value are returned as strings.
    #Each string in stimuli should point to an image that will be read into memory.
    #Durations indicates whatever duration parameters the experiment requires.  These values will be converted to floats.
    #ExtraArgs is provided as a place to put anything else that might be needed--anything there will be returned as strings.
    #Draw a loading message
    directory = os.path.dirname(schedule_file)
    msg.setText('Loading...')
    msg.draw() #Draw the message
    win.flip() #Refresh the window 
    types = []
    stimuli = []
    durations = []
    extras = []
    exp_order = csv.reader(open(schedule_file))
    exp_order.next() #throw away the header
    for i in exp_order:
        types.append(i[0])
        s = i[1].split()
        s1 = []
        for j in s:
            s1.append(visual.ImageStim(win, image=os.path.join(directory, j), units='pix')) #load images into memory
        stimuli.append(s1)
        
        d = i[2].split()
        d1 = []
        for j in d:
            d1.append(float(j)) #convert elements into floats
        durations.append(d1)
        extras.append(i[3].split())
    print durations
    stimuli = map(list, zip(*stimuli)) #convert lists like [[1,2],[2,3],[3,4]] into [[1,2,3],[2,3,4]]
    durations = map(list, zip(*durations))
    extras = map(list, zip(*extras))
    print types
    print stimuli
    print durations
    print extras
    return types,stimuli,durations,extras
        

def get_anxiety_rating(g):
    pass
def get_valence_or_arousal(valence, question, g):
    #valence will be either True or False
    if valence:
        image_file = os.path.join(os.path.dirname(__file__), 'media', 'valence.bmp')
        
    else:
        image_file = os.path.join(os.path.dirname(__file__), 'media', 'arousal.bmp')
    image = visual.ImageStim(g.win, image_file, pos=[0,-.4], units='norm', size=[2, .34]) 
    
    scale_1 = visual.RatingScale(g.win, lineColor='White', precision=1, low=1, high=5, singleClick=False, leftKeys=g.session_params['left'], rightKeys=g.session_params['right'], acceptKeys=g.session_params['select'], mouseOnly = False, marker=visual.TextStim(g.win, text='l', units='norm', color='red'),
        textColor='White', scale=None, pos=(0,-.65), showAccept=False, stretch=2.85, markerStart = 3, labels=['1', '2', '3', '4', '5'], tickMarks=range(1,6))
    msg = visual.TextStim(g.win,text="",units='norm',pos=[-0,-.8],color=[1,1,1],height=.1,wrapWidth=2, alignHoriz = 'center', alignVert='top')
    msg.setText(question)
    
    msg.draw()
    scale_1.draw()
    image.draw()
    g.win.flip()
    start_time = g.clock.getTime()
    while scale_1.noResponse:
        image.draw()
        check_for_esc()
        msg.draw()
        scale_1.draw()
        g.win.flip()
    end_time = g.clock.getTime()
    return scale_1.getRating(), end_time, end_time - start_time

def get_one_rating(question, responses, win, clk):
    msg = visual.TextStim(win,text="",units='pix',pos=[-600,250],color=[-1,-1,-1],height=50,wrapWidth=int(1200), alignHoriz = 'left', alignVert='top')
    msg.setText(question)
    scale_1 = visual.RatingScale(win, lineColor='Black', precision=1, low=1, high=7, singleClick=True, mouseOnly = True, marker=visual.TextStim(win, text='l', units='norm', color='red'),
        textColor='Black', scale=None, labels=responses,  pos=(0,0), showAccept=False, stretch=2, tickMarks=[1,2,3,4,5,6,7])
    msg.draw()
    scale_1.draw()
    win.flip()
    start_time = clk.getTime()
    while scale_1.noResponse: 
        if event.getKeys(["escape"]):
            raise QuitException()
        msg.draw()
        scale_1.draw()
        win.flip()
    end_time = clk.getTime()
    return scale_1.getRating(), end_time, end_time - start_time

def get_one_vas_rating(g, vas_text, mstart = 50):
    g.mouse.setVisible(1)
    top_text = visual.TextStim(g.win, text="Please use the mouse to make a rating.", units='pix', height=80, color='White', pos=[0,405], wrapWidth=int(1600))
    
    text_1 = visual.TextStim(g.win, text=vas_text, units='norm', height=0.07, color='White', pos=[0,0.2], wrapWidth=int(1600))
    scale_1 = visual.RatingScale(g.win, lineColor='White', marker=visual.TextStim(g.win, text='l', units='norm', color='White'), precision=1, low=0, singleClick=False, 
        high=100, textColor='White', markerStart=mstart, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0), showAccept=True, acceptKeys='z')
    
    #bot_text = visual.TextStim(g.win, text="Press enter when done", units='pix', height=50, color='White', pos=[0,-450], wrapWidth=int(1600))
    vas_start_time = g.clock.getTime()
    while scale_1.noResponse:
        if event.getKeys(["escape"]):
            raise QuitException()
        #if event.getKeys(["return"]):
        #    break
        #item.draw()
        text_1.draw()
        scale_1.draw()
        top_text.draw()
        #bot_text.draw()
        g.win.flip()
    now = g.clock.getTime()
    g.mouse.setVisible(0)
    return scale_1.getRating()

def get_effort_rating(g, vas_text):
    #used by ColdPressor and BreathHold to get effort ratings
    start_time = g.clock.getTime()
    g.mouse.setVisible(1)
    top_text = visual.TextStim(g.win, text="Please use the mouse to make a rating.", units='pix', height=80, color='White', pos=[0,405], wrapWidth=int(1600))
    
    text_1 = visual.TextStim(g.win, text=g.effort_question_text, units='norm', height=0.07, color='White', pos=[0,0.2], wrapWidth=int(1600))
    scale_1 = visual.RatingScale(g.win, lineColor='White', marker=visual.TextStim(g.win, text='l', units='norm', color='White'), precision=1, low=0, stretch=1.73, textSize=1,
        high=100, textColor='White', markerStart=50, scale=None, labels=g.effort_anchors, tickMarks=[0, 25, 50, 75, 100], showValue=False, pos=(0,0), showAccept=True)
    
    #bot_text = visual.TextStim(g.win, text="Press enter when done", units='pix', height=50, color='White', pos=[0,-450], wrapWidth=int(1600))
    vas_start_time = g.clock.getTime()
    while scale_1.noResponse:
        if event.getKeys(["escape"]):
            raise QuitException()
        #item.draw()
        text_1.draw()
        scale_1.draw()
        top_text.draw()
        #bot_text.draw()
        g.win.flip()
    g.mouse.setVisible(0)
    return scale_1.getRating()

#a routine to update the string on the screen as the participant types
def update_response_string(captured_string, captured_response, instructions, win):
    captured_response.setText(captured_string)
    captured_response.draw()
    instructions.draw()
    win.flip()
    
def get_text_response(question, win, clk):
    start_time = clk.getTime()
    captured_response = visual.TextStim(win, 
                        units='pix',height = 30,
                        pos=(-500, 0.0), text='',
                        alignHoriz = 'left',alignVert='top',
                        color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1], wrapWidth=int(1000))
    captured_response.draw()
    captured_string = ''
    instructions = visual.TextStim(win,text="",units='pix',pos=[0,130],color=[win.color[0] * -1, win.color[1] * -1, win.color[2] * -1],height=50,wrapWidth=int(1600))
    instructions.setText(question)
    instructions.draw()
    win.flip()
    while True:
        for key in event.getKeys():
            #quit at any point
            if key in ['escape']: 
                raise QuitException()
            #if the participant hits return, save the string so far out 
            #and reset the string to zero length for the next trial
            elif key in ['return']:
                end_time = clk.getTime()
                return captured_string, end_time, end_time - start_time
            #allow the participant to do deletions too , using the 
            # delete key, and show the change they made
            elif key in ['delete','backspace']:
                captured_string = captured_string[:-1] #delete last character
                update_response_string(captured_string, captured_response, instructions, win)
            #handle spaces and punctuation
            elif key in ['space']:
                captured_string = captured_string+' '
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['period']:
                captured_string = captured_string+'.'
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['comma']:
                captured_string = captured_string+','
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['semicolon']:
                captured_string = captured_string+';'
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['apostrophe']:
                captured_string = captured_string+"'"
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['slash']:
                captured_string = captured_string+'/'
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['backslash']:
                captured_string = captured_string+'\\'
                update_response_string(captured_string, captured_response, instructions, win)
            elif key in ['lshift','rshift','capslock']:
                pass #do nothing when some keys are pressed
            #etc ...
    #if any other key is pressed, add it to the string and 
            # show the participant what they typed
            else: 
                captured_string = captured_string+key
                #show it
                update_response_string(captured_string, captured_response, instructions, win)
    now = clk.getTime()
    return captured_string, now, now - start_time
    
def get_var_dict_from_file(filename, default_dict):
    #get a list of variables from a file--each line of the file should contain two space separated strings--the variable name and its value
    if not os.path.isfile(filename):
        return default_dict #no file, so all params remain unchanged
    fin = open(filename, 'r')
    for line in fin:
        these_vals = line.split()
        try:
            default_dict[these_vals[0]] = ast.literal_eval(these_vals[1]) #convert numbers and bools (possibly also dictionaries and lists)
        except ValueError:
            print default_dict
            print these_vals[0]
            print these_vals[1]
            default_dict[these_vals[0]] = these_vals[1] #leave others as strings
                
    fin.close()
    return default_dict #note: this function also changes the dictionary in place
    
def get_var_from_files(filenames, var): #return the first non-None value found in filenames (taken in order), or provide a popup if it can't be found in any of them
    for f in filenames:
        v = get_var_from_file(f, var)
        if v:
            return v
    #popup asking for value because it couldn't be found        
    while True:
        myDlg = gui.Dlg(title='Variable Read Fail')
        myDlg.addText('Could not read ' + var + ' from ' + str(filenames) + '. Please enter the appropriate value below.')
        myDlg.addField(var)
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
            break
        else:
            pass
    try:
        return ast.literal_eval(thisInfo[0])
    except:
        return thisInfo[0]
    
def get_var_from_file(filename, var):
    #opens file named filename, then reads line by line until it finds 'var value'
    #returns value from that file, or None if either the file or var DNE
    if not os.path.isfile(filename): #filename will be local file--check network storage second, then provide a popup for the user to enter the variable value
        return None
    fin = open(filename, 'r')
    for line in fin:
        these_vals = line.split()
        if these_vals[0] == var:
            fin.close()
            try:
                return ast.literal_eval(these_vals[1])
            except ValueError:
                return these_vals[1]
    fin.close()
    return None 
    
def write_var_to_files(filenames, var, value): #used to write the same value to multiple files--e.g. to a local file and another on storage if possible
    for f in filenames:
        write_var_to_file(f, var, value)

def write_var_to_file(filename, var, value):
    if isinstance(value, basestring):
        value = '\'' + value + '\'' #add single quotes so when it gets written to a file and then read, it will still be a string
    if get_var_from_file(filename, var) == None: #either file DNE, or variable isn't in the file
        fout = open(filename, 'a')
        fout.write(var + ' ' + str(value) + '\n')
        fout.close()
        return 
    fin = open(filename, 'r')
    time = core.getTime()
    fout_name = 'temp_file.' + str(time) 
    fout = open(fout_name, 'w')
    for line in fin:
        these_vals = line.split()
        if these_vals[0] == var:
            fout.write(var + ' ' + str(value) + '\n')
        else:
            fout.write(line)
    fin.close()
    fout.close()
    move(fout_name, filename)
       
def convert_run_args_to_dict(run_args):
    #run_args will be a string of the format 'var1=val1 var2=val2 var3=val3'
    #convert it to be {var1:val1, var2:val2, var3:val3}
    arg_dict = {}
    if run_args == []:
        arg_dict
    for arg in run_args.split():
        this_pair = arg.split('=')
        try:
            arg_dict[this_pair[0]] = ast.literal_eval(this_pair[1]) #convert numbers and bools (possibly also dictionaries and lists)
        except ValueError:
            arg_dict[this_pair[0]] = this_pair[1] #leave others as strings
    return arg_dict
     
def volume_workup(sound_file, start_volume):
    
    s = sound.Sound(sound_file)
    possible_options = ['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']
    c = possible_options[int(start_volume * 10):] #don't let the user pick a volume less than the starting volume
    last_volume = str(start_volume)
    while True:
        myDlg = gui.Dlg(title="Volume")
        myDlg.addText('Adjust the volume so you can comfortably hear the sound.  Press OK to play the sound and change "choice" to "accept" once you have found a volume you like.')
        myDlg.addField('Volume', choices=possible_options, initial=last_volume)
        myDlg.addField('Choice', choices=['play', 'accept'], initial='no')
        myDlg.show()  # show dialog and wait for OK or Cancel
        thisInfo = myDlg.data
        if myDlg.OK:  # then the user pressed OK
            last_volume = thisInfo[0]
            if thisInfo[1] == 'accept':
                return float(last_volume) * 0.3
            s.setVolume(float(last_volume) * 0.3)
            s.play()
        else:
            return float(last_volume)
            
def prefix_used(used_list, new_prefix):
    for u in used_list:
        if u.startswith(new_prefix):
            return True
    return False
def generate_prefix(g):
    #run_id will be specified in the config file for the current run and may be something like T0_..BH_R1_
    if not os.path.exists(g.session_params['output_dir']):
        os.makedirs(g.session_params['output_dir'])
    names_used = os.listdir(g.session_params['output_dir'])
    #names_used = os.listdir(os.path.join(os.path.dirname(__file__), 'DATA'))
    start_prefix = g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['run_id']
    i = 1
    prefix = start_prefix
    while True:
        if prefix_used(names_used, prefix):
            prefix = start_prefix + '-' + str(i)
            i = i + 1
        else:
            break
    
    #prefix = os.path.join(os.path.dirname(__file__), 'DATA', prefix)
    prefix = os.path.join(g.session_params['output_dir'], prefix)
    return prefix
 

def redirect_output(session_params):
    if not os.path.exists(session_params['output_dir']):
        os.makedirs(session_params['output_dir'])
    prefix = session_params['output_dir'] + session_params['SID'] + '_' + data.getDateStr() + '.txt'
    
    sys.stdout = open(prefix, 'a', 0)
    sys.stderr = open(prefix, 'a', 0)
 
def close_output():
    sys.stdout.close()
    sys.stderr.close()
        
  
def get_exam_number(session_params):
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = {'run_id':'SCAN-RX-EXAM'}
    prefix = generate_prefix(g)
    fileName = os.path.join(prefix + '.txt')
    g.output = open(fileName, 'w')
    while True:
        myDlg = gui.Dlg(title='Exam Number')
        myDlg.addText('What is the exam number (e.g. SXXXX)')
        myDlg.addField('Exam Number')
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            continue
        exam = thisInfo[0]
        if exam == '':
            continue
        break
    g.output.write(exam)
    g.output.close()
    
def check_retry_vMeter(g):
    if g.session_params['vMeter']:
        return
    g.session_params['vMeter'] = try_to_open_vMeter()
    while True:
        if g.session_params['vMeter']:
            return
        myDlg = gui.Dlg(title='vMeter Test')
        myDlg.addText('vMeter not found.  Reconnect it and OK to retry, or Cancel to abort')
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK--try to connect vMeter
            #open_and_close_vMeter()
            g.session_params['vMeter'] = try_to_open_vMeter()
        else:
            raise QuitException()
        
        
        
  
  
