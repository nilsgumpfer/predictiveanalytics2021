from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.callbacks import TensorBoard
from tensorflow.python.keras.datasets import mnist
from tensorflow.python.keras.layers import Conv1D, MaxPool1D, Dropout, GlobalAveragePooling1D, Dense
from tensorflow.python.keras.utils.np_utils import to_categorical

# Load train and test data
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

# Plot 100 training samples
fig, ax = plt.subplots(nrows=10, ncols=10, figsize=(10, 10))
axs = ax.ravel()
for i in range(100):
    axs[i].imshow(train_images[i], cmap='Greys')

plt.tight_layout()
plt.savefig('../data/mnist_digits_100.jpg')
plt.close()

# Normalize color values (here: grey-scales)
train_images = train_images / 255.0
test_images = test_images / 255.0

# Do one-hot encoding / do categorical conversion
train_labels = to_categorical(train_labels)
test_labels = to_categorical(test_labels)

# Extract number of classes from data dimensions
nclasses = np.shape(train_labels)[1]

# Define hyperparameters in dictionary for flexible use
config = {'conv_layers': 4,
          'conv_filters': 64,
          'conv_kernel_size': 3,
          'conv_initializer': 'he_uniform',
          'conv_padding': 'same',
          'conv_activation_function': 'relu',
          'conv_maxpool_stride': 2,
          'conv_maxpool_size': 2,
          'conv_dropout_rate': 0.1,
          'fc_layers': 2,
          'fc_neurons': 16,
          'fc_activation_function': 'relu',
          'fc_initializer': 'he_uniform',
          'fc_dropout_rate': 0.1,
          'optimizer': 'adam',
          'loss': 'categorical_crossentropy',
          'epochs': 20}

# Define model architecture
model = Sequential()

# First convolutional and pooling layer
model.add(Conv1D(input_shape=(28, 28), filters=config['conv_filters'], kernel_size=config['conv_kernel_size'], padding=config['conv_padding'], activation=config['conv_activation_function'], kernel_initializer=config['conv_initializer']))
model.add(MaxPool1D(strides=config['conv_maxpool_stride'], pool_size=config['conv_maxpool_size']))

# Convolutional and dropout layers
for i in range(config['conv_layers']):
    model.add(Conv1D(filters=config['conv_filters'], kernel_size=config['conv_kernel_size'], padding=config['conv_padding'], activation=config['conv_activation_function'], kernel_initializer=config['conv_initializer']))
    model.add(Dropout(config['conv_dropout_rate']))

# Global average pooling reduces number of dimensions
model.add(GlobalAveragePooling1D())

# Dense and dropout layers
for i in range(config['fc_layers']):
    model.add(Dense(units=config['fc_neurons'], activation=config['fc_activation_function'], kernel_initializer=config['fc_initializer']))
    model.add(Dropout(config['fc_dropout_rate']))

# Last dense layer has width of label (number of classes)
model.add(Dense(units=nclasses, activation='softmax', kernel_initializer=config['fc_initializer']))

# Compile model
model.compile(optimizer=config['optimizer'], loss=config['loss'], metrics=['accuracy'])

# Print model architecture
model.summary()

# Tensorboard callback
tensorboard_callback = TensorBoard(log_dir='tensorboard/' + 'mnist_digits_cnn_' + datetime.utcnow().strftime('%Y%m%d%H%M%S'))

# Train model
model.fit(x=train_images, y=train_labels, epochs=config['epochs'], validation_data=(test_images, test_labels), callbacks=[tensorboard_callback])

# Evaluate model
test_loss, test_acc = model.evaluate(test_images, test_labels)
print('Test accuracy:', test_acc)