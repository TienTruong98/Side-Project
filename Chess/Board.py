import itertools
import pygame
import Chess.Pieces as Pieces


class Square:
    size = 60

    def __init__(self, x, y, occupant: Pieces = None, left_up_corner=(0, 0)):
        self.x = x
        self.y = y
        self.occupant = occupant
        self.left_up_corner = left_up_corner
        self.being_clicked = False

    def __str__(self):
        return "Square {}{}: {} ".format(self.x, self.y, self.occupant)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __ne__(self, other):
        if self.x == other.x and self.y == other.y:
            return False
        return True


class Board:
    Y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
    X_axis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    root_X = 38
    root_Y = 38
    distance = 66.5

    def __init__(self, width=600, height=600):
        self.squares = []
        for x, y in itertools.product(self.X_axis, self.Y_axis):
            # find the left up corner coordinates
            a = (ord(x) - 65) * self.distance + self.root_X
            b = (y - 1) * self.distance + self.root_Y
            self.squares.append(Square(x, y, None, (a, b)))

        self.img = pygame.image.load("board.png")
        self.img = pygame.transform.scale(self.img, (width, height))

    def setOccupant(self, x, y, occupant: Pieces):
        square = self.findSquare(x, y)
        square.occupant = occupant

    def findSquare(self, x, y):
        # based on chess coordinates
        for square in self.squares:
            if square.x == x and square.y == y:
                return square

    def getSquare(self, pos):
        # get the square chess coordinates
        # based on screen coordinates
        x, y = pos
        for square in self.squares:
            square_x, square_y = square.left_up_corner
            if square_x <= x <= square_x + square.size and square_y <= y <= square_y + square.size:
                return square
        return None

    def draw(self, screen, x=0, y=0):
        screen.blit(self.img, (x, y))

    def drawSquare(self, screen, pos=None):
        for square in self.squares:
            if square.occupant is not None:
                if square.being_clicked:
                    screen.blit(square.occupant.img, pos)
                else:
                    x, y = square.left_up_corner
                    screen.blit(square.occupant.img, (x, y))

    def findSelectedSqure(self):
        for square in self.squares:
            if square.being_clicked:
                return square
        return None

    def getPosibleMove(self, x, y, turn):
        occupant: Pieces = self.findSquare(x, y).occupant
        moves = []
        for function, steps in occupant.move.items():
            f = getattr(occupant, function)
            for step in steps:
                next_x, next_y = occupant.getNextPosition(f(step))
                if not next_x or not next_y:
                    continue
                next_square = self.findSquare(next_x, next_y)
                if next_square.occupant is None or next_square.occupant.color != turn:
                    moves.append((next_x, next_y))

        print(moves)

    def __str__(self):
        result = ''
        for x in self.squares:
            result += str(x) + '\n'
        return result

    def __iter__(self):
        for x in self.squares:
            yield x


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_mode((0, 0))
    A = Board()
    A.setOccupant('A', 3, Pieces.King('white', 'A', 3))
    A.setOccupant('A', 2, Pieces.Queen('white', 'A', 2))
    A.getPosibleMove('A', 3, 'white')
