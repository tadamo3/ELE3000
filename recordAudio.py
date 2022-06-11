#!/usr/bin/env python3
"""Create a recording with arbitrary duration.
The soundfile module (https://PySoundFile.readthedocs.io/) has to be installed!
"""
import argparse
import tempfile
import queue
import sys

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

import multiprocessing


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument(
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args(remaining)

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


def startRecording(name, event):
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])
    if args.filename is not name:
        args.filename = tempfile.mktemp(prefix=name, suffix='.wav', dir='C:/Users/truiz/OneDrive/Desktop/ELE3000_Enregistrements/')
        #args.filename = 'C:/Users/truiz/OneDrive/Desktop/' + name + '.wav'

    # Make sure the file is opened before recording anything:
    with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                      channels=args.channels, subtype=args.subtype) as file:
        #Callback and put in queue audio blocks
        with sd.InputStream(samplerate=args.samplerate, device=args.device,
                            channels=args.channels, callback=callback):
            print('Recording started')
            while not event.is_set(): # while the event flag is false, write in file
                file.write(q.get())
            else:
                stopRecording(name)


def stopRecording(name):
    print('\nRecording finished: ' + repr(args.filename))
    with open('C:/Users/truiz/OneDrive/Desktop/ELE3000_InfoEnregistrement/' + name + '.txt', 'a') as f:
        f.write('\n')
        f.write(args.filename)
    parser.exit(0)
