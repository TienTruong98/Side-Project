import Chess.Board as Board
import Chess.Pieces as Pieces
import Chess.Player as Player


class Game:
    def __init__(self):
        self.board = Board.Board()
        self.player1 = Player.Player('black')
        self.player2 = Player.Player('white')
        self.turn = 'black'
        self.player_moving = False

    def setUp(self):
        colors = {'white': [1, 2], 'black': [8, 7]}
        for color, rows in colors.items():
            self.board.setOccupant('A', rows[0], Pieces.Rook(color, 'A', rows[0]))
            self.board.setOccupant('B', rows[0], Pieces.Knight(color, 'B', rows[0]))
            self.board.setOccupant('C', rows[0], Pieces.Bishop(color, 'C', rows[0]))
            self.board.setOccupant('D', rows[0], Pieces.King(color, 'D', rows[0]))
            self.board.setOccupant('E', rows[0], Pieces.Queen(color, 'E', rows[0]))
            self.board.setOccupant('F', rows[0], Pieces.Bishop(color, 'F', rows[0]))
            self.board.setOccupant('G', rows[0], Pieces.Knight(color, 'G', rows[0]))
            self.board.setOccupant('H', rows[0], Pieces.Rook(color, 'H', rows[0]))
            for x in self.board.X_axis:
                self.board.setOccupant(x, rows[1], Pieces.Pawn(color, x, rows[0]))

    def change_turn(self):
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

    def select(self, pos):
        selected_square = self.board.getSquare(pos)
        if selected_square is not None:
            # DROP
            # if the player is moving and press mouse then move the selected piece to new square
            if self.player_moving:
                old_square = self.board.findSelectedSqure()
                old_square.being_clicked = False

                # check if the player select again
                if old_square != selected_square:
                    selected_square.occupant = old_square.occupant
                    selected_square.occupant.setPosition((selected_square.x, selected_square.y))
                    old_square.occupant = None
                    self.change_turn()
                self.player_moving = False
            else:
                # CLICK
                # if the player is not moving and press the mouse then mark that the square is being move
                if selected_square.occupant is not None:
                    # only move pieces that has same colors
                    if selected_square.occupant.color == self.turn:
                        selected_square.being_clicked = True
                        self.player_moving = True


if __name__ == '__main__':
    game = Game()
    game.setUp()
    print(game.board)
