import itertools
import json
import numpy as np
import copy


class Sudoku:
    N = 9
    grid = None
    possibilites_grid = None
    backtracking_grid = []
    backtracking_possibilites_grid = []
    backtracking_last_position = []
    backtracking_last_value = []

    def __init__(self, given_grid):
        self.grid = given_grid[:]

    def print(self):
        print(self.grid)

    def solve_grid(self):
        while self.check_is_complete(type="complete") is False:
            flag = False
            while self.single_possibility() is True:
                flag = True
            while self.single_hidden() is True:
                flag = True
            while self.double_possibility() is True:
                flag = True
            while self.double_hidden() is True:
                flag = True
            if flag is False:
                self.backtrack()

    def backtrack(self):
        solvable_flag = True
        
        if self.check_is_complete("solvable") is True:
            new_grid = copy.deepcopy(self.grid)
            new_possibilites = copy.deepcopy(self.possibilites_grid)

            self.backtracking_grid.append(new_grid)
            self.backtracking_possibilites_grid.append(new_possibilites)

        else:
            solvable_flag = False
            self.grid = self.backtracking_grid[-1]
            self.possibilites_grid = self.backtracking_possibilites_grid[-1]

            self.backtracking_grid = self.backtracking_grid[:-1]
            self.backtracking_possibilites_grid = self.backtracking_possibilites_grid[:-1]

        mini = 10
        min_pos = [-1, -1]
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == 0 and 1 < len(str(self.possibilites_grid[i][j])) < mini:
                    flag = True

                    if len(self.backtracking_last_position) > 0:
                        last_position = self.backtracking_last_position[-1]
                        last_digit = self.backtracking_last_value
                        if last_position[0] == i and last_position[1] == j:
                            if last_digit == str(self.possibilites_grid[i][j])[-1]:
                                flag = False

                    if flag is True:
                        min_pos = [i, j]
                        mini = len(str(self.possibilites_grid[i][j]))

        i, j = min_pos
        digit = -1
        if len(self.backtracking_last_position) != 0:
            if self.backtracking_last_position[-1][0] == i and self.backtracking_last_position[-1][1] == j:
                it = str(self.possibilites_grid[i][j]).index(self.backtracking_last_value[-1])
                digit = str(self.possibilites_grid[i][j])[it + 1]
            else:
                digit = str(self.possibilites_grid[i][j])[0]
        else:
            digit = str(self.possibilites_grid[i][j])[0]

        if solvable_flag is False:
            self.backtracking_last_position = self.backtracking_last_position[:-1]
            self.backtracking_last_value = self.backtracking_last_value[:-1]

        self.backtracking_last_position.append([i, j])
        self.backtracking_last_value.append(digit)
        self.grid[i][j] = digit
        self.possibilites_grid[i][j] = digit
        self.update_possibilites_grid(i, j, digit)

    def single_possibility(self):
        """
        cauta toate celule goale cu o singura posibilitate
        updateaza matricea de posibilitati la fiecare celula gasita
        :return: True daca a gasit ceva sau False
        """
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == 0 and self.possibilites_grid[i][j] < 10:
                    cell = self.possibilites_grid[i][j]
                    self.grid[i][j] = cell
                    self.update_possibilites_grid(i, j, cell)
                    return True
        return False

    def single_hidden(self):
        """
        cauta daca intr-o zona o valoare este posibila doar intr-o celula
        :return: True daca a gasit ceva sau False
        """
        flag = False
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == 0:
                    if self.check_single_hidden(i, j) is True:
                        flag = True
                        return flag
        return flag

    def check_single_hidden(self, i, j):
        """
        verifica daca conditia de hidden single e indeplinita de celula i*j
        :param i: celula se afla pe linia i
        :param j: celula se afla pe coloana j
        :return: True sau False
        """
        cell = str(self.possibilites_grid[i][j])
        row = self.possibilites_grid[i]
        column = self.possibilites_grid[:, j]
        i_square = i // 3
        j_square = j // 3
        square = self.possibilites_grid[i_square * 3:(i_square + 1) * 3, j_square * 3:(j_square + 1) * 3]

        for digit in cell:
            flag_row = True
            flag_column = True
            flag_square = True

            for k in range(self.N):
                if k != j:
                    if digit in str(row[k]):
                        flag_row = False
                if k != i:
                    if digit in str(column[k]):
                        flag_column = False

            for k in range(3):
                for l in range(3):
                    if k != (i % 3) or l != (j % 3):
                        if digit in str(square[k][l]):
                            flag_square = False

            if flag_row is True or flag_column is True or flag_square is True:
                self.grid[i][j] = digit
                self.possibilites_grid[i][j] = digit
                self.update_possibilites_grid(i, j, digit)
                return True
        return False

    def double_possibility(self):
        """
        verifica daca conditia de double_possibility se intampla pe tabla
        :return: True sau False
        """
        for i in range(self.N):
            row = self.possibilites_grid[i]
            uniques, counts = np.unique(row, return_counts=True)
            for k in range(len(uniques)):
                if 9 < uniques[k] < 100 and counts[k] == 2:
                    j = [it for it, val in enumerate(row) if val == uniques[k]]
                    locations = [[i, j[0]], [i, j[1]]]
                    if self.update_double(locations, uniques[k], "row") is True:
                        return True

            column = self.possibilites_grid[:, i]
            uniques, counts = np.unique(column, return_counts=True)
            for k in range(len(uniques)):
                if 9 < uniques[k] < 100 and counts[k] == 2:
                    j = [it for it, val in enumerate(column) if val == uniques[k]]
                    locations = [[j[0], i], [j[1], i]]
                    if self.update_double(locations, uniques[k], "column") is True:
                        return True

        for i in range(3):
            for j in range(3):
                square = self.possibilites_grid[i * 3:(i + 1) * 3, j * 3:(j + 1) * 3]
                uniques, counts = np.unique(square, return_counts=True)
                for k in range(len(uniques)):
                    if 9 < uniques[k] < 100 and counts[k] == 2:
                        locations = [[i, j]]
                        for i_square in range(3):
                            for j_square in range(3):
                                if square[i_square][j_square] == uniques[k]:
                                    locations.append([i_square, j_square])
                        if self.update_double(locations, uniques[k], "square") is True:
                            return True

        return False

    def update_double(self, locations, double_value, region_type):
        """
        elimina din grup valoarea celor doua celule
        :param locations: indicele celor doua celule identice
        :param double_value: valoarea celulelor identice
        :param region_type: tipul regiunii
        :return: True daca o valoare a fost schimbata False altfel
        """
        flag = False

        if region_type == "row":
            i = locations[0][0]
            row = self.possibilites_grid[i]
            for k in range(self.N):
                if k != locations[0][1] and k != locations[1][1]:
                    for digit in str(double_value):
                        if digit in str(row[k]):
                            flag = True
                            row[k] = str(row[k]).replace(digit, "")

        if region_type == "column":
            j = locations[1][1]
            column = self.possibilites_grid[:, j]
            for k in range(self.N):
                if k != locations[0][0] and k != locations[1][0]:
                    for digit in str(double_value):
                        if digit in str(column[k]):
                            flag = True
                            column[k] = str(column[k]).replace(digit, "")

        if region_type == "square":
            i_square = locations[0][0]
            j_square = locations[0][1]
            square = self.possibilites_grid[i_square * 3:(i_square + 1) * 3, j_square * 3:(j_square + 1) * 3]
            for i in range(3):
                for j in range(3):
                    if [i, j] != locations[1] and [i, j] != locations[2]:
                        for digit in str(double_value):
                            if digit in str(square[i][j]):
                                flag = True
                                square[i][j] = str(square[i][j]).replace(digit, "")

        return flag

    def double_hidden(self):
        """
        verifica daca conditia de double hidden se intampla pe tabla
        :return: True sau False
        """
        for i in range(self.N):
            row = self.possibilites_grid[i]
            for it, cell in enumerate(row):
                if len(str(cell)) > 2:
                    doubles = list(itertools.combinations(str(cell), 2))
                    for double in doubles:
                        for j in range(self.N):
                            if j == it:
                                continue
                            other_cell = str(row[j])
                            if double[0] in other_cell and double[1] in other_cell:
                                flag = True
                                for k in range(self.N):
                                    if k == it or k == j:
                                        continue
                                    if double[0] in str(row[k]) or double[1] in str(row[k]):
                                        flag = False
                                        break
                                if flag is True:
                                    double_value = "".join(double)
                                    self.possibilites_grid[i][it] = double_value
                                    self.possibilites_grid[i][j] = double_value
                                    return True

        for i in range(self.N):
            column = self.possibilites_grid[:, i]
            for it, cell in enumerate(column):
                if len(str(cell)) > 2:
                    doubles = list(itertools.combinations(str(cell), 2))
                    for double in doubles:
                        for j in range(self.N):
                            if j == it:
                                continue
                            other_cell = str(column[j])
                            if double[0] in other_cell and double[1] in other_cell:
                                flag = True
                                for k in range(self.N):
                                    if k == it or k == j:
                                        continue
                                    if double[0] in str(column[k]) or double[1] in str(column[k]):
                                        flag = False
                                        break
                                if flag is True:
                                    double_value = "".join(double)
                                    self.possibilites_grid[it][i] = double_value
                                    self.possibilites_grid[j][i] = double_value
                                    return True

        for i_square in range(3):
            for j_square in range(3):
                square = self.possibilites_grid[i_square * 3:(i_square + 1) * 3, j_square * 3:(j_square + 1) * 3]
                for i in range(3):
                    for j in range(3):
                        cell = square[i][j]
                        if len(str(cell)) > 2:
                            doubles = list(itertools.combinations(str(cell), 2))
                            for double in doubles:
                                for other_cell_i in range(3):
                                    for other_cell_j in range(3):
                                        if i == other_cell_i and j == other_cell_j:
                                            continue
                                        other_cell = str(square[other_cell_i][other_cell_j])
                                        if double[0] in other_cell and double[1] in other_cell:
                                            flag = True
                                            for k_i in range(3):
                                                for k_j in range(3):
                                                    if (k_i == i and k_j == j) or\
                                                            (k_i == other_cell_i and k_j == other_cell_j):
                                                        continue
                                                    if double[0] in str(square[k_i][k_j]) or\
                                                            double[1] in str(square[k_i][k_j]):
                                                        flag = False
                                                        break
                                            if flag is True:
                                                double_value = "".join(double)
                                                self.possibilites_grid[i][j] = double_value
                                                self.possibilites_grid[other_cell_i][other_cell_j] = double_value
                                                return True

        return False

    def check_is_complete(self, type):
        """
        verifica daca un puzzle sudoku este terminat
        :param type: tipul de verificare
        :return: true sau false
        """
        if type == "complete":
            if self.check_grid(type) is True:
                uniques = np.unique(self.grid)
                if uniques[0] != 0:
                    return True
                return False
        elif type == "solvable":
            if self.check_grid(type) is True:
                return True
        return False

    def get_possibilites_grid(self, grid):
        """
        gaseste valorile posibile ale celulelor goale dintr-un puzzle
        :param grid: puzzle sudoku 9*9
        :return: puzzle sudoku in care celule goale au toate valorile posibile
        """
        self.possibilites_grid = copy.deepcopy(grid)
        for i in range(9):
            for j in range(9):
                if self.possibilites_grid[i][j] == 0:
                    self.possibilites_grid[i][j] = self.check_possibilites(i, j)

    def update_possibilites_grid(self, i, j, new_value):
        """
        actualizeaza valorile posibile pentru fiecare celula afectata de
        schimbarea valorii unei alte celule
        :param i: linia celulei schimbate
        :param j: coloana celulei schimbate
        :param new_value: valoarea cu care a fost actualizata celula
        :return: noile valori posibile ale celulei
        """
        row = self.possibilites_grid[i]
        column = self.possibilites_grid[:, j]
        i_square = i // 3
        j_square = j // 3
        square = self.possibilites_grid[i_square * 3:(i_square + 1) * 3, j_square * 3:(j_square + 1) * 3]

        for k in range(9):
            if row[k] > 9:
                if str(new_value) in str(row[k]):
                    row[k] = str(row[k]).replace(str(new_value), "")
            if column[k] > 9:
                if str(new_value) in str(column[k]):
                    column[k] = str(column[k]).replace(str(new_value), "")

        for k in range(3):
            for l in range(3):
                if square[k][l] > 9:
                    if str(new_value) in str(square[k][l]):
                        square[k][l] = str(square[k][l]).replace(str(new_value), "")

    def check_possibilites(self, i, j):
        """
        gaseste toate valorile posibile ale unei celule
        :param i: linia celulei
        :param j: coloana celulei
        :return: valorile posibile ca vector
        """
        possibilites = []
        row = copy.deepcopy(self.grid[i])
        column = copy.deepcopy(self.grid[:, j])
        i_square = i // 3
        j_square = j // 3
        square = copy.deepcopy(self.grid[i_square*3:(i_square+1)*3, j_square*3:(j_square+1)*3])

        for k in range(1, 10):
            flag = True

            # verifica daca noua valoare este posibila pe rand
            row[j] = k
            if self.check_array(row, "complete") is False:
                flag = False

            # verifica daca noua valoare este posibila pe coloana
            column[i] = k
            if self.check_array(column, "complete") is False:
                flag = False

            # verifica daca noua valoare este posibila in patrat
            i_square = i % 3
            j_square = j % 3
            square[i_square][j_square] = k
            if self.check_array(square, "complete") is False:
                flag = False
            if flag is True:
                possibilites.append(k)

        return ''.join(map(str, possibilites))

    def check_grid(self, type):
        """
        verifica ca intreaga tabla de joc sa fie corecta
        :param type: tipul de verificare
        :return: true sau false
        """
        for i in range(self.N):
            if self.check_row(i, type) is False:
                return False
            if self.check_column(i, type) is False:
                return False
        for i in range(3):
            for j in range(3):
                if self.check_square(i, j, type) is False:
                    return False
        return True

    def check_row(self, i, type):
        """
        verifica daca un rand este corect
        :param i: al catelea rand este verificat
        :param type: tipul de verificare
        :return: true sau false
        """
        row = self.grid[i]
        row_possibilities = self.possibilites_grid[i]
        return self.check_array(row, type=type, given_possibilities_array=row_possibilities)

    def check_column(self, i, type):
        """
        verifica daca o coloana este corecta
        :param i: a cata coloana este verificata
        :param type: tipul de verificare
        :return: true sau false
        """
        column = self.grid[:, i]
        column_possibilities = self.possibilites_grid[:, i]
        return self.check_array(column, type=type, given_possibilities_array=column_possibilities)

    def check_square(self, i, j, type):
        """
        verifica daca un patrat este corect
        :param i: pe ce linie este patratul (0-2)
        :param j: pe ce coloana este patratul (0-2)
        :param type: tipul de verificare
        :return: true sau false
        """
        square = self.grid[i*3:(i+1)*3, j*3:(j+1)*3]
        square_possibilities = self.possibilites_grid[i*3:(i+1)*3, j*3:(j+1)*3]
        return self.check_array(square, type=type, given_possibilities_array=square_possibilities)

    @staticmethod
    def check_array(given_array, type, given_possibilities_array=None):
        """
        verifica daca exista duplicate pentru orice numar diferit de zero
        :param given_array: un vector de valori
        :param type: tipul de verificare
        :param given_possibilities_array: un vector de posibilitati
        :return: True sau False
        """
        if type == "complete":
            uniques, counts = np.unique(given_array, return_counts=True)
            if uniques[0] == 0:
                counts = counts[1:]
            if any(count > 1 for count in counts):
                return False
        elif type == "solvable":
            uniques, counts = np.unique(given_possibilities_array, return_counts=True)
            for it in range(len(uniques)):
                if uniques[it] < 10 and counts[it] > 1:
                    return False
        return True


json_file = open('../Date/Json/sudoku_de_rezolvat.json', 'r')
data = json.load(json_file)['Grid']
data = np.array(data, dtype=np.int64).reshape((9, 9))
grid = data

sudoku = Sudoku(grid)
sudoku.get_possibilites_grid(sudoku.grid)
sudoku.solve_grid()

sudoku_json = {
    "Grid":
        sudoku.grid.flatten().tolist()
}

json_solved_path = "../Date/Json/sudoku_rezolvat.json"
with open(json_solved_path, "w") as path:
    json.dump(sudoku_json, path)
