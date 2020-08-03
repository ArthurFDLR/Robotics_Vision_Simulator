import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #Avoid the annoying tf warnings 

import tensorflow as tf
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def showModelComparison(modelsDict, sizePlot, commonDescription):
    '''Display the evolution of Loss and Accuracy versus epochs given histories of training

    Parameters:
        modelsDict (Dict{ str:Dict{ str:list[float] } }): Dictionary containing the training history of a model referenced by its name
        sizePlot (list[row,column])
        commonDescription (str): Common caracteristics of the models
    
    Return:
        Matplotlib figure: Comparison of given models
    '''

    fig, axes = plt.subplots(sizePlot[0], sizePlot[1])
    plt.text(x=0.5, y=0.94, s='MNIST dataset, Epochs size: ' + str(sizeTrainingSet) + ' (' + str((sizeTrainingSet*100)//sizeTrainingSetInit) + '%)', fontsize=20, ha="center", transform=fig.transFigure)
    plt.text(x=0.5, y=0.88, s= commonDescription, fontsize=17, ha="center", transform=fig.transFigure)


    for i, (nameModel, history) in enumerate(modelsDict.items()):

        try:
            ax = axes.flatten()[i]
        except:
            ax=axes

        for counter, (name, values) in enumerate(history.items()):
            ax.plot(values, label=name, marker='o', color='blue' if counter%2==0 else 'red', linestyle='--' if counter<2 else '-')
            if counter == 3:
                ax.set_title(nameModel + '\nBest accuracy (epochs=' + str(np.argmax(values)+1) + '): ' + str(round(max(values)*100.0,4)) + '%')
        ax.set_xticks([i for i in range(nbrEpochsMax)])
        ax.legend()
    plt.subplots_adjust(top=0.8, wspace=0.2, right=0.95, left=0.05, bottom=0.05, hspace=0.35)
    plt.show()

def Comparison_TrainingSize(classOutput:list, handID:int):
    modelsDict = {}

    allSamples_x, allSamples_y_oneHot = loadDataset(classOutput, -1, handID,True)

    for size in [25, 50, 75, 100, 125, 150, 175, 200]:

        trainSamples_x = allSamples_x[:size]
        trainSamples_y = allSamples_y_oneHot[:size]
        testSamples_x  = allSamples_x[size:]
        testSamples_y  = allSamples_y_oneHot[size:]


        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(32, input_dim=42, activation=tf.keras.activations.relu))
        model.add(tf.keras.layers.Dense(32, activation=tf.keras.activations.relu))
        model.add(tf.keras.layers.Dense(len(classOutput), activation=tf.keras.activations.softmax))

        model.summary()
        model.compile(optimizer=tf.keras.optimizers.Adam(),
                    loss='categorical_crossentropy', # prefere loss='sparse_categorical_crossentropy' if not one-hot encoded
                    metrics=['accuracy'])

        hist = model.fit(x=trainSamples_x, y=trainSamples_y, epochs=9, batch_size=20,  validation_data=(testSamples_x,testSamples_y)).history

        modelsDict['Size:' + str(size)] = hist
    
    return modelsDict

def loadFile(poseName:str, handID:int):
    fileName = '.\\Datasets\\{}\\{}\\data.txt'.format(poseName, 'right_hand' if handID == 1 else 'left_hand')
    listOut = []
    if os.path.exists(fileName):

        currentEntry = []

        dataFile = open(fileName)
        for i, line in enumerate(dataFile):
            if i == 0:
                info = line.split(',')
                if len(info) == 3:
                    poseName = info[0]
                    handID = int(info[1])
                    tresholdValue = float(info[2])
                else:
                    print('Not a supported dataset')
                    break
            else:
                if line[0] == '#' and line[1] != '#': # New entry
                    currentEntry = [[], []]
                    accuracy = float(line[1:])
                elif line[0] == 'x':
                    listStr = line[2:].split(' ')
                    for value in listStr:
                        currentEntry[0].append(float(value))
                elif line[0] == 'y':
                    listStr = line[2:].split(' ')
                    for value in listStr:
                        currentEntry[1].append(float(value))
                elif line[0] == 'a':  # Last line of entry
                    listOut.append([])
                    for i in range(len(currentEntry[0])):
                        listOut[-1].append(currentEntry[0][i])
                        listOut[-1].append(currentEntry[1][i])

        dataFile.close()

    return listOut

def saveModel(model:tf.keras.models, name:str, handID:int, outputClass):
    rootPath = r'.\Models'
    if not os.path.isdir(rootPath): #Create Models directory if missing
        os.mkdir(rootPath)
    modelPath = rootPath + r".\\" + name
    if not os.path.isdir(modelPath): #Create model directory if missing
        os.mkdir(modelPath)
    
    classFile = open(modelPath+r'\class.txt',"w")
    for i,c in enumerate(outputClass):
        classFile.write((',' if i!=0 else '') + c)
    classFile.close()

    model.save( modelPath + r'\\' + name + ('_right' if handID == 1 else '_left') + '.h5')

def loadDataset(classOutput:list, samplePerClass:int, handID:int, onehotEncoding:bool=False):
    
    trainSamples_x = []
    testSamples_x = []
    trainSamples_y = []
    trainSamples_y_oneHot = []
    for i, className in enumerate(classOutput):
        loadedSampels = loadFile(className, handID)
        if samplePerClass > 0:
            trainingLoad = loadedSampels[:min(samplePerClass, len(loadedSampels)-1)]
            testingLoad = loadedSampels[min(samplePerClass, len(loadedSampels)-1):]
        trainSamples_x += trainingLoad
        testSamples_x += testingLoad
        trainSamples_y += [i for j in range(len(trainingLoad))]

        outPut_tmp = [0]*len(classOutput)
        outPut_tmp[i] = 1
        trainSamples_y_oneHot += [outPut_tmp for j in range(len(trainingLoad))]
    
    trainSamples_x = np.array(trainSamples_x)
    testSamples_x = np.array(testSamples_x)
    trainSamples_y = np.array(trainSamples_y)
    trainSamples_y_oneHot = np.array(trainSamples_y_oneHot)

    index = np.arange(trainSamples_x.shape[0])
    np.random.shuffle(index)
    trainSamples_x = trainSamples_x[index]
    testSamples_x = testSamples_x[index]
    trainSamples_y = trainSamples_y[index]
    trainSamples_y_oneHot = trainSamples_y_oneHot[index]
    
    if len(trainSamples_x) < samplePerClass*len(classOutput):
        print('Size expectation not met.')

    return trainSamples_x, (trainSamples_y_oneHot if onehotEncoding else trainSamples_y)

if __name__ == "__main__":

    IdTesting, IdModelSaving, IdModelComparison = range(3)
    SELECTOR = 1

    if SELECTOR == IdModelComparison:
        pass

    if SELECTOR == IdModelSaving:

        classFingerCount = ['1_Eng', '2_Eng', '3_Eng', '4_Eng', '5']
        classRestaurant = ['Chef', 'Help', 'Super', 'VIP', 'Water']
        classDivers = ['Metal']
        classOutput = classFingerCount + classRestaurant + classDivers
        handID = 0

        allSamples_x, allSamples_y_oneHot = loadDataset(classOutput, -1, handID,True)
        
        ## Model definition

        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(32, input_dim=42, activation=tf.keras.activations.relu))
        model.add(tf.keras.layers.Dense(32, activation=tf.keras.activations.relu))
        model.add(tf.keras.layers.Dense(len(classOutput), activation=tf.keras.activations.softmax))

        model.summary()
        model.compile(optimizer=tf.keras.optimizers.Adam(),
                    loss='categorical_crossentropy', # prefere loss='sparse_categorical_crossentropy' if not one-hot encoded
                    metrics=['accuracy'])

        hist = model.fit(x=allSamples_x, y=allSamples_y_oneHot, epochs=9, batch_size=20,  validation_split=0.15).history

        saveModel(model, 'Test', handID, classOutput)