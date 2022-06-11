import numpy as np
import matplotlib.pyplot as plt
import librosa as lib
import librosa.display
import sys
np.set_printoptions(precision=16, threshold=sys.maxsize, suppress=True)
from pydub import AudioSegment
import noteDictionary
import warnings
warnings.filterwarnings('ignore')


# Load a .wav file into a numpy array using librosa.load(filename)
def loadFile(sampleRate, filename):
    # Numpy array y contains floating points representing the signal sampled at sampling rate (sr)
    y, sampleRate = lib.load(filename) # Default sr is 22.050kHz - can be higher if needed

    # Visualize data that was loaded
    """""
    librosa.display.waveshow(y, sr=sampleRate)
    plt.tight_layout()
    #plt.show()
    """

    return y


# Name of function : stftEvaluate
# Input :
    # sig : Fully loaded .wav signal
    # sr : Sample rate at which the .wav signal was loaded
# Returns :
    # Returns a numpy array containing the frequencies and length of each note. The numpy array is ordered to have one
    # frequency and its associated time right after
def stftEvaluate(sig, sr, filename):
    # Evaluate short-time fourier transform (stft) for all the signal
    stft = lib.stft(sig, n_fft=2048)

    # Get real values of each frequency bin (only magnitude of frequencies)
    real_stft = np.abs(stft)

    o_env = librosa.onset.onset_strength(y=sig, sr=sr, max_size=1)          # Compute onset envelopes
    times = librosa.times_like(o_env, sr=sr)                                # Time values to provide reference point for onset frames
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)  # Onset detection using the enveloppes - returns frames to be put together with time values
    onsetFramesFinal = []
    print(onset_frames)

    for i in range(1, len(onset_frames)):
        # If the time difference between 2 onset_frames is too small
        # This maximal time interval value is set arbitrarily to 0.1 seconds
        if times[onset_frames[i]] - times[onset_frames[i - 1]] < 0.1:
            # Check for which onset_frame has the highest envelope
            # If the current onset has a higher envelope than previous onset - Set the frame of previous onset
            #   to frame of current onset to make them correspond
            # If the current onset has a lower envelope than previous onset - Set the frame of current onset
            #   to frame of previous onset to make them correspond
            if o_env[onset_frames[i]] >= o_env[onset_frames[i - 1]]:
                # If the actual onset has a higher amplitude than the previous one, we have to replace all possible
                #   previous onsets that could be the same note
                for j in range(0, len(onset_frames)):
                    if(onset_frames[i-1] == onset_frames[j]):
                        onset_frames[j] = onset_frames[i]
                # Replace closest previous onset
                onset_frames[i - 1] = onset_frames[i]
            else:
                onset_frames[i] = onset_frames[i - 1]

    for i in range(len(onset_frames)):
        if(o_env[onset_frames[i]] > 2):
            if(i == 0):
                onsetFramesFinal.append(onset_frames[i]) # First onset is always in the array
            else:
                if(onset_frames[i] != onset_frames[i-1]):
                    onsetFramesFinal.append(onset_frames[i]) # Insert onset in array if it is not the same as previously detected

    print(onset_frames)
    print(onsetFramesFinal)

    """""
    #Plot spectrogram of signal and its onset detected
    fig, ax = plt.subplots(nrows=2, sharex=True)
    fig.set_size_inches(10.5, 10.5)
    librosa.display.specshow(librosa.amplitude_to_db(real_stft, ref=np.max), x_axis='time', y_axis='log', ax=ax[0])
    ax[0].set(title='Spectrogramme de puissance')
    ax[1].set_xlabel('Temps (s)')
    ax[1].plot(times, o_env, label='Différence de puissance')
    ax[1].vlines(times[onsetFramesFinal], 0, o_env.max(), color='r', alpha=0.9, linestyle='--', label='Onsets')
    ax[1].legend()
    #plt.show()
    plt.savefig('Spectrogramme_Onsets.png')
    """

    # Determine the playtime of each note
    # Each playtime is determined by the time of next onset - time of previous onset
    # The length of the timePlayed is the length of the onsetFramesFinal array - 1 since an onset is produced when the
    #   music stops, indicating the end of the last note
    timePlayed = np.empty([len(onsetFramesFinal)])
    for i in range(len(onsetFramesFinal)):
        if i == (len(onsetFramesFinal) - 1):
            timePlayed[i] = lib.get_duration(filename=filename) - times[onsetFramesFinal[i]]
        else:
            timePlayed[i] = (times[onsetFramesFinal[i+1]] - times[onsetFramesFinal[i]])
    # print(timePlayed)

    # Find frequencies which were played on the onset frames detected
    frequencyPlayed = findFrequencies(sig, times[onsetFramesFinal], filename)

    outputArray = np.stack((frequencyPlayed, timePlayed))
    return outputArray


# Name of function : findFrequencies
# Input :
    # fullSignal : Fully loaded .wav signal
    # timesOfOnsets : Time within the signal where each onset is played
# Returns :
    # Returns a numpy array containing the frequencies in order of play. Frequencies are calibrated to be exactly
    # equivalent to the frequencies obtained in theory
def findFrequencies(fullSignal, timesOfOnsets, filename):
    # Each note will have a frequency associated with it
    freqOutput = np.empty([len(timesOfOnsets)])

    # Generate cepstrum to determine fundamental frequency of signal
    # We firstly need to decompose the signal between its onsets. For each note supposedly played,
    #   we have to determine its fundamental frequency
    originalAudio = AudioSegment.from_wav(filename)

    for i in range(len(timesOfOnsets)):
        if i == (len(timesOfOnsets) - 1):
            t1 = timesOfOnsets[i] * 1000
            t2 = lib.get_duration(filename=filename) * 1000
        # Takes care of all notes played from start to last onset detected
        else:
            t1 = timesOfOnsets[i] * 1000  # Start of note in ms
            t2 = timesOfOnsets[i + 1] * 1000  # End of note in ms

        # Create new audio file containing only the note we want to analyse
        newAudio = originalAudio[t1:t2]
        newAudio.export('C:/Users/truiz/OneDrive/Desktop/ELE3000_NotesIndividuelles/Note_' + str(i) + 'ELE3000.wav', format="wav")
        newFileName = 'C:/Users/truiz/OneDrive/Desktop/ELE3000_NotesIndividuelles/Note_' + str(i) + 'ELE3000.wav'
        newSignal, sr = lib.load(newFileName)

        # For every new signal we create, generate its cepstrum and determine its fundamental frequency
        # Compute FFT of every new signal such as :
            # samplig rate = 22050Hz
        fftNewSignal = np.fft.rfft(newSignal, n=8192)
        N = len(fftNewSignal)
        n = np.arange(N) # Maps out the length of fftNewSignal
        T = N/sr
        freq = n/T # Generates frequency map to associate the generated fftNewSignal with on a plot

        """""
        # Plot the FFT of note played during the audio segment between two onsets
        fig, ax = plt.subplots(nrows=1, ncols=3, sharex=False)
        #plt.suptitle('FFT and related cepstrum of concerned note')
        fig.set_size_inches(25, 8)
        ax[0].plot(freq, np.abs(fftNewSignal))
        ax[0].set_xlim([0, 2000])
        ax[0].set_xlabel('Fréquence (Hz)')
        ax[0].set_ylabel('Puissance')
        ax[0].set_label('Amplitude FFT')
        """

        # Compute the cepstrum with the generated FFT
        cepstrum = np.fft.rfft(np.log(fftNewSignal)) # Inverse fft of the log-power spectrum of the fft of newSignal
        df = freq[1] - freq[0] # Frequency bin size
        quefrencyVector = np.fft.rfftfreq(fftNewSignal.size, df) # Is of length of  1 + size(fftNewSignal)/2

        """""
        ax[1].plot(np.abs(np.log(fftNewSignal)))
        ax[1].set_xlabel('Fréquence (Hz)')
        ax[1].set_ylabel('Amplitude (dB)')

        ax[2].plot(np.abs(quefrencyVector), np.abs(cepstrum))
        ax[2].set_xlim([0, 0.015])
        ax[2].set_ylim([0, 1000])
        ax[2].set_xlabel('Q-Fréquence (s)')
        ax[2].set_ylabel('Amplitude absolue')
        """

        # From cepstrum, get index of most important peak
        # We only take into account frequencies that are lower or equal to 2kHz
        # As an example, for a frequency of 1kHz, quefrency = 1/1000 - 0.001s will be the time at index
        freqThreshold = 2000
        for j in range(len(quefrencyVector)):
            # If the time at index j is superior than 1/2000, then it indicates that next time at index j represents a lower frequency than 2kHz
            if(quefrencyVector[j] > 1/freqThreshold):
                indexStart = j
                break

        # Get the peak of the cepstrum and store its index
        # The index lets us determine which frequency is associated with the peak when we insert it in the quefrencyVector vector
        permValue = 0
        for k in range(indexStart, len(cepstrum)):
            tempValue = np.abs(cepstrum[k])
            if(tempValue > permValue):
                permValue = tempValue
                maxIndex = k

        fundamentalFreq = 1/(2*quefrencyVector[maxIndex]) # We divide the result by an additional factor 2 because the FFT does not take into account the fundamental frequency
        freqOutput[i] = fundamentalFreq

       # plt.show()
       # plt.savefig('Cepstrum_evolution.png')

    # Convert experimental frequency values to theorical values. Theorical values
    #   will then be mapped to their gregorian representation
    # As 88 notes can be played on the piano, ranging from 27.5 to 4186.01 Hz. Each higher
    #   frequency is equal to the previous frequency multiplied by a factor of 2^(1/12)
    finalFrequency = np.empty(len(freqOutput))
    for i in range(len(freqOutput)):
        notePiano = 27.5  # Lowest note possible on piano
        finalResult = 10000  # Reset of final result
        for j in range(88):  # 88 notes possible
            # We compare the ratio of the experimental frequency obtained and the note piano we are comparing it to
            # If the absolute ratio is closest to 1 then we can assume that the piano note used
            #   is the closest to the frequency evaluated
            tempResult = freqOutput[i] / notePiano
            if(abs(tempResult - 1) < abs(finalResult - 1)):
                finalResult = tempResult
                finalFrequency[i] = notePiano
            notePiano = notePiano * 2**(1/12)

    return finalFrequency


# Main function : Will set the sample rate and the filename of the recording
    # Creates discrete signal of audio file
    # Generates the length of each note and its corresponding frequency
def setup(nameOfTextFile):
#def setup():
    # Get all information about the .wav file and its decomposition
    with open('C:/Users/truiz/OneDrive/Desktop/ELE3000_InfoEnregistrement/' + nameOfTextFile + '.txt', 'r') as f:
        lines = f.readlines()

    filenameOfPDF = lines[0].rstrip()
    tempo = int(lines[1].rstrip())
    toleranceTempo = int(lines[2].rstrip())
    filenameAudio = lines[3].rstrip()
    sampleRate = 22050  # 22.050kHz sample rate

    # Load the wav file with correct sample rate
    sig = loadFile(sampleRate, filenameAudio)

    # Get the frequencies and time played for each note
    output = stftEvaluate(sig, sampleRate, filenameAudio)

    #Print the output in a txt file in the correct format
    filenameUpdate = 'C:/Users/truiz/OneDrive/Desktop/' + filenameOfPDF + '.ly'
    noteDictionary.toText(output, tempo, toleranceTempo, filenameUpdate)


if __name__ == '__main__':
    setup()

