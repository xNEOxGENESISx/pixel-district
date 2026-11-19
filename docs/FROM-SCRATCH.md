# ゼロから自分の部屋（look）を作る

Pixel District と同じしくみで、自分だけの背景 mod を最初から作る手順です。
必要なのは Python 3 と Claude Code だけ。画像編集ソフトも npm パッケージもいりません。

全体の流れ:

```
1. 決める        サイズ・色・何が動くか
2. 描く          Python で 1 ドットずつ描いて SVG に書き出す
3. 動かす        SVG の中の CSS アニメーション
4. 状態クラス    Claude の状態 → SVG のルートのクラス → CSS が反応
5. mod にする    背景を設定して、状態に合わせて SVG を描き直す
6. 確かめる      プレビュー・テスト・実機
7. 配る          GitHub にマーケットプレイスとして置く
```

---

## 1. 決める

最初に紙 1 枚ぶんだけ決めておくと、あとで迷いません。

| 決めること | Pixel District の場合 |
|---|---|
| キャンバスの大きさ | 320 × 200 ドット（16:10。アプリの窓をだいたい埋める） |
| 色 | 夜の藍色を土台に、暖色（オレンジの猫・窓の灯り）を少しだけ |
| 主役 | 机でコードを書くグレーの猫 |
| 常に動くもの | 雨・街の窓・ネオン・植物・しっぽ・まばたき（どれも小さく、周期は数秒〜十数秒） |
| 状態で変わるもの | タイピングの速さ・モニターの画面・吹き出し・✓ |

背景は一日中目に入るので、**動きは小さく、遅く、まばらに** が基本です。
大きく光る・速く点滅するものは疲れます。

参考画像を使う場合は、雰囲気だけ参考にして絵は自分で描き直してください（他人の絵を mod に入れて配らない）。

## 2. 描く（Python → SVG）

ドット絵を「1 ドット = 1 マス」の辞書で持ち、最後に SVG にします。
Pixel District の `tools/gen_scene.py` の `Canvas` クラスが最小の形です。

```python
W, H = 320, 200

class Canvas:
    def __init__(self):
        self.px = {}                      # (x, y) -> "#rrggbb"

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[(x, y)] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def paths(self):
        # 横に続く同じ色のドットを 1 本の線にまとめ、色ごとに 1 つの <path> にする
        ...
```

ポイント:

- **同じ色の横並びは 1 本の線にまとめる**。1 ドット 1 要素にすると、すぐに大きくなりすぎます。
  背景の SVG は **131,072 文字まで** という上限があります（Pixel District は約 106,000 文字）。
- SVG には `shape-rendering="crispEdges"` を付けて、ドットがにじまないようにします。
- 小物は文字の配列で描くと楽です。

  ```python
  CAT = [
      "..k...k..",
      ".kgk.kgk.",
      ".kgggggk.",
      "kgweggwegk",
  ]
  canvas.sprite(100, 80, CAT, {"k": "#2b2340", "g": "#9a96b0", "w": "#ffffff", "e": "#1a1a1a"})
  ```

- **動く部品は別の Canvas に描く**（雨・しっぽの各コマ・画面など）。あとで `<g class="rain">…</g>` のように
  クラス付きのグループで包み、CSS で動かします。
- 乱数を使うときは `random.seed(23)` のように固定して、何度生成しても同じ絵になるようにします。
- 斜めの光やグラデーションはドット絵では段差（2〜3 段の色）で表現します。ディザ（市松模様）は文字数を大きく食うので控えめに。

## 3. 動かす（SVG の中の CSS）

SVG の先頭に `<style>` を入れ、普通の CSS アニメーションで動かします。JavaScript は使いません。

```css
/* 雨: 2 枚ぶん描いた雨粒を下にずらし続ける */
.rain { animation: fall 1.5s linear infinite }
@keyframes fall { from { transform: translateY(-65px) } to { transform: translateY(0) } }

/* しっぽ: 3 コマを順番に表示（opacity の切り替えでコマ送り） */
.t0 { animation: t0 7s steps(1) infinite }
@keyframes t0 { 0% { opacity: 1 } 70% { opacity: 0 } 88% { opacity: 1 } }

/* 動きを減らす設定の人には止める */
@media (prefers-reduced-motion: reduce) { * { animation: none !important } }
```

コツ:

- ドット絵は **コマ送り（`steps(1)` と opacity）** が似合います。なめらかに動かすとドット感が消えます。
- 周期をずらす（9 秒・11 秒・13 秒・17 秒など）と、同じ動きの繰り返しに見えません。
- ずっと動くものは 1 画面に数個まで。どれも小さく。

## 4. 状態クラス

mod は Claude の状態を、SVG のルート要素の `class` として渡します。
SVG 側の CSS はそのクラスを見て、出すもの・速さを変えるだけです。

```html
<svg class="work m-work t-edit p3"> … </svg>
```

| クラス | いつ付くか |
|---|---|
| `work` / `idle` | Claude が作業中か、待機中か（必ずどちらかが先頭） |
| `m-typing` | ターミナル版で入力欄に文字を打っている |
| `m-wait` | 許可や質問へのあなたの返事待ち |
| `m-sleep` | 待機が続いた（標準 3 分） |
| `t-think` | 作業中でツールを使っていない（考えている） |
| `t-term` / `t-read` / `t-search` / `t-edit` / `t-web` / `t-agent` / `t-todo` | 使っているツールの種類（`t-search` のときは `t-read` も付く） |
| `f-heard` | メッセージを受け取った直後 |
| `f-done` / `f-big` | 完了（ステップが多いときは `f-big` も） |
| `f-error` / `f-stopped` | エラーで終わった / 中断された |
| `f-compact` | 会話を圧縮している |
| `p1` … `p5` | このターンで終わったステップの数（5 で頭打ち） |
| `agents` と `a1` … `a3` | サブエージェントが動いている数 |
| `tired` | 利用上限の窓が 80% を超えた |
| `tod-dawn` / `tod-day` / `tod-dusk` | 朝・昼・夕方（夜は何も付かない） |

SVG 側はこう書きます。

```css
.st { display: none }                        /* 状態で出す部品は普段は隠す */
.work .tape { animation: scroll 1.3s steps(16) infinite }   /* 作業中はコードが流れる */
.idle .tape { opacity: .32 }                 /* 待機中は画面を暗く */
.t-term .s-term { display: inline }          /* ターミナル画面 */
.f-done .s-done, .f-done .heart { display: inline }          /* ✓ とハート */
.m-sleep .zz { display: inline }             /* Zz */
```

全部に対応しなくても大丈夫です。`work` と `idle` だけに反応するシーンでも、mod はそのまま動きます。

## 5. mod にする

mod のフォルダはこれだけです。

```
plugin/
  .claude-plugin/plugin.json   名前・説明・バージョン
  hooks/hooks.json             { "modules": ["./register.tsx"] }
  hooks/register.tsx           本体
  hooks/scene.ts               export const SCENE = "<svg …>"（ジェネレーターが書き出す）
  types/index.d.ts             mod が保存する状態の型
  tests/*.test.tsx             テスト
```

`register.tsx` でやることは 3 つです（Pixel District の実物は約 260 行）。

```tsx
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import { SCENE } from './scene'

const working = atom({ plugin: 'my-room', key: 'working' } as const, false)

export const register: Register = on => {
  // ① セッション開始時に「背景はこのシーン」と設定する（色はアプリのまま）
  on('session.start', async ($, e, next) => {
    const set = await $.theme.set({ backdrop: { scene: 'my-room', glass: { blur: 0, opacity: 0.9 } } })
    if (!set.isDrawn) $.ui.status(`My Room: ${set.reason}`)
    return next(e)
  })

  // ② Claude の状態を覚える（ここではメインのターンの開始と終了だけ）
  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) await update($, working, () => true)
    return next(e)
  })
  on('turn.complete', async ($, e, next) => {
    const done = await next(e)
    if (e.agentId === undefined) await update($, working, () => false)
    return done
  })

  // ③ 背景を描くときに、状態をルートのクラスにして SVG を渡す
  on('ui.render', { component: 'Backdrop' }, async ($, e, next) => {
    if (e.props.plugin !== 'my-room') return next(e)
    const { Svg } = $.ui.resolve(e)
    const cls = (await read($, working)) ? 'work' : 'idle'
    return <Svg source={SCENE.replace('class="work"', `class="${cls}"`)} alt="My room" />
  })
}
```

状態が変わると（`update`）背景が自動で描き直されます。
ツールごとの画面・許可待ち・完了・眠りなどは、Pixel District の `plugin/hooks/register.tsx` がそのまま見本になります
（`tool.call`、`tool.check`、`session.compact`、`session.measure`、`prompt.change` のフック）。

`types/index.d.ts` には保存する状態の型を書きます。

```ts
declare module 'claude-code' {
  interface PluginState {
    'my-room': { working: boolean }
  }
}
```

### アプリの色も変えたいとき

Pixel District は背景だけを変えていますが、`$.theme.set({ colors, backdrop })` で Claude のパネルや文字の色も変えられます。
色のセットは Claude Code の mod 作成ガイドにある `makeColors` で、数色の基準色から作ります（コントラストの確認もしてくれます）。
Claude Code に「mod の色テーマを作りたい」と頼むと、手順を案内してくれます。

## 6. 確かめる

1. **プレビュー**: シーンをブラウザで開き、ルートのクラスを書き換えて全部の状態を見ます。
   Pixel District の `preview/states.html` をコピーして、`STATES` を自分のクラスに合わせるのが早いです。
   ```bash
   python3 -m http.server 4039
   ```
2. **mod の検証とテスト**:
   ```bash
   claude plugin validate plugin
   ```
   ```bash
   claude plugin test plugin
   ```
   テスト用の環境では背景の設定（`$.theme.set` の backdrop）は試せないので、描画と状態の変化をテストします。
3. **実機**: [INSTALL.md の方法 2](INSTALL.md) でフォルダを読み込み、デスクトップアプリで新しいセッションを開きます。
   いくつか作業を頼んで、画面の切り替わり・完了・眠りまで見ます。

## 7. 配る

リポジトリのいちばん上に `.claude-plugin/marketplace.json` を置くと、そのリポジトリがマーケットプレイスになります。

```json
{
  "name": "my-room",
  "owner": { "name": "あなたの GitHub アカウント" },
  "plugins": [
    { "name": "my-room", "source": "./plugin", "description": "…", "version": "1.0.0" }
  ]
}
```

```bash
claude plugin validate .
```

push したら、使う人は次の 2 行で入れられます。

```bash
claude plugin marketplace add あなたのアカウント/my-room
```

```bash
claude plugin install my-room@my-room
```

## Claude Code に手伝ってもらう

この手順は全部 Claude Code に頼めます。たとえば:

> 320×200 のドット絵で、雪の降る山小屋の背景 mod を作って。Python のジェネレーターで SVG を書き出して、
> Claude が作業中は暖炉の火が強くなるようにして。動きは小さく。

Pixel District のリポジトリを開いた状態で頼めば、このリポジトリの作りを見本にしてくれます。
