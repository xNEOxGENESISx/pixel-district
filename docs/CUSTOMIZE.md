# カスタマイズ

自分で手を入れるときは [INSTALL.md の方法 2](INSTALL.md)（クローンしてローカルから読み込む）で入れておくと、
ファイルを書き換えて新しいセッションを開くだけで反映されます。

変えられる場所は 2 つだけです。

| 変えたいもの | ファイル | 反映のしかた |
|---|---|---|
| 透け具合・タイミング・ツールと画面の対応 | `plugin/hooks/register.tsx` | 新しいセッションを開く |
| 色・絵・動きの速さ | `tools/gen_scene.py` | `python3 tools/gen_scene.py` を実行 → 新しいセッション |

`plugin/hooks/scene.ts` と `scene/scene.svg` はジェネレーターが書き出すファイルです。直接編集しても、次に生成したときに消えます。

---

## 1. 背景の透け具合（register.tsx）

ファイル先頭の `GLASS` が、会話パネルの下にどれだけ部屋が見えるかを決めます。

```ts
const GLASS: ThemeBackdropGlass = { blur: 0, opacity: 0.9 }
```

| 例 | 見た目 |
|---|---|
| `{ blur: 0, opacity: 0.9 }` | 標準。パネルはほぼ不透明で文字が読みやすい |
| `{ blur: 0, opacity: 0.6 }` | 部屋がもっと透けて見える |
| `{ blur: 12, opacity: 0.7 }` | すりガラス風にぼかす |
| `{ blur: 0, tint: 'rgb(15 11 35)', opacity: 0.8 }` | パネルを部屋と同じ紫に染める |

> `glass: false` は「不透明」ではなく「パネルの下地なし」（文字の後ろに部屋がそのまま見える）なので注意してください。

## 2. タイミング（register.tsx）

同じく先頭にまとまっています。単位はミリ秒です。

| 名前 | 標準 | 意味 |
|---|---|---|
| `FLASH_MS` | 3500 | ✓・エラー・中断の表示時間 |
| `HEARD_MS` | 2000 | メッセージ送信時の「!」の表示時間 |
| `TOOL_HOLD_MS` | 1500 | 一瞬で終わるツールでも画面を出しておく最短時間 |
| `SLEEP_AFTER_MS` | 180000 | 何もしないで猫が眠るまで（3 分） |
| `BIG_FINISH_PIPS` | 6 | この数以上ステップがあったターンは豪華な完了演出 |
| `TIRED_AT_PERCENT` | 80 | 利用上限がこの % を超えるとマグが空になる |

## 3. どのツールでどの画面を出すか（register.tsx）

`toolKind()` がツール名をモニターの画面に対応させています。

| 画面 | 標準で対応するツール |
|---|---|
| `term`（ターミナル） | Bash, PowerShell など |
| `read`（ドキュメント） | Read。`search`（Grep, Glob）も同じ画面 |
| `edit`（エディター） | Edit, Write, NotebookEdit |
| `web`（ブラウザ） | WebSearch, WebFetch、名前に browser / chrome を含む MCP ツール |

たとえば自分の MCP ツール `mcp__mydb__query` をターミナル画面にしたいなら、1 行目を次のようにします。

```ts
if (/^(Bash|BashOutput|KillShell|PowerShell)$/.test(tool) || /^mcp__mydb__/.test(tool)) return 'term'
```

## 4. 色（gen_scene.py）

`tools/gen_scene.py` の先頭にある辞書 `C` が、部屋の全部の色です。名前で役割がわかるようになっています。

```python
C = {
    "wall": "#2a1f57",      # 壁
    "floor": "#2b1a42",     # 床
    "moon": "#ffe6ad",      # 月
    "win": "#ffb347",       # 街の窓の灯り
    "neon": "#ff5c9a",      # ネオンサイン
    "blanket": "#3a55a0",   # 布団
    ...
}
```

変えたら生成し直します。

```bash
python3 tools/gen_scene.py
```

`scene/scene.svg … chars (cap 131072)` と表示されれば成功です。
シーンは 131,072 文字までという上限があります。超えるとエラーで止まるので、色数を減らすか、細かい模様（ディザ）を減らしてください。

## 5. 動きの速さ（gen_scene.py）

`gen_scene.py` の中の `css = """ … """` が、部屋のアニメーションです。普通の CSS なので秒数を変えるだけで調整できます。

| 動き | 探す文字列 | 標準 |
|---|---|---|
| 雨の落ちる速さ | `.rain{…animation:fall 1.5s` | 1.5 秒 |
| 街の窓の点滅 | `animation:off 9s` など 4 つ | 9〜17 秒 |
| ネオンのちらつき | `animation:neon 12s` | 12 秒 |
| 猫のまばたき | `animation:blink 6.5s` | 6.5 秒 |
| 観葉植物の揺れ | `animation:la 6s` / `lb 6s` | 6 秒 |
| 作業中のコードのスクロール | `.work .tape{animation:scroll 1.3s` | 1.3 秒 |

部屋の状態ごとの見た目は、ルート要素のクラスで切り替えています（`.work …` は作業中、`.f-done …` は完了など）。
クラスの一覧は [FROM-SCRATCH.md の「状態クラス」](FROM-SCRATCH.md#4-状態クラス) にあります。

## 6. 変えたものを確かめる

```bash
python3 -m http.server 4039
```

| URL | できること |
|---|---|
| `http://localhost:4039/preview/states.html` | ボタンで全部の状態を切り替える |
| `…/states.html?auto=1` | 4 秒ごとに自動で切り替える |
| `…/states.html?s=error` | 指定した状態で開く |
| `…/states.html?x=240&y=78&w=80` | シーンの一部を拡大（ドット単位で確認） |
| `…/states.html?bar=0` | ボタンを隠す（スクリーンショット用） |

mod のテストと検証（Claude Code の CLI）:

```bash
claude plugin validate plugin
```

```bash
claude plugin test plugin
```

## 7. 自分の版を配る

フォークした自分のリポジトリで、

1. `plugin/.claude-plugin/plugin.json` と `.claude-plugin/marketplace.json` の `version` を上げる
2. `.claude-plugin/marketplace.json` の `owner` を自分にする
3. push する

使う人は `claude plugin marketplace add <あなたのアカウント>/<リポジトリ名>` で入れられます。
