import math

from domain import Point, StoneKind, EyeSpaceKind
from block_model import Block, EyeSpace

def print_board(board):
    for row in board:
        for col in row:
            match col:
                case 0:
                    print(" +", end="")
                case 1:
                    print(" ○", end="")
                case -1:
                    print(" ●", end="")
                case 2:
                    print(" ○", end="")
                case -2:
                    print(" ●", end="")
                case 3:
                    print(" △", end="")
                case -3:
                    print(" ▲", end="")
                case 5:
                    print(" ◇", end="")
                case -5:
                    print(" ◆", end="")
        print("")

class Board:
    def __init__(self, grid):
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.grid = grid
        self.blocks = self.generate_blocks()
        self.eye_spaces = self.generate_eye_spaces()
        self._link_blocks_and_eye_spaces()
        self._identify_eye_space_kind()
        self._link_nakade_blocks_and_essential_blocks()

    def generate_blocks(self) -> list[Block]:
        """
        盤面上のブロックを検出
        """
        visited: set[Point] = set()
        #blocks: list[Block] = []
        blocks = []

        for r in range(self.rows):
            for c in range(self.cols):
                p = Point(r, c)
                if self.grid[r][c] in (
                            StoneKind.BLACK_SAFETY.value, StoneKind.WHITE_SAFETY.value,
                            StoneKind.BLACK_ESSENTIAL.value, StoneKind.WHITE_ESSENTIAL.value,
                            StoneKind.BLACK_NAKADE.value, StoneKind.WHITE_NAKADE.value,
                            StoneKind.BLACK_ADDED.value, StoneKind.WHITE_ADDED.value
                        ) and p not in visited:
                    block = self._flood_block(p, visited)
                    blocks.append(block)
        return blocks

    def generate_eye_spaces(self) -> list[EyeSpace]:
        """
        盤面上の Eye Space を検出
        """
        visited: set[Point] = set()
        eye_spaces: list[EyeSpace] = []

        for r in range(self.rows):
            for c in range(self.cols):
                p = Point(r, c)
                if self.grid[r][c] == StoneKind.EMPTY.value and p not in visited:
                    eye_space = self._flood_eye_space(p, visited)
                    eye_spaces.append(eye_space)
        return eye_spaces

    def _link_blocks_and_eye_spaces(self):
        """
        Blockクラスのeye_spaceに追加していく処理
        """
        for block in self.blocks:
            block.eye_spaces.clear()

        for eye_space in self.eye_spaces:
            for block in eye_space.border_blocks:
                block.eye_spaces.append(eye_space)

    def _identify_eye_space_kind(self):
        """
        Eye_spaceの種類を特定
        """
        for eye_space in self.eye_spaces:
            border_kinds = {block.stone_num for block in eye_space.border_blocks}
            border_product = math.prod(border_kinds)
            # print("border product: ", border_product)

            if abs(border_product) == 2 or border_product == -4:
                # 攻め合いに無関係 -> SafeBlock(2,-2)にのみ接している
                eye_space.kind = EyeSpaceKind.UNRELATED_LIBERTY.value
            elif abs(border_product) == 6:
                # OutsideLiberty -> EssentialBlock(3,-3)と相手のSafeBlock(2,-2)に接している
                eye_space.kind = EyeSpaceKind.OUTSIDE_LIBERTY.value
            elif abs(border_product) == 9:
                # SharedLiberty -> 両対局者のEssentialBlock(3,-3)に接している
                eye_space.kind = EyeSpaceKind.SHARED_LIBERTY.value
            elif abs(border_product) == 3 or abs(border_product) == 15 or border_product % 5 == 0:
                # EyeLiberty -> EssentialBlock(3,-3)のみもしくはそれとNakade(5,-5)に接している
                eye_space.kind = EyeSpaceKind.EYE_LIBERTY.value
            else:
                raise ValueError("Unknown eye space kind")

    def _link_nakade_blocks_and_essential_blocks(self):
        """
        Nakadeのブロックがどの対象ブロックに囲まれているか紐づけ
        """
        for eye_space in self.eye_spaces:
            if eye_space.kind != EyeSpaceKind.EYE_LIBERTY.value:
                continue
            nakade_blocks = set()
            essential_blocks = set()

            for block in eye_space.border_blocks:
                if abs(block.stone_num) in (StoneKind.BLACK_NAKADE.value, StoneKind.BLACK_ADDED.value):
                    nakade_blocks.add(block)
                elif abs(block.stone_num) == StoneKind.BLACK_ESSENTIAL.value:
                    essential_blocks.add(block)

            for nakade_block in nakade_blocks:
                for essential_block in essential_blocks:
                    essential_block.nakade_block.add(nakade_block)

    def _flood_block(self, start: Point, visited: set[Point]) -> Block:
        """
        深さ優先探索でブロックを検出(隣接する同色の石を一気に取得)
        """
        stone_kind = self.grid[start.r][start.c]
        block = Block(stone_kind)

        stack = [start]
        visited.add(start)

        while stack:
            p = stack.pop()
            block.stones.add(p)
            for q in self._neighbors(p):
                if q in visited:
                    continue
                if self.grid[q.r][q.c] == stone_kind:
                    visited.add(q)
                    stack.append(q)

        return block

    def _flood_eye_space(self, start: Point, visited: set[Point]) -> EyeSpace:
        """
        深さ優先探索で Eye Space を検出
        """
        eye_space = EyeSpace(border_blocks=set())
        border_stones = set()

        stack = [start]
        visited.add(start)

        while stack:
            p = stack.pop()
            eye_space.points.add(p)
            for q in self._neighbors(p):
                if q in visited:
                    continue
                if self.grid[q.r][q.c] == StoneKind.EMPTY.value:
                    visited.add(q)
                    stack.append(q)
                else:
                    #print(self.grid[q.r][q.c])
                    self._adjacent_block(q)
                    border_stones.add(q) # 眼に隣接している石を記録
        for bs in border_stones:
            block = self._identify_block(bs)
            eye_space.border_blocks.add(block)

        #print("eye_space points: ", eye_space.points)
        #print("eye_space border_blocks: ", eye_space.border_blocks)
        return eye_space

    def _adjacent_block(self, ad_point: Point) -> set[Block]:
        """
        Eye Space に隣接するブロックを検出
        """
        border = set()
        #print(ad_point.c, ad_point.r)
        for block in self.blocks:
            #print(block.stone_num)
            if ad_point in block.stones:
                border.add(block)
                #print("matched")
            #print(self.grid[ad_point.r][ad_point.c])
        #print(border)
        #for b in border:
            #print(b.stone_num, b.stones)
        return border

    def _identify_block(self, ad_point: Point) -> Block:
        """
        Eye Space に隣接するブロックを特定
        """
        for block in self.blocks:
            if ad_point in block.stones:
                #print("identified block stone num: ", block.stone_num)
                return block
        raise ValueError("Block not found for the given point.")

    def _neighbors(self, p: Point):
        """
        隣接する座標の取得
        """
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = p.r + dr, p.c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                yield Point(nr, nc)