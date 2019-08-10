

*****************************************************************SUMMARY**************************************************************************

This task shows blocks of images, followed by a craving rating and then an intertrial interval.
It was developed for meth cue reactivity, but could be configured for other categories.

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

   10s						   5s		0.2s				  5s		  			0.2s			   	  5s							   8-12s
[Lead in]			->		[image] -> [blank] -> [			 image			] 	-> [blank]     -> [		rating		] 		-> 		[		ITI		] -> [image]
							^					  ^				    ^		  				  	  ^      		^ ^ ^				^
						IMAGE_ONSET		IMAGE_ONSET-BOX_ONSET	BOX_RESPONSE				RATING_ONSET   RATING_RESPONSE	    IMAGE_ONSET
	


*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: Trial type (see below for a list of trial types)
COLUMN 2: Image to show
COLUMN 3: trial duration
COLUMN 4: not used
TRIAL ORDER: fixed


090 -> leadin/out
091 -> fixation

000 -> neutral object
001 -> neutral object with hand
002 -> neutral tools
003 -> neutral tools with hands, simple
004 -> neutral tools with hands, complex
005 -> neutral tools with faces
009 -> neutral block rating

010 -> meth
011 -> meth and hand
012 -> meth instruments
013 -> meth instruments and hands
014 -> meth injection and hands
015 -> meth activities and faces
019 -> meth block rating

change the leading 0 to a 1 to indicate it is a box trial, where the subject should press a button to remove a border from the image (not applicable for rating trials)


*****************************************************************OUTPUT DETAILS*******************************************************************

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

IMAGE_ONSET (3)
response_time: not used
response: not used
result: image shown

BOX_ONSET (4)
response_time: not used
response: not used
result: not used

BOX_RESPONSE (5)
response_time: time between BOX_ONSET and BOX_RESPONSE, or NA for no response
response: which button was pressed, or NA if no response
result: 0 for no response, 1 for first response in a box trial, 2 otherwise (i.e. for extra responses, button presses on non-box trials)

RATING_ONSET (6)
response_time: not used
response: not used
result: image shown, should have text for a question with 4 possible responses

RATING_RESPONSE (7)
response_time: time between RATING_ONSET and RATING_SELECTION, or NA for no response
response: selection chosen, from 1-4, or NA for no response
result: not used, or NA for no response





