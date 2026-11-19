# インストール

Pixel District は Claude Code の mod（プラグイン）です。
背景は **Claude デスクトップアプリの Code タブ** と **モバイルアプリ** に表示されます。ターミナル版の Claude Code は背景を描かないので、入れても見た目は変わりません。

動作確認: Claude Code 2.1.326（デスクトップアプリ同梱版）

## 方法 1: マーケットプレイスから入れる（おすすめ）

ターミナルで実行します。

```bash
claude plugin marketplace add xNEOxGENESISx/pixel-district
```

```bash
claude plugin install pixel-district@pixel-district
```

そのあと **新しいセッションを開く** と部屋が表示されます（すでに開いているセッションには反映されません）。

更新が出たとき:

```bash
claude plugin marketplace update pixel-district
```

```bash
claude plugin update pixel-district@pixel-district
```

## 方法 2: クローンして自分のフォルダから読み込む（カスタマイズする人向け）

自分で色や動きを変えたいときはこちら。フォルダを書き換えると、次のセッションから反映されます。

```bash
git clone https://github.com/xNEOxGENESISx/pixel-district.git ~/pixel-district
```

`~/.claude/settings.json` の `env` に、`plugin` フォルダの **絶対パス** を書きます
（すでに `CLAUDE_CODE_PLUGIN_DIRS` がある場合は `:` でつなげて足します）。

```json
{
  "env": {
    "CLAUDE_CODE_PLUGIN_DIRS": "/Users/あなたの名前/pixel-district/plugin"
  }
}
```

保存して新しいセッションを開けば完了です。

## 方法 3: 1 回だけ試す

ターミナル版でフォルダを指定して起動すると、そのセッションだけ読み込まれます（mod の動作やテストの確認用）。

```bash
claude --plugin-dir ~/pixel-district/plugin
```

## うまく表示されないとき

- **ほかのテーマ系 mod と同時に入れない**: 背景を設定する mod が 2 つあると、後から設定した方が勝ちます。片方を無効にしてください。
  ```bash
  claude plugin list
  ```
- **新しいセッションで確認する**: 背景はセッション開始時に設定されます。
- **ステータス行を見る**: 背景を描けない理由があると、`Pixel District: …` という一行が出ます。
- **ターミナル版では表示されない**: デスクトップアプリかモバイルアプリで見てください。

## アンインストール

```bash
claude plugin uninstall pixel-district@pixel-district
```

```bash
claude plugin marketplace remove pixel-district
```

方法 2 で入れた場合は、`CLAUDE_CODE_PLUGIN_DIRS` からパスを消してください。

## 安全性について

- ネットワーク通信はしません。ファイルも読み書きしません（シーンは `plugin/hooks/scene.ts` に入っています）。
- 見ているのは Claude の状態（ターンの開始と終了、どのツールを使ったか、許可待ちか、利用上限の割合、ターミナル版の入力欄が空かどうか）だけです。会話やファイルの中身は使いません。
- 中身は `plugin/hooks/register.tsx` の 1 ファイルなので、入れる前に読んで確認できます。
