import copy
import pygame
import time
import os

pygame.init()

# 格子
space = 50  # 四周留下的边距
cell_size = 50  # 每个格子大小
row_num, col_num = 7, 5  # 棋盘长宽
grid_size = cell_size * (row_num - 1) + space * 2  # 棋盘的大小
bt_w, bt_h = 80, 45

screen_caption = pygame.display.set_caption('Tiger & Dogs')  # 窗口标题
screen = pygame.display.set_mode((grid_size, grid_size))  # 设置窗口长宽

point_d = -1  # 选取棋子
point_u = -1  # 释放棋子
click_arr = []  # 棋子移动


# 棋盘 采用无向图作为数据结构
class ChessBoardPoint:
    # (x,y) represent position ; chess represent what is on the point
    # chess: 0 -> empty  1 -> dog  2 -> tiger  -1 -> does not exist
    def __init__(self, x: int = 0, y: int = 0, chess: int = 0):
        self.x = x
        self.y = y
        self.chess = chess

    def show_point(self):
        # print("x = ", self.x, end=" ")
        # print("y = ", self.y, end=" ")
        # print("The point is: ", self.chess)
        return "x =  %d y =  %d The point is:  %d" % (self.x, self.y, self.chess)

    def set_point(self, info: tuple):
        self.x, self.y, self.chess = info[0], info[1], info[2]


class ChessBoard:
    def __init__(self, total_row: int = 7, total_line: int = 5):
        self.board = {}
        self.row = total_row
        self.line = total_line
        self.path = None
        self.step = []
        self.dogs = []
        self.tiger = []
        self.flag = True  # mark who's turn [True for dog, False for tiger]
        self.restart = []
        # generate chess board
        for row in range(self.row):
            for line in range(self.line):
                # point's position(x,y) can name point as well
                point_name = row * self.line + line
                self.board[point_name] = ChessBoardPoint(line, row, 0)

    def print(self):
        for key in self.board.keys():
            print(key, " -> ", self.board[key].show_point())

    def show_chess_board(self):
        self.tiger = []
        self.dogs = []
        for key in self.board.keys():
            if self.board[key].chess != -1:
                # information : (x, y, chess)
                # print((self.board[key].x, self.board[key].y, self.board[key].chess), end=" ")
                # information : (chess) only
                if self.board[key].chess == 1:
                    self.dogs.append((self.board[key].x, self.board[key].y))
                if self.board[key].chess == 2:
                    self.tiger.append((self.board[key].x, self.board[key].y))
                print(self.board[key].chess, end=" ")
            else:
                # information : (x, y, chess)
                # print("         ", end=" ")
                # information : (chess) only
                print(" ", end=" ")
            if (key - 4) % 5 == 0:
                print()
        # print(self.dogs, self.tiger)
        print("-------------------------------")

    def set_path(self):
        self.path = creat_path_graph(self)

    def set_chess_board(self):
        new_game = {
            # empty point
            (0, 0, -1), (1, 0, -1), (3, 0, -1), (4, 0, -1), (0, 1, -1), (4, 1, -1),
            # dogs
            (0, 2, 1), (1, 2, 1), (2, 2, 1), (3, 2, 1), (4, 2, 1),
            (0, 3, 1), (0, 4, 1), (0, 5, 1),
            (4, 3, 1), (4, 4, 1), (4, 5, 1),
            (0, 6, 1), (1, 6, 1), (2, 6, 1), (3, 6, 1), (4, 6, 1),
            # tiger
            (2, 4, 2)
        }
        for info in new_game:
            self.board[info[1] * self.line + info[0]].chess = info[2]

    def swap(self, point1: int, point2: int):
        # point1 & point2 is the point's name -> key in the dictionary
        # first : check the point is empty or not
        if (self.board[point1].chess != 0) & (self.board[point2].chess == 0):
            # check path
            if point2 in self.path[point1]:
                self.board[point1].chess, self.board[point2].chess = self.board[point2].chess, self.board[point1].chess
            else:
                # print("Path does not exist.", self.path[point1])
                print("Path does not exist.")
                return False
        else:
            print("Cannot execute the swap.")
            print("The point is empty or target point is not empty.")
            return False
        # print chessboard
        self.show_chess_board()
        return True

    def eat(self, tiger: int, turn: bool):
        if not turn:
            surr = []
            # surroundings = self.path[tiger]  # 引用 导致删除原路径
            for dire in self.path[tiger]:
                surr.append(dire)
            # print(surr)
            while len(surr) > 0:
                if (surr[0] == -1) or (surr[-1] == -1):
                    print("Path does not exist.")
                    del surr[0], surr[-1]
                else:
                    if self.board[surr[0]].chess == self.board[surr[-1]].chess == 1:
                        print("Eat", surr[0], surr[-1])
                        self.board[surr[0]].chess, self.board[surr[-1]].chess = 0, 0
                        chess_board.show_chess_board()
                        del surr[0], surr[-1]
                    else:
                        # print("Cannot eat", surr[0], surr[-1])
                        del surr[0], surr[-1]

    def save(self):
        temp = copy.deepcopy({
            "board": copy.deepcopy(self.board),
            "tiger": copy.deepcopy(self.tiger),
            "dogs": copy.deepcopy(self.dogs),
            "flag": copy.deepcopy(self.flag),
        })
        self.step.append(temp)
        # for item in self.step:
        #    print(item["tiger"])
        # Here address is saved not the object
        # so when chessboard changed all saved things change
        # and all of them are the same
        # so use deepcopy
        # test:
        # for i in range(len(self.step)):
        #     print("The %d-th step is:" % i)
        #     self.board = self.step[i]
        #     self.show_chess_board()

    def win(self, f: bool):
        dogs_win = True
        tiger_wins = True
        # dog's turn
        if f & (len(user_input) >= 2):
            for point in self.path[user_input[-2][1]]:
                # tiger can move -> game continues
                # print("Checking point", user_input[-2][1], point)
                if point != -1:
                    if self.board[point].chess == 0:
                        print("Game continues!")
                        return bool(1 - dogs_win)
            # tiger cannot move -> dogs win
            # print("Tiger cannot move! Dogs win!", self.path[user_input[-2][1]])
            os.system("cls")
            print("Tiger cannot move! Dogs win!")
            end_game()
            return dogs_win
        # tiger's turn
        if not f:
            # tiger in trap -> dogs win
            if self.board[2].chess == 2:
                os.system("cls")
                print("Tiger in trap! Dogs win!")
                end_game()
                return self.board[2].chess == 2
            # total dogs number <= 2 -> tiger wins
            sum_all = 0
            for point in self.board.values():
                sum_all += point.chess
            if sum_all <= -2:
                os.system("cls")
                print("Tiger wins!")
                end_game()
                return tiger_wins

    def regret_init(self):
        self.step.append({
            "tiger": [(2, 4)],
            "dogs": [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (0, 3), (0, 4), (0, 5), (4, 3), (4, 4), (4, 5), (0, 6),
                     (1, 6),
                     (2, 6), (3, 6), (4, 6)],
            "board": copy.deepcopy(chess_board.board),
            "flag": True,
        })


# check who's in turn
def check_turn(f: bool):
    if f:
        return f
    else:
        print("It's not your turn.")
        return


# for creating path graph
def check_odd(num):
    return num % 2 == 0


# for creating path graph
def check_boarder(x: int, y: int, dire: int):
    if dire == -6:
        x, y = x - 1, y - 1
    elif dire == -5:
        x, y = x, y - 1
    elif dire == -4:
        x, y = x + 1, y - 1
    elif dire == -1:
        x, y = x - 1, y
    elif dire == 1:
        x, y = x + 1, y
    elif dire == 4:
        x, y = x - 1, y + 1
    elif dire == 5:
        x, y = x, y + 1
    elif dire == 6:
        x, y = x + 1, y + 1
    else:
        return False
    return (0 <= x <= 4) & (2 <= y <= 6)


# creat path graph
def creat_path_graph(board: ChessBoard):
    path = {
        2: [-1, -1, -1, -1, -1, 6, 7, 8],
        6: [-1, -1, 2, -1, 7, -1, -1, 12],
        7: [-1, 2, -1, 6, 8, -1, 12, -1],
        8: [2, -1, -1, 7, -1, 12, -1, -1],
    }
    # for point in range(10, 35):
    for point in range(10, 35):
        path[point] = []
        # use odd and even number
        # to distinguish 'directions' list
        # which contents legal numbers representing the specific direction
        if check_odd(point):
            directions = [-6, -5, -4, -1, 1, 4, 5, 6]
        else:
            directions = [-5, -1, 1, 5]
        # check point's all legal directions
        for direction in directions:
            target = point + direction
            # make sure no KeyError in board.board[target]
            if 10 <= target <= 34:
                # check if out of boarder
                if check_boarder(board.board[point].x, board.board[point].y, direction):
                    path[point].append(target)
                else:
                    path[point].append(-1)
            else:
                path[point].append(-1)
    # set upper area
    path[12] = [6, 7, 8, 11, 13, 16, 17, 18]
    # for key in path.keys():
    #     print(key, ": ", path[key])
    return path


def get_point() -> int:
    x_raw, y_raw = pygame.mouse.get_pos()  # 获取鼠标位置
    xi = int(round((x_raw - space) * 1.0 / cell_size))  # 获取到x方向上取整的序号
    yi = int(round((y_raw - space) * 1.0 / cell_size))  # 获取到y方向上取整的序号
    if 0 <= xi < col_num and 0 <= yi < row_num:
        return xi + col_num * yi
    # Start
    elif 300 < x_raw < 380 and 100 < y_raw < 145:
        return 222
    # Back
    elif 300 < x_raw < 380 and 200 < y_raw < 245:
        return 333
    # Quit
    elif 300 < x_raw < 380 and 300 < y_raw < 345:
        return 555
    # Invalid area
    else:
        return 111


def update_chessboard(cs: ChessBoard):
    screen.fill((0, 0, 0))  # 将界面设置为黑色
    # 画 5*7 的大棋盘
    for r in range(0, cell_size * col_num, cell_size):
        pygame.draw.line(screen, (150, 150, 150), (r + space, 0 + space),
                         (r + space, cell_size * (row_num - 1) + space), 1)
    for c in range(0, cell_size * row_num, cell_size):
        pygame.draw.line(screen, (150, 150, 150), (0 + space, c + space),
                         (cell_size * (col_num - 1) + space, c + space), 1)
    # or: 这些画出来的作为定点  然后贴图覆盖美化和完善地图细节（斜线、陷阱）
    # 画斜线
    st_add = [(0, 4), (0, 2), (1, 1), (3, 1), (4, 2), (4, 4), (2, 0), (2, 0)]
    en_add = [(2, 6), (4, 6), (4, 4), (0, 4), (0, 6), (2, 6), (3, 1), (1, 1)]
    for i in range(0, len(st_add)):
        pygame.draw.line(screen, (150, 150, 150), (st_add[i][0] * cell_size + space, st_add[i][1] * cell_size + space),
                         (en_add[i][0] * cell_size + space, en_add[i][1] * cell_size + space), 1)

    # 删去不需要的线段(描黑罢了)

    st_del = [(0, 0), (0, 0), (1, 0), (3, 0), (4, 0), (0, 1), (3, 1)]
    en_del = [(4, 0), (0, 2), (1, 2), (3, 2), (4, 2), (1, 1), (4, 1)]
    for i in range(0, len(st_del)):
        pygame.draw.line(screen, (0, 0, 0), (st_del[i][0] * cell_size + space, st_del[i][1] * cell_size + space),
                         (en_del[i][0] * cell_size + space, en_del[i][1] * cell_size + space), 1)

    # 根据返回的新棋盘数组更新棋盘
    # 画狗
    for i in range(0, len(cs.dogs)):
        pygame.draw.circle(screen, (255, 0, 0), (cs.dogs[i][0] * cell_size + space, cs.dogs[i][1] * cell_size + space),
                           5, 5)
    # 画老虎
    pygame.draw.circle(screen, (0, 255, 0), (cs.tiger[0][0] * cell_size + space, cs.tiger[0][1] * cell_size + space), 5,
                       5)

    # 画按钮
    st_x, st_y = space + col_num * cell_size, space + cell_size
    re_x, re_y = space + col_num * cell_size, 3 * space + cell_size
    q_x, q_y = space + col_num * cell_size, 5 * space + cell_size
    pygame.draw.rect(screen, (150, 150, 150), (st_x - 1, st_y - 1, bt_w + 2, bt_h + 2), 1)
    pygame.draw.rect(screen, (150, 150, 150), (re_x - 1, re_y - 1, bt_w + 2, bt_h + 2), 1)
    pygame.draw.rect(screen, (150, 150, 150), (q_x - 1, q_y - 1, bt_w + 2, bt_h + 2), 1)
    st_image = pygame.image.load("start.png")
    re_image = pygame.image.load("regret.png")
    q_image = pygame.image.load("quit.png")
    st_img = pygame.transform.smoothscale(st_image, (bt_w, bt_h))
    re_img = pygame.transform.smoothscale(re_image, (bt_w, bt_h))
    q_img = pygame.transform.smoothscale(q_image, (bt_w, bt_h))
    screen.blit(st_img, (st_x, st_y))
    screen.blit(re_img, (re_x, re_y))
    screen.blit(q_img, (q_x, q_y))


def end_game():
    print("You can restart the game or continue playing with chess board for fun!\n")
    print("Thanks for playing with me!\n")
    print("Please give me star if you can! Thanks!")
    print("Here's the link to star. https://github.com/Mr-Porridge/Tiger-Dogs")
    print("Thanks for playing!")
    print("Here the thanks from Xiao Qi! http://47.110.134.247/thanks.gif")


# Preparations
chess_board = ChessBoard()  # create new chess board
chess_board.set_chess_board()  # set chess to new-game-position
chess_board.set_path()  # set path --- creat path graph
chess_board.show_chess_board()  # show chess board
chess_board.regret_init()  # init or re-init 'take back move'
user_input = []  # init user_input
regret_cnt = 0

# for restart
game_restart = copy.deepcopy(chess_board)

while True:
    # 事件监听
    for event in pygame.event.get():
        # 退出监听
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        # 鼠标监听
        if event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标落下
            click_arr.append(get_point())
            # print(click_arr)

        if event.type == pygame.MOUSEBUTTONUP:  # 鼠标弹起
            click_arr.append(get_point())
            # print(click_arr)
            if click_arr[-2] == 111 or click_arr[-1] == 111:
                break
            elif click_arr[-2] == 222 and click_arr[-1] == 222:
                os.system("cls")
                print("Start!")
                chess_board = copy.deepcopy(game_restart)
                chess_board.show_chess_board()
                break
            elif click_arr[-2] == 333 and click_arr[-1] == 333:
                # if click_arr[-3] == 333 and click_arr[-4] == 333:
                if click_arr[-3] is None:
                    break
                else:
                    print("Back to last move!")
                    try:
                        chess_board.board = chess_board.step[-2 - regret_cnt]["board"]
                        chess_board.flag = bool(1 - chess_board.flag)
                        chess_board.tiger = chess_board.step[-2 - regret_cnt]["tiger"]
                        chess_board.dogs = chess_board.step[-2 - regret_cnt]["dogs"]
                        regret_cnt += 1
                        update_chessboard(chess_board)
                        print(chess_board.flag)

                    except IndexError as err:
                        print("This is the last move. Cannot take back more.")
                # chess_board.show_chess_board()
                break
            elif click_arr[-2] == 555 and click_arr[-1] == 555:
                os.system("cls")
                print("Thanks for playing with me!")
                time.sleep(1)
                print("Bye!")
                time.sleep(2)
                exit(0)
            elif click_arr[-2] in [0, 1, 3, 4, 5, 9] or click_arr[-1] in [0, 1, 3, 4, 5, 9]:
                break
            else:
                # check flag
                # if (chess_board.board[user_input[0]].chess - flag == 2 or 0
                # 2 for tiger 0 for dogs
                # 2-1 == 1-0 == 1 turn's error
                if regret_cnt != 0:
                    del chess_board.step[-2 - regret_cnt:]
                    regret_cnt = 0
                    chess_board.save()
                user_input.append((click_arr[-2], click_arr[-1]))
                if chess_board.board[user_input[-1][0]].chess - chess_board.flag != 1:
                    print(user_input[-1])
                    if chess_board.swap(user_input[-1][0], user_input[-1][1]):
                        chess_board.eat(user_input[-1][1], chess_board.flag)
                        chess_board.win(chess_board.flag)
                        chess_board.save()
                        chess_board.flag = bool(1 - chess_board.flag)
                else:
                    print("Turn's error.")
                    # print("Please click valid area.")

    update_chessboard(chess_board)
    pygame.display.update()  # 必须调用update才能看到绘图显示
