#!/opt/apps/core/python/2.7.11/bin/python

from random import shuffle
from random import seed

seed(123)

image_file = open('DCR_selected_split-MatchedHSV.csv', 'r')


#list of list of lists--session:block:image
neutral_images = [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]
meth_images = [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]
opioid_images = [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]


neutral_path = 'media\\MethOpioidDatabase\\finalcueset\\ExtractedNeutralCues120\\'
meth_path = 'media\\MethOpioidDatabase\\finalcueset\\ExtractedMethCues120\\'
opioid_path = 'media\\MethOpioidDatabase\\finalcueset\\ExtractedOpioidCues120\\'

meth_count = 0
for l in image_file.readlines()[1:]: #skip header line, build lists of images
   this_line = l.split(',')
   category = int(this_line[75]) - 1
   fname = this_line[0]
   run = int(this_line[77])
   if this_line[64] == 'control':
      image_fullpath = neutral_path + fname
      neutral_images[run][category].append(image_fullpath)
   if this_line[64] == 'meth':
      image_fullpath = meth_path + fname
      meth_images[run][category].append(image_fullpath)
   if this_line[64] == 'opioid':
      image_fullpath = opioid_path + fname
      opioid_images[run][category].append(image_fullpath)



print neutral_images
print meth_images
print opioid_images



for i in range(0, 3):
   for j in range(0, 6):
      shuffle(opioid_images[i][j])
      shuffle(meth_images[i][j])
      shuffle(neutral_images[i][j])




def generate_one(neutral_images, drug_images, output_name):
   schedule_lines = []
   iti_durations = ['8','8','8','10','10','12','12','12']
   iti_idx = 0
   shuffle(iti_durations)
   schedule_lines.append('TrialTypes,Stimuli,Durations,ExtraArgs')
   schedule_lines.append('090,media\\blank.png,10,')
   box_values = ['0', '0', '0', '0', '0', '1']
   for i in range(0,4): #four blocks, alternating between neutral and drug blocks
      shuffle(box_values)
      neutral_lines = [box_values[0] + '00,' + neutral_images[0][i] + ',5,']
      neutral_lines.append(box_values[1] + '01,' + neutral_images[1][i] + ',5,')
      neutral_lines.append(box_values[2] + '02,' + neutral_images[2][i] + ',5,')
      neutral_lines.append(box_values[3] + '03,' + neutral_images[3][i] + ',5,')
      neutral_lines.append(box_values[4] + '04,' + neutral_images[4][i] + ',5,')
      neutral_lines.append(box_values[5] + '05,' + neutral_images[5][i] + ',5,')
      shuffle(neutral_lines)
      neutral_lines.append('009,media\\meth\\urge_question.PNG,5,')
      neutral_lines.append('091,media\\fixation.png,' + iti_durations[iti_idx] + ',')
      iti_idx = iti_idx + 1
      shuffle(box_values)
      drug_lines = [box_values[0] + '10,' + drug_images[0][i] + ',5,']
      drug_lines.append(box_values[1] + '11,' + drug_images[1][i] + ',5,')
      drug_lines.append(box_values[2] + '12,' + drug_images[2][i] + ',5,')
      drug_lines.append(box_values[3] + '13,' + drug_images[3][i] + ',5,')
      drug_lines.append(box_values[4] + '14,' + drug_images[4][i] + ',5,')
      drug_lines.append(box_values[5] + '15,' + drug_images[5][i] + ',5,')
      shuffle(drug_lines)
      drug_lines.append('019,media\\meth\\urge_question.PNG,5,')
      drug_lines.append('091,media\\fixation.png,' + iti_durations[iti_idx] + ',')
      iti_idx = iti_idx + 1
      schedule_lines = schedule_lines + neutral_lines + drug_lines
   schedule_lines = schedule_lines + ['090,media\\blank.png,10,']
   schedule_out = open(output_name, 'w')
   for l in schedule_lines:
      print l
      schedule_out.write(l + '\n')
   schedule_out.close()


generate_one(neutral_images[0], meth_images[0], 'DCR_R1_METH.schedule')
generate_one(neutral_images[1], meth_images[1], 'DCR_R2_METH.schedule')
generate_one(neutral_images[2], meth_images[2], 'DCR_R3_METH.schedule')

generate_one(neutral_images[0], opioid_images[0], 'DCR_R1_OPIOID.schedule')
generate_one(neutral_images[1], opioid_images[1], 'DCR_R2_OPIOID.schedule')
generate_one(neutral_images[2], opioid_images[2], 'DCR_R3_OPIOID.schedule')






















