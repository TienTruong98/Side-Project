import itertools
import pygame
import Chess.Pieces as Pieces


class Square:
    size = 60  # pixel size

    def __init__(self, pos: tuple, occupant: Pieces = None, left_up_corner: tuple = (0, 0)):
        self.pos = pos
        self.occupant = occupant
        self.left_up_corner = left_up_corner
        self.being_clicked = False

    def __str__(self):
        return "Square {}: {} ".format(self.pos, self.occupant)

    def __eq__(self, other):
        if self.pos == other.pos:
            return True
        return False

    def __ne__(self, other):
        if self.pos == other.pos:
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
        self.screen_width = width
        self.screen_height = height
        for x, y in itertools.product(self.X_axis, self.Y_axis):
            # find the left up corner screen coordinates
            screen_x = (ord(x) - 65) * self.distance + self.root_X
            screen_y = (y - 1) * self.distance + self.root_Y
            self.squares.append(Square((x, y), None, (screen_x, screen_y)))

        self.img = pygame.image.load("board.png")
        self.img = pygame.transform.scale(self.img, (width, height))

    def setOccupant(self, pos: tuple, occupant: Pieces):
        square = self.findSquare(pos)
        square.occupant = occupant

    def findSquare(self, pos: tuple):
        # based on chess coordinates
        for square in self.squares:
            if square.pos == pos:
                return square
        return None

    def getSquare(self, screen_pos: tuple):
        # get the square chess coordinates
        # based on screen coordinates
        x, y = screen_pos
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
                # if the player is clicking then the clicked square moving respectively to the cursor position
                if square.being_clicked:
                    x, y = pos
                    # check the screen boundary
                    if x not in range(0, self.screen_width - Square.size):
                        x = 0 if x < 0 else self.screen_width - Square.size
                    if y not in range(0, self.screen_height - Square.size):
                        y = 0 if x < 0 else self.screen_height - Square.size
                    screen.blit(square.occupant.img, (x, y))
                else:
                    screen.blit(square.occupant.img, square.left_up_corner)

    def findSelectedSqure(self):
        for square in self.squares:
            if square.being_clicked:
                return square
        return None

    def getPosibleMove(self, pos: tuple, turn):
        occupant: Pieces = self.findSquare(pos).occupant
        possible_moves = []
        
        for function, step in occupant.move.items():
            is_block = False
            if function == 'LShape':
                for pos in occupant.getMove(L_shape=True):
                    square = self.findSquare(pos)
                    if square.occupant is None or square.occupant.color != turn:
                        possible_moves.append(self.findSquare(pos))
            else:
                f = getattr(occupant, function)
                range_x, range_y = f(step)
                moves = occupant.getMove(range_x, range_y)
                for pos in moves:
                    if is_block:
                        break
                    square = self.findSquare(pos)
                    if square.occupant is None:
                        possible_moves.append(square)
                    else:
                        if square.occupant.color == turn:
                            is_block = True
                        else:
                            possible_moves.append(square)
                            is_block = True
        return possible_moves

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
    A.setOccupant(('A', 7), Pieces.Pawn('white', 'A', 7))
    x = A.getPosibleMove(('A', 7), 'white')
    print(x)
