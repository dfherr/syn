import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as nd
from scipy import signal as sig

from .masks import classifier

__all__ = ['solve_captcha']


digit_width = 8
digit_height = 10


def solve_captcha(img, output=False):
    # Transform to a numpy array
    img = np.asarray(img)
    img.setflags(write=True)

    # make picture bigger and center size:
    # the digit recognition and the masks do not
    # go out of the image
    height, width = img.shape
    center_img = np.zeros(
        (height+2*digit_height, width+2*digit_width)
    )
    center_img[
        digit_height:digit_height+height,
        digit_width:digit_width+width
    ] = img
    if output:
        plt.imshow(center_img, cmap='gray', interpolation='none')
        plt.colorbar()
        plt.show()
    img = center_img

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
    # saving of last max necessary cause of multiple
    # maxima occurring for the digit '1'
    # here we just take the first one
    last_max = (-2, -2)
    for i, j in zip(*local_max):
        if conv[i, j] == conv[i-1:i+2, j-1:j+2].max():
            if last_max[0] != i or j-last_max[1] > 2:
                maxima.append((i, j))
                last_max = (i, j)

    maxima = sorted(maxima, key=lambda p: p[1])
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