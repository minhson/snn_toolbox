# coding=utf-8

"""

Small CNN for Cifar10 classification, adapted from
https://github.com/akrizhevsky/cuda-convnet2/blob/master/layers/layers-cifar10-11pct.cfg

Get to 11% error, using methodology described here:
https://code.google.com/p/cuda-convnet/wiki/Methodology

"""

from __future__ import absolute_import
from __future__ import print_function

from keras.datasets import cifar10
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, Conv2D
from keras.layers import MaxPooling2D, BatchNormalization
from keras.utils import np_utils

from snntoolbox.io_utils.plotting import plot_history

batch_size = 64
nb_epoch = 100

# Data set
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
x_train = x_train.astype("float32")
x_test = x_test.astype("float32")
y_train = np_utils.to_categorical(y_train, 10)
y_test = np_utils.to_categorical(y_test, 10)

model = Sequential()

model.add(Conv2D(64, (5, 5), padding='same', input_shape=(3, 32, 32)))
model.add(BatchNormalization(axis=1))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
model.add(Dropout(0.1))

model.add(Conv2D(64, (5, 5), padding='same'))
model.add(BatchNormalization(axis=1))
model.add(Activation('relu'))
model.add(Dropout(0.1))
model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))

model.add(Conv2D(64, (3, 3)))
model.add(BatchNormalization(axis=1))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(BatchNormalization(axis=1))
model.add(Activation('relu'))

model.add(Flatten())
model.add(Dense(10))
model.add(Activation('softmax'))

model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

# Whether to apply global contrast normalization and ZCA whitening
gcn = False
zca = False

traingen = ImageDataGenerator(rescale=1./255, featurewise_center=gcn,
                              featurewise_std_normalization=gcn,
                              zca_whitening=zca, horizontal_flip=True,
                              rotation_range=10, width_shift_range=0.1,
                              height_shift_range=0.1)

# Compute quantities required for featurewise normalization
# (std, mean, and principal components if ZCA whitening is applied)
traingen.fit(x_train/255.)

trainflow = traingen.flow(x_train, y_train, batch_size=batch_size)

testgen = ImageDataGenerator(rescale=1./255, featurewise_center=gcn,
                             featurewise_std_normalization=gcn,
                             zca_whitening=zca)

testgen.fit(x_test/255.)

testflow = testgen.flow(x_test, y_test, batch_size=batch_size)

checkpointer = ModelCheckpoint(filepath='alexnet.{epoch:02d}-{val_acc:.2f}.h5',
                               verbose=1, save_best_only=True)

# Fit the model on the batches generated by datagen.flow()
history = model.fit_generator(trainflow, len(x_train) / batch_size, nb_epoch,
                              validation_data=testflow,
                              validation_steps=len(x_test) / batch_size,
                              callbacks=[checkpointer])
plot_history(history)

score = model.evaluate_generator(testflow, val_samples=len(x_test))
print('Test score:', score[0])
print('Test accuracy:', score[1])

model.save('{:2.2f}.h5'.format(score[1]*100))
