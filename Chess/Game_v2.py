import Chess.Board_v2 as Board
import Chess.Player_v2 as Player
import Chess.Pieces_v2 as Pieces
import pygame


class Game:
    def __init__(self, size, player={'black': 'human', 'white': 'human'}):
        self.board = Board.Board(size)
        self.player1 = Player.Human('black') if player['black'] == 'human' else Player.Bot('black')
        self.player2 = Player.Human('white') if player['white'] == 'human' else Player.Bot('white')
        self.turn = 'player1'
        self.player_moving = False
        self.moving_piece = None
        self.status = True
        self.winner = None

    def setUp(self):
        colors = {'white': [1, 2], 'black': [8, 7]}
        # give player the pieces
        for color, rows in colors.items():
            player = self.player1 if color == 'black' else self.player2
            player.pieces.append(Pieces.Rook(color, (1, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.Knight(color, (2, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.Bishop(color, (3, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.King(color, (4, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.Queen(color, (5, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.Bishop(color, (6, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.Knight(color, (7, rows[0]), self.board.square_size))
            player.pieces.append(Pieces.Rook(color, (8, rows[0]), self.board.square_size))

            for x in range(1, 9):
                player.pieces.append(Pieces.Pawn(color, (x, rows[1]), self.board.square_size))
        # setup board
        for name in ['player1', 'player2']:
            player = getattr(self, name)
            for piece in player.pieces:
                pos = piece.pos
                self.board.setOccupant(pos, piece)

        # give the player sight on the board
        self.player1.board = self.board
        self.player2.board = self.board
        # give the player sight on the opponent
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

    def clickDetection(self, screen_pos):
        pos = self.board.getChessPos(screen_pos)
        # check if pos is in chess square
        if pos is None:
            return
        player = getattr(self, self.turn)
        # check if player select right color
        # check if it is human turn
        if type(player) is Player.Human:
            if self.player_moving:
                has_moved = player.drop(pos)
                self.moving_piece = None
                self.player_moving = False
                if has_moved:
                    self.changeTurn()
            else:
                self.moving_piece = player.click(pos)
                if self.moving_piece:
                    self.player_moving = True

    def changeTurn(self):
        self.turn = 'player2' if self.turn == 'player1' else 'player1'


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_mode((0, 0))
    game = Game(600)
    game.setUp()
    print(game.board)
