import pygame


class Piece:
    Y_axis = [1, 2, 3, 4, 5, 6, 7, 8]
    X_axis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    def __init__(self, name, color, x, y):
        self.name = name
        self.color = color
        self.x = x
        self.y = y
        if self.color == 'black':
            self.direction = -1
        else:
            self.direction = 1

    def moveVertical(self, step):
        return step, 0

    def moveHorizontal(self, step):
        return 0, step

    def moveMainDiagonal(self, step):
        return -step, step

    def moveAntiDiagonal(self, step):
        return step, step

    def moveLShape(self):
        return [
            (1, 2),
            (2, 1),
            (2, -1),
            (1, -2),
            (-1, -2),
            (-2, -1),
            (-2, 1),
            (-1, 2)
        ]

    def getNextPosition(self, moves: tuple):
        a, b = moves
        x = chr(ord(self.x) + a)
        y = self.y + b
        if x in self.X_axis and y in self.Y_axis:
            return x, y
        else:
            return None, None

    def setPosition(self, pos):
        self.x, self.y = pos

    def __str__(self):
        return f'{self.color} {self.name}: {self.x},{self.y}'


class King(Piece):
    def __init__(self, color, x, y):
        Piece.__init__(self, 'king', color, x, y)
        self.img = pygame.image.load('Pieces/' + color + '_king' + '.png').convert()
        self.img.set_colorkey((255, 255, 255))
        self.move = {
            'moveHorizontal': [1, -1],
            'moveVertical': [1, -1],
            'moveMainDiagonal': [1, -1],
            'moveAntiDiagonal': [1, -1]
        }

    '''
    def getBasicMove(self):
        moves = []
        posible_moves = []
        moves.append(self.moveHorizontal(self.direction * 1))
        moves.append(self.moveVertical(self.direction * 1))
        moves.append(self.moveMainDiagonal(self.direction * 1))
        moves.append(self.moveAntiDiagonal(self.direction * 1))
        moves.append(self.moveHorizontal(self.direction * -1))
        moves.append(self.moveVertical(self.direction * -1))
        moves.append(self.moveMainDiagonal(self.direction * -1))
        moves.append(self.moveAntiDiagonal(self.direction * -1))
        for a, b in moves:
            x = chr(ord(self.x) + a)
            y = self.y + b
            if x in self.X_axis and y in self.Y_axis:
                posible_moves.append((x, y))
        return posible_moves
    '''


class Queen(Piece):
    def __init__(self, color, x, y):
        Piece.__init__(self, 'queen', color, x, y)
        self.img = pygame.image.load('Pieces/' + color + '_queen' + '.png').convert()
        self.img.set_colorkey((255, 255, 255))

    '''
    def getBasicMove(self):
        moves = []
        posible_moves = []
        for i in range(1, 8):
            moves.append(self.moveHorizontal(self.direction * i))
            moves.append(self.moveVertical(self.direction * i))
            moves.append(self.moveMainDiagonal(self.direction * i))
            moves.append(self.moveAntiDiagonal(self.direction * i))
            moves.append(self.moveHorizontal(self.direction * -i))
            moves.append(self.moveVertical(self.direction * -i))
            moves.append(self.moveMainDiagonal(self.direction * -i))
            moves.append(self.moveAntiDiagonal(self.direction * -i))
        for a, b in moves:
            x = chr(ord(self.x) + a)
            y = self.y + b
            if x in self.X_axis and y in self.Y_axis:
                posible_moves.append((x, y))
        return posible_moves
    '''


class Rook(Piece):
    def __init__(self, color, x, y):
        Piece.__init__(self, 'rock', color, x, y)
        self.img = pygame.image.load('Pieces/' + color + '_rook' + '.png').convert()
        self.img.set_colorkey((255, 255, 255))

    '''
    def getBasicMove(self):
        moves = []
        posible_moves = []
        for i in range(1, 8):
            moves.append(self.moveHorizontal(self.direction * i))
            moves.append(self.moveVertical(self.direction * i))
            moves.append(self.moveHorizontal(self.direction * -i))
            moves.append(self.moveVertical(self.direction * -i))
        for a, b in moves:
            x = chr(ord(self.x) + a)
            y = self.y + b
            if x in self.X_axis and y in self.Y_axis:
                posible_moves.append((x, y))
        return posible_moves
    '''


class Knight(Piece):
    def __init__(self, color, x, y):
        Piece.__init__(self, 'knight', color, x, y)
        self.img = pygame.image.load('Pieces/' + color + '_knight' + '.png').convert()
        self.img.set_colorkey((255, 255, 255))

    '''
    def getBasicMove(self):
        moves = []
        posible_moves = []
        moves.extend(self.moveLShape())
        for a, b in moves:
            x = chr(ord(self.x) + a)
            y = self.y + b
            if x in self.X_axis and y in self.Y_axis:
                posible_moves.append((x, y))
        return posible_moves
    '''


class Bishop(Piece):
    def __init__(self, color, x, y):
        Piece.__init__(self, 'bishop', color, x, y)
        self.img = pygame.image.load('Pieces/' + color + '_bishop' + '.png').convert()
        self.img.set_colorkey((255, 255, 255))

    '''
    def getBasicMove(self):
        moves = []
        posible_moves = []
        for i in range(1, 8):
            moves.append(self.moveMainDiagonal(self.direction * i))
            moves.append(self.moveAntiDiagonal(self.direction * i))
            moves.append(self.moveMainDiagonal(self.direction * -i))
            moves.append(self.moveAntiDiagonal(self.direction * -i))
        for a, b in moves:
            x = chr(ord(self.x) + a)
            y = self.y + b
            if x in self.X_axis and y in self.Y_axis:
                posible_moves.append((x, y))
        return posible_moves
    '''


class Pawn(Piece):
    def __init__(self, color, x, y):
        Piece.__init__(self, 'pawn', color, x, y)
        self.img = pygame.image.load('Pieces/' + color + '_pawn' + '.png').convert()
        self.img.set_colorkey((255, 255, 255))

    '''
    def getBasicMove(self):
        moves = []
        posible_moves = []
        moves.append(self.moveHorizontal(self.direction * 1))
        for a, b in moves:
            x = chr(ord(self.x) + a)
            y = self.y + b
            if x in self.X_axis and y in self.Y_axis:
                posible_moves.append((x, y))
        return posible_moves
    '''


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((0, 0))
    knight = Queen('white', 'A', 1)
    print(knight)
    print(knight.getBasicMove())
