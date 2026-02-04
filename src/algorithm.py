from domain import Point, StoneKind, EyeSpaceKind, EvaluateResult
from block_model import Block, EyeSpace
from board_model import Board, print_board
import utils

def search_vital_points(board: Board, block: Block, second: bool=False) -> set[Point]:
    vital_points = set()
    for point in block.vital_point_candidates():
        cp_board = board.grid
        cp_board = utils.tuple_to_list_two_dims(cp_board)
        for r in range(len(cp_board)):
            for c in range(len(cp_board[0])):
                #if utils.sign(cp_board[r][c]) != utils.sign(block.stone_num):
                if cp_board[r][c] == utils.sign(block.stone_num) * StoneKind.WHITE_NAKADE.value and not second:
                    #print(r, c, "Nakade to remove", block.stone_num)
                    cp_board[r][c] = 0
        cp_board[point.r][point.c] = utils.sign(block.stone_num) * StoneKind.BLACK_NAKADE.value
        #print_board(cp_board)
        search_board = Board(cp_board)
        for b in search_board.blocks:
            if block.stone_num == b.stone_num and b.have_two_eyes():
                vital_points.add(point)
    #print(block.stone_num, "have vital points : ", vital_points)
    return vital_points

def search_second_vital_points(board: Board, block: Block) -> set[(Point, Point)]:
    second_vital_points = set()

    for point in block.vital_point_candidates():
        cp_board = board.grid
        cp_board = utils.tuple_to_list_two_dims(cp_board)
        for r in range(len(cp_board)):
            for c in range(len(cp_board[0])):
                #if abs(cp_board[r][c]) == StoneKind.BLACK_NAKADE.value:
                #print(utils.sign(block.stone_num) * StoneKind.BLACK_NAKADE.value)
                if cp_board[r][c] == utils.sign(block.stone_num) * StoneKind.WHITE_NAKADE.value:
                    cp_board[r][c] = 0
        print_board(cp_board)
        cp_board[point.r][point.c] = utils.sign(block.stone_num) * StoneKind.BLACK_NAKADE.value
        search_board = Board(cp_board)
        for b in search_board.blocks:
            if block.stone_num == b.stone_num:
                b_vp = search_vital_points(search_board, b, True)
                for svp in b_vp:
                    if point != svp and ((svp, point) not in second_vital_points):
                        second_vital_points.add((point, svp))
    #print(block.stone_num, "have second vital points : ", second_vital_points)
    return second_vital_points

def playable_vital_points(board: Board, block: Block) -> set[Point]:
    vital_points = search_vital_points(board, block)
    print("vital_points: ", vital_points)
    playable_vp: set[Point] = set()
    if vital_points == None or len(vital_points) == 0:
        #print("This block have any vital points", block.stone_num)
        return playable_vp
    for vp in vital_points:
        if board.grid[vp.r][vp.c] == StoneKind.EMPTY.value:
            playable_vp.add(vp)
    #print(block.stone_num, " vital points: ", playable_vp)
    return playable_vp

def is_invalid_move(es_block: Block) -> bool:
    #print("[is_invalid_move]")
    sum_libs = es_block.count_liberties()
    eye_libs = es_block.count_eye_points_in_eye_liberties()
    if sum_libs > 1 and eye_libs == 1:
        #print("This vp is invalid")
        return True
    #print("This vp is not invalid")
    return False

def playable_second_vital_points(board: Board, block: Block) -> set[Point]:
    second_vital_points = search_second_vital_points(board, block)
    print("second_vital_points : ", second_vital_points)
    playable_second_vital_points: set[Point] = set()

    if second_vital_points == None or len(second_vital_points) == 0:
        #print("This block have any second vital points", block.stone_num)
        return playable_second_vital_points

    for svp in second_vital_points:
        #print(board.grid[svp[0].r][svp[0].c] == StoneKind.EMPTY.value)
        #print(board.grid[svp[1].r][svp[1].c] == StoneKind.EMPTY.value)
        if board.grid[svp[0].r][svp[0].c] == StoneKind.EMPTY.value and board.grid[svp[1].r][svp[1].c] == StoneKind.EMPTY.value:
            playable_second_vital_points.add(svp[0])
            playable_second_vital_points.add(svp[1])
    #print(block.stone_num, "second vital points: ", playable_second_vital_points)
    return playable_second_vital_points

def identify_attacker(black_eb, white_eb, lb, lw) -> int:
    """
    Attackerを特定する
    """
    black_es = black_eb.eye_status()
    white_es = white_eb.eye_status()

    if black_es > white_es:
        return -1
    elif black_es < white_es:
        return 1
    else:
        if lb < lw:
            return -1
        else: # eye statusもlibertiesも同じならどっちでもいいので黒ってことにしておく
            return 1

def own_better_eye(black_eb, white_eb) -> int:
    """
    Eye Statusを比較
    """
    black_es = black_eb.eye_status()
    white_es = white_eb.eye_status()

    if black_es > white_es:
        return -1
    elif black_es < white_es:
        return 1
    else:
        return 0

def muller_evaluation(board: Board):
    """
    Mullerの判定手法で勝敗判定
    """
    # ! 対象ブロックが一つもしくはない場合のみ考えている
    for block in board.blocks:
        if block.stone_num == StoneKind.BLACK_ESSENTIAL.value:
            black_eb = block
        elif block.stone_num == StoneKind.WHITE_ESSENTIAL.value:
            white_eb = block

    S= 0 # 内ダメの数S
    for eye_space in board.eye_spaces:
        if eye_space.kind == EyeSpaceKind.SHARED_LIBERTY.value:
            S += eye_space.count_eye_points()

    lsb = black_eb.calculate_eye_evaluation_score_with_formula()
    lsw = white_eb.calculate_eye_evaluation_score_with_formula()
    lb = black_eb.count_outside_liberties() + lsb
    lw = white_eb.count_outside_liberties() + lsw

    better_eye = own_better_eye(black_eb, white_eb)

    F = S - 1 if S > 0 and (black_eb.eye_spaces or white_eb.eye_spaces) else S

    delta_bw = lb - lw
    delta = abs(delta_bw)

    if better_eye == 0:
        if delta <= F:
            semeai_status = 0
            seki_level = F - delta
        else:
            F = -F if delta_bw > 0 else F
            semeai_status = delta_bw + F
    else:
        F = F if better_eye == 1 else -F
        semeai_status = delta_bw + F

    if semeai_status == 0:
        print("Winner: None")
        if seki_level > 0:
            print("It is Seki")
    elif semeai_status > 0:
        print("Winner: Black")
    else:
        print("Winner: White")

def thesis_evaluation(board: Board):
    """
    Mullerの手法を拡張した版
    """
    for block in board.blocks:
        if block.stone_num == StoneKind.BLACK_ESSENTIAL.value:
            black_eb = block
        elif block.stone_num == StoneKind.WHITE_ESSENTIAL.value:
            white_eb = block

    S= 0 # 内ダメの数S
    for eye_space in board.eye_spaces:
        if eye_space.kind == EyeSpaceKind.SHARED_LIBERTY.value:
            S += eye_space.count_eye_points()

    lsb = black_eb.calculate_eye_evaluation_score_with_formula()
    lsw = white_eb.calculate_eye_evaluation_score_with_formula()
    lb = black_eb.count_outside_liberties() + lsb
    lw = white_eb.count_outside_liberties() + lsw

    delta = lb - lw

    black_es = black_eb.eye_status()
    white_es = white_eb.eye_status()
    #print("Black eye status: ", black_es)
    #print("White eye status: ", white_es)

    F = S - 1 if S > 0 and (black_eb.eye_spaces or white_eb.eye_spaces) else S

    if black_eb.have_two_eyes(): # 両対局者が二眼を持ってる状況は考えない
        print("Black player have two eyes")
        return
    elif white_eb.have_two_eyes():
        print("White player have two eyes")
        return
    elif black_es == white_es:
        print("Both have same eye status")
        return result_possible_seki(delta, F), calculate_advantage(delta, F)
    else:
        print("One side has better eye status")
        return result_never_seki(delta, F), calculate_advantage(delta, F)

def calculate_advantage(delta, F):
    """
    F-delta手分の余裕がある
    """
    return delta - F

def result_never_seki(delta, F):
    if delta > F:
        print("Black can win")
        return EvaluateResult.BLACK_WINNER
    elif delta < F:
        print("White can win")
        return EvaluateResult.WHITE_WINNER
    else:
        print("Sente can win")
        return EvaluateResult.FIRST_WINNER

def result_possible_seki(delta, F):
    if delta > F:
        print("Black can win")
        return EvaluateResult.BLACK_WINNER
    elif delta < -F:
        print("White can win")
        return EvaluateResult.WHITE_WINNER
    elif delta == 0 and F == 0:
        print("Sente can win")
        return EvaluateResult.FIRST_WINNER
    elif delta == F:
        print("If Black plays first: Black can win")
        print("If White plays first: Seki")
        return EvaluateResult.BLACK_AD
    elif delta == -F:
        print("If Black plays first: Seki")
        print("If White plays first: White can win")
        return EvaluateResult.WHITE_AD
    else:
        print("Seki")
        return EvaluateResult.SEKI

def best_move_for_winner(board: Board, winner: EvaluateResult, ad: int) -> set[Point]:
    # ! まずは黒から
    if winner not in (EvaluateResult.BLACK_WINNER, EvaluateResult.WHITE_WINNER, EvaluateResult.FIRST_WINNER, EvaluateResult.BLACK_AD, EvaluateResult.WHITE_AD):
        raise("[best_move_for_winner] Invalid input")

    if winner in (EvaluateResult.BLACK_WINNER, EvaluateResult.BLACK_AD):
        for block in board.blocks:
            # ! Essential blockが一つである前提
            if block.stone_num == StoneKind.WHITE_ESSENTIAL.value:
                enemy_eb = block
                break
    elif winner in (EvaluateResult.WHITE_WINNER, EvaluateResult.WHITE_AD):
        for block in board.blocks:
            if block.stone_num == StoneKind.BLACK_ESSENTIAL.value:
                enemy_eb = block
                break

    #playable_vp = [vital_point for vital_point in playable_vital_points(board, enemy_eb) if not is_invalid_move(enemy_eb)]
    playable_vp = [vital_point for vital_point in playable_vital_points(board, enemy_eb) if not is_invalid_move(enemy_eb)]
    playable_sec_vp = [sec_vital_point for sec_vital_point in playable_second_vital_points(board, enemy_eb) if not is_invalid_move(enemy_eb)]
    eye_points = enemy_eb.get_eye_liberty_points()
    print("playable_vp", playable_vp, "playable_sec_vp", playable_sec_vp, "eye_points", eye_points)

    if len(playable_vp) > 0:
        best_move = playable_vp # ! playable_vpの中身に優位劣位がないとしている
    elif ad > 0: # F-Δ手の余裕がある
        best_move = None
        print("Winner can play other place ", ad, "times")
    elif len(playable_sec_vp) > 0: # ! ここ順番検討してない
        best_move = playable_sec_vp
    elif len(eye_points) > 0:
        # ! これも優劣がないとしている(2手で眼が作れる場合など考えていない)
        best_move = [eye_point for eye_point in eye_points if not is_invalid_move(enemy_eb)]
        if len(best_move) == 0:
            best_move = enemy_eb.get_outside_liberties()
    else:
        best_move = enemy_eb.get_liberties() # ! ダメが一つ以上ある前提

    print("Best move for winner is", best_move)
    return best_move

def best_move_for_loser(board: Board, winner: EvaluateResult) -> set[Point]:
    if winner not in (EvaluateResult.BLACK_WINNER, EvaluateResult.WHITE_WINNER, EvaluateResult.FIRST_WINNER, EvaluateResult.BLACK_AD, EvaluateResult.WHITE_AD):
        raise("[best_move_for_loser] Invalid input")

    if winner == EvaluateResult.BLACK_WINNER:
        for block in board.blocks:
            # ! Essential blockが一つである前提
            if block.stone_num == StoneKind.WHITE_ESSENTIAL.value:
                eb = block
                break
    elif winner == EvaluateResult.WHITE_WINNER:
        for block in board.blocks:
            if block.stone_num == StoneKind.BLACK_ESSENTIAL.value:
                eb = block
                break

    playable_vp = [vital_point for vital_point in playable_vital_points(board, eb)] if can_remove_nakade(eb) else set()
    playable_sec_vp = playable_second_vital_points(board, eb)

    if len(playable_vp) > 0:
        best_move = playable_vp
    elif len(playable_sec_vp) > 0: # ! ここ順番検討してない
        best_move = playable_sec_vp
    else:
        print("Loser don't have to play for this race") # たぶんそう
        best_move = None

    #print("Best move for loser is ", best_move)
    return best_move

def can_remove_nakade(es_block: Block) -> bool:
    nakade_blocks = es_block.nakade_block
    for nakade in nakade_blocks:
        #print("nakade ", nakade.stones)
        if nakade.count_liberties() == 1:
            #print("can remove nakade")
            break
    else:
        #print("cannot remove nakade")
        return False
    return True

def best_move_for_seki(board: Board, winner: EvaluateResult) -> set[Point]:
    if winner not in (EvaluateResult.SEKI, EvaluateResult.BLACK_AD, EvaluateResult.WHITE_AD):
        raise("[best_move_for_seki] Invalid input")

    for block in board.blocks:
        if block.stone_num == StoneKind.BLACK_ESSENTIAL.value:
            black_eb = block
        elif block.stone_num == StoneKind.WHITE_ESSENTIAL.value:
            white_eb = block

    black_vp = playable_vital_points(board, black_eb)
    black_sec_vp = playable_second_vital_points(board, black_eb)
    white_vp = playable_vital_points(board, white_eb)
    white_sec_vp = playable_second_vital_points(board, white_eb)

    # ! 相手の眼をつぶせるならつぶすのがベストということにしている
    if white_vp:
        best_move_for_black = white_vp
    elif white_sec_vp:
        best_move_for_black = white_sec_vp
    else:
        best_move_for_black = None

    if black_vp:
        best_move_for_white = black_vp
    elif black_sec_vp:
        best_move_for_white = black_sec_vp
    else:
        best_move_for_white = None

    #print("     Best move for black", best_move_for_black)
    #print("     Best move for white", best_move_for_white)

    return best_move_for_black, best_move_for_white

def suggest_best_move(board: Board):
    winner, advantage = thesis_evaluation(board)

    if winner == EvaluateResult.BLACK_WINNER:
        black_vp = best_move_for_winner(board, winner, advantage)
        white_vp = best_move_for_loser(board, winner)
    elif winner == EvaluateResult.WHITE_WINNER:
        black_vp = best_move_for_loser(board, winner)
        white_vp = best_move_for_winner(board, winner, advantage)
    elif winner == EvaluateResult.FIRST_WINNER:
        black_vp = best_move_for_winner(board, EvaluateResult.BLACK_WINNER, advantage)
        white_vp = best_move_for_winner(board, EvaluateResult.WHITE_WINNER, advantage)
    elif winner == EvaluateResult.SEKI:
        black_vp, white_vp = best_move_for_seki(board, winner)
    elif winner == EvaluateResult.BLACK_AD:
        black_vp = best_move_for_winner(board, winner, advantage)
        white_vp = best_move_for_seki(board, winner)[1]
    elif winner == EvaluateResult.WHITE_AD:
        black_vp = best_move_for_seki(board, winner)[0]
        white_vp = best_move_for_winner(board, winner, advantage)

    print("Black player's best moves are ", black_vp)
    print("White player's best moves are ", white_vp)

    return black_vp, white_vp