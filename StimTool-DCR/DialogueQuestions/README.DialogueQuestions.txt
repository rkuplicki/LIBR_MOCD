README for the Rest task

*****************************************************************SUMMARY**************************************************************************

This task presents a set of questions in dialogues and records the responses.
E.g., it can be used to automate collection/storage of a set of impedance values after setting up physio recording equipment.

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         question         ] -> [question] ->...
                                 ^                           ^
                              RESPONSE                   TASK_END



*****************************************************************INPUT DETAILS********************************************************************

This task uses a somewhat different input format.
Each line in a .schedule file specifies a single question.
There should be two comma separated values: the first is the question, the second is True or False.
If the second value is True, the response is forced to be a numerical value--so if the user input cannot be cast into a float then the question is repeated.

*****************************************************************OUTPUT DETAILS*******************************************************************

RESPONSE (1)
response_time: time the dialogue box was up before it was answered
response: response entered into the box
result: actual question text used

TASK_END (99)
response_time: not used
response: not used
result: not used


