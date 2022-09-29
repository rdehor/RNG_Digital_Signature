import numpy as np
import cv2
import pyaudio
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import tkinter as tk

randomizedArrayOfInt = []

def binarizeImage(image,treshold):
    #binarize image
    img = np.where(image < treshold, 0, 255)
    return img

def calculateSpectrums(Image) : 
    #calculate fourier transform - complex spectrum
    image_fourier = np.fft.fft2(Image)              
    #magnitude spectrum
    magnitude = np.abs(image_fourier)
    #magnitude in logaritmic scale                            
    #phase spectrum
    phase = np.angle(image_fourier) 
    return magnitude


def recordSound():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream= p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    seconds = 10
    for i in range(0, int (RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    numbers = [item for sublist in frames for item in sublist]

    return numbers

def takePicture():
    camera_port = 0
    camera = cv2.VideoCapture(-1)
    arrayOfPhotos = []
    numberOfFrames = 0
    while(True):
        numberOfFrames += 1
        time.sleep(0.1)  # If you don't wait, the image will be dark
        return_value, image = camera.read()
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        flat_list = grayImage.tolist()
        array2D = [item for sublist in flat_list for item in sublist]
        arrayOfPhotos.append(array2D)
        if numberOfFrames >= 15:
            break
    del(camera)  # so that others can use the camera as soon as possible
    return arrayOfPhotos
  


def getRandomizedSeed(audioSeed, imageSeed, numberBits=8):
    randomizedSeed = ""
    workingAudioSeed = ""
    workingImageSeed = ""
    for i in audioSeed:
        workingAudioSeed += i
    for i in imageSeed:
        workingImageSeed += i

    for i in range(len(workingImageSeed)):
        if(i == len(workingAudioSeed)):
            break
        if(workingImageSeed[i] == "0"):
            randomizedSeed = randomizedSeed + workingAudioSeed[i]
    if(len(randomizedSeed)<8):
        return "00000100"
    return randomizedSeed

def getImageSeed(imageArray):

    
    imageSeedDecimal = [item for sublist in imageArray for item in sublist]
    import random

    numbers = []
    
    random.shuffle(imageSeedDecimal)

    workin = ""
    space = 0
    for i in imageSeedDecimal: 
        if(space <= 0):
            x = format(i, "b")
            workin = x[6:7] + workin
            if(len(workin)>= 8 ):
                numbers.append(workin[:8])
                space = int(workin[:8], 2)
                workin=""
        space = space -1
    return numbers



def getAudioSeed(audioData):
    numbers = []
    workingString = ""
    space = 0
    for i in audioData:
        if(i > 0):
            if(space <= 0 and i != 0 and i != 255):
                x = format(i, "b")
                workingString = workingString + x[len(x)-1:]
                if(len(workingString)>= 8 ):
                    numbers.append(workingString[:8])
                    space = int(workingString[:8], 2)
                    workingString=""
            space = space -1
    return numbers

def genrateIntArray(stringOfBits):
    bits = 8
    arrayOfInt = []
    for index in range(0, len(stringOfBits), bits):
        arrayOfInt.append(int(stringOfBits[index : index + bits], 2))
    return arrayOfInt

def generateRandomArray():
    global randomizedArrayOfInt
    sound = recordSound()
    image = takePicture()
    img = getImageSeed(image)
    snd = getAudioSeed(sound)
    randomSeed = getRandomizedSeed(snd,img)
    randomizedArrayOfInt = genrateIntArray(randomSeed)

def randomNum(bracket):
    global randomizedArrayOfInt
    temp = []
    if(bracket != 1):
        if(bracket > len(randomizedArrayOfInt)):
            generateRandomArray()
            temp = randomizedArrayOfInt[:bracket]
            randomizedArrayOfInt = randomizedArrayOfInt[:-bracket]
            return bytes(temp)
        else:
            temp = randomizedArrayOfInt[:bracket]
            randomizedArrayOfInt = randomizedArrayOfInt[:-bracket]
            return bytes(temp)
    else:
        if not randomizedArrayOfInt:
            generateRandomArray()
            temp.append(randomizedArrayOfInt[0])
        else:
            temp.append(randomizedArrayOfInt[0])
            del randomizedArrayOfInt[0]
    
        return bytes(temp)

frame = tk.Tk()
frame.title("TextBox Input")
frame.geometry('960x720')

  
def printInput():
    inp = inputtxt.get(1.0, "end-1c")
    start = time.time()


    privateKey = RSA.generate(1024, randomNum)

    publicKey = privateKey.publickey()
    message = inp.encode('UTF-8')

    cipher = PKCS1_OAEP.new(key=publicKey)
    encoded = cipher.encrypt(message)

    cipher = PKCS1_OAEP.new(key=privateKey)
    decoded = cipher.decrypt(encoded)

    privateKey2 = RSA.generate(1024, randomNum)
    cipher = PKCS1_OAEP.new(key=privateKey2)
    decodedBad = cipher.decrypt(encoded)

    end = time.time()
    
    lbl.config(text = 
    f"klucz prywatny: {privateKey} \n"
    f"klucz publiczny: {publicKey}\n"
    f"wiadomość: {message}\n"
    f"zakodowana wiadomość: \n{encoded}\n"
    f"zdekodowana wiadomość: {decoded}\n"
    f"nowy klucz prywatny: {privateKey2}\n"
    f"wiadomość zdekodowana nowym kluczem: \n{decodedBad}\n"
    f"czas wygenerowania pierwszego klucza: {end-start}"
    )

inputtxt = tk.Text(frame,
                   height = 5,
                   width = 20)
  
inputtxt.pack()
  

printButton = tk.Button(frame,
                        text = "nowy klucz", 
                        command = printInput)
printButton.pack()
  

lbl = tk.Label(frame, text = "")
lbl.pack()
frame.mainloop()