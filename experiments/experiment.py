import utils
from algorithm import suggest_best_move, thesis_evaluation, is_invalid_move
from board_model import Board, print_board
from domain import StoneKind, EvaluateResult

def remove_nakade_dead_stones(input, board):
  dead_stones = set()
  for block in board.blocks:
      #print("eye liberties: ", block.count_liberties(), block.stone_num)
      if block.count_liberties() == 0 and (abs(block.stone_num) == StoneKind.BLACK_NAKADE.value):
        #print("This is dead block")
        for point in block.stones:
          dead_stones.add(point)
  #print("dead stones: ", dead_stones)
  for dead_stone in dead_stones:
    input[dead_stone.r][dead_stone.c] = StoneKind.EMPTY.value
  #print_board(input)
  return input

board_grid = (
    (-2,  3,  0,  0,  3,  0, -3,  0,  5, -3,  0,  2),
    (-2,  3,  0,  0,  3,  0, -3,  5, -3, -3,  0,  2),
    (-2,  3,  3,  3,  3, -3, -3, -3, -3,  2,  2,  0),
    (-2, -2, -2, -2, -2,  2,  2,  2,  2,  2,  2,  0)
)
print_board(board_grid)

b = Board(board_grid)
bm = suggest_best_move(b)
best_black = bm[0]

if best_black == None:
  print("Don't play is best for Black")
else:
    print("Black best moves")
    for bb in best_black:
        cp_board = board_grid
        cp_board = utils.tuple_to_list_two_dims(cp_board)
        cp_board[bb.r][bb.c] = StoneKind.BLACK_ADDED.value
        after_board = remove_nakade_dead_stones(cp_board, Board(cp_board))
        after_play = Board(after_board)
        print_board(after_play.grid)
        thesis_evaluation(after_play)

best_white = bm[1]

if best_white == None:
  print("Don't play is best for White")
else:
    print("White best moves")
    for bw in best_white:
        cp_board = board_grid
        cp_board = utils.tuple_to_list_two_dims(cp_board)
        cp_board[bw.r][bw.c] = StoneKind.WHITE_ADDED.value
        after_board = remove_nakade_dead_stones(cp_board, Board(cp_board))
        after_play = Board(after_board)
        print_board(after_play.grid)
        thesis_evaluation(after_play)