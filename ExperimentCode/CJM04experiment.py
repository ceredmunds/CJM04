#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CJM02 - PIT experiment, adapted from Seabrooke et al. (2017)
# CERE - 2-10-2017 - Created
from psychopy import visual
import os
from itertools import permutations
from numpy.random import choice
from random import shuffle

from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import sound, event, core, gui, data

class PIT:
    def __init__(self):
        self.expName = "CJM04"
        self.dataPath = "Data"
        
        self.rt_clock = core.Clock()
        self.ITI = 0.5
        self.feedbackTime = 3
        self.waitTime = 6
        self.stimulusTime = 3
        self.extinctionTime = 10
        self.transferTime = 10
        
        self.pptNo = None
        self.pptGender = None
        self.pptAge = None
        self.pptLH = None
        self.experimenter = "CERE"
        self.date = data.getDateStr()
        
        self.outcomes = ["O1","O2","O3","O4"]
        self.stimuli = ["crisps", "popcorn", "nachos", "cashews"]
        self.cues = ["H","K", "S", "W"]
        self.cueFiles = {"H":"Images/H.png", "K":"Images/K.png", "S":"Images/S.png", "W":"Images/W.png"}
        self.choiceText = u'\u2190' + ' or ' + u'\u2192'
    
    def runExperiment(self):
        self.start_experiment()
        self.run_liking_ratings()
        
        self.run_continuous_instrumental_training()
        self.run_pavlovian_training()
        
        self.run_outcome_devaluation()
        self.run_liking_ratings(time="second")
        
        self.run_continuous_transfer_test()
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
        self.counterbalance = self.counterbalancing[0]+self.counterbalancing[1]+self.counterbalancing[2]+self.counterbalancing[3]
    
    def open_data_file(self):
        self.get_file_name()
        self.dataFile = open(self.fileName, 'w') 
        
        self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                "DAU","ParticipantNo","Date","Age","Gender","Experimenter", "Counterbalancing",
                "ExperimentPhase","Trial","SubTrial","TrialType","Outcome","Food","Cue",
                "InstrumentalResponse","Devalued","Response","RT","LeftCount",
                "RightCount","Correct"))
    
    def get_file_name(self):
        if not os.path.isdir(self.dataPath):
            os.makedirs(self.dataPath)  # if this fails (e.g. permissions) we will get error
        
        self.fileName = self.dataPath + "/" + "%s_Ppt_%s.csv" %(self.expName, self.pptNo)
    
    def open_window(self):
        self.win = visual.Window(size=[1920, 1080], color="black",
                    fullscr=True, allowGUI=False, checkTiming=True)
    
    def get_counterbalancing(self):
        reorderedFoods = [self.stimuli[i-1] for i in self.counterbalancing]
        self.outcomeMapping = dict(zip(self.outcomes, reorderedFoods))
        
        shuffle(self.cues)
        self.outcomeCueMapping = dict(zip(self.outcomes, self.cues))
        
        if self$pptNo%2:
            devalued = [0,1,0,1]
        else:
            devalued = [1,0,1,0]
        self.devalued = dict(zip(self.outcomes, devalued))
        self.instrumentalResponse = dict(zip(self.outcomes, ['Right','Left','Right','Left']
    
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
            
            self.win.flip()
            core.wait(self.ITI)
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter,self.counterbalance,
                ExpPhase,trialNo,"NA","Liking",outcome,self.outcomeMapping[outcome],self.outcomeCueMapping[outcome],
                self.instrumentalResponse[outcome],self.devalued[outcome],ratingScale.getRating(),ratingScale.getRT(),"NA",
                "NA","NA"))
    
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
        if self.pptNo==99:
            n = 4
        else:
            n = 24
        trialTypes = ["O1O2","O3O4"]*n
        shuffle(trialTypes)
        return trialTypes
    
    def run_continuous_instrumental_training(self):
        choiceText = visual.TextStim(self.win, text=self.choiceText, color="white", font="Arial", height=0.2)
        trials = self.get_instrumental_training_trials()
        trialNo = 0
        
        self.display_continuous_instrumental_training_instructions()
        
        for t in trials:
            trialNo += 1
            keys = []
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
            
            while True:
                key_press = event.waitKeys(keyList=['q','p'])
                self.play_button_sound()
                
                keys += key_press
                
                if choice([0,1], p=[0.9,0.1]):
                    rt = self.rt_clock.getTime()
                    if key_press[0][0]=='q':
                        cue = leftCue
                        food = leftFood
                        response = "Left"
                    elif key_press[0][0]=='p':
                        cue = rightCue
                        food = rightFood
                        response = "Right"
                    event.clearEvents(eventType='keyboard')
                    
                    text = "You win one " + food.upper() + " point"
                    feedback = visual.TextStim(self.win, text=text, pos=(0,0), height=0.09)
                    feedback.draw()
                    self.win.flip()
                    core.wait(self.feedbackTime)
                    
                    self.win.flip()
                    core.wait(self.ITI)
                    
                    self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                    self.expName,self.pptNo,self.date,self.pptAge,self.pptGender,self.experimenter,self.counterbalance,
                    "InstrumentalTraining",trialNo,"NA",t,cue,food,self.outcomeCueMapping[cue],
                    response,self.devalued[t],response,rt,keys.count("q"),
                    keys.count("p"),"NA"))
                    
                    break
        core.wait(2)
        self.run_instrumental_knowledge_test(time="first")
    
    def display_continuous_instrumental_training_instructions(self):
        line1 = visual.TextStim(self.win, text='In the following task, your aim is to learn which key, the left ("Q") or the right ("P") key, results in points for which food.', 
                                font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        line2 = visual.TextStim(self.win, text='Please only use the first finger of your dominant hand to respond.', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1)
        line2.draw()
        
        line3 = visual.TextStim(self.win, text='You may have to press each key multiple times for anything to be displayed.', 
                                font='helvetica', pos=(0,-0.35), wrapWidth=1.5, height=0.1)
        line3.draw()
        
        self.press_space()
    
    def play_button_sound(self):
        click = sound.Sound('Sounds/click.wav')
        click.setVolume(0.5)
        click.play()
        
        boing = sound.Sound('Sounds/boing.wav')
        boing.setVolume(0.5)
        boing.play()
    
    def run_instrumental_knowledge_test(self, time="first"):
        outcomes = self.outcomes
        shuffle(outcomes)
        trialNo = 0
        if time=="first":
            ExpPhase = "FirstInstrumentalTest"
        else:
            ExpPhase = "SecondInstrumentalTest"
        
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
            
            key_press = event.waitKeys(keyList=['q','p'], timeStamped=self.rt_clock)
            if key_press[0][0]=="q":
                response = "Left"
                if outcome=="O2" or outcome=="O4":
                    correct = 1
            elif key_press[0][0]=="p":
                response = "Right"
                if outcome=="O1" or outcome=="O3":
                    correct = 1
            
            self.win.flip()
            core.wait(self.ITI)
            
                
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName,self.pptNo,self.date,self.pptAge,self.pptGender,self.experimenter,self.counterbalance,
                ExpPhase,trialNo,"NA","Choice",outcome,self.outcomeMapping[outcome],self.outcomeCueMapping[outcome],
                self.instrumentalResponse[outcome],self.devalued[outcome],response,key_press[0][1],"NA",
                "NA",correct))
            
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
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName,self.pptNo,self.date,self.pptAge,self.pptGender,self.experimenter,self.counterbalance,
                ExpPhase,trialNo,"NA","Confidence",outcome,self.outcomeMapping[outcome],self.outcomeCueMapping[outcome],
                self.instrumentalResponse[outcome],self.devalued[outcome],ratingScale.getRating(),ratingScale.getRT(),"NA",
                "NA","NA"))
    
    def display_instrumental_knowledge_instructions(self):
        line1 = visual.TextStim(self.win, text='We would now like to test whether you know which key earned which foods', 
                                font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        self.press_space()
    
    def get_pavlovian_training_trials(self):
        if self.pptNo==99:
            n = 2
        else:
            n = 16
        trialTypes = self.outcomes*n
        shuffle(trialTypes)
        return trialTypes
    
    def run_pavlovian_training(self):
        trials = self.get_pavlovian_training_trials()
        trialNo = 0
        
        self.display_pavlovian_training_instructions()
        self.mouse = event.Mouse(visible=True, newPos=False, win=self.win)
        
        predicts = visual.TextStim(self.win, text='predicts', 
                                font='helvetica', pos=(0,0.2), wrapWidth=1.5, height=0.1, alignHoriz='center')
        
        for t in trials:
            trialNo += 1
            
            self.draw_single_cue(stimulus=self.outcomeCueMapping[t])
            predicts.draw()
            self.win.flip()
            core.wait(0.5)
            
            self.draw_single_cue(stimulus=self.outcomeCueMapping[t])
            predicts.draw()
            response, rt, position = self.get_response()
            
            correct = 0
            if response==self.outcomeMapping[t]:
                correct = 1
            
            self.draw_prediction_feedback(outcome=t)
            
            self.win.flip()
            core.wait(self.ITI)
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName,self.pptNo,self.date,self.pptAge,self.pptGender,self.experimenter,self.counterbalance,
                "PavlovianTraining",trialNo,"NA",position,t,self.outcomeMapping[t],self.outcomeCueMapping[t],
                self.instrumentalResponse[t],self.devalued[t],response,rt,"NA",
                "NA",correct))
        
        self.mouse = event.Mouse(visible=False, newPos=False, win=self.win)
        self.run_stimulus_knowledge_test(time="first")
    
    def display_pavlovian_training_instructions(self):
        line1 = visual.TextStim(self.win, text='In the next section, your task is to predict which letter results in point for which food.', 
                                font='helvetica', pos=(0,0.35), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        line2 = visual.TextStim(self.win, text='Please use the mouse to respond.', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1)
        line2.draw()
        
        self.press_space()
    
    def draw_single_cue(self, stimulus, color="white", shift=0):
        if color=="white":
            stimulus = visual.ImageStim(self.win, image=self.cueFiles[stimulus], pos=(0+shift,0.6))
        elif color=="black":
            stimulus = visual.ImageStim(self.win, image=self.cueFilesBlack[stimulus], pos=(0+shift,0.6))
        stimulus.draw()
    
    def get_response(self):
        responses = self.get_response_counterbalancing()
        
        rect1 = visual.Rect(self.win, height=0.15, width=0.3, pos=(0, 0), lineColor='white')
        rect1.draw()
        opt1 = visual.TextStim(self.win, text=responses[0], pos=(0, 0))
        opt1.draw()
        
        rect2 = visual.Rect(self.win, height=0.15, width=0.3, pos=(0, -0.2), lineColor='white')
        rect2.draw()
        opt2 = visual.TextStim(self.win, text=responses[1], pos=(0, -0.2))
        opt2.draw()
        
        rect3 = visual.Rect(self.win, height=0.15, width=0.3, pos=(0, -0.4), lineColor='white')
        rect3.draw()
        opt3 = visual.TextStim(self.win, text=responses[2], pos=(0, -0.4))
        opt3.draw()
        
        rect4 = visual.Rect(self.win, height=0.15, width=0.3, pos=(0, -0.6), lineColor='white')
        rect4.draw()
        opt4 = visual.TextStim(self.win, text=responses[3], pos=(0, -0.6))
        opt4.draw()
        
        self.win.flip()
        
        waiting=True
        self.rt_clock.reset()
        while waiting:
            if self.mouse.isPressedIn(rect1, buttons=[0]):
                rt = self.rt_clock.getTime()
                response = responses[0]
                position = "top"
                waiting = False
            elif self.mouse.isPressedIn(rect2, buttons=[0]):
                rt = self.rt_clock.getTime()
                response = responses[1]
                position = "topmid"
                waiting = False
            elif self.mouse.isPressedIn(rect3, buttons=[0]):
                rt = self.rt_clock.getTime()
                response = responses[2]
                position = "botmid"
                waiting = False
            elif self.mouse.isPressedIn(rect4, buttons=[0]):
                rt = self.rt_clock.getTime()
                response = responses[3]
                position = "bot"
                waiting = False
        
        event.clearEvents()
        return (response, rt, position)
    
    def get_response_counterbalancing(self):
        responses = self.stimuli
        shuffle(responses)
        return responses
    
    def draw_prediction_feedback(self, outcome):
        self.draw_single_cue(stimulus=self.outcomeCueMapping[outcome])
        
        text = "earns one " + self.outcomeMapping[outcome].upper() + " point"
        feedback = visual.TextStim(self.win, text=text, pos=(0,0), height=0.09)
        feedback.draw()
        self.win.flip()
        core.wait(self.feedbackTime)
        
    def run_stimulus_knowledge_test(self, time="first"):
        trialNo = 0
        if time=="first":
            ExpPhase = "FirstPavlovianTest"
        else:
            ExpPhase = "SecondPavlovianTest"
        
        options = self.stimuli
        shuffle(options)
        
        option1 = visual.TextStim(self.win, text="1. "+ options[0].upper(), font='helvetica', pos=(-0.6,-0.7), height=0.1)
        option2 = visual.TextStim(self.win, text="2. "+ options[1].upper(), font='helvetica', pos=(-0.2,-0.7), height=0.1)
        option3 = visual.TextStim(self.win, text="3. "+ options[2].upper(), font='helvetica', pos=(0.2,-0.7), height=0.1)
        option4 = visual.TextStim(self.win, text="4. "+ options[3].upper(), font='helvetica', pos=(0.6,-0.7), height=0.1)
        
        outcomes = self.outcomes
        shuffle(outcomes)
        self.display_stimulus_knowledge_instructions()
        
        instruction = visual.TextStim(self.win, text="Which food did this stimulus represent?", 
                                      font='helvetica', pos=(0,0), height=0.1)
        
        for outcome in outcomes:
            trialNo += 1
            correct=0
            
            stimulus = visual.ImageStim(self.win, image=self.cueFiles[self.outcomeCueMapping[outcome]], pos=(0,0.5))
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
            
            self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName,self.pptNo,self.date,self.pptAge,self.pptGender,self.experimenter,self.counterbalance,
                ExpPhase,trialNo,"NA",outcome,outcome,self.outcomeMapping[outcome],self.outcomeCueMapping[outcome],
                self.instrumentalResponse[outcome],self.devalued[outcome],options[int(key_press[0][0])-1],key_press[0][1],"NA",
                "NA",correct))
            
    def display_stimulus_knowledge_instructions(self):
        line1 = visual.TextStim(self.win, text='We would now like to check whether you know which picture represented which food', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1, alignHoriz='center')
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
        key_press = event.waitKeys(keyList=['c'])
    
    def run_continuous_transfer_test(self):
        self.display_transfer_test_instructions()
        
        trials = self.get_transfer_test_trials()
        choiceText = visual.TextStim(self.win, text=self.choiceText, color="white", font="Arial")
        trialNo = 0
        
        self.display_transfer_test_final_instructions()
        
        for t in trials:
            trialNo += 1
            keys = []
            
            self.win.callOnFlip(self.rt_clock.reset)
            choiceText.draw()
            self.win.flip()
            
            for subt in range(2):
                while self.rt_clock.getTime() < subt*5 + 5:
                    key_press = event.getKeys(keyList=['q','p'])
                    if key_press:
                        self.play_button_sound()
                        keys += key_press
                        event.clearEvents(eventType='keyboard')
                
                self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, self.counterbalance,
                "TransferTest",trialNo,subt+1,"Extinction",t,self.outcomeMapping[t],self.outcomeCueMapping[t],
                self.instrumentalResponse[t],self.devalued[t],"NA","NA",keys.count('q'),
                keys.count('p'),"NA"))
            
            self.win.callOnFlip(self.rt_clock.reset)
            stimulus = visual.ImageStim(self.win, image=self.cueFiles[self.outcomeCueMapping[t]], pos=(0,0.5))
            stimulus.draw()
            choiceText.draw()
            self.win.flip()
            
            for subt in range(2):
                while self.rt_clock.getTime() < subt*5 + 5:
                    key_press = event.getKeys(keyList=['q','p'])
                    if key_press:
                        self.play_button_sound()
                        keys += key_press
                        event.clearEvents(eventType='keyboard')
                

                self.dataFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                self.expName, self.pptNo, self.date, self.pptAge, self.pptGender, self.experimenter, self.counterbalance,
                "TransferTest",trialNo,subt+1,"Stimulus",t,self.outcomeMapping[t],self.outcomeCueMapping[t],
                self.instrumentalResponse[t],self.devalued[t],"NA","NA",keys.count('q'),
                keys.count('p'),"NA"))

    def display_transfer_test_instructions(self):
        line1 = visual.TextStim(self.win, text=('In this part of the task, you can earn the four foods by pressing'+
                                                ' the left ("Q") or right ("P") key in the same way as before'), 
                                font='helvetica', pos=(0,0.5), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line1.draw()
        
        line2 = visual.TextStim(self.win, text=('You will only be told how much of each food'+
                                                ' you have earned at the end of the experiment.'), 
                                font='helvetica', pos=(0,0.2), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line2.draw()
        
        line3 = visual.TextStim(self.win, text=('Also, sometimes the letter stimuli of the foods will be presented'), 
                                font='helvetica', pos=(0,-0.1), wrapWidth=1.5, height=0.1, alignHoriz='center')
        line3.draw()
        
        
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
        self.run_instrumental_knowledge_test(time="second")
        
        self.run_stimulus_knowledge_test(time="second")
    
    def get_transfer_test_trials(self):
        if self.pptNo==99:
            n = 1
        else:
            n = 8
            
        trialTypes = self.outcomes*n
        shuffle(trialTypes)
        return trialTypes
    
    def thanksAndGoodbye(self):
        self.display_goodbye()
        
        self.win.close()
        core.quit()
        self.dataFile.close()
        
    def display_goodbye(self):      
        line1 = visual.TextStim(self.win, text='Thanks for taking part in the experiment!', 
                                font='helvetica', pos=(0,0), wrapWidth=1.5, height=0.1)
        line1.draw()
        
        self.press_space()

exp = PIT()
exp.runExperiment()
