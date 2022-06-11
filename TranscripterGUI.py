from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from threading import Event
from threading import Thread
from kivy.core.window import Window
import randomname as random
import time

import recordAudio
import main


class InfoWindow(Screen):
    tempo = ObjectProperty(None)
    toleranceTempo = ObjectProperty(None)
    filename = ObjectProperty(None)


    def submitBtn(self):
        if int(self.tempo.text) > 30 and int(self.tempo.text) < 200:
            if int(self.toleranceTempo.text) > 0 and int(self.toleranceTempo.text) < 50:
                if self.filename.text != "":
                    # Initiate the current of RecordWindow to be the filename
                    RecordWindow.current = self.filename.text
                    print(RecordWindow.current)
                    # Save the information entered
                    self.saveSelf()
                    # Reset information in Info Window
                    self.reset()
                    sm.current = "record"
                else:
                    return invalidFilename()
            else:
                return invalidTolerance()
        else:
            return invalidTempo()

    def reset(self):
        self.tempo.text = '60'
        self.toleranceTempo.text = '25'
        self.filename.text = 'Essai'

    def saveSelf(self):
        with open('C:/Users/truiz/OneDrive/Desktop/ELE3000_InfoEnregistrement/' + self.filename.text + '.txt', 'w') as f:
            f.write(self.filename.text)
            f.write('\n')
            f.write(self.tempo.text)
            f.write('\n')
            f.write(self.toleranceTempo.text)


class RecordWindow(Screen):
    fileName = ObjectProperty(None)
    tempoInfo = ObjectProperty(None)
    toleranceInfo = ObjectProperty(None)
    record = ObjectProperty(None)
    threadRecord = ObjectProperty(None)
    threadGenerate = ObjectProperty(None)
    stopThread = ObjectProperty(None)
    current = ""


    def on_enter(self):
        self.loadSelf()


    def loadSelf(self):
        # Use current of RecordWindow to open the file where the info is
        with open('C:/Users/truiz/OneDrive/Desktop/ELE3000_InfoEnregistrement/' + self.current + '.txt', 'r') as f:
            lines = f.readlines()

        self.fileName.text = "File name is " + lines[0].rstrip() + ".pdf"
        self.tempoInfo.text = "Tempo is " + lines[1].rstrip() + " bpm"
        self.toleranceInfo.text = "Tolerance is " + lines[2].rstrip() + "%"

        # Enable or disable buttons
        self.startRecording.disabled = False
        self.generate.disabled = True

        # Create thread and create a threading event
        stopThread = Event()  # Set flag is false by default
        # Creation of thread for recording audio - will need a stopThread event
        nameThreadRecord = random.get_name()
        nameThreadRecord = Thread(target=recordAudio.startRecording, args=(self.current, stopThread))

        # Creation of thread for generating score - will not need a stopThread event
        nameThreadGenerate = random.get_name()
        nameThreadGenerate = Thread(target=main.setup, args=(self.current,))

        # Assign the objects to their objects in the window objects
        self.threadRecord = nameThreadRecord
        self.threadGenerate = nameThreadGenerate
        self.stopThread = stopThread


    def startRecord(self):
        # If we want to start a recording
        if(self.startRecording.text == 'Start recording'):
            # Update buttons
            self.startRecording.text = 'Stop recording'

            # Clear the stopThread flag to make sure recording will ensue
            self.stopThread.clear()
            # Start the thread (call function recordAudio.startRecording)
            self.threadRecord.start()

        # If we want to stop a current recording
        elif(self.startRecording.text == 'Stop recording'):
            # Update buttons
            self.startRecording.text = 'Start recording'
            self.startRecording.disabled = True
            self.generate.disabled = False

            # Set the flag to true and make the recording stop
            self.stopThread.set()


    def generatePartition(self):
        # Call the setup function in main.py with the name of the file to be generated
        main.setup(self.current)

        self.startRecording.disabled = False
        #self.threadGenerate.join()
        # Reset the scree to the information window to start a new score
        sm.current = "info"


class WindowManager(ScreenManager):
    pass


def invalidTempo():
    pop = Popup(title='Invalid Tempo',
                  content=Label(text='Invalid tempo. Please insert tempo between 30 and 200 bpm.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidTolerance():
    pop = Popup(title='Invalid Tolerance',
                content=Label(text='Invalid Tolerance. Please insert tolerance between 1 and 99%.'),
                size_hint=(None, None), size=(500, 400))
    pop.open()


def invalidFilename():
    pop = Popup(title='Invalid Filename',
                content=Label(text='Invalid filename.'),
                size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(400, 400))

    pop.open()


kv = Builder.load_file("TranscripterGUI.kv")


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    sm = WindowManager()
    screens = [InfoWindow(name="info"), RecordWindow(name="record")]
    for screen in screens:
        sm.add_widget(screen)

    sm.current = "info"

    #Window.fullscreen = 'auto'

    MyMainApp().run()