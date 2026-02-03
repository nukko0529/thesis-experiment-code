# 2025年度卒業論文 検証用ソースコード

## 概要
卒業論文で提案した手法の評価に使用した検証用のPythonコードをまとめている．

**題目**: 囲碁の単純な攻め合いに対する最善手探索の簡略化手法の提案 <br>
**氏名**: 温水心琴 <br>
**学籍番号**: 1223033129 <br>
**所属**: 岐阜大学 電気電子・情報工学科 情報コース <br>
**卒業年度**: 2025年度

## 目的
このコードの目的は，提案した手法(アルゴリズム)の妥当性と動作を検証することである．
卒業論文の4章での検証のために実装を行った．
囲碁における単純な攻め合いの局面に対して実行することで検証を行う．

## リポジトリ構成
``` bash
├ src/
│   ├ algorithm.py
│   ├ block_model.py
│   ├ board_model.py
│   ├ domain.py
│   └ utils.py
├ experiments/
│   └ experiment.py
└ README.md
```

## 環境
- Python 3.10

## 実行方法
以下のコマンドで実行
``` bash
python experiments/experiment.py
```

## 補足
- 検証に用いた局面は `experiments/experiment.py` 内に直接定義している．

## ライセンス
このプロジェクトは MIT License のもとで公開されている．
