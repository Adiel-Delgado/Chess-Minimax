import pygame
import sys
# Añadido para el infinito
import math 

# Inicializar pygame
pygame.init()

WIDTH, HEIGHT = 480, 480 # Ancho y Alto de la ventana
ROWS, COLS = 8, 8 # Filas y Columnas del tablero
SQUARE = WIDTH // COLS # Tamaño de cada casilla

# Colores
WHITE_COL = (245, 245, 220) 
DARK_BROWN = (101, 67, 33) 
LIGHT_BROWN = (233, 174, 95)
HIGHLIGHT = (50, 205, 50, 150) 
SELECTED_COLOR = (30, 144, 255, 150) 
RED = (255, 60, 60)
BLACK_COL = (20, 20, 20)
PIECE_WHITE = (255, 255, 255)
PIECE_BLACK = (0, 0, 0)

# Fuentes
FONT = pygame.font.SysFont('Arial', 24)
SMALL_FONT = pygame.font.SysFont('Arial', 18) 
SETUP_FONT = pygame.font.SysFont('Arial', 20) 

WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Crear la ventana del juego
pygame.display.set_caption("Rey & Peón (IA) vs Rey (Humano)") # Título de la ventana

# --- Globales para la Configuración de Piezas ---
PIECES_TO_SETUP = [('W', 'K'), ('W', 'P'), ('B', 'K')] # Piezas a configurar: Rey Blanco, Peón Blanco, Rey Negro
SETUP_MESSAGES = [
    "Clic para colocar Rey Blanco (RB)",
    "Clic para colocar Peón Blanco (PB)",
    "Clic para colocar Rey Negro (RN)"
] # Mensajes para el usuario durante la configuración

def draw_board(win):
    # Dibuja el tablero de ajedrez
    win.fill(WHITE_COL) # Rellena el fondo
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE) # Define el rectángulo para la casilla
            if (row + col) % 2 == 0: # Alterna colores de casillas
                pygame.draw.rect(win, LIGHT_BROWN, rect)
            else:
                pygame.draw.rect(win, DARK_BROWN, rect)

def draw_piece(win, row, col, piece_code): # piece_code es como 'WK' (Rey Blanco), 'BP' (Peón Negro)
    # Dibuja una pieza en la posición dada
    center_x = col * SQUARE + SQUARE // 2 # Centro X de la casilla
    center_y = row * SQUARE + SQUARE // 2 # Centro Y de la casilla
    radius = SQUARE // 3 # Radio para las piezas circulares

    piece_color_char = piece_code[0] # 'W' o 'B'
    piece_type_char = piece_code[1] # 'K', 'P', 'Q'

    draw_color = PIECE_WHITE if piece_color_char == 'W' else PIECE_BLACK # Color de relleno de la pieza
    outline_color = PIECE_BLACK if piece_color_char == 'W' else PIECE_WHITE # Color del borde de la pieza
    text_color = PIECE_BLACK if piece_color_char == 'W' else PIECE_WHITE # Color del texto ('K', 'P', 'Q')

    if piece_type_char == 'K': # Si es un Rey
        pygame.draw.circle(win, draw_color, (center_x, center_y), radius)
        pygame.draw.circle(win, outline_color, (center_x, center_y), radius, 3) # Borde
        label = FONT.render("K", True, text_color)
    elif piece_type_char == 'P': # Si es un Peón
        pygame.draw.circle(win, draw_color, (center_x, center_y), radius // 1.5) # Más pequeño
        label = FONT.render("P", True, text_color)
    elif piece_type_char == 'Q': # Si es una Reina (peón promocionado)
        pygame.draw.circle(win, draw_color, (center_x, center_y), radius)
        pygame.draw.circle(win, outline_color, (center_x, center_y), radius, 3) # Borde
        label = FONT.render("Q", True, text_color)
    else:
        return # Pieza desconocida

    lbl_rect = label.get_rect(center=(center_x, center_y)) # Centra la etiqueta de texto
    win.blit(label, lbl_rect) # Dibuja la etiqueta


def pos_to_coords(pos):
    # Convierte la posición del mouse (píxeles) a coordenadas del tablero (fila, columna)
    x, y = pos
    col = x // SQUARE
    row = y // SQUARE
    return row, col

def in_bounds(r, c):
    # Verifica si las coordenadas (fila, columna) están dentro del tablero
    return 0 <= r < ROWS and 0 <= c < COLS

def get_king_moves(r, c, pieces, color_char):
    # Obtiene los movimientos posibles para un rey desde la posición (r, c)
    moves = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] # 8 direcciones
    for dr, dc in directions:
        nr, nc = r + dr, c + dc # Nueva fila, nueva columna
        if in_bounds(nr, nc): # Si está dentro del tablero
            # Si la casilla está vacía o contiene una pieza del oponente
            if (nr, nc) not in pieces or pieces[(nr, nc)][0] != color_char:
                moves.append((nr, nc))
    return moves

def get_pawn_moves(r, c, pieces, color_char):
    # Obtiene los movimientos posibles para un peón desde la posición (r, c)
    # Esta función maneja peones blancos y negros, aunque en este juego solo se usa para blancos.
    moves = []
    if color_char == 'W':  # Peón Blanco (se mueve hacia arriba, disminuyendo la fila)
        # Mover un paso adelante
        if in_bounds(r - 1, c) and (r - 1, c) not in pieces:
            moves.append((r - 1, c))
            # Mover dos pasos adelante (movimiento inicial desde la fila 6)
            if r == 6 and in_bounds(r - 2, c) and (r - 2, c) not in pieces:
                moves.append((r - 2, c))
        # Capturas (diagonalmente hacia adelante)
        for dc in [-1, 1]: # Columnas adyacentes
            nr, nc = r - 1, c + dc
            if in_bounds(nr, nc) and (nr, nc) in pieces and pieces[(nr, nc)][0] == 'B': # Si hay pieza enemiga
                moves.append((nr, nc))
    elif color_char == 'B': # Peón Negro (se mueve hacia abajo, aumentando la fila)
        # Esta lógica no la usa la IA en esta configuración, pero se mantiene por si acaso
        if in_bounds(r + 1, c) and (r + 1, c) not in pieces:
            moves.append((r + 1, c))
            if r == 1 and in_bounds(r + 2, c) and (r + 2, c) not in pieces: # Movimiento inicial desde fila 1
                 moves.append((r + 2, c))
        for dc in [-1, 1]:
            nr, nc = r + 1, c + dc
            if in_bounds(nr, nc) and (nr, nc) in pieces and pieces[(nr, nc)][0] == 'W':
                moves.append((nr, nc))
    return moves


def is_in_check(pieces, king_color_char):
    # Verifica si el rey del color 'king_color_char' está en jaque
    king_pos = None
    # Encuentra la posición del rey
    for pos, (color, piece_type) in pieces.items():
        if color == king_color_char and piece_type == 'K':
            king_pos = pos
            break
    if king_pos is None:
        return True # No debería ocurrir si el rey está en el tablero

    opponent_color_char = 'B' if king_color_char == 'W' else 'W' # Color del oponente

    # Revisa todas las piezas del oponente para ver si alguna ataca al rey
    for piece_pos, (p_color, p_type) in pieces.items():
        if p_color == opponent_color_char:
            if p_type == 'K': # Rey oponente
                r_k, c_k = piece_pos
                if max(abs(r_k - king_pos[0]), abs(c_k - king_pos[1])) == 1: return True
            elif p_type == 'P': # Peón oponente
                r_p, c_p = piece_pos
                if opponent_color_char == 'W': # Peón Blanco atacando Rey Negro
                    if king_pos in [(r_p - 1, c_p - 1), (r_p - 1, c_p + 1)]: return True
                else: # Peón Negro atacando Rey Blanco (no debería ocurrir en este final)
                    if king_pos in [(r_p + 1, c_p - 1), (r_p + 1, c_p + 1)]: return True
            elif p_type == 'Q': # Reina oponente (resultado de promoción)
                q_r, q_c = piece_pos; k_r, k_c = king_pos
                # Como Torre
                if q_r == k_r or q_c == k_c:
                    clear_path = True
                    if q_r == k_r: # Horizontal
                        for col_check in range(min(q_c, k_c) + 1, max(q_c, k_c)):
                            if (q_r, col_check) in pieces: clear_path = False; break
                    else: # Vertical
                        for row_check in range(min(q_r, k_r) + 1, max(q_r, k_r)):
                            if (row_check, q_c) in pieces: clear_path = False; break
                    if clear_path: return True
                # Como Alfil
                if abs(q_r - k_r) == abs(q_c - k_c):
                    clear_path = True; dr = 1 if k_r > q_r else -1; dc = 1 if k_c > q_c else -1
                    curr_r, curr_c = q_r + dr, q_c + dc
                    while (curr_r, curr_c) != king_pos:
                        if (curr_r, curr_c) in pieces: clear_path = False; break
                        curr_r += dr; curr_c += dc
                    if clear_path: return True
    return False # No está en jaque


def generate_legal_moves(current_pieces, side_to_move_char):
    # Genera todos los movimientos legales para el bando 'side_to_move_char'
    legal_moves = []
    for start_pos, (color, piece_type) in current_pieces.items(): # Itera sobre todas las piezas
        if color == side_to_move_char: # Si la pieza es del bando que mueve
            possible_destinations = [] # Lista de destinos posibles para esta pieza
            if piece_type == 'K':
                possible_destinations = get_king_moves(start_pos[0], start_pos[1], current_pieces, color)
            elif piece_type == 'P': # Solo peones blancos para la IA
                if color == 'W': # Asegurarse de que es un peón blanco (IA)
                    possible_destinations = get_pawn_moves(start_pos[0], start_pos[1], current_pieces, color)
            # La Reina (promocionada) no genera movimientos activamente aquí, su presencia es evaluada.

            for end_pos in possible_destinations: # Para cada destino posible
                temp_pieces = dict(current_pieces) # Copia del estado del tablero
                moved_piece_color, moved_piece_original_type = temp_pieces.pop(start_pos) # Quita la pieza de su origen
                
                current_moved_piece_type = moved_piece_original_type
                if moved_piece_original_type == 'P':
                    if side_to_move_char == 'W' and end_pos[0] == 0: # Peón blanco llega a la fila 0
                        current_moved_piece_type = 'Q' # Promociona a Reina para la prueba de jaque
                
                temp_pieces[end_pos] = (moved_piece_color, current_moved_piece_type) # Coloca la pieza (o la promocionada) en el destino

                if not is_in_check(temp_pieces, side_to_move_char): # Si el rey de este bando NO está en jaque después del movimiento
                    legal_moves.append((start_pos, end_pos)) # Es un movimiento legal
    return legal_moves

def has_white_pawn_promoted(pieces):
    # Verifica si el peón blanco ha promocionado
    for pos, (color, piece_type) in pieces.items():
        if color == 'W' and piece_type == 'P' and pos[0] == 0: # Peón blanco en fila 0
            return True
        if color == 'W' and piece_type == 'Q': # Si ya hay una Reina blanca (promocionada)
            return True
    return False

def white_pawn_exists(pieces):
    # Verifica si todavía existe un peón blanco en el tablero
    for color, piece_type in pieces.values():
        if color == 'W' and piece_type == 'P':
            return True
    return False

def evaluate_board(current_pieces):
    # Evalúa el tablero desde la perspectiva de las Blancas (IA).
    # ESTA ES LA FUNCIÓN HEURÍSTICA CON AJUSTES PARA PROTEGER EL PEÓN
    if has_white_pawn_promoted(current_pieces):
        return 100000  # Peón blanco promocionado - Victoria para las Blancas

    initial_wp_exists_check = any(pt == 'P' for c,pt in INITIAL_PIECES.values() if c == 'W')
    if initial_wp_exists_check and not white_pawn_exists(current_pieces):
         return -200000 # ### CAMBIO HEURÍSTICO ### Penalización aún mayor por perder el peón.

    score = 0 # Puntaje inicial
    white_king_pos, white_pawn_pos, black_king_pos = None, None, None

    for pos, (color, piece_type) in current_pieces.items():
        if color == 'W':
            if piece_type == 'P': white_pawn_pos = pos
            elif piece_type == 'K': white_king_pos = pos
        elif color == 'B' and piece_type == 'K':
            black_king_pos = pos

    if white_pawn_pos:
        wp_r, wp_c = white_pawn_pos
        # Avance del Peón
        score += (6 - wp_r) * 60 # ### CAMBIO HEURÍSTICO ### Ligeramente más valor al avance.

        # --- Lógica de Seguridad del Peón ---
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
            score -= 7000 # ### CAMBIO HEURÍSTICO ### Penalización MUY FUERTE si el peón está atacado y no defendido.
        elif pawn_is_defended_by_wk:
            score += 200  # ### CAMBIO HEURÍSTICO ### Buena bonificación si el peón está defendido por el rey.
            if pawn_is_attacked_by_bk: # Atacado pero defendido
                score -= 100 # ### CAMBIO HEURÍSTICO ### Penalización menor, pero aún es un punto de tensión.
        
        # --- Posicionamiento del Rey Blanco ---
        if white_king_pos:
            wk_r, wk_c = white_king_pos
            dist_wk_wp = abs(wk_r - wp_r) + abs(wk_c - wp_c)
            score -= dist_wk_wp * 15 # ### CAMBIO HEURÍSTICO ### Mayor penalización si el rey está lejos del peón.

            # Bonificación por rey delante del peón (si el peón no está en las dos últimas filas antes de promocionar)
            if wp_r > 1 and wk_r == wp_r - 1 and wk_c == wp_c:
                score += 60 # ### CAMBIO HEURÍSTICO ### Bonificación por rey liderando/protegiendo directamente.
        
        # --- Posicionamiento del Rey Negro ---
        if black_king_pos:
            bk_r, bk_c = black_king_pos
            # Penaliza si el rey negro está delante o muy cerca del peón
            if bk_r < wp_r and abs(bk_c - wp_c) <= 1:
                score -= 40 # ### CAMBIO HEURÍSTICO ### Ligeramente mayor penalización por bloqueo.
            
            dist_bk_wp = abs(bk_r - wp_r) + abs(bk_c - wp_c)
            if dist_bk_wp < 2 : score -= 30 # ### CAMBIO HEURÍSTICO ### Ligeramente mayor penalización.

            # Intentar alejar al rey negro de la casilla de promoción
            # (considerando la columna actual del peón)
            dist_bk_promo_sq = abs(bk_r - 0) + abs(bk_c - wp_c) 
            score += dist_bk_promo_sq * 3 # ### CAMBIO HEURÍSTICO ### Ligeramente mayor bonificación.
    
    # Penalización si el rey blanco está pasivo en su fila inicial
    if white_king_pos and white_king_pos[0] == 7:
        if not (white_pawn_pos and white_pawn_pos[0] <= 2): 
            score -= 20 # ### CAMBIO HEURÍSTICO ### Ligeramente mayor penalización.

    return score


def minimax(current_pieces, depth, is_maximizing_white_turn, alpha, beta):
    # Algoritmo Minimax con poda Alfa-Beta
    if has_white_pawn_promoted(current_pieces):
        return 100000, None 
    
    initial_wp_exists_check_mm = any(pt == 'P' for c,pt in INITIAL_PIECES.values() if c == 'W')
    if initial_wp_exists_check_mm and not white_pawn_exists(current_pieces):
         return -200000, None # Coincide con la penalización en evaluate_board

    if depth == 0:
        return evaluate_board(current_pieces), None

    current_player_char = 'W' if is_maximizing_white_turn else 'B'
    possible_next_moves = generate_legal_moves(current_pieces, current_player_char)

    if not possible_next_moves:
        if is_in_check(current_pieces, current_player_char):
            return (-90000 if is_maximizing_white_turn else 90000), None # Jaque mate
        else:
            return 0, None # Ahogado

    best_move_found = None

    if is_maximizing_white_turn: # Turno de las Blancas (IA)
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
    else: # Turno de las Negras (Humano)
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
    # Dibuja un resaltado semitransparente
    for r, c in squares_to_highlight:
        s = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
        s.fill(color)
        win.blit(s, (c * SQUARE, r * SQUARE))

INITIAL_PIECES = {}

def setup_pieces(win):
    # Fase donde el usuario coloca las piezas
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
                        valid_placement = False; print("Casilla ocupada. Intenta de nuevo.")
                    if piece_to_place_type == 'P' and piece_to_place_color == 'W':
                        if not (1 <= r <= 6): # Peón blanco debe estar en filas 2 a 7 (índices 1 a 6)
                            valid_placement = False; print("El peón no puede estar en la primera/última fila (ni en la de promoción inicial). Intenta de nuevo.")
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
    
    INITIAL_PIECES = dict(pieces) # Guardar la configuración inicial
    return pieces

def main():
    global INITIAL_PIECES
    clock = pygame.time.Clock()
    current_board_pieces = setup_pieces(WIN)
    if not current_board_pieces or len(INITIAL_PIECES) != 3: # Asegura que INITIAL_PIECES se haya llenado
        print("La configuración de piezas falló o se cerró. Saliendo."); pygame.quit(); sys.exit()

    initial_wp_exists_at_start = any(pt == 'P' for c, pt in INITIAL_PIECES.values() if c == 'W')

    selected_piece_pos = None
    possible_player_moves = []
    current_turn_char = 'W'
    game_over_status = False
    winner_text = None
    minimax_depth = 3 # Puedes probar aumentarlo a 4 si el rendimiento es aceptable

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if game_over_status: continue
            if current_turn_char == 'B': # Turno del Humano
                if event.type == pygame.MOUSEBUTTONDOWN:
                    r_clicked, c_clicked = pos_to_coords(pygame.mouse.get_pos())
                    clicked_square_pos = (r_clicked, c_clicked)
                    if selected_piece_pos: # Si ya hay una pieza (Rey Negro) seleccionada
                        if clicked_square_pos in possible_player_moves:
                            moved_piece_tuple = current_board_pieces.pop(selected_piece_pos)
                            current_board_pieces[clicked_square_pos] = moved_piece_tuple
                            selected_piece_pos = None; possible_player_moves = []
                            current_turn_char = 'W'
                        else: # Nueva selección o deselección
                            selected_piece_pos = None; possible_player_moves = []
                            if clicked_square_pos in current_board_pieces and current_board_pieces[clicked_square_pos][0] == 'B':
                                selected_piece_pos = clicked_square_pos
                                # Asegurarse que la pieza seleccionada sea el Rey Negro
                                if current_board_pieces[selected_piece_pos] == ('B', 'K'):
                                    possible_player_moves = [m_end for s, m_end in generate_legal_moves(current_board_pieces, 'B') if s == selected_piece_pos]
                    # Si no hay pieza seleccionada y se hace clic en el Rey Negro
                    elif clicked_square_pos in current_board_pieces and current_board_pieces[clicked_square_pos] == ('B', 'K'):
                        selected_piece_pos = clicked_square_pos
                        possible_player_moves = [m_end for s, m_end in generate_legal_moves(current_board_pieces, 'B') if s == selected_piece_pos]

        if not game_over_status and current_turn_char == 'W': # Turno de la IA
            print("IA (Blancas) está pensando...")
            eval_score, best_ai_move = minimax(current_board_pieces, minimax_depth, True, -math.inf, math.inf)
            print(f"IA recomienda mover: {best_ai_move} con evaluación: {eval_score}")
            if best_ai_move:
                ai_start_pos, ai_end_pos = best_ai_move
                piece_color, piece_type = current_board_pieces.pop(ai_start_pos)
                final_piece_type = piece_type
                if piece_type == 'P' and piece_color == 'W' and ai_end_pos[0] == 0:
                    final_piece_type = 'Q'; print("¡IA promocionó peón a Reina!")
                current_board_pieces[ai_end_pos] = (piece_color, final_piece_type)
                current_turn_char = 'B'
            else: # No hay movimientos legales para la IA
                game_over_status = True
                winner_text = "¡Ahogado por Blancas!" if not is_in_check(current_board_pieces, 'W') else "¡Negras ganan por Jaque Mate a Blancas!"

        if not game_over_status: # Verificar Fin de Juego
            if has_white_pawn_promoted(current_board_pieces):
                game_over_status = True; winner_text = "¡Blancas (IA) ganan! Peón Promocionado."
            elif initial_wp_exists_at_start and not white_pawn_exists(current_board_pieces):
                game_over_status = True; winner_text = "¡Negras (Humano) ganan! Peón de IA Capturado."
            else:
                player_about_to_move = 'B' if current_turn_char == 'B' else 'W'
                if not generate_legal_moves(current_board_pieces, player_about_to_move):
                    game_over_status = True
                    if is_in_check(current_board_pieces, player_about_to_move):
                        winner_text = f"¡{'Blancas (IA)' if player_about_to_move == 'B' else 'Negras (Humano)'} GANA por Jaque Mate!"
                    else:
                        winner_text = "¡Ahogado! Es un Empate."
        
        draw_board(WIN)
        if selected_piece_pos: draw_highlights(WIN, [selected_piece_pos], SELECTED_COLOR)
        if possible_player_moves: draw_highlights(WIN, possible_player_moves, HIGHLIGHT)
        for pos_tuple, (p_color, p_type) in current_board_pieces.items():
            draw_piece(WIN, pos_tuple[0], pos_tuple[1], p_color + p_type)
        if game_over_status and winner_text:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((50, 50, 50, 180)); WIN.blit(overlay, (0,0))
            text_surface = FONT.render(winner_text, True, RED); text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)); WIN.blit(text_surface, text_rect)
            info_surface = SMALL_FONT.render("Cierra la ventana para salir.", True, WHITE_COL); info_rect = info_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)); WIN.blit(info_surface, info_rect)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()