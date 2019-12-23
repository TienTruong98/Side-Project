import Chess.Board_v2 as Board
import Chess.Pieces_v2 as Pieces


class Players:
    def __init__(self, color, pieces=None):
        self.color = color
        self.pieces = pieces
        self.score = 0
        self.history = []
        self.board = Board.Board()
        self.moving_piece = None  # if player click one piece
        self.old_square = None  # if player click then remember the old square
        self.opponent = None


class Human(Players):
    def __init__(self, color):
        Players.__init__(self, color, [])

    def click(self, pos: tuple) -> Pieces:
        # if player click a piece then remove that piece on the board
        # and player remember the selected piece and the old square
        # return the moving piece
        square = self.board.findSquare(pos)
        if square.occupant is None or square.occupant.color != self.color:
            return
        self.moving_piece = square.occupant
        self.old_square = square
        square.occupant = None
        return self.moving_piece

    def drop(self, pos):
        has_move = False  # check if the move is legal
        next_square = self.board.findSquare(pos)
        # check if the player click on the old square again
        if next_square == self.old_square:
            self.old_square.occupant = self.moving_piece
            self.old_square = None
            self.moving_piece = None
            return has_move

        else:
            has_move = self.eatPieces(next_square)
            return has_move

    def eatPieces(self, next_square):
        has_move = True
        # check if the next square is not the same color
        if next_square.occupant not in self.pieces:
            possible_move = self.getPossibleMove(self.old_square, self.color)
            for x in possible_move:
                print(x, end=' ')
            print()
            # check if the next square is legal move
            if next_square in possible_move:
                next_square.occupant = self.moving_piece
                self.moving_piece.pos = next_square.pos
                has_move = True
            else:
                has_move = False
        else:
            has_move = False
        if not has_move:
            # return the piece to old square
            self.old_square.occupant = self.moving_piece

        self.old_square = None
        self.moving_piece = None
        return has_move

    def getPossibleMove(self, square, turn):
        def KnightMove():
            for pos in occupant.getMove(L_shape=True):
                square = self.board.findSquare(pos)
                if square.occupant is None:
                    possible_moves.append(square)
                elif square.occupant.color != turn:
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
                        if square.occupant.color == turn:
                            is_block = True
                        else:
                            possible_eats.append(square)
                            is_block = True

            def piecesMoveCondition(moves):
                is_block = False
                for pos in moves:
                    if is_block:
                        break
                    square = self.board.findSquare(pos)
                    if square.occupant is None:
                        possible_moves.append(square)
                    else:
                        if square.occupant.color == turn:
                            is_block = True
                        else:
                            possible_eats.append(square)
                            is_block = True

            # get possible square in piece's directions
            for direction, step in getattr(occupant, action).items():
                f = getattr(occupant, direction)
                range_x, range_y = f(step)
                moves = occupant.getMove(range_x, range_y)
                # choose suitable square
                choose = eval(condition)
                choose(moves)

        occupant: Pieces = self.moving_piece
        possible_moves = []
        possible_eats = []
        if type(occupant) is Pieces.Knight:
            KnightMove()
        elif type(occupant) is Pieces.Pawn:
            getMove('move', 'pawnMoveCondition')
            getMove('eat', 'pawnEatCondition')
        else:
            getMove('move', 'piecesMoveCondition')
        possible_moves.extend(possible_eats)
        return possible_moves


class Bot(Players):
    def __init__(self, color):
        Players.__init__(self, color, [])
