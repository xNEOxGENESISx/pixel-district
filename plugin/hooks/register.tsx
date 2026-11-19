import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, ThemeBackdropGlass, Timer } from 'claude-code'

import type { SceneState, SceneTool, TimeOfDay } from '../types'
import { SCENE } from './scene'

// ---------------------------------------------------------------------------------------------
// Settings you can change (docs/CUSTOMIZE.md)
// ---------------------------------------------------------------------------------------------

// The chat panels over the scene: no blur, the app's own panel colour at 90%, so text reads on a
// plain background. Lower `opacity` to see more of the room; add `tint: 'rgb(15 11 35)'` for purple.
const GLASS: ThemeBackdropGlass = { blur: 0, opacity: 0.9 }

// How long the small moments stay up, and when the cat falls asleep.
const FLASH_MS = 3500 // done ✓, error, stopped
const HEARD_MS = 2000 // the "!" when you send a message
const TOOL_HOLD_MS = 1500 // a fast tool's screen stays up at least this long
const TYPING_MS = 5000 // the "…" bubble while you type (terminal only)
const SLEEP_AFTER_MS = 3 * 60 * 1000 // idle this long → the cat sleeps
const TOD_CHECK_MS = 10 * 60 * 1000 // how often the sky checks the clock
const BIG_FINISH_PIPS = 6 // a turn with this many finished steps ends with the big finish
const TIRED_AT_PERCENT = 80 // a rate-limit window this full → the mug is empty

const ALT = 'Pixel District: a night pixel room with two cats; the grey one codes while Claude works'

// ---------------------------------------------------------------------------------------------

const SCENE_ID = 'pixel-district'
const IDLE_SCENE: SceneState = { mode: 'idle', tool: '', flash: '', pips: 0, agents: 0, tired: false, tod: 'night' }
const sceneAtom = atom({ plugin: 'pixel-district', key: 'scene' } as const, IDLE_SCENE)

// Which screen the desk cat's monitor shows for a tool.
export function toolKind(tool: string): SceneTool {
  if (/^(Bash|BashOutput|KillShell|PowerShell)$/.test(tool)) return 'term'
  if (/^(Grep|Glob)$/.test(tool)) return 'search'
  if (/^(Read|LS|NotebookRead)$/.test(tool)) return 'read'
  if (/^(Edit|Write|MultiEdit|NotebookEdit)$/.test(tool)) return 'edit'
  if (/^(WebSearch|WebFetch)$/.test(tool) || /^mcp__.*(browser|chrome|navigate|fetch)/i.test(tool)) return 'web'
  if (/^(Agent|Task)$/.test(tool)) return 'agent'
  if (/^(TodoWrite|TaskCreate|TaskUpdate)$/.test(tool) || /^mcp__.*update_plan$/.test(tool)) return 'todo'
  return ''
}

// Tools that stop and wait for you: the cat turns round with a "?".
const WAITS_FOR_PERSON = new Set(['AskUserQuestion', 'ExitPlanMode'])

export function timeOfDay(now: Date): TimeOfDay {
  const h = now.getHours()
  if (h >= 5 && h < 8) return 'dawn'
  if (h >= 8 && h < 17) return 'day'
  if (h >= 17 && h < 19) return 'dusk'
  return 'night'
}

// The classes the scene's root wears. The CSS inside scene.svg reacts to them.
export function rootClass(s: SceneState): string {
  const cls = [s.mode === 'work' ? 'work' : 'idle', `m-${s.mode}`]
  if (s.mode === 'work') {
    // no tool running = the model is thinking; search also counts as read
    cls.push(s.tool === '' ? 't-think' : `t-${s.tool}`)
    if (s.tool === 'search') cls.push('t-read')
  }
  if (s.flash !== '') cls.push(`f-${s.flash}`)
  if (s.flash === 'big') cls.push('f-done')
  if (s.pips > 0) cls.push(`p${Math.min(5, s.pips)}`)
  if (s.agents > 0) cls.push('agents', `a${Math.min(3, s.agents)}`)
  if (s.tired) cls.push('tired')
  if (s.tod !== 'night') cls.push(`tod-${s.tod}`)
  return cls.join(' ')
}

// Timers live in the module: a reload starts them over, which only delays a nap or a fade.
let flashTimer: Timer | undefined
let typingTimer: Timer | undefined
let sleepTimer: Timer | undefined
let toolTimer: Timer | undefined
let activeTools = 0

async function patch($: EngineInterface, change: Partial<SceneState>): Promise<void> {
  await update($, sceneAtom, s => {
    const next = { ...s, ...change }
    // write only when something drawn changes, so the scene isn't redrawn for nothing
    return rootClass(next) === rootClass(s) && next.pips === s.pips ? s : next
  })
}

function flash($: EngineInterface, kind: SceneState['flash'], ms = FLASH_MS): void {
  flashTimer?.cancel()
  void patch($, { flash: kind })
  flashTimer = $.clock.after(ms, () => {
    void update($, sceneAtom, (s): SceneState => (s.flash === kind ? { ...s, flash: '' } : s))
  })
}

function armSleep($: EngineInterface): void {
  sleepTimer?.cancel()
  sleepTimer = $.clock.after(SLEEP_AFTER_MS, () => {
    void update($, sceneAtom, (s): SceneState => (s.mode === 'idle' ? { ...s, mode: 'sleep', flash: '' } : s))
  })
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    activeTools = 0
    await update($, sceneAtom, () => ({ ...IDLE_SCENE, tod: timeOfDay(new Date()) }))
    $.clock.every(TOD_CHECK_MS, () => void patch($, { tod: timeOfDay(new Date()) }))
    armSleep($)

    try {
      // only the backdrop: Claude's own panels and text keep the app's colours
      const set = await $.theme.set({ backdrop: { scene: SCENE_ID, glass: GLASS } })
      $.ui.status(set.isDrawn ? undefined : `Pixel District: ${set.reason}`)
    } catch (error) {
      $.ui.status(`Pixel District: the theme was refused (${String(error)})`)
    }

    return next(e)
  })

  // You typing in the box (terminal only): a "…" bubble, back to idle when you pause.
  on('prompt.change', async ($, e, next) => {
    const scene = await read($, sceneAtom)

    if (scene.mode === 'idle' || scene.mode === 'sleep' || scene.mode === 'typing') {
      typingTimer?.cancel()

      if (e.text.trim() === '') {
        await patch($, { mode: 'idle' })
        armSleep($)
      } else {
        sleepTimer?.cancel()
        await patch($, { mode: 'typing' })
        typingTimer = $.clock.after(TYPING_MS, () => {
          void update($, sceneAtom, (s): SceneState => (s.mode === 'typing' ? { ...s, mode: 'idle' } : s))
          armSleep($)
        })
      }
    }

    return next(e)
  })

  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) {
      typingTimer?.cancel()
      sleepTimer?.cancel()
      flashTimer?.cancel()
      toolTimer?.cancel()
      activeTools = 0
      await patch($, { mode: 'work', tool: '', pips: 0 })
      // the desktop box doesn't report typing to mods, so the cat "hears" you when you send
      flash($, 'heard', HEARD_MS)
    } else {
      // a helper agent started: a second cat comes to help
      await update($, sceneAtom, s => ({ ...s, agents: s.agents + 1 }))
    }

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const done = await next(e)

    if (e.agentId !== undefined) {
      await update($, sceneAtom, s => ({ ...s, agents: Math.max(0, s.agents - 1) }))

      return done
    }

    activeTools = 0
    toolTimer?.cancel()
    const { pips } = await read($, sceneAtom)
    await patch($, { mode: 'idle', tool: '' })
    const kind = e.reason === 'answer' ? (pips >= BIG_FINISH_PIPS ? 'big' : 'done') : e.reason === 'aborted' ? 'stopped' : 'error'
    flash($, kind)
    armSleep($)

    return done
  })

  // A permission prompt is up: the desk cat turns to you with a "?".
  on('tool.check', async ($, e, next) => {
    const verdict = await next(e)

    if (verdict.decision === 'ask') {
      await update($, sceneAtom, (s): SceneState => (s.mode === 'work' ? { ...s, mode: 'wait' } : s))
    }

    return verdict
  })

  // Each tool shows its own screen; each finished step adds a pip.
  on('tool.call', async ($, e, next) => {
    activeTools += 1
    const kind = toolKind(e.tool)

    if (WAITS_FOR_PERSON.has(e.tool)) {
      await patch($, { mode: 'wait' })
    } else if (kind !== '') {
      toolTimer?.cancel() // a new screen replaces the held one
      await patch($, { mode: 'work', tool: kind })
    } else {
      await patch($, { mode: 'work' })
    }

    try {
      return await next(e)
    } finally {
      activeTools = Math.max(0, activeTools - 1)
      await update($, sceneAtom, (s): SceneState => {
        if (s.mode === 'idle' || s.mode === 'sleep') {
          return s // the turn already ended
        }

        return { ...s, mode: 'work', pips: s.pips + 1 }
      })

      if (activeTools === 0) {
        toolTimer?.cancel()
        toolTimer = $.clock.after(TOOL_HOLD_MS, () => {
          if (activeTools === 0) {
            void patch($, { tool: '' })
          }
        })
      }
    }
  })

  on('session.compact', async ($, e, next) => {
    flashTimer?.cancel()
    await patch($, { flash: 'compact' })

    try {
      return await next(e)
    } finally {
      await patch($, { flash: '' })
    }
  })

  on('session.measure', async ($, e, next) => {
    await patch($, { tired: e.rateLimits.some(limit => limit.percentUsed >= TIRED_AT_PERCENT) })

    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, async ($, e, next) => {
    if ((e.surface !== 'desktop' && e.surface !== 'mobile') || e.props.plugin !== 'pixel-district' || e.props.scene !== SCENE_ID) {
      return next(e)
    }

    const state = await read($, sceneAtom)
    const { Svg } = $.ui.resolve(e)

    return <Svg source={SCENE.replace('class="work"', `class="${rootClass(state)}"`)} alt={ALT} />
  })
}
