from __future__ import annotations

import utils
from domain import Point, StoneKind, EyeSpaceKind, EvaluateResult

class EyeSpace:
    def __init__(self, border_blocks: set[Block]):
        self.border_blocks: set[Block] = border_blocks
        self.points: set[Point] = set()
        self.kind = EyeSpaceKind.UNDEFINED.value

    def count_eye_points(self) -> int:
        return len(self.points)

class Block:
    def __init__(self, stone_num):
        self.stone_num = stone_num
        self.stones: set[Point] = set()
        self.eye_spaces: list[EyeSpace] = []
        self.nakade_block: set[Block] = set()
        self.vital_points: set[Point] = set()
        self.second_vital_points: set[(Point, Point)] = set()

    def count_stones(self) -> int:
        """
        そのブロックを構成する石の数
        """
        return len(self.stones)

    def get_liberties(self) -> list[Point]:
        """
        すべての呼吸点のリストを返す
        """
        liberty_points: set[Point] = set()
        for eye_space in self.eye_spaces:
            for p in eye_space.points:
                liberty_points.add(p)
        return list(liberty_points) # ここなんでlistで返してる？

    def count_liberties(self) -> int:
        """
        単純な呼吸点のリスト(Eye Libertiesの計算式を考慮してない）
        """
        return len(self.get_liberties())

    def get_eye_liberties(self) -> list[EyeSpace]:
        """
        Eye Space のうち，Eye Liberty に該当するものだけ取得
        """
        eye_liberties: list[EyeSpace] = []
        for eye_space in self.eye_spaces:
            if eye_space.kind == EyeSpaceKind.EYE_LIBERTY.value:
                eye_liberties.append(eye_space)
        return eye_liberties

    def get_eye_liberty_points(self) -> list[Point]:
        """
        眼形ダメ内の空点を返す
        """
        eye_points: set[Point] = set()
        eye_liberties = self.get_eye_liberties()
        for el in eye_liberties:
            for point in el.points:
                eye_points.add(point)

        return eye_points

    def count_eye_liberties(self) -> int:
        """
        Eye Liberty の数(二眼あるかどうかチェックできる)
        """
        return len(self.get_eye_liberties())

    def count_eye_points_in_eye_liberties(self) -> int:
        """
        Eye Liberty に含まれる目の数を取得
        """
        # ! Eye Liberty すべての目の数を合計しているので，一つだけ取得したいとかなら別の処理を
        count = 0
        for eye_space in self.get_eye_liberties():
            count += eye_space.count_eye_points()
        return count

    def get_outside_liberties(self) -> set[Point]:
        outside_spaces = [eye_space for eye_space in self.eye_spaces if eye_space.kind == EyeSpaceKind.OUTSIDE_LIBERTY.value]
        outside_liberties = set()
        for out_space in outside_spaces:
            for point in out_space.points:
                outside_liberties.add(point)
        return outside_liberties

    def count_outside_liberties(self) -> int:
        """
        外ダメの数を合計
        """
        return len(self.get_outside_liberties())

    def count_nakade_in_eye(self) -> int:
        """
        中手として置かれている石を数える
        """
        # ! 石の色は考慮してない
        nb_count = 0
        #print(len(self.nakade_block))
        for nb in self.nakade_block:
            #print(" nakade stone num: ", nb.stone_num)
            nb_count += nb.count_stones()
        return nb_count

    def calculate_eye_size(self) -> int:
        """
        中手もカウントした目の数(Eye size)
        """
        el = self.count_eye_points_in_eye_liberties()
        nakade = self.count_nakade_in_eye()
        # print(self.stone_num, "Eye size : ", el, "+", nakade)
        return el + nakade

    def eye_status(self) -> int:
        """
        Eye Statusを返す
        """
        eye_size = self.calculate_eye_size()
        if eye_size == 0:
            return 0
        elif eye_size >= 1 and eye_size <= 3:
            return 1
        elif eye_size <= 6:
            #print("Eye size is ", eye_size, self.stone_num)
            return eye_size
        else:
            raise ValueError("Eye size is too large")

    def calculate_eye_liberties_formula(self) -> int:
        """
        中手の計算式でEye Libertiesを求める
        """
        eye_size = self.calculate_eye_size()

        if eye_size <= 1:
            return eye_size
        elif eye_size >= 2 and eye_size <= 6:
            return (eye_size * (eye_size - 3)) / 2 + 3

    def calculate_eye_evaluation_score_with_formula(self) -> int:
        """
        L(n) - nakadeを計算
        """
        return self.calculate_eye_liberties_formula() - self.count_nakade_in_eye()

    def have_two_eyes(self) -> bool:
        """
        二眼を持っているかチェック
        """
        if abs(self.stone_num) != StoneKind.BLACK_ESSENTIAL.value:
            #print("This block isn't essential block")
            return False

        eye_liberties = [eye_space for eye_space in self.eye_spaces if eye_space.kind == EyeSpaceKind.EYE_LIBERTY.value] # eye_kind ga EYE_LIBERTYdaddaratuika
        eye_space_count = len(eye_liberties)
        # print("eye_space_count: ", eye_space_count)
        # print("self stone_num: ", self.stone_num)
        if eye_space_count >= 2:
            for n in self.nakade_block:
                # print(" nakade's stone_num:", n.stone_num)
                if utils.sign(n.stone_num) != utils.sign(self.stone_num):
                    # print(" This block's eye is broken")
                    break
            else:
                # print(" This block has two or more eyes")
                return True
        else:
            pass
            #print(" This block doesn't have eye or has a eye")
        return False

    def vital_point_candidates(self) -> set[Point]:
        points = set()
        for eye_space in self.eye_spaces:
            if eye_space.kind == EyeSpaceKind.EYE_LIBERTY.value:
                points |= eye_space.points
        for nakade in self.nakade_block:
            points |= nakade.stones
        return points