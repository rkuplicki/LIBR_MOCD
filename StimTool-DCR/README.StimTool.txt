README for the StimTool application

*****************************************************************SUMMARY**************************************************************************

StimTool is a framework for running a series of behavioral tasks.
Each task is implemented as a separate module which is then called by StimTool.


*****************************************************************INSTALL INSTRUCTIONS*************************************************************
Install PsychoPy (used for all components)
Update PsychoPy to 1.80.06 (various bug fixes--some later versions seem to introduce new bugs and would need to be tested)
Install OpenCV (used for video capture) (instructions here: http://docs.opencv.org/trunk/doc/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html)
	run opencv-2.4.9.exe to extract the files
	copy opencv/build/python/2.7/x86/cv2.pyd to C:\Program Files (x86)\PsychoPy2\Lib\site-packages (assuming default PsychoPy location)
	In a python interpreter, run 'import cv2' and then 'cv2.__version__' to confirm successful install
Install Xvid codec (used for video capture)
	Run Xvid-1.3.3-20140407.exe
	Select 'No, I want to check for updates manually.'
Install inpout32 (parallel port driver--used for signalling to BIOPAC or similar)
	run InpOutBinaries_1500/Win32/InstallDriver.exe
	Modify Default.params to set the parallel port address
Install pygame version 1.9.1--this is necessary because the current version of PsychoPy comes with version pygame 1.9.2a0, which has a bug when using portmidi (control for the VMeter)
	run pygame-1.9.1.win32-py2.7.msi
	select Python from another location -> Will be installed on local hard drive
		set the path to C:\Program Files (x86)\PsychoPy2\
Modify two lines in C:\Program Files (x86)\PsychoPy2\Lib\site-packages\PsychoPy-1.80.03-py2.7.egg\psychopy\hardware\joystick\pyglet_input\directinput.py
	This is a bug in the current version of PsychoPy and will likely be fixed (and no longer necessary) in a future release
	These changes are needed to use the joystick
	On lines 131 and 150, change _dispatch_events = dispatch_events (remove the underscore)
Install ASIO4ALL
	Right now, this is necessary to decrease sound latency.  You may not need to take this step depending on your sound card/drivers.
	ASIO4ALL_2_11_English.exe
	Test latency by running sound_test.py.
		An 'X' will appear and disappear a few times--there should also be a burst of white noise that occurs simultaneously if things are working properly.  If things are not, there may be a delay of ~400ms.
Replace C:\Program Files (x86)\PsychoPy2\Lib\site-packages\PsychoPy-1.80.03-py2.7.egg\psychopy\visual\dot.py with dot.py the version found in the installation files
	This is due to a bug in the current PsychoPy2 release (causing dots units to be used incorrectly) that will be fixed with the next release
*****************************************************************INPUT FORMAT*********************************************************************

*****************************************************************MODULE OUTPUT FORMAT*************************************************************
Modules all create output by calling the function StimToolLib.mark_event(fout, trial, trial_type, event_id, event_time, response_time, response, result, write_to_parallel).


Modules should raise (and catch) a StimToolLib.QuitException anytime esc is pressed, then do whatever cleanup is necessary and return -1.
Modules are responsible for their own cleanup (close window on exit, close output files, etc.).
Modules should call task_start_parallel() at the beginning of instructions (after loading stimuli)--this will send a signal to BIOPAC and start recording from the camera (if the appropriate paramters are set--found in a .parameters file with the same prefix as the .TL file that was run).