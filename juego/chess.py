import pygame
import sys

# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 480, 480
ROWS, COLS = 8, 8
SQUARE = WIDTH // COLS

# Colors
WHITE = (245, 245, 220)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (233, 174, 95)
HIGHLIGHT = (50, 205, 50)
SELECTED = (30, 144, 255)
RED = (255, 60, 60)
BLACK = (20, 20, 20)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
SMALL_FONT = pygame.font.SysFont('Arial', 18)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King & Pawn vs King Chess")

def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE)
            if (row + col) % 2 == 0:
                pygame.draw.rect(win, LIGHT_BROWN, rect)
            else:
                pygame.draw.rect(win, DARK_BROWN, rect)

def draw_piece(win, row, col, piece):
    center = (col * SQUARE + SQUARE//2, row * SQUARE + SQUARE//2)
    radius = SQUARE // 3
    if piece == 'WK':
        pygame.draw.circle(win, (255, 255, 255), center, radius)
        pygame.draw.circle(win, BLACK, center, radius, 3)
        label = FONT.render("K", True, BLACK)
        lbl_rect = label.get_rect(center=center)
        win.blit(label, lbl_rect)
    elif piece == 'BK':
        pygame.draw.circle(win, BLACK, center, radius)
        pygame.draw.circle(win, WHITE, center, radius, 3)
        label = FONT.render("K", True, WHITE)
        lbl_rect = label.get_rect(center=center)
        win.blit(label, lbl_rect)
    elif piece == 'BP':
        pygame.draw.circle(win, BLACK, center, radius//2)
        label = FONT.render("P", True, WHITE)
        lbl_rect = label.get_rect(center=center)
        win.blit(label, lbl_rect)

def pos_to_coords(pos):
    x, y = pos
    col = x // SQUARE
    row = y // SQUARE
    return row, col

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def king_moves(pos, pieces, color):
    r, c = pos
    moves = []
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc):
            if (nr, nc) not in pieces or pieces[(nr, nc)][0] != color:
                moves.append((nr, nc))
    return moves

def pawn_moves(pos, pieces):
    r, c = pos
    moves = []
    # black pawn moves down (r+1)
    if in_bounds(r+1, c) and (r+1, c) not in pieces:
        moves.append((r+1, c))
    for dc in [-1, 1]:
        nr, nc = r+1, c+dc
        if in_bounds(nr, nc) and (nr, nc) in pieces and pieces[(nr, nc)][0] == 'W':
            moves.append((nr, nc))
    return moves

def is_king_captured(pieces, color):
    for pos in pieces:
        if pieces[pos] == (color, 'K'):
            return False
    return True

def is_check(pieces, side):
    king_pos = None
    for pos in pieces:
        if pieces[pos] == (side, 'K'):
            king_pos = pos
            break
    if king_pos is None:
        return True
    opponent = 'B' if side == 'W' else 'W'
    for pos in pieces:
        c, p = pieces[pos]
        if c != opponent:
            continue
        if p == 'K':
            if king_pos in king_moves(pos, pieces, c):
                return True
        elif p == 'P':
            r, cc = pos
            attacks = [(r+1, cc-1), (r+1, cc+1)]
            if king_pos in attacks:
                return True
    return False

def generate_moves(pieces, side):
    moves = []
    for pos in pieces:
        color, piece = pieces[pos]
        if color != side:
            continue
        if piece == 'K':
            for nm in king_moves(pos, pieces, color):
                new_pieces = dict(pieces)
                del new_pieces[pos]
                if nm in new_pieces:
                    del new_pieces[nm]
                new_pieces[nm] = (color, piece)
                if not is_check(new_pieces, side):
                    moves.append((pos, nm))
        elif piece == 'P':
            for nm in pawn_moves(pos, pieces):
                new_pieces = dict(pieces)
                del new_pieces[pos]
                if nm in new_pieces:
                    del new_pieces[nm]
                # Promotion to King only
                if nm[0] == 7:
                    new_pieces[nm] = (color, 'K')
                else:
                    new_pieces[nm] = (color, piece)
                if not is_check(new_pieces, side):
                    moves.append((pos, nm))
    return moves

def evaluate(pieces):
    score = 0
    for pos in pieces:
        color, piece = pieces[pos]
        r, c = pos
        if color == 'B':
            if piece == 'K':
                score += 1000
            elif piece == 'P':
                score += 500 + 10*r
        else:
            if piece == 'K':
                score -= 1000
    return score

def minimax(pieces, depth, maximizing, alpha, beta):
    if is_king_captured(pieces, 'W'):
        return 1000000, None
    if is_king_captured(pieces, 'B'):
        return -1000000, None
    if depth == 0:
        return evaluate(pieces), None
    side = 'B' if maximizing else 'W'
    moves = generate_moves(pieces, side)
    if not moves:
        if is_check(pieces, side):
            return (1000000 if side=='W' else -1000000), None
        else:
            return (-50000 if maximizing else 50000), None
    best_move = None
    if maximizing:
        max_eval = -float('inf')
        for move in moves:
            start, end = move
            new_pieces = dict(pieces)
            piece = new_pieces[start]  # store before deleting
            del new_pieces[start]
            if end in new_pieces:
                del new_pieces[end]
            if piece[1] == 'P' and end[0] == 7:
                new_pieces[end] = ('B', 'K')
            else:
                new_pieces[end] = piece
            eval_score, _ = minimax(new_pieces, depth-1, False, alpha, beta)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            start, end = move
            new_pieces = dict(pieces)
            piece = new_pieces[start]  # store before deleting
            del new_pieces[start]
            if end in new_pieces:
                del new_pieces[end]
            if piece[1] == 'P' and end[0] == 7:
                new_pieces[end] = ('B', 'K')
            else:
                new_pieces[end] = piece
            eval_score, _ = minimax(new_pieces, depth-1, True, alpha, beta)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def draw_highlights(win, squares, color):
    for r, c in squares:
        s = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
        s.fill((*color, 100))
        win.blit(s, (c * SQUARE, r * SQUARE))

def main():
    clock = pygame.time.Clock()
    pieces = {
        (7, 4): ('W', 'K'),  # White King e1
        (0, 4): ('B', 'K'),  # Black King e8
        (1, 4): ('B', 'P'),  # Black Pawn e7
    }
    selected = None
    possible_moves = []
    turn = 'W'
    game_over = False
    winner = None

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_over:
                continue
            if turn == 'W':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = pos_to_coords(pos)
                    if selected:
                        if (row, col) in possible_moves:
                            # Move white king
                            if (row, col) in pieces:
                                del pieces[(row, col)]
                            piece = pieces[selected]  # store piece before deletion
                            del pieces[selected]
                            pieces[(row, col)] = piece
                            selected = None
                            possible_moves = []
                            if is_king_captured(pieces, 'B'):
                                game_over = True
                                winner = 'White'
                            else:
                                turn = 'B'
                        else:
                            # New selection if clicked on white king
                            if (row, col) in pieces and pieces[(row, col)] == ('W', 'K'):
                                selected = (row, col)
                                possible_moves = king_moves(selected, pieces, 'W')
                            else:
                                selected = None
                                possible_moves = []
                    else:
                        if (row, col) in pieces and pieces[(row, col)] == ('W', 'K'):
                            selected = (row, col)
                            possible_moves = king_moves(selected, pieces, 'W')

        if not game_over and turn == 'B':
            _, move = minimax(pieces, 3, True, -float('inf'), float('inf'))
            if move is None:
                if is_check(pieces, 'B'):
                    game_over = True
                    winner = 'White'
                else:
                    game_over = True
                    winner = 'Draw'
            else:
                start, end = move
                piece = pieces[start]  # store piece before deletion
                if end in pieces:
                    del pieces[end]
                del pieces[start]
                # promotion
                if piece[1] == 'P' and end[0] == 7:
                    pieces[end] = ('B', 'K')
                else:
                    pieces[end] = piece
                if is_king_captured(pieces, 'W'):
                    game_over = True
                    winner = 'Black'
                else:
                    turn = 'W'

        draw_board(WIN)
        if selected:
            draw_highlights(WIN, [selected], SELECTED)
        if possible_moves:
            draw_highlights(WIN, possible_moves, HIGHLIGHT)

        for pos in pieces:
            draw_piece(WIN, pos[0], pos[1], pieces[pos][0] + pieces[pos][1])

        if game_over:
            if winner == 'Draw':
                text = "Game Over! Draw"
            else:
                text = f"Game Over! {winner} wins!"
            label = FONT.render(text, True, RED)
            WIN.blit(label, (10, HEIGHT // 2 - 20))

            info = SMALL_FONT.render("Close window to exit.", True, RED)
            WIN.blit(info, (10, HEIGHT // 2 + 10))

        pygame.display.update()

if __name__ == '__main__':
    main()

