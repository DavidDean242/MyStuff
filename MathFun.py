"""
History
    Dec 15, 2020    David Dean   Initial creation.
"""

# Dump any object
def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

from tkinter import *
from tkinter import messagebox
import tkinter.font
import RPi.GPIO as GPIO
import random
import pygame
import time
from datetime import datetime
import sys
#import os
import subprocess
print('sys.version = ',sys.version)
print('TclVersion =',TclVersion)

GRN=5
YEL=6
RED=13

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for p in [GRN,YEL,RED]:
    GPIO.setup(p,GPIO.OUT)

PADY=5
PADX=10
x=0
y=0
z=0
tries=0
total=0
bonus=0
COST1=100
COST2=1000
readyMode=True
pygame.mixer.init()

prize1Dict={
    "Mirror video"     :"-hf",
    "Upsidedown video" :"-rot 180",
    "Sketch video"     :"-ifx sketch",
    "Negative video"   :"-ifx negative",
    "Emboss video"     :"-ifx emboss",
    "Hatch video"      :"-ifx hatch",
    "Colourswap video" :"-ifx colourswap",
    "Opaque video"     :"-op 128",
    }
prize1List=[d for d in sorted(prize1Dict)]

prize2Dict={
    "Swinging the Alphabet"  :"bgmdnxtz3Bo",
    "Cats and Cucumbers"     :"_7vML9C3PZk",
    "Chip and Dale"          :"a9vaxG99_UU&t=3187s",
    "Funny Goats"            :"FfsmLgD2ZFM",
    "Down on the Farm"       :"vTfNHSbs3pQ&t=11s",
    "Stop, Look, and Listen" :"nr_Dd2Rpsc0",
    }
prize2List=[d for d in sorted(prize2Dict)]

nameList=[
    'Guest',
    'Annabel',
    'Dad',
    'Daphne',
    'Gigi',
    'Gramps',
    'Lucy',
    'Mom',
    'Nana',
    'Pierce',
    'Rowan',
    'Trey',
    'Uno',
    ]
#dump(nameList)
name=nameList[0]

rewardList=['Disable','Random','applause','explos','glasses','gong','kongas','roll','romans','sparcle','train','top','untie','wallewal']
boobooList=['Disable','Random','beam','cow','drama','falling','horse','kling','ups']
goodList=['Good job','You rock','Way to go','Out of this world','No way','Awesome','Hooray']
badList=['Sorry','Too bad','Oops','Go study','Duh','Yikes','Ouch','Bummer']
wav_dir='/usr/lib/libreoffice/share/gallery/sounds/'

now = datetime.now()
seconds_since_midnight=(now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
random.seed(seconds_since_midnight)

root=Tk()
root.title("Math Fun")
Label(root,text="Let's have some family fun with Arithmetic!",font=('Helvetica',16,'bold')).grid(row=0,column=0,padx=PADX,pady=PADY)

# Message area
message=Label(root,text='Click on the Ready button to get your first problem.',width=50,font=('Helvetica',10,'bold'))
message.grid(row=6,column=0)

# Frame for Drop Down Lists
frameDDL=Frame(root)
frameDDL.grid(row=1,column=0,padx=PADX,pady=PADY)

# DDL for names
Label(frameDDL,text='Name').grid(row=0,column=0,sticky=E,padx=PADX,pady=PADY)
nameVar=StringVar(frameDDL)
nameVar.set(name)
nameMenu=OptionMenu(frameDDL,nameVar,*nameList)
nameMenu.grid(row=0,column=1)
nameMenu.config(width=10)
def change_name(*args):
    global name,total
    if debugVar.get():
        print('name =',nameVar.get())
    if total>0:
        msgBox=messagebox.askquestion('Warning','You will lose your '+str(total)+' points if you change your name.  Continue?',icon='warning')
        if msgBox == 'yes':
            total=0
            message.config(text='Back to zero points for '+nameVar.get()+'.')
        else:
            nameVar.set(name)
            nameMenu.config(state=NORMAL)
    name=nameVar.get()
nameVar.trace('w',change_name)

# DDL for rewards
Label(frameDDL,text='Reward Sound').grid(row=1,column=0,sticky='E',padx=PADX,pady=PADY)
rewardVar=StringVar(frameDDL)
rewardVar.set('Random')
rewardMenu=OptionMenu(frameDDL,rewardVar,*rewardList)
rewardMenu.grid(row=1,column=1)
rewardMenu.config(width=10)

# DDL for booboos
Label(frameDDL,text='Booboo Sound').grid(row=2,column=0,sticky='E',padx=PADX,pady=PADY)
boobooVar=StringVar(frameDDL)
boobooVar.set('Random')
boobooMenu=OptionMenu(frameDDL,boobooVar,*boobooList)
boobooMenu.grid(row=2,column=1)
boobooMenu.config(width=10)

# Frame for radio buttons of operations
frameRadio=Frame(root,borderwidth=1,relief=SUNKEN)
frameRadio.grid(row=2,column=0,padx=PADX,pady=PADY)
Label(frameRadio,text='Choose an operation:').grid(row=0,column=0,padx=PADX,pady=PADY)
operVar=StringVar()
Radiobutton(frameRadio,text="Addition"      ,variable=operVar,value='+').grid(row=1,column=0,sticky=W)
Radiobutton(frameRadio,text="Subtraction"   ,variable=operVar,value='-').grid(row=2,column=0,sticky=W)
Radiobutton(frameRadio,text="Multiplication",variable=operVar,value='*').grid(row=3,column=0,sticky=W)
Radiobutton(frameRadio,text="Division"      ,variable=operVar,value='/').grid(row=4,column=0,sticky=W)

# Frame for checkboxes
frameCheck=Frame(root,borderwidth=1,relief=SUNKEN)
frameCheck.grid(row=3,column=0,padx=PADX,pady=PADY)
Label(frameCheck,text='Options:').grid(row=0,column=0,padx=PADX,pady=PADY,sticky=W)

# Checkbox for negatives 
negsVar=IntVar()
Checkbutton(frameCheck,text="Allow negatives",variable=negsVar).grid(row=1,column=0,sticky=W)

# Checkbox for GPIO lights 
lightsVar=IntVar()
def lightsToggle():
    if debugVar.get():
        print('lightsVar =',lightsVar.get())
    if lightsVar.get():
        for p in [GRN,YEL,RED]:
            GPIO.output(p,GPIO.HIGH)
            time.sleep(.1)
        time.sleep(1)
        for p in [GRN,YEL,RED]:
            GPIO.output(p,GPIO.LOW)
            time.sleep(.1)
Checkbutton(frameCheck,text="Enable lights",variable=lightsVar,command=lightsToggle).grid(row=2,column=0,sticky=W)

# Checkbox for background
dbackVar=IntVar()
def dbackToggle():
    if debugVar.get():
        print('dbackVar =',dbackVar.get())
    if dbackVar.get()==1:
        root.configure(background='black')
    else:
        root.configure(background='lightgray')
Checkbutton(frameCheck,text="Dark background",variable=dbackVar,command=dbackToggle).grid(row=3,column=0,sticky=W)

# Checkbox for debug 
debugVar=IntVar()
def debugToggle():
    print('debugVar =',debugVar.get())
Checkbutton(frameCheck,text="Debug",variable=debugVar,command=debugToggle).grid(row=4,column=0,sticky=W)

# Frame for scale slider
frameScale=Frame(root,borderwidth=1,relief=SUNKEN)
frameScale.grid(row=4,column=0,padx=PADX,pady=PADY)

Label(frameScale,text='Difficulty:').grid(row=0,column=0,sticky=W)
scale=Scale(frameScale,from_=10,to=100,orient=HORIZONTAL,length=400,tickinterval=10,resolution=1)
scale.grid(row=1,column=0,padx=PADX,pady=PADY)

# Frame for equation and answer
frameEntry=Frame(root)
frameEntry.grid(row=5,column=0,padx=PADX,pady=PADY)

problem=Label(frameEntry,width=9)
problem.grid(row=0,column=0,sticky=E)
answer=Entry(frameEntry,width=8)
answer.grid(row=0,column=2,sticky=W)

# Frame for buttons
frameButton=Frame(root)
frameButton.grid(row=7,column=0,padx=PADX,pady=PADY)

# Ready button
def ready():
    global x,y,z,total,tries,bonus,readyMode
    if debugVar.get():
        print('Ready button pressed')
    for p in [GRN,YEL,RED]:
        GPIO.output(p,GPIO.LOW)
    if operVar.get()=='':
        message.config(text='You must select an operation.')
        return None
    readyButton['state']=DISABLED
    submitButton['state']=NORMAL
    readyMode=False
    if negsVar.get()==0:
        x=random.randint(1,scale.get())
        y=random.randint(1,scale.get())
    else:
        x=random.randint(-scale.get(),scale.get())
        y=random.randint(-scale.get(),scale.get())
    if operVar.get()=='+':
        bonus=1*(abs(x)+abs(y))
        z=x+y
    elif operVar.get()=='-':
        bonus=1*(abs(x)+abs(y))
        if not negsVar.get():
            if x<y:
                temp=x
                x=y
                y=temp
        z=x-y
    elif operVar.get()=='*':
        bonus=2*(abs(x)+abs(y))
        z=x*y
    elif operVar.get()=='/':
        bonus=2*(abs(x)+abs(y))
        x=x*y
        z=x/y
    tries=0
    problem.config(text=str(x)+' '+operVar.get()+' '+str(y)+' = ')
    answer.delete(0,END)
readyButton=Button(frameButton,text='Ready',command=ready)
readyButton.grid(row=0,column=0,padx=PADX,pady=PADY)

# Submit button
def submit():
    global x,y,z,total,tries,bonus,readyMode
    if debugVar.get():
        print('Submit button pressed')
        print('nameVar.get() = ',nameVar.get());
        print('scale.get() =',scale.get())
        print(x,operVar.get(),y,'=',answer.get())
    try:
        int(answer.get())
    except:
        message.config(text="That's not a number.")
        return None
    if z==int(answer.get()):
        if rewardVar.get()=='Random':
            wav=rewardList[random.randint(2,len(rewardList)-1)]
        else:
            wav=rewardVar.get()
        if debugVar.get():
            print('wav =',wav)
        try:
            pygame.mixer.music.load(wav_dir+wav+'.wav')
            pygame.mixer.music.play()
        except:
            if debugVar.get():
                print('Load '+str+'.wav file failed.')
        if lightsVar.get():
            GPIO.output(GRN,GPIO.HIGH)
            GPIO.output(YEL,GPIO.LOW)
            GPIO.output(RED,GPIO.LOW)
        readyButton['state']=NORMAL
        submitButton['state']=DISABLED
        readyMode=True
        total=total+int((5-tries)/5.0*bonus)
        message.config(text=goodList[random.randint(0,len(goodList)-1)]+' '+nameVar.get()+'!  You have '+str(total)+' points.')
        if total>COST1:
            prize1Label  ['state']=NORMAL
            prize1Menu   ['state']=NORMAL
            prize1Button ['state']=NORMAL
            if total>COST2:
                prize2Label  ['state']=NORMAL
                prize2Menu   ['state']=NORMAL
                prize2Button ['state']=NORMAL
    else:
        if boobooVar.get()=='Random':
            wav=boobooList[random.randint(2,len(boobooList)-1)]
        else:
            wav=boobooVar.get()
        if debugVar.get():
            print('wav =',wav)
        try:
            pygame.mixer.music.load(wav_dir+wav+'.wav')
            pygame.mixer.music.play()
        except:
            if debugVar.get():
                print('Load '+str+'.wav file failed.')
        tries=tries+1
        if tries==5:
            readyButton['state']=NORMAL
            submitButton['state']=DISABLED
            readyMode=True
            message.config(text=badList[random.randint(0,len(badList)-1)]+' '+nameVar.get()+'!  No more tries.')
            if lightsVar.get():
                GPIO.output(GRN,GPIO.LOW)
                GPIO.output(YEL,GPIO.LOW)
                GPIO.output(RED,GPIO.HIGH)
        else:
            message.config(text=badList[random.randint(0,len(badList)-1)]+' '+nameVar.get()+'!  Try again for '+str(100-tries*20)+'% credit.')
            if lightsVar.get():
                GPIO.output(GRN,GPIO.LOW)
                GPIO.output(YEL,GPIO.HIGH)
                GPIO.output(RED,GPIO.LOW)

submitButton=Button(frameButton,text='Submit',command=submit)
submitButton.grid(row=0,column=1,padx=PADX,pady=PADY)
submitButton['state']=DISABLED

def enterKey(event=None):
    if readyMode:
        ready()
    else:
        submit()
root.bind('<Return>',enterKey)

# Frame for prizes
framePrizes=Frame(root)
framePrizes.grid(row=8,column=0,padx=PADX,pady=PADY)

prize1Label=Label(framePrizes,text='Prizes')
prize1Label.grid(row=0,column=0,sticky=E,padx=PADX,pady=PADY)
prize1Label['state']=DISABLED
prize1Var=StringVar(framePrizes)
prize1Var.set(prize1List[0])
prize1Menu=OptionMenu(framePrizes,prize1Var,*prize1List)
prize1Menu.grid(row=0,column=1)
prize1Menu.config(width=20)
prize1Menu['state']=DISABLED

prize2Label=Label(framePrizes,text='Big Prizes')
prize2Label.grid(row=1,column=0,sticky=E,padx=PADX,pady=PADY)
prize2Label['state']=DISABLED
prize2Var=StringVar(framePrizes)
prize2Var.set(prize2List[0])
prize2Menu=OptionMenu(framePrizes,prize2Var,*prize2List)
prize2Menu.grid(row=1,column=1)
prize2Menu.config(width=20)
prize2Menu['state']=DISABLED

# Button for prizes
def redeem1():
    if debugVar.get():
        print('Prize1 =',prize1Var.get())
    global total
    try:
        procInfo=subprocess.run(['raspivid','-p 100,50,800,800 -t 10000 '+prize1Dict[prize1Var.get()]+' &'])
    except:
        if debugVar.get():
            print('subprocess.run failed')    
    finally:
        if debugVar.get():
            print('procInfo =',procInfo)    
    total=total-COST1
    if total<COST1:
        prize1Label  ['state']=DISABLED
        prize1Menu   ['state']=DISABLED
        prize1Button ['state']=DISABLED
    if total<COST2:
        prize2Label  ['state']=DISABLED
        prize2Menu   ['state']=DISABLED
        prize2Button ['state']=DISABLED
    message.config(text='You now have '+str(total)+' points.')
prize1Button=Button(framePrizes,text='Redeem',command=redeem1)
prize1Button.grid(row=0,column=2,padx=PADX,pady=PADY)
prize1Button['state']=DISABLED

def redeem2():
    if debugVar.get():
        print('Prize2 =',prize2Var.get())
    global total
    try:
        procInfo=subprocess.run(['chromium-browser','https://www.youtube.com/watch?v='+prize2Dict[prize2Var.get()]+' &'])
    except:
        if debugVar.get():
            print('subprocess.run failed')    
    finally:
        if debugVar.get():
            print('procInfo =',procInfo)    
    total=total-COST2
    if total<COST1:
        prize1Label  ['state']=DISABLED
        prize1Menu   ['state']=DISABLED
        prize1Button ['state']=DISABLED
    if total<COST2:
        prize2Label  ['state']=DISABLED
        prize2Menu   ['state']=DISABLED
        prize2Button ['state']=DISABLED
    message.config(text='You now have '+str(total)+' points.')
prize2Button=Button(framePrizes,text='Redeem',command=redeem2)
prize2Button.grid(row=1,column=2,padx=PADX,pady=PADY)
prize2Button['state']=DISABLED

# Close button
def close():
    if debugVar.get():
        print('Exit button pressed')
    for p in [GRN,YEL,RED]:
        GPIO.output(p,GPIO.LOW)
    GPIO.cleanup()
    root.destroy()
exitButton=Button(frameButton,text='Exit',command=close)
exitButton.grid(row=0,column=3,padx=PADX,pady=PADY)

# About button
def about():
    if debugVar.get():
        print('About button pressed')
    msg=[
        'Solve math problems to win prizes.',
        '',
        'Redeem '+str(COST1)+' points for a prize or '+str(COST2)+' points for a BIG prize!',
        '',
        __file__+' Version 1.1',
        ]
    messagebox.showinfo('Info',"\n".join(msg))
aboutButton=Button(frameButton,text='About',command=about)
aboutButton.grid(row=0,column=4,padx=PADX,pady=PADY)
    
# Main loop
root.mainloop()
