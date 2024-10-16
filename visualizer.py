# links to look at for low pass filter:
# https://medium.com/analytics-vidhya/how-to-filter-noise-with-a-low-pass-filter-python-885223e5e9b7
# https://123.physics.ucdavis.edu/week_5_files/filters/digital_filter.pdf

import soundfile as sf # used to read the wav
import pygame
from scipy.signal import butter, filtfilt
from os import listdir # used to get available songs
import random
import colorsys

fps = 30 # must be a factor of samplerate
windowSize = (1080, 720)

# takes a signal and returns it simplified as the max amplitude of each frame
def simplifySig(originalSig):
    maxGroup = list()
    groupSize = samplerate / fps # the number of samples in one frame
    condensedSig = list()

    # condense groups of groupSize into a list of their max
    for amp in originalSig:
        maxGroup.append(amp)
        if len(maxGroup) == groupSize:
            condensedSig.append(max(maxGroup))
            maxGroup = list()
    
    return condensedSig

# returns the signal after being apssed through a low pass filter --- BASS
def lowPassFilter(originalSig):
    cutoff = 100 # cutoff frequency in hertz
    
    b, a = butter(4, (cutoff * 2 / samplerate), btype='lowpass', analog=False)
    lowSig = filtfilt(b, a, originalSig)

    # return it simplified to the fps, using simplifySig()
    return simplifySig(lowSig)

# returns the signal after being apssed through a high pass filter --- TREBLE
def highPassFilter(originalSig):
    cutoff = 600 # cutoff frequency in hertz
    
    b, a = butter(4, (cutoff * 2 / samplerate), btype='highpass', analog=False)
    highSig = filtfilt(b, a, originalSig)

    # return it simplified to the fps, using simplifySig()
    return simplifySig(highSig)



if __name__ == '__main__':
    # get available songs and print these options
    availableSongs = [f for f in listdir() if f.endswith(".wav")]
    availableSongs.sort()
    print()
    for i in range(len(availableSongs)):
        print(i+1, availableSongs[i])

    # get user selection
    print()
    fileName = availableSongs[int(input())-1]
    print()
    print("Playing:", fileName)

    # read audio file
    sig, samplerate = sf.read(fileName)
    assert samplerate % fps == 0, "fps does not evenly divide samplerate" # it would cause sync issues

    # combine into one channel
    monoSig = list()
    for i in range(sig.shape[0]):
        monoSig.append((sig[i, 0] + sig[i, 1]) / 2)

    # process audio
    simpleSig = simplifySig(monoSig)
    lowSig = lowPassFilter(monoSig)
    highSig = highPassFilter(monoSig)

    # setting up pygame
    pygame.init()
    screen = pygame.display.set_mode(windowSize)
    running = True

    # setting up timing
    clock = pygame.time.Clock()
    timestamp = 0
    frameLength = 1000 / fps # float: length of frame in ms

    # setting up pygame mixer
    pygame.mixer.init()
    music = pygame.mixer.Sound(fileName)
    music.set_volume(1)

    # starting audio + video
    screenColor = (0, 0, 0)
    screen.fill(screenColor)
    pygame.display.flip()
    music.play()
    clock.tick()

    # setting up colors and rectangle thickness
    bgColors = [(i, i, i) for i in range(100, 200, 25)]
    rectThick = 50
    circleHue = 0

    while running:
        # quitting early is handled here:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # if at the end of the song:
        if int(timestamp / frameLength) >= len(simpleSig)-1:
            break
        
        # getting the current amplitudes
        timestamp += clock.tick(fps)
        simpleAmp = simpleSig[int(timestamp / frameLength)]
        lowAmp = lowSig[int(timestamp / frameLength)]
        highAmp = highSig[int(timestamp / frameLength)]

        # start drawing by filling screen
        screen.fill(screenColor)

        # high signal rectangles
        if abs(highAmp) > 0.4:
            # draw horizontal rectangle
            rectColor = random.choice(bgColors)
            horizontalRect = (0, 0, screen.get_size()[0], rectThick)
            pygame.draw.rect(screen, rectColor, horizontalRect)

            # draw vertical rectangle
            verticalRect = (0, 0, rectThick, screen.get_size()[1])
            pygame.draw.rect(screen, rectColor, verticalRect)

        # low signal rectangles
        if abs(lowAmp) > 0.4:
            # draw horizontal rectangle
            rectColor = random.choice(bgColors)
            horizontalRect = (0, screen.get_size()[1]-rectThick, screen.get_size()[0], rectThick)
            pygame.draw.rect(screen, rectColor, horizontalRect)

            # draw vertical rectangle
            verticalRect = (screen.get_size()[0]-rectThick, 0, rectThick, screen.get_size()[1])
            pygame.draw.rect(screen, rectColor, verticalRect)
        
        # getting circle color
        circleColor = colorsys.hls_to_rgb(circleHue, 0.5, 1)
        circleColor = (circleColor[0]*255, circleColor[1]*255, circleColor[2]*255)
        circleHue += 0.1 / fps

        # drawing circles
        pygame.draw.circle(screen, "grey", tuple(i/2 for i in screen.get_size()), abs(simpleAmp) * (windowSize[1] // 6))
        pygame.draw.circle(screen, circleColor, tuple(i/2 + 200 for i in screen.get_size()), abs(lowAmp) * (windowSize[1] // 3))
        pygame.draw.circle(screen, circleColor, tuple(i/2 - 200 for i in screen.get_size()), abs(highAmp) * (windowSize[1] // 3))
        pygame.display.flip()

    pygame.quit()