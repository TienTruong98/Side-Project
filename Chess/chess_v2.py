import pygame
import Chess.Game_v2 as Game
import Chess.Board_v2 as Board


def drawBoard(board: Board.Board, board_pos: tuple):
    screen.blit(board.img, board_pos)
    for square in board.squares:
        if square.occupant is not None:
            x, y = square.left_up_corner
            screen.blit(square.occupant.img, (x, y))


if __name__ == '__main__':
    pygame.init()

    height = 600
    width = 600
    board_size = 600

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Chess')

    game = Game.Game(board_size)
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
        pygame.display.update()
