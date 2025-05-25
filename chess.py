import pygame
import sys
# Added for infinity (likely referring to a game loop or resource path)
import os
import math 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
# Initialize pygame
pygame.init()

WIDTH, HEIGHT = 480, 480 # Window Width and Height
ROWS, COLS = 8, 8 # Board Rows and Columns
SQUARE = WIDTH // COLS # Size of each square

# Colors
WHITE_COL = (245, 245, 220) 
DARK_BROWN = (101, 67, 33) 
LIGHT_BROWN = (233, 174, 95)
HIGHLIGHT = (50, 205, 50, 150) 
SELECTED_COLOR = (30, 144, 255, 150) 
RED = (255, 60, 60)
BLACK_COL = (20, 20, 20)
PIECE_WHITE = (255, 255, 255)
PIECE_BLACK = (0, 0, 0)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
SMALL_FONT = pygame.font.SysFont('Arial', 18) 
SETUP_FONT = pygame.font.SysFont('Arial', 20) 

WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Create the game window
pygame.display.set_caption("King & Pawn (AI) vs King (Human)") # Window title

# --- Globals for Piece Setup ---
PIECES_TO_SETUP = [('W', 'K'), ('W', 'P'), ('B', 'K')] # Pieces to set up: White King, White Pawn, Black King
SETUP_MESSAGES = [
    "Click to place White King (WK)",
    "Click to place White Pawn (WP)",
    "Click to place Black King (BK)"
] # Messages for the user during setup

def draw_board(win):
    # Draws the chessboard
    win.fill(WHITE_COL) # Fill the background
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE) # Define the rectangle for the square
            if (row + col) % 2 == 0: # Alternate square colors
                pygame.draw.rect(win, LIGHT_BROWN, rect)
            else:
                pygame.draw.rect(win, DARK_BROWN, rect)
# Load images (do this once, before the main loop)
IMAGES = {
    'WK': pygame.image.load(os.path.join(IMAGE_DIR, 'king_white.png')),
    'WP': pygame.image.load(os.path.join(IMAGE_DIR, 'pawn_white.png')),
    'BK': pygame.image.load(os.path.join(IMAGE_DIR, 'king_black.png')),
}
for key in IMAGES:
    IMAGES[key] = pygame.transform.smoothscale(IMAGES[key], (SQUARE, SQUARE))

def draw_piece(win, row, col, piece_code):
    if piece_code not in IMAGES:
        return  # Don't draw if the piece is not in images

    x = col * SQUARE
    y = row * SQUARE
    win.blit(IMAGES[piece_code], (x, y))


def pos_to_coords(pos):
    # Converts mouse position (pixels) to board coordinates (row, column)
    x, y = pos
    col = x // SQUARE
    row = y // SQUARE
    return row, col

def in_bounds(r, c):
    # Checks if the coordinates (row, column) are within the board
    return 0 <= r < ROWS and 0 <= c < COLS

def get_king_moves(r, c, pieces, color_char):
    # Gets the possible moves for a king from position (r, c)
    moves = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] # 8 directions
    for dr, dc in directions:
        nr, nc = r + dr, c + dc # New row, new column
        if in_bounds(nr, nc): # If it's within the board
            # If the square is empty or contains an opponent's piece
            if (nr, nc) not in pieces or pieces[(nr, nc)][0] != color_char:
                moves.append((nr, nc))
    return moves

def get_pawn_moves(r, c, pieces, color_char):
    # Gets the possible moves for a pawn from position (r, c)
    # This function handles white and black pawns, although in this game it's only used for white.
    moves = []
    if color_char == 'W':  # White Pawn (moves upwards, decreasing row)
        # Move one step forward
        if in_bounds(r - 1, c) and (r - 1, c) not in pieces:
            moves.append((r - 1, c))
            # Move two steps forward (initial move from row 6)
            if r == 6 and in_bounds(r - 2, c) and (r - 2, c) not in pieces:
                moves.append((r - 2, c))
        # Captures (diagonally forward)
        for dc in [-1, 1]: # Adjacent columns
            nr, nc = r - 1, c + dc
            if in_bounds(nr, nc) and (nr, nc) in pieces and pieces[(nr, nc)][0] == 'B': # If there's an enemy piece
                moves.append((nr, nc))
    elif color_char == 'B': # Black Pawn (moves downwards, increasing row)
        # This logic is not used by the AI in this setup, but kept just in case
        if in_bounds(r + 1, c) and (r + 1, c) not in pieces:
            moves.append((r + 1, c))
            if r == 1 and in_bounds(r + 2, c) and (r + 2, c) not in pieces: # Initial move from row 1
                 moves.append((r + 2, c))
        for dc in [-1, 1]:
            nr, nc = r + 1, c + dc
            if in_bounds(nr, nc) and (nr, nc) in pieces and pieces[(nr, nc)][0] == 'W':
                moves.append((nr, nc))
    return moves


def is_in_check(pieces, king_color_char):
    # Checks if the king of 'king_color_char' color is in check
    king_pos = None
    # Find the king's position
    for pos, (color, piece_type) in pieces.items():
        if color == king_color_char and piece_type == 'K':
            king_pos = pos
            break
    if king_pos is None:
        return True # Shouldn't happen if the king is on the board

    opponent_color_char = 'B' if king_color_char == 'W' else 'W' # Opponent's color

    # Check all opponent's pieces to see if any attack the king
    for piece_pos, (p_color, p_type) in pieces.items():
        if p_color == opponent_color_char:
            if p_type == 'K': # Opponent's King
                r_k, c_k = piece_pos
                if max(abs(r_k - king_pos[0]), abs(c_k - king_pos[1])) == 1: return True
            elif p_type == 'P': # Opponent's Pawn
                r_p, c_p = piece_pos
                if opponent_color_char == 'W': # White Pawn attacking Black King
                    if king_pos in [(r_p - 1, c_p - 1), (r_p - 1, c_p + 1)]: return True
                else: # Black Pawn attacking White King (shouldn't happen in this endgame)
                    if king_pos in [(r_p + 1, c_p - 1), (r_p + 1, c_p + 1)]: return True
            elif p_type == 'Q': # Opponent's Queen (result of promotion)
                q_r, q_c = piece_pos; k_r, k_c = king_pos
                # Like a Rook
                if q_r == k_r or q_c == k_c:
                    clear_path = True
                    if q_r == k_r: # Horizontal
                        for col_check in range(min(q_c, k_c) + 1, max(q_c, k_c)):
                            if (q_r, col_check) in pieces: clear_path = False; break
                    else: # Vertical
                        for row_check in range(min(q_r, k_r) + 1, max(q_r, k_r)):
                            if (row_check, q_c) in pieces: clear_path = False; break
                    if clear_path: return True
                # Like a Bishop
                if abs(q_r - k_r) == abs(q_c - k_c):
                    clear_path = True; dr = 1 if k_r > q_r else -1; dc = 1 if k_c > q_c else -1
                    curr_r, curr_c = q_r + dr, q_c + dc
                    while (curr_r, curr_c) != king_pos:
                        if (curr_r, curr_c) in pieces: clear_path = False; break
                        curr_r += dr; curr_c += dc
                    if clear_path: return True
    return False # Not in check


def generate_legal_moves(current_pieces, side_to_move_char):
    # Generates all legal moves for the 'side_to_move_char' side
    legal_moves = []
    for start_pos, (color, piece_type) in current_pieces.items(): # Iterate over all pieces
        if color == side_to_move_char: # If the piece belongs to the side to move
            possible_destinations = [] # List of possible destinations for this piece
            if piece_type == 'K':
                possible_destinations = get_king_moves(start_pos[0], start_pos[1], current_pieces, color)
            elif piece_type == 'P': # Only white pawns for the AI
                if color == 'W': # Ensure it's a white pawn (AI)
                    possible_destinations = get_pawn_moves(start_pos[0], start_pos[1], current_pieces, color)
            # The Queen (promoted) does not actively generate moves here; its presence is evaluated.

            for end_pos in possible_destinations: # For each possible destination
                temp_pieces = dict(current_pieces) # Copy of the board state
                moved_piece_color, moved_piece_original_type = temp_pieces.pop(start_pos) # Remove the piece from its origin
                
                current_moved_piece_type = moved_piece_original_type
                if moved_piece_original_type == 'P':
                    if side_to_move_char == 'W' and end_pos[0] == 0: # White pawn reaches row 0
                        current_moved_piece_type = 'Q' # Promote to Queen for the check test
                
                temp_pieces[end_pos] = (moved_piece_color, current_moved_piece_type) # Place the piece (or the promoted one) at the destination

                if not is_in_check(temp_pieces, side_to_move_char): # If this side's king is NOT in check after the move
                    legal_moves.append((start_pos, end_pos)) # It's a legal move
    return legal_moves

def has_white_pawn_promoted(pieces):
    # Checks if the white pawn has promoted
    for pos, (color, piece_type) in pieces.items():
        if color == 'W' and piece_type == 'P' and pos[0] == 0: # White pawn on row 0
            return True
        if color == 'W' and piece_type == 'Q': # If there is already a white Queen (promoted)
            return True
    return False

def white_pawn_exists(pieces):
    # Checks if a white pawn still exists on the board
    for color, piece_type in pieces.values():
        if color == 'W' and piece_type == 'P':
            return True
    return False

def evaluate_board(current_pieces):
    # Evaluates the board from White's (AI) perspective.
    # THIS IS THE HEURISTIC FUNCTION WITH ADJUSTMENTS TO PROTECT THE PAWN
    if has_white_pawn_promoted(current_pieces):
        return 100000  # White pawn promoted - Win for White

    initial_wp_exists_check = any(pt == 'P' for c,pt in INITIAL_PIECES.values() if c == 'W')
    if initial_wp_exists_check and not white_pawn_exists(current_pieces):
         return -200000 # ### HEURISTIC CHANGE ### Even greater penalty for losing the pawn.

    score = 0 # Initial score
    white_king_pos, white_pawn_pos, black_king_pos = None, None, None

    for pos, (color, piece_type) in current_pieces.items():
        if color == 'W':
            if piece_type == 'P': white_pawn_pos = pos
            elif piece_type == 'K': white_king_pos = pos
        elif color == 'B' and piece_type == 'K':
            black_king_pos = pos

    if white_pawn_pos:
        wp_r, wp_c = white_pawn_pos
        # Pawn advancement
        score += (6 - wp_r) * 60 # ### HEURISTIC CHANGE ### Slightly more value to advancement.

        # --- Pawn Safety Logic ---
        pawn_is_attacked_by_bk = False
        if black_king_pos:
            bk_r, bk_c = black_king_pos
            if max(abs(bk_r - wp_r), abs(bk_c - wp_c)) == 1:
                pawn_is_attacked_by_bk = True

        pawn_is_defended_by_wk = False
        if white_king_pos:
            wk_r, wk_c = white_king_pos
            if max(abs(wk_r - wp_r), abs(wk_c - wp_c)) == 1:
                pawn_is_defended_by_wk = True
        
        if pawn_is_attacked_by_bk and not pawn_is_defended_by_wk:
            score -= 7000 # ### HEURISTIC CHANGE ### VERY STRONG penalty if the pawn is attacked and not defended.
        elif pawn_is_defended_by_wk:
            score += 200  # ### HEURISTIC CHANGE ### Good bonus if the pawn is defended by the king.
            if pawn_is_attacked_by_bk: # Attacked but defended
                score -= 100 # ### HEURISTIC CHANGE ### Lesser penalty, but still a point of tension.
        
        # --- White King Positioning ---
        if white_king_pos:
            wk_r, wk_c = white_king_pos
            dist_wk_wp = abs(wk_r - wp_r) + abs(wk_c - wp_c)
            score -= dist_wk_wp * 15 # ### HEURISTIC CHANGE ### Greater penalty if the king is far from the pawn.

            # Bonus for king in front of the pawn (if pawn is not in the last two ranks before promotion)
            if wp_r > 1 and wk_r == wp_r - 1 and wk_c == wp_c:
                score += 60 # ### HEURISTIC CHANGE ### Bonus for king leading/protecting directly.
        
        # --- Black King Positioning ---
        if black_king_pos:
            bk_r, bk_c = black_king_pos
            # Penalize if the black king is in front of or very close to the pawn
            if bk_r < wp_r and abs(bk_c - wp_c) <= 1:
                score -= 40 # ### HEURISTIC CHANGE ### Slightly greater penalty for blocking.
            
            dist_bk_wp = abs(bk_r - wp_r) + abs(bk_c - wp_c)
            if dist_bk_wp < 2 : score -= 30 # ### HEURISTIC CHANGE ### Slightly greater penalty.

            # Try to move the black king away from the promotion square
            # (considering the pawn's current column)
            dist_bk_promo_sq = abs(bk_r - 0) + abs(bk_c - wp_c) 
            score += dist_bk_promo_sq * 3 # ### HEURISTIC CHANGE ### Slightly greater bonus.
    
    # Penalty if the white king is passive on its starting rank
    if white_king_pos and white_king_pos[0] == 7:
        if not (white_pawn_pos and white_pawn_pos[0] <= 2): 
            score -= 20 # ### HEURISTIC CHANGE ### Slightly greater penalty.

    return score


def minimax(current_pieces, depth, is_maximizing_white_turn, alpha, beta):
    # Minimax algorithm with Alpha-Beta pruning
    if has_white_pawn_promoted(current_pieces):
        return 100000, None 
    
    initial_wp_exists_check_mm = any(pt == 'P' for c,pt in INITIAL_PIECES.values() if c == 'W')
    if initial_wp_exists_check_mm and not white_pawn_exists(current_pieces):
         return -200000, None # Matches the penalty in evaluate_board

    if depth == 0:
        return evaluate_board(current_pieces), None

    current_player_char = 'W' if is_maximizing_white_turn else 'B'
    possible_next_moves = generate_legal_moves(current_pieces, current_player_char)

    if not possible_next_moves:
        if is_in_check(current_pieces, current_player_char):
            return (-90000 if is_maximizing_white_turn else 90000), None # Checkmate
        else:
            return 0, None # Stalemate

    best_move_found = None

    if is_maximizing_white_turn: # White's turn (AI)
        max_eval = -math.inf
        for start_pos, end_pos in possible_next_moves:
            new_pieces_state = dict(current_pieces)
            piece_color, piece_type = new_pieces_state.pop(start_pos)
            
            final_piece_type = piece_type
            if piece_type == 'P' and piece_color == 'W' and end_pos[0] == 0:
                final_piece_type = 'Q'
            new_pieces_state[end_pos] = (piece_color, final_piece_type)

            eval_score, _ = minimax(new_pieces_state, depth - 1, False, alpha, beta)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move_found = (start_pos, end_pos)
            alpha = max(alpha, eval_score)
            if beta <= alpha: break
        return max_eval, best_move_found
    else: # Black's turn (Human)
        min_eval = math.inf
        for start_pos, end_pos in possible_next_moves:
            new_pieces_state = dict(current_pieces)
            piece_data = new_pieces_state.pop(start_pos)
            new_pieces_state[end_pos] = piece_data

            eval_score, _ = minimax(new_pieces_state, depth - 1, True, alpha, beta)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move_found = (start_pos, end_pos)
            beta = min(beta, eval_score)
            if beta <= alpha: break
        return min_eval, best_move_found

def draw_highlights(win, squares_to_highlight, color):
    # Draws a semi-transparent highlight
    for r, c in squares_to_highlight:
        s = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
        s.fill(color)
        win.blit(s, (c * SQUARE, r * SQUARE))

INITIAL_PIECES = {}

def setup_pieces(win):
    # Phase where the user places the pieces
    global INITIAL_PIECES
    pieces = {}
    placed_count = 0
    running_setup = True

    while running_setup:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if placed_count < len(PIECES_TO_SETUP):
                    r, c = pos_to_coords(pygame.mouse.get_pos())
                    piece_to_place_color, piece_to_place_type = PIECES_TO_SETUP[placed_count]
                    valid_placement = True
                    if (r,c) in pieces:
                        valid_placement = False; print("Square occupied. Try again.")
                    if piece_to_place_type == 'P' and piece_to_place_color == 'W':
                        if not (1 <= r <= 6): # White pawn must be on rows 2 to 7 (indices 1 to 6)
                            valid_placement = False; print("The pawn cannot be on the first/last rank (nor on the initial promotion rank). Try again.")
                    if valid_placement:
                        pieces[(r, c)] = (piece_to_place_color, piece_to_place_type)
                        placed_count += 1
                    if placed_count == len(PIECES_TO_SETUP): running_setup = False
        
        draw_board(win)
        for pos_tuple, (p_color, p_type) in pieces.items():
            draw_piece(win, pos_tuple[0], pos_tuple[1], p_color + p_type)
        if placed_count < len(PIECES_TO_SETUP):
            message = SETUP_MESSAGES[placed_count]
            msg_surface = SETUP_FONT.render(message, True, RED)
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, SQUARE // 2))
            win.blit(msg_surface, msg_rect)
        pygame.display.flip()
        pygame.time.Clock().tick(30)
    
    INITIAL_PIECES = dict(pieces) # Save the initial configuration
    return pieces

def main():
    global INITIAL_PIECES
    clock = pygame.time.Clock()
    current_board_pieces = setup_pieces(WIN)
    if not current_board_pieces or len(INITIAL_PIECES) != 3: # Ensure INITIAL_PIECES has been populated
        print("Piece setup failed or was closed. Exiting."); pygame.quit(); sys.exit()

    initial_wp_exists_at_start = any(pt == 'P' for c, pt in INITIAL_PIECES.values() if c == 'W')

    selected_piece_pos = None
    possible_player_moves = []
    current_turn_char = 'W'
    game_over_status = False
    winner_text = None
    minimax_depth = 3 # You can try increasing it to 4 if performance is acceptable

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if game_over_status: continue
            if current_turn_char == 'B': # Human's turn
                if event.type == pygame.MOUSEBUTTONDOWN:
                    r_clicked, c_clicked = pos_to_coords(pygame.mouse.get_pos())
                    clicked_square_pos = (r_clicked, c_clicked)
                    if selected_piece_pos: # If a piece (Black King) is already selected
                        if clicked_square_pos in possible_player_moves:
                            moved_piece_tuple = current_board_pieces.pop(selected_piece_pos)
                            current_board_pieces[clicked_square_pos] = moved_piece_tuple
                            selected_piece_pos = None; possible_player_moves = []
                            current_turn_char = 'W'
                        else: # New selection or deselection
                            selected_piece_pos = None; possible_player_moves = []
                            if clicked_square_pos in current_board_pieces and current_board_pieces[clicked_square_pos][0] == 'B':
                                selected_piece_pos = clicked_square_pos
                                # Ensure the selected piece is the Black King
                                if current_board_pieces[selected_piece_pos] == ('B', 'K'):
                                    possible_player_moves = [m_end for s, m_end in generate_legal_moves(current_board_pieces, 'B') if s == selected_piece_pos]
                    # If no piece is selected and the Black King is clicked
                    elif clicked_square_pos in current_board_pieces and current_board_pieces[clicked_square_pos] == ('B', 'K'):
                        selected_piece_pos = clicked_square_pos
                        possible_player_moves = [m_end for s, m_end in generate_legal_moves(current_board_pieces, 'B') if s == selected_piece_pos]

        if not game_over_status and current_turn_char == 'W': # AI's turn
            print("AI (White) is thinking...")
            eval_score, best_ai_move = minimax(current_board_pieces, minimax_depth, True, -math.inf, math.inf)
            print(f"AI recommends move: {best_ai_move} with evaluation: {eval_score}")
            if best_ai_move:
                ai_start_pos, ai_end_pos = best_ai_move
                piece_color, piece_type = current_board_pieces.pop(ai_start_pos)
                final_piece_type = piece_type
                if piece_type == 'P' and piece_color == 'W' and ai_end_pos[0] == 0:
                    final_piece_type = 'Q'; print("AI promoted pawn to Queen!")
                current_board_pieces[ai_end_pos] = (piece_color, final_piece_type)
                current_turn_char = 'B'
            else: # No legal moves for the AI
                game_over_status = True
                winner_text = "Stalemate by White!" if not is_in_check(current_board_pieces, 'W') else "Black wins by Checkmate to White!"

        if not game_over_status: # Check Game End
            if has_white_pawn_promoted(current_board_pieces):
                game_over_status = True; winner_text = "White (AI) wins! Pawn Promoted."
            elif initial_wp_exists_at_start and not white_pawn_exists(current_board_pieces):
                game_over_status = True; winner_text = "Black (Human) wins! AI's Pawn Captured."
            else:
                player_about_to_move = 'B' if current_turn_char == 'B' else 'W'
                if not generate_legal_moves(current_board_pieces, player_about_to_move):
                    game_over_status = True
                    if is_in_check(current_board_pieces, player_about_to_move):
                        winner_text = f"{'White (AI)' if player_about_to_move == 'B' else 'Black (Human)'} WINS by Checkmate!"
                    else:
                        winner_text = "Stalemate! It's a Draw."
        
        draw_board(WIN)
        if selected_piece_pos: draw_highlights(WIN, [selected_piece_pos], SELECTED_COLOR)
        if possible_player_moves: draw_highlights(WIN, possible_player_moves, HIGHLIGHT)
        for pos_tuple, (p_color, p_type) in current_board_pieces.items():
            draw_piece(WIN, pos_tuple[0], pos_tuple[1], p_color + p_type)
        if game_over_status and winner_text:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((50, 50, 50, 180)); WIN.blit(overlay, (0,0))
            text_surface = FONT.render(winner_text, True, RED); text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)); WIN.blit(text_surface, text_rect)
            info_surface = SMALL_FONT.render("Close the window to exit.", True, WHITE_COL); info_rect = info_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)); WIN.blit(info_surface, info_rect)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()