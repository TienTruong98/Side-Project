import Chess.Board_v2 as Board
import Chess.Pieces_v2 as Pieces


class Players:
    def __init__(self, color, pieces=None):
        self.color = color
        self.pieces = pieces
        self.score = 0
        self.board = Board.Board()
        self.old_square = None  # if player click then remember the old square
        self.moving_piece = None  # if player is moving a piece
        self.opponent = None

    def getPossibleMove(self):
        def KnightMove():
            for pos in occupant.getMove(L_shape=True):
                # get all possible L_shape Move
                square = self.board.findSquare(pos)
                if square.occupant is None:
                    possible_moves.append(square)
                elif square.occupant not in self.pieces:
                    possible_eats.append(square)
        def getMove(action, condition):
            def pawnMoveCondition(moves):
                is_block = False
                for pos in moves:
                    if is_block:
                        break
                    square = self.board.findSquare(pos)
                    if square.occupant is None:
                        possible_moves.append(square)
                    else:
                        is_block = True

            def pawnEatCondition(moves):
                is_block = False
                for pos in moves:
                    if is_block:
                        break
                    square = self.board.findSquare(pos)
                    if square.occupant is None:
                        is_block = True
                    else:
                        if square.occupant in self.pieces:
                            is_block = True
                        else:
                            possible_eats.append(square)
                            is_block = True

            def piecesMoveCondition(moves):
                is_block = False  # check if that direction is blocked by a friendly piece
                for pos in moves:
                    if is_block:
                        break
                    square = self.board.findSquare(pos)
                    if square.occupant is None:
                        possible_moves.append(square)
                    else:
                        if square.occupant in self.pieces:
                            is_block = True
                        else:
                            possible_eats.append(square)
                            is_block = True

            # get possible square in piece's movement
            for direction, step in getattr(occupant, action).items():
                moves = occupant.getMove(direction, step)  # get possible move to the 'direction'
                # choose suitable square based on their movement condition
                choose = eval(condition)
                choose(moves)

        occupant: Pieces = self.moving_piece
        possible_moves = []  # posible move
        possible_eats = []  # possible opponet pieces to eat
        if type(occupant) is Pieces.Knight:
            KnightMove()
        elif type(occupant) is Pieces.Pawn:
            getMove('move', 'pawnMoveCondition')
            getMove('eat', 'pawnEatCondition')
        else:
            getMove('move', 'piecesMoveCondition')
        possible_moves.extend(possible_eats)
        return possible_moves

    def removePiece(self, piece):
        for index, p in enumerate(self.pieces):
            if p == piece:
                self.pieces.pop(index)
                return
class Human(Players):
    def __init__(self, color):
        Players.__init__(self, color, [])

    def click(self, pos: tuple) -> Pieces:
        # if player click a piece then remove that piece on the board
        # and player remember the selected piece and the old square
        # return the moving piece
        square = self.board.findSquare(pos)
        if square.occupant is None or square.occupant not in self.pieces:
            return None
        self.moving_piece = square.occupant
        self.old_square = square
        square.occupant = None
        return self.moving_piece

    def drop(self, pos):
        # decide if the pos is legal
        # true: return the old square and the new square
        # false: return the old square
        next_square = self.board.findSquare(pos)
        # check if the player click on the old square again
        if next_square == self.old_square:
            self.old_square = None
            return next_square, next_square
        else:
            # check if the next square is not the same color
            if next_square.occupant not in self.pieces:
                possible_move = self.getPossibleMove()
                # check if the next square is legal move
                if next_square in possible_move:
                    return self.old_square, next_square
            return self.old_square, self.old_square
import random

class Bot(Players):
    def __init__(self, color):
        Players.__init__(self, color, [])
    def chooseMove(self):
        possible_move = []
        while len(possible_move)==0:
            self.moving_piece = random.choice(self.pieces)
            possible_move = self.getPossibleMove()
        move = random.choice(possible_move)
        old_square = self.board.findSquare(self.moving_piece.pos)
        new_square = move
        self.moving_piece = None
        return old_square, new_square

