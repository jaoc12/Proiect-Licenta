import os
import pickle
import cv2
import json
import numpy as np
from skimage.feature import hog
from sklearn.svm import SVC


class Classificator:

    sudoku_path = "../Date/Sudoku/sudoku.json"
    data_path = "../Date/Dataset/"
    cell_path = "../Date/Celule/"
    svm_path = "../Date/Pickle_Objects/svc.pickle"
    hog_train_path = "../Date/Pickle_Objects/train.pickle"
    hog_test_path = "../Date/Pickle_Objects/test.pickle"
    image_size = (36, 36)
    hog_cell_size = (4, 4)
    svm = None

    def __init__(self):
        self.train_data = []
        self.train_label = []

        self.test_data = []
        self.test_label = []

        # gaseste etichetele pentru fiecare imagine din dataset
        for digit in range(1, 10):
            for it in range(2400):
                self.train_label.append(digit)
            for it in range(2400, 3000):
                self.test_label.append(digit)
        self.train_label = np.array(self.train_label)
        self.test_label = np.array(self.test_label)

        if os.path.exists(self.hog_train_path) is False or os.path.exists(self.hog_test_path) is False:
            for digit in range(1, 10):
                print(digit)
                # primele 4/5 imagini sunt folosite pentru antrenare
                for it in range(2400):
                    self.train_data.append(cv2.imread(self.data_path + str(digit) + '/' + str(it) + '.jpg',
                                           cv2.IMREAD_GRAYSCALE))
                # ultimele 1/5 imagini sunt folosite pentru testare
                for it in range(2400, 3000):
                    self.test_data.append(cv2.imread(self.data_path + str(digit) + '/' + str(it) + '.jpg',
                                          cv2.IMREAD_GRAYSCALE))

            self.train_data = np.array(self.train_data)
            self.test_data = np.array(self.test_data)

    def get_hog(self, data):
        """
        functie ce calculeaza vectorul de caracteristici hog pentru o lista de imagini data
        :param data: lista de imagini
        :return: o lista de descriptori hog
        """
        hog_data = []
        for digit in data:
            # calculam descriptorul hog pentru fiecare imagine in parte
            hog_digit = hog(digit.reshape(self.image_size), orientations=9,
                            pixels_per_cell=self.hog_cell_size, cells_per_block=(2, 2))
            hog_data.append(hog_digit)
        hog_data = np.array(hog_data)
        print(hog_data.shape)
        return hog_data

    def get_svm(self):
        """
        functie care genereaza sau incarca dintr-un fisier pickle un svm pentru clasificare
        :return: nimic
        """
        # daca nu exista un fisier cu SVM-ul atunci antrenam un nou clasificator
        if os.path.exists(self.svm_path) is False:
            # daca nu exista un fisier cu descriptori pentru antrenare atunci il cream
            if os.path.exists(self.hog_train_path) is False:
                self.train_data = self.get_hog(self.train_data)
                file_hog_train = open(self.hog_train_path, "wb")
                pickle.dump(self.train_data, file_hog_train)
            else:
                file_hog_train = open(self.hog_train_path, "rb")
                self.train_data = pickle.load(file_hog_train)

            # daca nu exista un fisier cu descriptori pentru testare atunci il cream
            if os.path.exists(self.hog_test_path) is False:
                self.test_data = self.get_hog(self.test_data)
                file_hog_test = open(self.hog_test_path, "wb")
                pickle.dump(self.test_data, file_hog_test)
            else:
                file_hog_test = open(self.hog_test_path, "rb")
                self.test_data = pickle.load(file_hog_test)

            # antrenarea unui nou SVM
            self.svm = SVC(C=0.01, kernel="rbf", verbose=True, decision_function_shape="ovr")
            self.svm.fit(self.train_data, self.train_label)

            file = open(self.svm_path, "wb")
            pickle.dump(self.svm, file)

        else:
            file = open(self.svm_path, "rb")
            self.svm = pickle.load(file)

    def prepare_cell(self, cell):
        """
        converteste o imagine a unei celule intr-o imagine in alb-negru,
        compatibila cu setul de antrenare
        :param cell: imaginea unei celule din puzzle-ul de Sudoku
        :return: noua imagine ce contine doar cifra in tonuri de alb si negru
        """
        # imaginea originala este redimensionata, blurata si transformata in imagine alb-negru
        prepared_cell = cv2.resize(cell, self.image_size)
        prepared_cell = cv2.cvtColor(prepared_cell, cv2.COLOR_BGR2GRAY)
        prepared_cell = cv2.blur(prepared_cell, (5, 5))
        prepared_cell = cv2.adaptiveThreshold(prepared_cell, 255,
                                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # cautam contururile din imagine si il selectam pe cel mai mare
        contours, hierarchy = cv2.findContours(prepared_cell, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return None
        contours_sorted = sorted(contours, key=cv2.contourArea)[-1]

        # cream o masca alb-negru pe care desenam cel mai mare contur
        mask = np.zeros(self.image_size, dtype=np.uint8)
        cv2.drawContours(mask, [contours_sorted], -1, (255, 255, 255), thickness=cv2.FILLED)

        # "decupam" conturul din imagine folosind masca
        digit = cv2.bitwise_and(prepared_cell, prepared_cell, mask=mask)

        return digit

    def check_cell_blank(self, cell):
        """
        verifica daca o celula contine sau nu o cifra
        :param cell: imaginea alb-negru a unei celule
        :return: True sau False
        """
        if cell is None:
            return True

        # calculeaza procentul din imagine care este diferit de zero
        percent = cv2.countNonZero(cell) / float(self.image_size[0] * self.image_size[1])
        if percent < 0.1:
            return True
        else:
            return False

    def get_cell(self, i, j):
        """
        calculeaza ce cifra se afla intr-o imagine data
        :param i: pe ce linie din puzzle se afla imaginea
        :param j: pe ce coloana din puzzle se afla imaginea
        :return: cifra prezisa de SVM
        """
        # incarca imaginea dintr-un fisier si o transforma in una alb-negru
        current_path = self.cell_path + "celula" + str(i) + str(j) + ".png"
        cell = cv2.imread(current_path)
        cell = self.prepare_cell(cell)

        # daca imaginea nu contine o cifra prin conventie o notam cu 0
        if self.check_cell_blank(cell) is True:
            return 0
        else:
            # calculam descriptorul hog pentru imaginea curenta si folosim folosim un SVM pentru a clasifica cifra
            digit_hog = hog(cell, orientations=9, pixels_per_cell=self.hog_cell_size, cells_per_block=(2, 2))
            return self.svm.predict([digit_hog])[0]

    def get_sudoku(self):
        """
        clasifica fiecare imagine a unei celule din Sudoku
        :return: o matrice 9x9 ce reprezinta jocul de Sudoku
        """
        sudoku = np.zeros((9, 9))

        for i in range(9):
            for j in range(9):
                # pentru fiecare celula gasim cifra prezenta in imagine
                sudoku[i][j] = self.get_cell(i, j)
                print((i*9+j)/81 * 100)

        return sudoku


classificator = Classificator()
classificator.get_svm()
sudoku = classificator.get_sudoku()

sudoku_json = {
    "Grid":
        sudoku.flatten().tolist()
}

with open(classificator.sudoku_path, "w") as path:
    json.dump(sudoku_json, path)
