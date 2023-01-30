import copy

import numpy as np
import sys

row, col = 6, 3  # board size



class CANTRIS():

    def __init__(self):

        self.gameover = False
        self.board = np.zeros([row, col], dtype=int)
        self.stable = True  # False:need to clean
        self.step = 0  # total turns , start from 0
        self.turn = -1
        self.mypoints = 0
        self.oppopoints = 0
        self.board = np.loadtxt("board.txt", dtype=int)
        self.board = np.array(self.board)
        self.depth = max(row, col)

    def checkstable(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[0]) - 2):
                if abs(self.board[r][c]) == abs(self.board[r][c + 1]) == abs(self.board[r][c + 2]) != 0:
                    self.stable = False
                    return self.stable
        self.stable = True
        return self.stable

    def drop(self):  # drop the tile
        for c in range(col):
            if self.board[:, c].sum() != 0:
                k = -len(self.board[:, c][self.board[:, c] > 0])
                self.board[k:, c] = self.board[:, c][self.board[:, c] > 0]
                self.board[:k, c] = 0

    def checkgameover(self):  # any of last row == 0
        self.gameover = np.any(self.board[-1] == 0)
        return self.gameover

    def clean(self):  # clean the tile , return points
        unstable = 1
        points = 0
        while unstable:
            unstable = 0
            for i in range(row):
                for j in range(col - 2):
                    if abs(self.board[i][j]) == abs(self.board[i][j + 1]) == abs(self.board[i][j + 2]) != 0:
                        self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = -abs(self.board[i][j])
                        unstable = 1
            points -= self.board[self.board < 0].sum()
            self.board[self.board < 0] = 0
            self.drop()
        self.checkgameover()
        return points

    # functions what I add: minmax, possible_moves, next_state

    def possible_moves(self, board):
        moves = []
        for i, value in np.ndenumerate(board):
            if value > 0:
                moves.append(i)
        return moves

    # should simulate new state
    def next_state(self, board, move, mypts, opppts, player, curr):
        new_board = copy.deepcopy(board)
        x = move[0]
        y = move[1]
        value = board[x][y]
        new_board[1:x + 1, y] = new_board[0:x, y]
        new_board[0][y] = 0

        # clear
        unstable = 1
        pts=0
        while unstable:
            unstable = 0
            for i in range(row):
                for j in range(col - 2):
                    if abs(new_board[i][j]) == abs(new_board[i][j + 1]) == abs(new_board[i][j + 2]) != 0:
                        new_board[i][j] = new_board[i][j + 1] = new_board[i][j + 2] = -abs(new_board[i][j])
                        unstable = 1
            # pts -= new_board[new_board < 0].sum()
            if curr == player:
                pts -= new_board[new_board < 0].sum()
                mypts = pts + mypts + value
            else:
                pts -= new_board[new_board < 0].sum()
                opppts = pts + opppts + value
            # print("---------> pts=", pts, "mypts=", mypts, "opppts=", opppts)
            new_board[new_board < 0] = 0
            # drop
            for c in range(col):
                if new_board[:, c].sum() != 0:
                    k = -len(new_board[:, c][new_board[:, c] > 0])
                    new_board[k:, c] = new_board[:, c][new_board[:, c] > 0]
                    new_board[:k, c] = 0
        return (new_board, mypts, opppts)

    def make_decision(self):
        if self.turn == 1:
            opp = 0
        else:
            opp = 1
        board = copy.deepcopy(self.board)
        score, point = _minmax(game=self, board=board, player=self.turn, opp=opp, curr=self.turn, alpha=-float("inf"),
                               beta=float("inf"), depth=self.depth, mypts=copy.deepcopy(self.mypoints),
                               opppts=copy.deepcopy(self.oppopoints))
        x = point[0]
        y = point[1]
        return [x, y]

    def rand_select(self):
        p = 0
        while not (p):
            x = np.random.randint(row)
            y = np.random.randint(col)
            p = self.board[x][y]
        return [x, y]

    def make_move(self, x, y):
        pts = self.board[x][y]
        self.board[1:x + 1, y] = self.board[0:x, y]
        self.board[0][y] = 0

        if self.checkgameover():
            return pts

        pts += self.clean()
        return pts

    def start(self):
        print("Game start!")
        print('――――――――――――――――――')
        self.show_board()
        self.turn = int(input("Set the player's order(0:first, 1:second): "))

        # start playing
        while not self.gameover:
            print('Turn:', self.step)
            if (self.step % 2) == self.turn:
                print('It\'s your turn')
                x, y = self.make_decision()
                print(f"Your move is {x},{y}.")
                # [x,y] = [int(x) for x in input("Enter the move : ").split()]
                assert (0 <= x and x <= row - 1 and 0 <= y and y <= col - 1)
                assert (self.board[x][y] > 0)
                pts = self.make_move(x, y)
                self.mypoints += pts
                print(f'You get {pts} points')
                self.show_board()

            else:
                print('It\'s opponent\'s turn')
                # x,y = self.rand_select() # can use this while testing ,close it when you submit
                [x, y] = [int(x) for x in input("Enter the move : ").split()]  # open it when you submit
                assert (0 <= x and x <= row - 1 and 0 <= y and y <= col - 1)
                assert (self.board[x][y] > 0)
                print(f"Your opponent move is {x},{y}.")
                pts = self.make_move(x, y)
                self.oppopoints += pts
                print(f'Your opponent\'s get {pts} points')
                self.show_board()

            self.step += 1

        # game over
        if self.mypoints > self.oppopoints:
            print('You win!')
            return 1
        elif self.mypoints < self.oppopoints:
            print('You lose!')
            return -1
        else:
            print('Tie!')
            return 0

    def show_board(self):
        print('my points:', self.mypoints)
        print('opponent\'s points:', self.oppopoints)
        print('The board is :')
        print(self.board)
        print('――――――――――――――――――')


def _minmax(game, board, player, opp, curr, alpha, beta, depth, mypts, opppts):
    if game.checkgameover() or depth <= 0:
        score = mypts - opppts
        return (score, None)

    moves = game.possible_moves(board=board)  # return all possible moves
    move_to_return = None
    for move in moves:
        ns, sim_mypts, sim_opppts = game.next_state(board, move, mypts, opppts, player, curr)

        score, position = _minmax(game=game, board=ns, player=player, opp=opp, curr=opp if curr == player else player,
                                  alpha=alpha, beta=beta, depth=depth - 1, mypts=sim_mypts, opppts=sim_opppts)

        # alpha beta pruning
        if curr == player:
            if score > alpha:
                alpha = score
                move_to_return = move
            if alpha >= beta:
                break
        else:
            if score < beta:
                beta = score
            if alpha >= beta:
                break
    # max level or min level
    if curr == player:
        return (alpha, move_to_return)
    else:
        return (beta, None)

if __name__ == '__main__':
    game = CANTRIS()
    game.start()
