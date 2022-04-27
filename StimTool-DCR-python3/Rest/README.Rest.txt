README for the Rest task

*****************************************************************SUMMARY**************************************************************************

This task presents crosshairs for a set duration (e.g. for resting state fMRI)

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] -> [       fixation       ]
      ^                              ^                           ^
INSTRUCT_ONSET                   TASK_ONSET	                    TASK_END



*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: only one line--total run length
COLUMN 1: not used
COLUMN 2: not used
COLUMN 3: duration of fixation
COLUMN 4: not used
TRIAL ORDER IS: fixed

*****************************************************************OUTPUT DETAILS*******************************************************************

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

TASK_END (99)
response_time: not used
response: not used
result: not used


