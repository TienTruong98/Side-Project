import pygame
import Chess.Game_v2 as Game
import Chess.Board_v2 as Board
import Chess.Player_v2 as Player


def endGame():
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(f'{game.winner} win!!!!!', True, (255, 255, 255), (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (600 // 2, 600 // 2)
    screen.blit(text, textRect)


def drawBoard(board: Board.Board, board_pos: tuple):
    screen.blit(board.img, board_pos)
    for square in board.squares:
        if square.occupant is not None:
            x, y = square.left_up_corner
            screen.blit(square.occupant.img, (x, y))


def botMove():
    player = getattr(game, game.turn)
    if type(player) is Player.Bot:
        old, new = player.chooseMove()
        print(old, new)
        game.moving_piece = old.occupant
        game.checkPawn()
        game.writeHistory(old, new)
        old.occupant = None
        game.changeTurn()
        drawBoard(game.board, (0, 0))
        screen.blit(game.moving_piece.img, new.left_up_corner)
        new.occupant = game.moving_piece
        game.moving_piece.pos = new.pos
        game.moving_piece = None






if __name__ == '__main__':
    pygame.init()

    height = 600
    width = 600
    board_size = 600

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Chess')

    game = Game.Game(board_size, player={'black': 'bot', 'white': 'human'})
    game.setUp()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.status:
                    screen_pos = pygame.mouse.get_pos()
                    game.clickDetection(screen_pos)
        screen.fill((0, 0, 0))
        drawBoard(game.board, (0, 0))
        # draw moving pieces
        if game.moving_piece is not None:
            screen.blit(game.moving_piece.img, pygame.mouse.get_pos())
        if not game.status:
            endGame()
        pygame.display.update()
        if game.status:
            botMove()

