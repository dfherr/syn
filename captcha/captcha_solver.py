import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as nd
from scipy import signal as sig

from masks import *

digit_width = 8
digit_height = 10

# TODO: fix captchas containing a '1'
# TODO: save captchas to the database


def solve_captcha(img, output=False, save_to_db=False):
    # Transform to a numpy array
    img = np.asarray(img)
    img.setflags(write=True)

    # output the processed captcha
    if output:
        plt.imshow(img, cmap='gray', interpolation='none')
        plt.show()

    # find the positions of the numbers
    # the minimal values in the convolution gives the
    # most likely center position of a digit
    kernel = np.ones((digit_height, digit_width))
    conv = nd.convolve(img, kernel, mode='constant', cval=0)
    # output the convolution
    if output:
        plt.imshow(conv, cmap='gray', interpolation='none')
        plt.colorbar()
        plt.show()

    # find the 3 maximal values to get the 3 digit centers
    local_max = sig.argrelmax(conv)
    maxima = []
    # TODO: multiple minima...
    for i, j in zip(*local_max):
        if conv[i, j] == conv[i-1:i+2, j-1:j+2].max():
            maxima.append((i, j))

    maxima = sorted(maxima, key=lambda p: p[1])
    # output all maxima
    if output:
        print(maxima)

    # save all digits
    # 13 height, 12 width
    numbers = []
    for position in maxima:
        numbers.append(
            img[
                position[0]-7:position[0]+8,
                position[1]-5:position[1]+7
            ]
        )
        if output:
            plt.imshow(numbers[-1], cmap='gray', interpolation='none')
            plt.show()

    # compare them to the masks
    captcha_code = []
    for number in numbers:
        captcha_code.append(classifier.predict(number.flatten())[0])
    captcha = map(str, captcha_code)
    return ''.join(captcha)
