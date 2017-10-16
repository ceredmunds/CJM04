#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CJM02 - PIT experiment, adapted from Seabrooke et al. (2017)
# CERE - 2-10-2017 - Created
import os
from itertools import permutations
from random import shuffle
from psychopy import visual, event, core, gui, data

#os.chdir("C:/Users/cjmitchell/Desktop/PIT Charlotte")

class PIT:
    def __init__(self):
        self.expName = "CJM02"
        self.dataPath = "Data"
        
        self.rt_clock = core.Clock()
        self.ITI = 0.5
        self.feedbackTime = 3
        self.waitTime = 6
        self.stimulusTime = 3
        
        self.pptNo = None
        self.pptGender = None
        self.pptAge = None
        self.pptLH = None
        self.experimenter = "CERE"
        self.date = data.getDateStr()
        
        self.outcomes = ["O1","O2","O3","O4"]
        self.stimuli = ["crisps", "popcorn", "nachos", "cashews"]
        self.imageFiles = {"crisps":"Images/crisps.bmp", "popcorn":"Images/popcorn.bmp",
                           "nachos":"Images/nachos.bmp", "cashews":"Images/cashews.bmp"}
        self.choiceText = u'\u2190' + ' or ' + u'\u2192'
    
    def runExperiment(self):
        self.start_experiment()
        
        self.run_liking_ratings()
        self.run_instrumental_training()
        self.run_instrumental_knowledge_test()
        
        self.run_outcome_devaluation()
        self.run_liking_ratings(time="second")
        
        self.run_transfer_test()
        self.run_experiment_knowledge_tests()
        
        self.thanksAndGoodbye()
    
    def start_experiment(self):
        self.get_ppt_info()
        self.open_data_file()
        self.open_window()
        self.get_counterbalancing()
        
        self.display_welcome()
    
    def get_ppt_info(self):
        ppt_info = { 
                    "Participant number" : "", 
                    "Gender" : ("Female", "Male", "Other"), 
                    "Age" : "", 
                    "Left-handed" : False, 
                    }
        dlg_box = gui.DlgFromDict(dictionary=ppt_info, title=(self.expName+' Participant information'))
        # Check whether valid participant number data
        if dlg_box.OK == False:  # then the user pressed OK
            print 'User cancelled'
            core.quit() 
        if len(ppt_info["Participant number"])!=2:
            print "Error: Invalid participant number"
            core.quit()
        self.pptNo = int(ppt_info["Participant number"])
        self.pptGender = ppt_info["Gender"]
        self.pptAge = ppt_info["Age"]
        self.pptLH = ppt_info["Left-handed"]
        
        counterbalancing = list(permutations([1,2,3,4]))
        self.counterbalancing = list(counterbalancing[self.pptNo%24])
    
    def open_data_file(self):
        self.get_file_name()
        self.dataFile = open(self.fileName, 'w') 
        
        self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                "DAU","ParticipantNo","Date","Age","Gender","Experimenter", 
                "ExperimentPhase", "Trial", "TrialType","Response", "Outcome", "Food",
                "Devalued","RT", "Correct"))
    
    def get_file_name(self):
        if not os.path.isdir(self.dataPath):
            os.makedirs(self.dataPath)  # if this fails (e.g. permissions) we will get error
        
        self.fileName = self.dataPath + "/" + "%s_Ppt_%s.csv" %(self.expName, self.pptNo)
    
    def open_window(self):
        self.win = visual.Window(size=[2880, 1800], color="black",
                    fullscr=True, allowGUI=False, checkTiming=True)
    
    def get_counterbalancing(self):
        reorderedFoods = [self.stimuli[i-1] for i in self.counterbalancing]
        self.outcomeMapping = dict(zip(self.outcomes, reorderedFoods))
    
    def display_welcome(self):
        line1 = visual.TextStim(self.win, text='Welcome!', font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.2)
        line1.draw()
        
        line2 = visual.TextStim(self.win, text='Thank you for taking part in the experiment', font='helvetica', 
                                pos=(0,0), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line2.draw()
        
        self.press_space()
    
    def press_space(self):
        pressSpace = visual.TextStim(self.win, text="Please press space", font='helvetica', 
                                     pos=(0,-0.7), wrapWidth=1.5, height=0.1)
        pressSpace.draw()
        self.win.flip()
        keys = event.waitKeys(keyList=['space'])
    
    def run_liking_ratings(self, time="first"):
        outcomes = self.outcomes
        shuffle(outcomes)
        trialNo = 0
        
        self.display_liking_ratings_instructions(time)
        if time=="first": 
            ExpPhase = "LikingBefore"
        else:
            ExpPhase = "LikingAfter"
        
        for outcome in outcomes:
            trialNo += 1
            self.win.callOnFlip(self.rt_clock.reset)
            question = "How much would you like to eat " + self.outcomeMapping[outcome].upper() + "?"
            item = visual.TextStim(self.win, text=question, height=.05, units='norm', pos=(0, 0.3))
            
            ratingScale = visual.RatingScale(self.win, low=1, high=7, textSize=0.6, noMouse=True, minTime=0.2,
                                         textFont='Helvetica', singleClick=True, showAccept=False,
                                         textColor='white', pos=(0,0), choices=["1","2","3","4","5","6","7"], 
                                         respKeys=["1","2","3","4","5","6","7"], marker=visual.TextStim(self.win, text='[]', units='norm', opacity=0),
                                         scale="Not at all . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . Very much")
            while ratingScale.noResponse:
                ratingScale.draw()
                item.draw()
                self.win.flip()
            rating = ratingScale.getRating()
            confRT = ratingScale.getRT()
            
            self.win.flip()
            core.wait(self.ITI)
            
            if outcome=="O1" or outcome=="O2":
                devalued = 0
            else:
                devalued = 1 
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                ExpPhase, trialNo, outcome, rating, outcome, self.outcomeMapping[outcome], devalued, confRT, "NA"))
    
    def display_liking_ratings_instructions(self, time="first"):
        if time=="first":
            line1 = visual.TextStim(self.win, text='In this task, you can earn crisps, popcorn, cashews and nachos points.', 
                                    font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.1, alignHoriz='center')
            line1.draw()
        
        line2 = visual.TextStim(self.win, text='We would like you to rate how much you would like to eat each food.', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1)
        line2.draw()
        
        self.press_space()
    
    def get_instrumental_training_trials(self):
        trialTypes = ["O1O2","O3O4"]*24
        shuffle(trialTypes)
        return trialTypes
    
    def run_instrumental_training(self):
        trials = self.get_instrumental_training_trials()
        choiceText = visual.TextStim(self.win, text=self.choiceText, color="white", font="Arial", height=0.2)
        trialNo = 0
        
        self.display_instrumental_training_instructions()
        
        for t in trials:
            trialNo += 1
            if t == "O1O2":
                rightCue = "O1"
                leftCue = "O2"
            elif t=="O3O4":
                rightCue = "O3"
                leftCue = "O4"
            rightFood = self.outcomeMapping[rightCue]
            leftFood = self.outcomeMapping[leftCue]
            
            choiceText.draw()
            self.win.callOnFlip(self.rt_clock.reset)
            self.win.flip()
            
            key_press = event.waitKeys(keyList=['e','i'], timeStamped=self.rt_clock)
            
            if key_press[0][0]=="e":
                cue = leftCue
                food = leftFood
                response = "Left"
            elif key_press[0][0]=="i":
                cue = rightCue
                food = rightFood
                response = "Right"
            
            text = "You win one " + food.upper() + " point"
            
            feedback = visual.TextStim(self.win, text=text, pos=(0,0), height=0.09)
            feedback.draw()
            self.win.flip()
            core.wait(self.feedbackTime)
            
            self.win.flip()
            core.wait(self.ITI)
            
            if cue=="O1" or cue=="O2":
                devalued = 0
            else:
                devalued = 1 
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                "InstrumentalTraining", trialNo, t, response, cue, food, devalued, key_press[0][1],"NA"))
    
    def display_instrumental_training_instructions(self):
        line1 = visual.TextStim(self.win, text='You can now earn the four foods shown before by pressing the left ("E") or right ("I") key.', 
                                font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        line2 = visual.TextStim(self.win, text='Your task is to learn which keys earn each food.', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1)
        line2.draw()
        
        self.press_space()
    
    def run_instrumental_knowledge_test(self):
        outcomes = self.outcomes
        shuffle(outcomes)
        trialNo = 0
        
        self.display_instrumental_knowledge_instructions()
        
        for outcome in outcomes:
            trialNo += 1
            correct = 0
            
            question = visual.TextStim(self.win, text=("Which key earned "+ self.outcomeMapping[outcome] +" points, the left or right key?"), pos=(0,0), height=0.09)
            question.draw()
            
            question1 = visual.TextStim(self.win, text=("Please choose carefully"), pos=(0,-0.2), height=0.09)
            question1.draw()
            
            self.win.callOnFlip(self.rt_clock.reset)
            self.win.flip()
            
            key_press = event.waitKeys(keyList=['e','i'], timeStamped=self.rt_clock)
            if key_press[0][0]=="e":
                response = "Left"
                if outcome=="O2" or outcome=="O4":
                    correct = 1
            elif key_press[0][0]=="i":
                response = "Right"
                if outcome=="O1" or outcome=="O3":
                    correct = 1
            
            self.win.flip()
            core.wait(self.ITI)
            
            if outcome=="O1" or outcome=="O2":
                devalued = 0
            else:
                devalued = 1 
                
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                "InstrumentalKnowledge", trialNo, "Choice", response, outcome, 
                self.outcomeMapping[outcome], devalued, key_press[0][1], correct))
            
            trialNo += 1
            self.win.callOnFlip(self.rt_clock.reset)
            
            item = visual.TextStim(self.win, text="How confident are you of this choice?", 
                                   height=.05, units='norm', pos=(0, 0.3))
            ratingScale = visual.RatingScale(self.win, low=1, high=7, textSize=0.6, noMouse=True, minTime=0.2,
                                         textFont='Helvetica', singleClick=True, showAccept=False,
                                         textColor='white', pos=(0,0), choices=["1","2","3","4","5","6","7"], 
                                         respKeys=["1","2","3","4","5","6","7"], marker=visual.TextStim(self.win, text='[]', units='norm', opacity=0),
                                         scale="Not at all confident . . . . . . . . . . . . . . . . . . . . . . . . . . . . . Very confident")
            while ratingScale.noResponse:
                ratingScale.draw()
                item.draw()
                self.win.flip()
            rating = ratingScale.getRating()
            confRT = ratingScale.getRT()
            
            self.win.flip()
            core.wait(self.ITI)
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                "InstrumentalKnowledge", trialNo, "Confidence", rating, outcome, 
                self.outcomeMapping[outcome], devalued, confRT, "NA"))
    
    def display_instrumental_knowledge_instructions(self):
        line1 = visual.TextStim(self.win, text='We would now like to test whether you know which key earned which foods', 
                                font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        self.press_space()
    
    def run_outcome_devaluation(self):
        wellDone = visual.TextStim(self.win, text=("Well done!"), pos=(0,0), height=0.12)
        text1 = visual.TextStim(self.win, text=("You've finished the first half of the experiment"), 
                               pos=(0,-0.2), height=0.09, wrapWidth=2)
        text2 = visual.TextStim(self.win, text=("Please see the experimenter"), pos=(0,-0.7), height=0.12)
        
        wellDone.draw()
        text1.draw()
        text2.draw()
        
        self.win.flip()
        core.wait(self.waitTime)
    
    def run_transfer_test(self):
        self.display_transfer_test_instructions()
        
        self.run_transfer_test_training()
        
        trials = self.get_transfer_test_trials()
        choiceText = visual.TextStim(self.win, text=self.choiceText, color="white", font="Arial")
        trialNo = 0
        
        self.display_transfer_test_final_instructions()
        
        
        for t in trials:
            trialNo += 1
            correct=0
            
            self.win.callOnFlip(self.rt_clock.reset)
            stimulus = visual.ImageStim(self.win, image=self.imageFiles[self.outcomeMapping[t]], pos=(0,0.5))
            stimulus.draw()
            self.win.flip()
            core.wait(self.stimulusTime)
            
            stimulus.draw()
            choiceText.draw()
            self.win.flip()
            
            key_press = event.waitKeys(keyList=['e','i'], timeStamped=self.rt_clock)
            if key_press[0][0]=="e":
                response = "Left"
                if t=="O2" or t=="O4":
                    correct = 1
            elif key_press[0][0]=="i":
                response = "Right"
                if t=="O1" or t=="O3":
                    correct = 1
            
            self.win.flip()
            core.wait(self.ITI)
            
            if t=="O1" or t=="O2":
                devalued = 0
            else:
                devalued = 1 
                
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                "TransferTest", trialNo, t, response, t, self.outcomeMapping[t], 
                devalued, key_press[0][1], correct))
    
    def display_transfer_test_instructions(self):
        line1 = visual.TextStim(self.win, text=('In this part of the task, you can earn the four foods by pressing'+
                                                ' the left ("E") or right ("I") key in the same way as before'), 
                                font='helvetica', pos=(0,0.5), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        line2 = visual.TextStim(self.win, text=('You will only be told how much of each food'+
                                                ' you have earned at the end of the experiment.'), 
                                font='helvetica', pos=(0,0.2), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line2.draw()
        
        line3 = visual.TextStim(self.win, text=('Also, sometimes pictures of the foods will be presented'+
                                                ' before you choose the left or right key.'), 
                                font='helvetica', pos=(0,-0.1), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line3.draw()
        
        line3 = visual.TextStim(self.win, text=('NOTE: You will be required to eat all of the food you have earned'+
                                                ' at the end of the experiment so choose carefully.'), 
                                font='helvetica', pos=(0,-0.4), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line3.draw()
        
        self.press_space()
    
    def run_transfer_test_training(self):
        self.display_transfer_test_training_instructions()
        
        trials = self.get_transfer_test_trials()
        trials = trials[:10]
        choiceText = visual.TextStim(self.win, text=self.choiceText, color="white", font="Arial")
        trialNo = 0
        
        for t in trials:
            trialNo += 1
            correct=0
            
            self.win.callOnFlip(self.rt_clock.reset)
            stimulus = visual.ImageStim(self.win, image=self.imageFiles[self.outcomeMapping[t]], pos=(0,0.5))
            stimulus.draw()
            self.win.flip()
            core.wait(self.stimulusTime)
            
            stimulus.draw()
            choiceText.draw()
            self.win.flip()
            
            key_press = event.waitKeys(keyList=['e','i'], timeStamped=self.rt_clock)
            if key_press[0][0]=="e":
                response = "Left"
                if t=="O2" or t=="O4":
                    correct = 1
            elif key_press[0][0]=="i":
                response = "Right"
                if t=="O1" or t=="O3":
                    correct = 1
            
            self.win.flip()
            core.wait(self.ITI)
            
            if t=="O1" or t=="O2":
                devalued = 0
            else:
                devalued = 1 
                
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                "TransferTestPractice", trialNo, t, response, t, self.outcomeMapping[t], 
                devalued, key_press[0][1], correct))
    
    def display_transfer_test_training_instructions(self):
        line1 = visual.TextStim(self.win, text=('First, you will be given a few practice trials'), 
                                font='helvetica', pos=(0,0.5), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        self.press_space()
    
    def display_transfer_test_final_instructions(self):
        line1 = visual.TextStim(self.win, text=('Now, you will be earning food points.'), 
                                font='helvetica', pos=(0,0.5), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        line3 = visual.TextStim(self.win, text=('REMEMBER: You will be required to eat all of the food you have earned'+
                                                ' at the end of the experiment so choose carefully.'), 
                                font='helvetica', pos=(0,-0.4), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line3.draw()
        
        self.press_space()
    
    def run_experiment_knowledge_tests(self):
        self.run_instrumental_knowledge_test()
        
        self.run_stimulus_knowledge_test()
    
    def run_stimulus_knowledge_test(self):
        trialNo = 0
        options = self.stimuli
        shuffle(options)
        
        option1 = visual.TextStim(self.win, text="1. "+ options[0].upper(), font='helvetica', pos=(-0.6,-0.7), height=0.1)
        option2 = visual.TextStim(self.win, text="2. "+ options[1].upper(), font='helvetica', pos=(-0.2,-0.7), height=0.1)
        option3 = visual.TextStim(self.win, text="3. "+ options[2].upper(), font='helvetica', pos=(0.2,-0.7), height=0.1)
        option4 = visual.TextStim(self.win, text="4. "+ options[3].upper(), font='helvetica', pos=(0.6,-0.7), height=0.1)
        
        outcomes = self.outcomes
        shuffle(outcomes)
        self.display_stimulus_knowledge_instructions()
        
        instruction = visual.TextStim(self.win, text="Which food did this picture represent?", 
                                      font='helvetica', pos=(0,0), height=0.1)
        
        for outcome in outcomes:
            trialNo += 1
            correct=0
            
            stimulus = visual.ImageStim(self.win, image=self.imageFiles[self.outcomeMapping[outcome]], pos=(0,0.5))
            stimulus.draw()
            option1.draw()
            option2.draw()
            option3.draw()
            option4.draw()
            instruction.draw()
            
            self.win.callOnFlip(self.rt_clock.reset)
            self.win.flip()
            key_press = event.waitKeys(keyList=['1','2','3','4'], timeStamped=self.rt_clock)
            
            if options[int(key_press[0][0])-1]==self.outcomeMapping[outcome]:
                correct=1
            
            self.win.flip()
            core.wait(self.ITI)
            
            if outcome=="O1" or outcome=="O2":
                devalued = 0
            else:
                devalued = 1 
                
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, 
                "StimulusTest", trialNo, outcome, key_press[0][0], options[int(key_press[0][0])-1], 
                self.outcomeMapping[outcome], devalued, key_press[0][1], correct))
    
    def display_stimulus_knowledge_instructions(self):
        line1 = visual.TextStim(self.win, text='We would now like to check whether you know which picture represented which food', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        self.press_space()
    
    def get_transfer_test_trials(self):
        trialTypes = self.outcomes*8
        shuffle(trialTypes)
        return trialTypes
    
    def thanksAndGoodbye(self):
        self.display_goodbye()
        
        self.win.close()
        core.quit()
        self.dataFile.close()
        
    def display_goodbye(self):      
        line1 = visual.TextStim(self.win, text='Thanks for taking part in the experiment!', font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.2)
        line1.draw()
        
        self.press_space()

exp = PIT()
exp.runExperiment()
