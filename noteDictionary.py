import numpy as np
import os
import subprocess
import time

##########################################
# Dictionnaries

# Dictionary containing every playable note on a piano and its representation in LilyPond
# Lowest note on violin is G (196Hz)
frequencyDict = {
    27.5: "A2",
    29.1353: "B2",
    30.8677: "H2",
    32.7032: "C1",
    34.6479: "Cis1",
    36.7081: "D1",
    38.8909: "Dis1",
    41.2035: "E1",

    195.998: "g",           # Sol
    207.652: "aes",         # Lab
    220: "a",               # La
    223.082: "bes",         # Sib
    246.942: "b",           # Si
    261.626: "c'",          # Do
    277.183: "cis'",        # Do#
    293.665: "d'",          # Ré
    311.127: "ees'",        # Mib
    329.628: "e'",          # Mi
    349.228: "f'",          # Fa
    369.994: "fis'",        # Fa#
    391.995: "g'",          # Sol
    415.305: "gis'",        # Sol#
    440: "a'",              # La
    466.164: "bes'",        # Sib
    493.883: "b'",          # Si
    523.251: "c''",         # Do
    554.365: "cis''",       # Do#
    587.33: "d''",          # Ré
    622.254: "dis''",       # Ré#
    659.255: "e''",         # Mi
    698.456: "f''",         # Fa
    739.989: "fis''",       # Fa#
    783.991: "g''",         # Sol
    830.609: "gis''",       # Sol#
    880: "a''",             # La
    932.328: "ais''",       # La#
    987.767: "b''",         # Si

    1046.5: "c''",          # Do
    1108.73: "cis'''",
    1174.66: "d'''",
    1244.51: "dis'''",
    1318.51: "e'''",
    1396.91: "f'''",
    1479.98: "fis'''",
    1567.98: "g'''",
    1661.22: "gis'''",
    1760: "a'''",
    1864.66: "b'''",
    1975.53: "bis'''",
    2093: "c''''"
}

# Dictionary containing all of the possible length of notes and their representation in LilyPond
lengthNoteDict = {
    0: "16", # counter = 0 means that a double croche has been played
    0.5: "8", #counter = 0.5 means that a croche has been played
    1: "4", #counter = 1 means that a noire has been played
    1.5: "4.", # noire pointée
    2: "2", # blanche
    2.5: "2.", # blanche pointée
    3: "2.", # blanche pointée
    3.5: "1", #ronde
    4: "1", #ronde
    4.5: "1."
}


###############################################################################
# Code section

def defineLength(listFrequencyLength, tempo, toleranceTempo):
    notePerSecond = 60 / tempo # This is the length of une noire
    toleranceTempo = (toleranceTempo / 100) * notePerSecond # Interval of tolerance for every length
    noteArray = np.empty(len(listFrequencyLength[1]), dtype="object")

    for i in range(len(listFrequencyLength[1])):
        counter = 0
        for j in range(10): # 10 length options
            if (notePerSecond * counter) - toleranceTempo < listFrequencyLength[1][i] < (notePerSecond * counter) + toleranceTempo:
                noteArray[i] = lengthNoteDict[counter]
                break
            elif(counter < 4.5):
                counter = counter+0.5
            else:
                noteArray[i] = lengthNoteDict[0];
    return noteArray


def toText(listFrequencyLength, tempo, toleranceTempo, filename):
    # Find the reprensetation of every length of every frequency played
    noteArray = defineLength(listFrequencyLength, tempo, toleranceTempo)
    print(noteArray)

    print(listFrequencyLength)

    with open(filename, 'w') as f:
        # Format .txt file to correspond to regular notation of Lilypond
        # Insert version
        f.write('\\version "2.22.2"  % necessary for upgrading to future LilyPond versions.')
        f.write('\n')

        # Determine header of file
        f.write(r'\header{')
        f.write('\n')
        f.write('title = "Votre partition"}')
        f.write('\n')
        f.write('{ ')
        f.write(r'\tempo 4 = ' + str(tempo))
        f.write(r'\time 4/4')
        f.write('\n')
        f.write(r'\key g \major')
        f.write('\n')

        # For each frequency noted, write it in the .txt file
        # Each note has a certain length accordingly to the output array passed
            # If the passed tempo is 60bpm, then we have 1 note / second. With a certain tolerance, we can evaluate that
            # if a note is a certain length, it is equivalent to a certain value
        for i in range(len(listFrequencyLength[0])):
            # print(noteArray[i])
            if(listFrequencyLength[0][i] > 194 and listFrequencyLength[0][i] < 1046.5):
                print(frequencyDict[np.around(listFrequencyLength[0][i], decimals=3)])
                f.write(frequencyDict[np.around(listFrequencyLength[0][i], decimals=3)])
                f.write(noteArray[i])
                f.write(" ")
        f.write('}')
        f.close()

    # Execute the .ly file to produce the partition on .pdf file
    try:
        os.startfile(filename)
        time.sleep(3)

        # Open the pdf on screen
        filenameUpdate = filename
        filenameUpdate = filenameUpdate.replace('.ly', '.pdf')
        time.sleep(1)
        subprocess.Popen([filenameUpdate], shell=True)
    except:
        print('Trying to open file again...')
        subprocess.Popen([filenameUpdate], shell=True)


def main():
    print("yes")


if __name__ == '__main__':
    main()