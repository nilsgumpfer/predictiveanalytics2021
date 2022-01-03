"""
Title: Grad-CAM class activation visualization (adapted)
Author: Nils Gumpfer
Original Author: [fchollet](https://twitter.com/fchollet)
Adapted from Deep Learning with Python (2017).
Source: https://raw.githubusercontent.com/keras-team/keras-io/master/examples/vision/grad_cam.py
"""

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import ResNet152
from tensorflow.keras.applications.resnet import preprocess_input
from tensorflow.keras.preprocessing import image


def make_gradcam_heatmap(img_array, model, last_conv_layer_name):
    # First, we create a model that maps the input image to the activations
    # of the last conv layer as well as the output predictions
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    # Then, we compute the gradient of the top predicted class for our input image
    # with respect to the activations of the last conv layer
    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    # This is the gradient of the output neuron (top predicted or chosen)
    # with regard to the output feature map of the last conv layer
    grads = tape.gradient(class_channel, last_conv_layer_output)

    # This is a vector where each entry is the mean intensity of the gradient
    # over a specific feature map channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # We multiply each channel in the feature map array
    # by 'how important this channel is' with regard to the top predicted class
    # then sum all the channels to obtain the heatmap class activation
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # For visualization purpose, we will also normalize the heatmap between 0 & 1
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()


def save_and_display_gradcam(img_path, heatmap, cam_path, cmap_name, alpha):
    # Load the original image
    img = keras.preprocessing.image.load_img(img_path)
    img = keras.preprocessing.image.img_to_array(img)

    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # Use colormap to colorize heatmap
    cmap = cm.get_cmap(cmap_name)

    # Use RGB values of the colormap
    cmap_colors = cmap(np.arange(256))[:, :3]
    cmap_heatmap = cmap_colors[heatmap]

    # Create an image with RGB colorized heatmap
    cmap_heatmap = keras.preprocessing.image.array_to_img(cmap_heatmap)
    cmap_heatmap = cmap_heatmap.resize((img.shape[1], img.shape[0]))
    cmap_heatmap = keras.preprocessing.image.img_to_array(cmap_heatmap)

    # Superimpose the heatmap on original image
    superimposed_img = cmap_heatmap * alpha + img
    superimposed_img = keras.preprocessing.image.array_to_img(superimposed_img)

    # Save the superimposed image
    superimposed_img.save(cam_path)


def main(cmap_name='afmhot', alpha=2.0):
    # Load model
    model = ResNet152(weights='imagenet')

    # Parameters
    last_conv_layer_name = 'conv5_block3_out'
    # img_path = '../data/rooster.jpg'
    # img_path = '../data/myrooster.jpg'
    # img_path = '../data/tower.jpg'
    img_path = '../data/castle.jpg'
    # img_path = '../data/castledark.jpg'
    cam_path = '{}_cam.jpg'.format(img_path.rsplit('.', maxsplit=1)[0])

    # Load and preprocess image
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    # Remove last layer's softmax activation (we need the raw values!)
    model.layers[-1].activation = None

    # Generate class activation heatmap (CAM)
    heatmap = make_gradcam_heatmap(x, model, last_conv_layer_name)

    # Display heatmap
    plt.matshow(heatmap, cmap=cmap_name)
    plt.show()

    # Create and save superimposed visualization
    save_and_display_gradcam(img_path, heatmap, cam_path, cmap_name, alpha)


main()