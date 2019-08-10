
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound

#Emotional Reactivity module: present a series of images, sometimes accompanied by startles

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.x = None #X fixation stimulus
        self.output = None #The output file
        self.msg = None
        self.ideal_trial_start = None #ideal time the current trial started
        self.trial = None #trial number
        self.trial_type = None #trial type
        self.rate_mark_start = [0,-117]
        self.rate_length = 5
        self.rating_marker = None
        self.rating_marker_selected = None


event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'IMAGE_ONSET':3, #this will be for fixation, neutral, or drug cues
    'BOX_ONSET':4, #at the beginning of image trials where the subject should respond by pressing a button
    'BOX_RESPONSE':5, #when the subject responds to the box 
    'RATING_ONSET':6, #after each block, when subjects should make a craving rating
    'RATING_RESPONSE':7,#when the subject makes a craving rating
    'TASK_END':StimToolLib.TASK_END 
    }



def do_one_image_trial(trial_type, image, duration):
    #run a single image trial, which can also be a fixation
    #draw image to show
    image.draw() 
    draw_box = False #will be True for border trials, and then set to False once they hit a button
    if trial_type[0] == '1':
        #box trial--draw the box and detect a response
        draw_box = True
        g.box.draw()

    g.win.flip()
    image_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['IMAGE_ONSET'], image_start, 'NA', 'NA', image._imName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if draw_box: #record the time when the border was shown
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BOX_ONSET'], image_start, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    event.clearEvents() #clear old keypresses
    while g.clock.getTime() < g.ideal_trial_start + duration:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['up'], g.session_params['down']])
        if resp: #subject pressed a key
            now = g.clock.getTime()
            if draw_box:
                response_result = 1
            else:
                response_result = 2
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BOX_RESPONSE'], now, now - image_start, resp[0], response_result, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            draw_box = False
        image.draw() #have to draw the image first--otherwise it will cover the box!
        if draw_box:
            g.box.draw()
        g.win.flip()
        StimToolLib.short_wait()
    if draw_box: #mark that the subject missed the response, so it's easy to find later (instead of having to look for a BOX_ONSET
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BOX_RESPONSE'], g.clock.getTime(), 'NA', 'NA', 0, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])    

            
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration + 0.2) #200ms blank screen
    #update trial start time
    g.ideal_trial_start = g.ideal_trial_start + duration + 0.2
    if draw_box and g.run_params['practice']:
        #for practice trials where the subject didn't respond to the box, show a reminder about responding to the yellow frame and then repeat the trial until they respond
        g.frame_reminder.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + 3)
        g.ideal_trial_start = g.ideal_trial_start + 3
        do_one_image_trial(trial_type, image, duration)

def do_one_rating_trial(trial_type, image, duration):
    #get one (craving) rating, from 1-4
    #draw question image
    image_to_show = g.question_image
    image_to_show.draw() 
    g.win.flip()
    rating_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], rating_start, 'NA', 'NA', g.question_image._imName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents() #clear old keypresses
    responded = False
    while g.clock.getTime() < g.ideal_trial_start + duration:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        #the g.run_params['select_X'] is needed to handle left/right button boxes with 4 buttons
        resp = event.getKeys([g.session_params[g.run_params['select_1']], g.session_params[g.run_params['select_2']], g.session_params[g.run_params['select_3']], g.session_params[g.run_params['select_4']]])
        if resp: #subject pressed a key
            responded = True
            response = resp[0]
            if response == g.session_params[g.run_params['select_1']]:
                image_to_show = g.response_image_1
                r = 1
            if response == g.session_params[g.run_params['select_2']]:
                image_to_show = g.response_image_2
                r = 2
            if response == g.session_params[g.run_params['select_3']]:
                image_to_show = g.response_image_3
                r = 3
            if response == g.session_params[g.run_params['select_4']]:
                image_to_show = g.response_image_4
                r = 4
            now = g.clock.getTime()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_RESPONSE'], now, now - rating_start, r, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            draw_box = False
        image_to_show.draw() #have to draw the image first--otherwise it will cover the box!
        g.win.flip()
        StimToolLib.short_wait()
    if not responded: #mark that the subject missed the response, so it's easy to find later (instead of having to look for a BOX_ONSE
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])    
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    g.win.flip()
    #update trial start time
    g.ideal_trial_start = g.ideal_trial_start + duration


def do_one_trial(trial_type, image, duration):
    if trial_type[2] == '9':
        #rating trial, draw rating image, or rating text...
        do_one_rating_trial(trial_type, image, duration)
    else:
        do_one_image_trial(trial_type, image, duration)
    
    
    
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/CR.Default.params', {})
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
        myDlg = gui.Dlg(title="CR")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)


    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    StimToolLib.general_setup(g)
    trial_types,images,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    durations = durations[0] #durations of the images/itis
    images = images[0]
    for i in images:
        i.size = (g.session_params['screen_x'], g.session_params['screen_y']) #set stimulus images to be fullscreen
    #for i in range(len(trial_types)): #convert to int for easier decoding
    #    trial_types[i] = int(trial_types[i])
    

    #g.rating_marker = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_mark_down.png'), pos=[285,-450], units='pix')
    #g.rating_marker_selected = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_mark_down_selected.png'), pos=[285,-450], units='pix')
    
    
    g.box = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media','YellowFrame.gif'), units='pix', mask=os.path.join(os.path.dirname(__file__),  'media/frame_mask.gif'))
    g.box.size = (g.session_params['screen_x'], g.session_params['screen_y']) #set stimulus images to be fullscreen

    #initialize question/response images
    g.question_image = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['question_image']))
    g.response_image_1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_1']))
    g.response_image_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_2']))
    g.response_image_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_3']))
    g.response_image_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_4']))
    g.frame_reminder = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media', 'frame_reminder.PNG'))

    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.iteritems(), key=operator.itemgetter(1))
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.CUE_REACTIVITY_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = instruct_end_time
    g.win.flip()
    
    
    for t, i, d in zip(trial_types, images, durations):
        g.trial_type = t
        do_one_trial(t, i, d)
        g.trial = g.trial + 1
    
  
 


