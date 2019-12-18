import Chess.Board as Board
import Chess.Pieces as Pieces
import Chess.Game as Game
import pygame


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption('Chess')
    game = Game.Game()
    game.setUp()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                game.select(pos)
        screen.fill((0, 0, 0))
        game.board.draw(screen)
        game.board.drawSquare(screen, pygame.mouse.get_pos())

        pygame.display.update()
