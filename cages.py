from copy import deepcopy
import sys
import re
DEBUG = False


class ForsytheNotationError(ValueError):
    pass


class InvalidFrozenSquareError(ValueError):
    pass


def get_square_string(square):
    return f"{['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][square[0]]}{square[1]+1}"


def get_square(square_string):
    file = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(square_string[0])
    rank = int(square_string[1]) - 1
    return file, rank


def empty_board():
    return [[(EMPTY, EMPTY) for _ in range(8)] for _ in range(8)]


def print_board(board):
    result = ''
    for rank in range(7, -1, -1):
        result += str(rank + 1) + ' '
        for file in range(8):
            unit_str = board[file][rank][1]
            if board[file][rank][0] == BLACK:
                unit_str = unit_str.lower()
            result += unit_str + ' '
        result += '\n'
    result += '  a b c d e f g h\n'
    print(result)


def set_board(board, square_string, unit_string):
    file, rank = get_square(square_string)
    if unit_string.upper() == unit_string:
        board[file][rank] = (WHITE, unit_string)
    else:
        board[file][rank] = (BLACK, unit_string.upper())


def get_board_from_forsythe(forsythe_string):
    board = empty_board()
    forsythe_string_split = forsythe_string.strip().split('/')
    rank = 8
    for row in forsythe_string_split:
        rank -= 1
        if rank < 0:
            raise ForsytheNotationError(f'Too many ranks in Forsythe notation {forsythe_string}')
        file = -1
        for character in row:
            if '1' <= character <= '8':
                file += int(character)
                if file > 7:
                    raise ForsytheNotationError(f'File is too long on rank {rank+1} in Forsythe notation {forsythe_string}')
            elif character.upper() in ['K', 'Q', 'R', 'B', 'N', 'P']:
                file += 1
                if file > 7:
                    raise ForsytheNotationError(f'File is too long on rank {rank+1} in Forsythe notation {forsythe_string}')
                if character.upper() == character:
                    board[file][rank] = (WHITE, character)
                else:
                    board[file][rank] = (BLACK, character.upper())
            else:
                raise ForsytheNotationError(f'Invalid character {character} in Forsythe notation {forsythe_string}')
        if file < 7:
            raise ForsytheNotationError(f'File is too short on rank {rank + 1} in Forsythe notation {forsythe_string}')
    return board


KING = 'K'
QUEEN = 'Q'
ROOK = 'R'
BISHOP = 'B'
KNIGHT = 'N'
PAWN = 'P'
EMPTY = '.'
WHITE = 'w'
BLACK = 'b'

knight_vectors = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
rook_vectors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
bishop_vectors = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
queen_vectors = rook_vectors + bishop_vectors
white_pawn_vectors = [(-1, -1), (0, -1), (1, -1)]
white_pawn_capture_vectors = [(-1, -1), (1, -1)]
black_pawn_vectors = [(-1, 1), (0, 1), (1, 1)]
black_pawn_capture_vectors = [(-1, 1), (1, 1)]

original_squares = {
    (WHITE, ROOK): [get_square('a1'), get_square('h1')],
    (WHITE, KNIGHT): [get_square('b1'), get_square('g1')],
    (WHITE, BISHOP): [get_square('c1'), get_square('f1')],
    (WHITE, QUEEN): [get_square('d1')],
    (WHITE, KING): [get_square('e1')],
    (WHITE, PAWN): [(file, 1) for file in range(8)],
    (BLACK, ROOK): [get_square('a8'), get_square('h8')],
    (BLACK, KNIGHT): [get_square('b8'), get_square('g8')],
    (BLACK, BISHOP): [get_square('c8'), get_square('f8')],
    (BLACK, QUEEN): [get_square('d8')],
    (BLACK, KING): [get_square('e8')],
    (BLACK, PAWN): [(file, 6) for file in range(8)]
}
known_cages = []


def unoccupied(square, board):
    return square[0] in range(8) and square[1] in range(8) and board[square[0]][square[1]][1] == EMPTY


def occupied(square, board):
    return square[0] in range(8) and square[1] in range(8) and board[square[0]][square[1]][1] != EMPTY


def get_vector_retractions(square, vectors, board, unpromote=False, promoted_piece=(EMPTY, EMPTY)):
    unfiltered = [(square[0] + vector[0], square[1] + vector[1]) for vector in vectors]
    return [(square, new_square, unpromote, promoted_piece, False) for new_square in unfiltered
            if unoccupied(new_square, board)]


def get_line_retractions_along_vector(square, vector, board):
    result = []
    next_square = (square[0] + vector[0], square[1] + vector[1])
    while unoccupied(next_square, board):
        result.append((square, next_square, False, (EMPTY, EMPTY), False))
        next_square = (next_square[0] + vector[0], next_square[1] + vector[1])
    return result


def get_line_retractions(square, vectors, board):
    result = []
    for vector in vectors:
        result.extend(get_line_retractions_along_vector(square, vector, board))
    return result


def get_unpromotions(square, board):
    color_unit = board[square[0]][square[1]]
    if color_unit[0] == WHITE and square[1] == 7:
        return get_vector_retractions(square, white_pawn_vectors, board, unpromote=True, promoted_piece=color_unit)
    elif color_unit[0] == BLACK and square[1] == 0:
        return get_vector_retractions(square, black_pawn_vectors, board, unpromote=True, promoted_piece=color_unit)
    else:
        return []


def get_uncastlings(square, board):
    if square == (6, 0):  # white uncastle kingside
        if board[4][0] == (EMPTY, EMPTY) and board[5][0] == (WHITE, ROOK) and board[6][0] == (WHITE, KING) and \
                board[7][0] == (EMPTY, EMPTY):
            return [((6, 0), (4, 0), False, (EMPTY, EMPTY), True)]
    elif square == (2, 0):  # white uncastle queenside
        if board[0][0] == (EMPTY, EMPTY) and board[1][0] == (EMPTY, EMPTY) and board[2][0] == (WHITE, KING) and \
                board[3][0] == (WHITE, ROOK) and board[4][0] == (EMPTY, EMPTY):
            return [((2, 0), (4, 0), False, (EMPTY, EMPTY), True)]
    elif square == (6, 7):  # black uncastle kingside
        if board[4][7] == (EMPTY, EMPTY) and board[5][7] == (BLACK, ROOK) and board[6][7] == (BLACK, KING) and \
                board[7][7] == (EMPTY, EMPTY):
            return [((6, 7), (4, 7), False, (EMPTY, EMPTY), True)]
    elif square == (2, 7):  # black uncastle queenside
        if board[0][7] == (EMPTY, EMPTY) and board[1][7] == (EMPTY, EMPTY) and board[2][7] == (BLACK, KING) and \
                 board[3][7] == (BLACK, ROOK) and board[4][7] == (EMPTY, EMPTY):
            return [((2, 7), (4, 7), False, (EMPTY, EMPTY), True)]
    return []


def get_retractions_from_square(board, square):
    color_unit = board[square[0]][square[1]]
    if color_unit[1] == EMPTY:
        return []
    if len(color_unit) > 2 and color_unit[2]:  # frozen
        return []
    elif color_unit[1] == KING:
        return get_vector_retractions(square, queen_vectors, board) + get_uncastlings(square, board)
    elif color_unit[1] == QUEEN:
        return get_line_retractions(square, queen_vectors, board) + get_unpromotions(square, board)
    elif color_unit[1] == ROOK:
        return get_line_retractions(square, rook_vectors, board) + get_unpromotions(square, board)
    elif color_unit[1] == BISHOP:
        return get_line_retractions(square, bishop_vectors, board) + get_unpromotions(square, board)
    elif color_unit[1] == KNIGHT:
        return get_vector_retractions(square, knight_vectors, board) + get_unpromotions(square, board)
    elif color_unit[1] == PAWN and color_unit[0] == WHITE:
        if square[1] >= 2:
            return get_vector_retractions(square, white_pawn_vectors, board)
        else:
            return []
    elif color_unit[1] == PAWN and color_unit[0] == BLACK:
        if square[1] <= 5:
            return get_vector_retractions(square, black_pawn_vectors, board)
        else:
            return []
    else:
        raise ValueError(f"Invalid color_unit {color_unit} at square {square}")


def get_retractions(board, squares):
    result = []
    for square in squares:
        result.extend(get_retractions_from_square(board, square))
    return result


def is_unblockable_check_from_square(board, square, king_square):
    color_unit = board[square[0]][square[1]]
    if color_unit[1] == EMPTY:
        return False
    if color_unit[0] == board[king_square[0]][king_square[1]][0]:
        return False
    vector = (square[0] - king_square[0], square[1] - king_square[1])
    if color_unit[1] == KING:
        check_vectors = queen_vectors
    elif color_unit[1] == QUEEN:
        check_vectors = queen_vectors
    elif color_unit[1] == ROOK:
        check_vectors = rook_vectors
    elif color_unit[1] == BISHOP:
        check_vectors = bishop_vectors
    elif color_unit[1] == KNIGHT:
        check_vectors = knight_vectors
    elif color_unit[1] == PAWN and color_unit[0] == WHITE:
        check_vectors = white_pawn_capture_vectors
    elif color_unit[1] == PAWN and color_unit[0] == BLACK:
        check_vectors = black_pawn_capture_vectors
    else:
        raise ValueError(f"Invalid color_unit {color_unit} at square {square}")

    return vector in check_vectors


def get_unblockable_checkers(board, king_square):
    if king_square is None:
        return []
    result = []
    for vector in queen_vectors + knight_vectors:
        new_square = (king_square[0] + vector[0], king_square[1] + vector[1])
        if occupied(new_square, board) and is_unblockable_check_from_square(board, new_square, king_square):
            result.append(new_square)
    return result


def do_retraction(board, white_king_square, black_king_square, retraction):
    (original_square, new_square, unpromote, promoted_piece, uncastle) = retraction
    if DEBUG:
        print(f'Retracting {get_square_string(original_square)}-{get_square_string(new_square)}')
    retracted_unit = board[original_square[0]][original_square[1]]
    previous_retractor = retracted_unit[0]
    board[original_square[0]][original_square[1]] = (EMPTY, EMPTY)
    if unpromote:
        board[new_square[0]][new_square[1]] = (promoted_piece[0], PAWN)
    else:
        board[new_square[0]][new_square[1]] = retracted_unit

    if uncastle:  # move the rook
        first_rank = original_square[1]
        if original_square[0] == 6:  # kingside
            board[4][first_rank] = (board[4][first_rank][0], board[4][first_rank][1], True)  # freeze king
            board[7][first_rank] = (board[5][first_rank][0], board[5][first_rank][1], True)  # freeze rook
            board[5][first_rank] = (EMPTY, EMPTY)
        elif original_square[0] == 2:  # queenside
            board[4][first_rank] = (board[4][first_rank][0], board[4][first_rank][1], True)  # freeze king
            board[0][first_rank] = (board[3][first_rank][0], board[3][first_rank][1], True)  # freeze rook
            board[3][first_rank] = (EMPTY, EMPTY)
        else:
            raise ValueError(f"Impossible uncastling {get_square_string(original_square)}-{get_square_string(new_square)}")

    if retracted_unit == (WHITE, KING):
        white_king_square = new_square
    elif retracted_unit == (BLACK, KING):
        black_king_square = new_square
    return board, white_king_square, black_king_square, previous_retractor


def undo_retraction(board, white_king_square, black_king_square, retraction):
    (original_square, new_square, unpromote, promoted_piece, uncastle) = retraction
    if DEBUG:
        print(f'Undoing {get_square_string(original_square)}-{get_square_string(new_square)}')

    if unpromote:
        retracted_unit = promoted_piece
    else:
        retracted_unit = board[new_square[0]][new_square[1]]
    board[new_square[0]][new_square[1]] = (EMPTY, EMPTY)
    board[original_square[0]][original_square[1]] = retracted_unit

    if uncastle:  # move the rook
        first_rank = original_square[1]
        if original_square[0] == 6:  # kingside
            board[6][first_rank] = (board[6][first_rank][0], board[6][first_rank][1])  # unfreeze king
            board[5][first_rank] = (board[7][first_rank][0], board[7][first_rank][1])  # unfreeze rook
            board[7][first_rank] = (EMPTY, EMPTY)
        elif original_square[0] == 2:  # queenside
            board[2][first_rank] = (board[2][first_rank][0], board[2][first_rank][1])  # unfreeze king
            board[3][first_rank] = (board[0][first_rank][0], board[0][first_rank][1])  # unfreeze rook
            board[0][first_rank] = (EMPTY, EMPTY)
        else:
            raise ValueError(f"Impossible uncastling {get_square_string(original_square)}-{get_square_string(new_square)}")

    if retracted_unit == (WHITE, KING):
        white_king_square = original_square
    elif retracted_unit == (BLACK, KING):
        black_king_square = original_square
    return board, white_king_square, black_king_square


def in_home_squares(board, squares):
    for square in squares:
        color_unit = board[square[0]][square[1]]
        if color_unit[1] != EMPTY and square not in original_squares[color_unit[:2]]:
            return False
    return True


def contains_cage(board, cage):
    for file in range(8):
        for rank in range(8):
            if cage[file][rank][1] != EMPTY and cage[file][rank] != board[file][rank]:
                return False
    return True


def is_cage_internal(board, zone_squares, white_king_square, black_king_square, previous_retractor,
                     current_path, retraction_sequence, depth, cache):
    if DEBUG:
        print(f'Depth remaining: {depth}')
        print_board(board)

    # check cache
    if board in cache:
        if DEBUG:
            print('Illegal because already in cache')
        return True

    # check for loop to an existing position on the current path
    if board in current_path:
        if DEBUG:
            print('Illegal because of a loop')
        return True

    # no double (or higher) checks and both kings cannot be in check
    white_king_checkers = get_unblockable_checkers(board, white_king_square)
    black_king_checkers = get_unblockable_checkers(board, black_king_square)
    if len(white_king_checkers) + len(black_king_checkers) > 1:
        if DEBUG:
            print('Illegal because of an illegal check')
        return True

    # previous retractor cannot leave the opposing king in check
    if previous_retractor == WHITE and len(black_king_checkers) > 0:
        if DEBUG:
            print('Illegal because previous retraction left opposing king in check')
        return True
    if previous_retractor == BLACK and len(white_king_checkers) > 0:
        if DEBUG:
            print('Illegal because previous retraction left opposing king in check')
        return True

    # check if position contains an already known illegal cage
    for cage in known_cages:
        if contains_cage(board, cage):
            if DEBUG:
                print('Illegal because it contains a previously known cage: ')
                print_board(cage)
            return True

    # check if maximum depth reached
    if depth == 0:
        if DEBUG:
            print('Failure because maximum depth reached')
            print_board(board)
        return False

    # check if all units are back in their home squares
    if in_home_squares(board, zone_squares):
        if DEBUG:
            print('Failure because all units are back on their home squares')
            print_board(board)
        return False

    # If someone is in check, then only the checking unit can be retracted.
    # Otherwise, any unit can be retracted.
    if len(white_king_checkers) + len(black_king_checkers) > 0:
        possible_squares = [(white_king_checkers + black_king_checkers)[0]]
    else:
        possible_squares = zone_squares

    retractions = get_retractions(board, possible_squares)
    removed_units = []

    # Remove any units that can be retracted outside of the zone
    for retraction in retractions:
        (original_square, new_square, unpromote, promoted_piece, uncastle) = retraction
        if not uncastle and new_square not in zone_squares:
            removed_unit = board[original_square[0]][original_square[1]]
            if removed_unit[1] == EMPTY:  # we already removed this unit from another retraction
                continue
            retraction_sequence.append(retraction)
            removed_units.append((original_square[0], original_square[1], removed_unit))
            if DEBUG:
                print(f'Removing {removed_unit} from {get_square_string(original_square)} because it can retract to ' +
                      f'{get_square_string(new_square)}')
                print_board(board)
            board[original_square[0]][original_square[1]] = (EMPTY, EMPTY)
            if removed_unit == (WHITE, KING):
                white_king_square = None
            elif removed_unit == (BLACK, KING):
                black_king_square = None

    if removed_units:
        # If we removed any units, then recurse with the position after removing those units.
        if not is_cage_internal(board, zone_squares, white_king_square, black_king_square,
                                previous_retractor, current_path, retraction_sequence, depth-1, cache):
            return False
        for removed_unit in removed_units:
            del retraction_sequence[-1]
            board[removed_unit[0]][removed_unit[1]] = removed_unit[2]
            if DEBUG:
                print(f'Restoring {removed_unit[2]} at {get_square_string((removed_unit[0], removed_unit[1]))}')
            if removed_unit[2] == (WHITE, KING):
                white_king_square = (removed_unit[0], removed_unit[1])
            elif removed_unit[2] == (BLACK, KING):
                black_king_square = (removed_unit[0], removed_unit[1])
    else:
        # Otherwise, recurse with each possible retraction.
        current_path.append(deepcopy(board))
        for retraction in retractions:
            retraction_sequence.append(retraction)
            (board, white_king_square, black_king_square, previous_retractor) = \
                do_retraction(board, white_king_square, black_king_square, retraction)
            if not is_cage_internal(board, zone_squares, white_king_square, black_king_square,
                                    previous_retractor, current_path, retraction_sequence, depth-1, cache):
                return False
            del retraction_sequence[-1]
            (board, white_king_square, black_king_square) = \
                undo_retraction(board, white_king_square, black_king_square, retraction)
        del current_path[-1]
    if DEBUG:
        print('Illegal because all retractions from this position were illegal')
    cache.append(deepcopy(board))
    return True


def is_cage(board, frozen_squares, additional_zone_squares, depth, save=True):
    white_king_square = None
    black_king_square = None
    zone_squares = set(additional_zone_squares)
    for file in range(8):
        for rank in range(8):
            square = (file, rank)
            if board[file][rank] == (WHITE, KING):
                white_king_square = square
            elif board[file][rank] == (BLACK, KING):
                black_king_square = square
            if board[file][rank][1] != EMPTY:
                zone_squares.add(square)
                for vector in queen_vectors:
                    adjacent_square = (square[0] + vector[0], square[1] + vector[1])
                    if adjacent_square[0] in range(8) and adjacent_square[1] in range(8):
                        zone_squares.add(adjacent_square)
    for frozen_square in frozen_squares:
        color_unit = board[frozen_square[0]][frozen_square[1]]
        if color_unit[1] == EMPTY:
            raise InvalidFrozenSquareError(f"Specified frozen square {get_square_string(frozen_square)} is an empty square")
        elif frozen_square not in original_squares[color_unit]:
            raise InvalidFrozenSquareError(f"Specified frozen square {get_square_string(frozen_square)} contains a {color_unit}. " +
                                           f"This is not its home square.")
        else:
            board[frozen_square[0]][frozen_square[1]] = (color_unit[0], color_unit[1], True)

    cache = []
    retraction_sequence = []
    result = is_cage_internal(board, zone_squares, white_king_square, black_king_square, None,
                              [], retraction_sequence, depth, cache)
    if result and save:
        known_cages.extend(cache)
    return result, retraction_sequence


def test_position(forsythe_string, frozen_squares, additional_squares, depth):
    board = get_board_from_forsythe(forsythe_string)
    if DEBUG:
        print_board(board)
    result, retraction_sequence = is_cage(board, frozen_squares, additional_squares, depth)
    print(f'{forsythe_string} {result} ' +
          ' '.join([
              f'{get_square_string(retraction[0])}-{"P" if retraction[2] else ""}{get_square_string(retraction[1])}'
              for retraction in retraction_sequence]))
    return result


def parse_square_strings(square_strings):
    match = re.fullmatch('([a-h][1-8])(,[a-h][1-8])*', square_strings)
    if match:
        return [get_square(sq) for sq in square_strings.split(',')]
    else:
        return None


if __name__ == "__main__":
    line_number = 0
    for line in sys.stdin:
        line_number += 1
        raw = line.strip().split()
        forsythe_string = raw[0]
        additional_square_strings = []
        depth = 20
        frozen_squares = []
        skip = False
        for parameter in raw[1:]:
            parameter_split = parameter.split('=', 1)
            if len(parameter_split) < 2:
                print(f'ERROR: Skipping line {line_number} with invalid input {parameter} (expecting key=value)')
                skip = True
                break
            key, value = parameter_split
            if key.lower() == 'zone':
                additional_square_strings = parse_square_strings(value)
                if not additional_square_strings:
                    print(f'ERROR: Skipping line {line_number} with invalid zone value {value}')
                    skip = True
                    break
            elif key.lower() == 'depth':
                try:
                    depth = int(value)
                except ValueError:
                    print(f'ERROR: Skipping line {line_number} with invalid depth {value}')
                    skip = True
                    break
                if depth < 0:
                    print(f'ERROR: Skipping line {line_number} with invalid depth {value}')
                    skip = True
                    break
            elif key.lower() == 'frozen':
                frozen_squares = parse_square_strings(value)
                if not frozen_squares:
                    print(f'ERROR: Skipping line {line_number} with invalid frozen value {value}')
                    skip = True
                    break
            else:
                print(f'ERROR: Skipping line {line_number} with invalid key {key} (valid keys are: zone, depth, frozen)')
                skip = True
        if skip:
            continue
        try:
            test_position(forsythe_string, frozen_squares, additional_square_strings, depth)
        except (ForsytheNotationError, InvalidFrozenSquareError) as e:
            print(f'ERROR: Skipping line {line_number} because: {e}')
