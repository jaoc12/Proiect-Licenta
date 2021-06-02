import numpy as np
import cv2


class Detector:
    directory_path = R"C:\Users\chitu\Desktop\Licenta\Cod\Licenta\Licenta\Python\Date\Celule\celula"
    image = None

    def __init__(self, img_path):
        self.image = cv2.imread(img_path)

    @staticmethod
    def get_distance(point1, point2):
        """
        calculeaza distanta dintre doua puncte, sub form unui numar intreg
        :param point1: punctul 1
        :param point2: punctul 2
        :return: parte intreaga din distanta dintre puncte
        """
        distance = np.sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))
        return int(distance)

    @staticmethod
    def left_sort_squares(row):
        """
        sorteaza un rand de patrate dat de la stanga la dreapta
        :param row: rand de patrate, reprezentat de coordonatele colturilor
        :return:
        """
        sorted_row = sorted(row, key=lambda square: sum(square[1:3, 0]))
        return sorted_row

    @staticmethod
    def upscale_grid(corners, size_factor):
        """
        largeste cadrul unui patrat din imagine cu un procent dat
        :param corners: colturile patratului
        :param size_factor: factorul cu care sa fie marit
        :return: colturile patratului marit
        """
        if size_factor == 1:
            return corners

        top_right = [int(corners[0][0] * size_factor), int(corners[0][1] * (2-size_factor))]
        top_left = [int(corners[1][0] * (2-size_factor)), int(corners[1][1] * (2-size_factor))]
        bottom_left = [int(corners[2][0] * (2-size_factor)), int(corners[2][1] * size_factor)]
        bottom_right = [int(corners[3][0] * size_factor), int(corners[3][1] * size_factor)]

        new_corners = [top_right, top_left, bottom_left, bottom_right]
        return new_corners

    @staticmethod
    def sort_corners(corners):
        """
        sorteaza colturile unui patrat in ordine trigonometrica
        :param corners: coordonatele colturilor
        :return: colturile ordonate trigonometric
        """
        sorted_corners = []

        # sorteaza colturile dupa inaltime
        corners = sorted(corners, key=lambda corner: corner[1])
        top_corners = corners[:2]
        bottom_corners = corners[2:]

        # sorteaza colturile de sus de la stanga la dreapta
        if top_corners[0][0] > top_corners[1][0]:
            sorted_corners.append(top_corners[0])
            sorted_corners.append(top_corners[1])
        else:
            sorted_corners.append(top_corners[1])
            sorted_corners.append(top_corners[0])

        # sorteaza colturile de jos de la stanga la dreapta
        if bottom_corners[0][0] < bottom_corners[1][0]:
            sorted_corners.append(bottom_corners[0])
            sorted_corners.append(bottom_corners[1])
        else:
            sorted_corners.append(bottom_corners[1])
            sorted_corners.append(bottom_corners[0])

        return sorted_corners

    @staticmethod
    def prepare_image(img):
        """
        transforma o imagine color intr-o imagine binara
        :param img: imaginea de transformat
        :return: imaginea binara
        """
        prepared_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        prepared_img = cv2.blur(prepared_img, (5, 5))
        prepared_img = cv2.adaptiveThreshold(prepared_img, 255,
                                             cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        return prepared_img

    def sort_squares(self, squares):
        """
        sorteaza patratele dintr-un joc de sudoku de sus in jos, de la stanga la dreapta
        :param squares: lista patratelor, reprezentate prin conturul lor
        :return: lista ordonata a patratelor din joc
        """
        simplified_squares = []

        for square in squares:
            # contururile sunt simplificate a.i sa ramana doar cele 4 colturi aproximative
            approx = cv2.approxPolyDP(square, 0.009 * cv2.arcLength(square, True), True)
            approx_squeezed = approx.squeeze()

            # colturile obtinute sunt sortate trigonometric
            approx_squeezed = self.sort_corners(approx_squeezed)
            simplified_squares.append(approx_squeezed)

        # sortam patratele dupa inaltime
        simplified_squares = np.array(simplified_squares)
        simplified_squares = sorted(simplified_squares, key=lambda square: sum(square[:2, 1]))

        # fiecare rand obtinut este sortat de la stanga la dreapta
        top_squares = self.left_sort_squares(simplified_squares[:3])
        middle_squares = self.left_sort_squares(simplified_squares[3:6])
        bottom_squares = self.left_sort_squares(simplified_squares[6:9])

        sorted_squares = top_squares + middle_squares + bottom_squares

        sorted_squares = np.array(sorted_squares)
        return sorted_squares

    def img_transformation(self, img, contour, size_factor=1.):
        """
        schimbam perspectiva pozei a.i. sa avem o vedere de sus in jos al unei bucati din poza
        :param img: poza asupra careia are loc transformarea
        :param contour: conturul regiunii pe care vrem sa o vedem de sus
        :param size_factor: factorul cu care se mareste zona pe care vrem sa o vedem
        :return: imaginea privita de sus a regiunii alese
        """

        approx = cv2.approxPolyDP(contour, 0.009 * cv2.arcLength(contour, True), True)
        approx_squeezed = approx.squeeze()
        approx_squeezed = self.sort_corners(approx_squeezed)

        # marim zona aleasa cu un factor dat
        approx_squeezed = self.upscale_grid(approx_squeezed, size_factor)

        # calculam latimea si inaltimea maxima a conturului
        width = max(self.get_distance(approx_squeezed[0], approx_squeezed[1]),
                    self.get_distance(approx_squeezed[2], approx_squeezed[3]))
        height = max(self.get_distance(approx_squeezed[0], approx_squeezed[3]),
                     self.get_distance(approx_squeezed[1], approx_squeezed[2]))

        # calculam dimensiunea imaginii noi
        new_dimension = np.array([
            [width, 0],
            [0, 0],
            [0, height],
            [width, height]
        ], dtype="float32")

        # transformarea propriu-zisa
        m = cv2.getPerspectiveTransform(np.float32(approx_squeezed), new_dimension)
        warped = cv2.warpPerspective(img, m, (width, height))
        return warped

    def get_grid(self, img):
        """
        returneaza zona in care se afla jocul de sudoku in poza
        :param img: poza data de utilizator
        :return: zona in care se afla sudoku, privita de sus
        """
        binary_img = self.prepare_image(img)

        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_sorted = sorted(contours, key=cv2.contourArea)
        grid = contours_sorted[-1]

        warped = self.img_transformation(img, grid, size_factor=1.05)
        return warped

    def get_squares(self, img_warped):
        """
        gaseste cele 9 patrate mari care alcatuiesc jocul de sudoku
        :param img_warped: imagine cu perspectiva de sus, centrata pe jocul de sudoku
        :return: lista cu imagini cu fiecare patrat, vazut de sus
        """
        binary_img = self.prepare_image(img_warped)

        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        squares = contours[1:10]

        squares = self.sort_squares(squares)
        return squares

    def save_cells(self, img, square, it):
        """
        salveaza intr-un folder toate celule dintr-un patrat
        :param img: imaginea din care sunt decupate celulele
        :param square: coordonatele patratului
        :param it: al catelea patrat este cel curent
        :return: nimic
        """

        # centreaza imaginea pe patratul curent
        warped_square = self.img_transformation(img, square)

        # calculeaza dimensiunea unei celule
        width, height, _ = warped_square.shape
        width = width // 3
        height = height // 3

        # calculeaza unde se afla patratul curent
        square_row = it // 3
        square_column = it % 3

        for i in range(3):
            for j in range(3):
                # decupeaza o celula si calculeaza ce indice are
                cell = warped_square[i * width:(i + 1) * width, j * height:(j + 1) * height, :]
                cell_x = i + square_row * 3
                cell_y = j + square_column * 3

                # salveaza celula in folderul specificat
                path = self.directory_path + str(cell_x) + str(cell_y) + ".png"
                cv2.imwrite(path, cell)

    def run(self):
        """
        ruleaza algoritmul de detectie al celulelor de sudoku din poza
        :return: nimic
        """

        # gaseste jocul de sudoku si centreaza imaginea asupra lui
        warped = self.get_grid(self.image)

        # gaseste patratele mari din jocul de sudoku
        squares = self.get_squares(warped)

        # pentru fiecare patrat gaseste si salveaza celulele sale
        for it, square in enumerate(squares):
            self.save_cells(warped, square, it)


detector = Detector("../Date/Sudoku/sudoku.jpg")
detector.run()
