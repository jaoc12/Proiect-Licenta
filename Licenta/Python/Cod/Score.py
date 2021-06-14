import os

import numpy as np
import pickle
import cv2
from skimage.feature import hog
from sklearn import metrics
from sklearn.svm import SVC

hog_test_path = "../Date/Pickle_Objects/test.pickle"
hog_train_path = "../Date/Pickle_Objects/train.pickle"
cell_path = "../Date/Celule_Test/"
svm_path = "../Date/Pickle_Objects/svc.pickle"

image_size = (36, 36)
hog_cell_size = (4, 4)


def prepare_cell(cell):
    prepared_cell = cv2.resize(cell, image_size)
    prepared_cell = cv2.cvtColor(prepared_cell, cv2.COLOR_BGR2GRAY)
    prepared_cell = cv2.blur(prepared_cell, (5, 5))
    prepared_cell = cv2.adaptiveThreshold(prepared_cell, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    contours, hierarchy = cv2.findContours(prepared_cell, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None
    contours_sorted = sorted(contours, key=cv2.contourArea)[-1]

    mask = np.zeros(image_size, dtype=np.uint8)
    cv2.drawContours(mask, [contours_sorted], -1, (255, 255, 255), thickness=cv2.FILLED)

    digit = cv2.bitwise_and(prepared_cell, prepared_cell, mask=mask)

    return digit


def get_cell(i, svm):
    current_path = cell_path + str(i) + ".png"
    cell = cv2.imread(current_path)
    cell = prepare_cell(cell)

    digit_hog = hog(cell, orientations=9, pixels_per_cell=hog_cell_size, cells_per_block=(2, 2))
    return svm.predict_proba([digit_hog])[0]


file_hog_train = open(hog_train_path, "rb")
train_data = pickle.load(file_hog_train)

file_hog_test = open(hog_test_path, "rb")
test_data = pickle.load(file_hog_test)

test_label = []
train_label = []
for digit in range(1, 10):
    for it in range(2400):
        train_label.append(digit)
    for it in range(2400, 3000):
        test_label.append(digit)
train_label = np.array(train_label)
test_label = np.array(test_label)

if os.path.exists(svm_path) is False:
    svm = SVC(C=0.1, kernel="poly", degree=2, verbose=True, decision_function_shape="ovr", probability=True)
    svm.fit(train_data, train_label)

    file = open(svm_path, "wb")
    pickle.dump(svm, file)
else:
    file = open(svm_path, "rb")
    svm = pickle.load(file)

cell_label = np.array([8, 1, 9, 5, 8, 7, 1, 4, 9, 7, 6, 7, 1, 2, 5, 8,
                       6, 1, 7, 1, 5, 2, 9, 7, 4, 6, 8, 3, 9, 4, 3, 5, 8,
                       6, 4, 7, 7, 6, 9, 5, 8, 7, 2, 9, 3, 8, 5, 4, 3, 1,
                       7, 5, 2, 3, 2, 8, 2, 3, 1])
cell_data = []
for i in range(59):
    cell_data.append(get_cell(i, svm))
cell_data = np.array(cell_data)

print(metrics.roc_auc_score(cell_label, cell_data, multi_class='ovr'))
