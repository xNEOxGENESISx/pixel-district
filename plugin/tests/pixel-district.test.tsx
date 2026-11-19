import type { On } from 'claude-code'
import { expect, test, type Engine } from 'claude-code/testing'

import { rootClass, timeOfDay, toolKind } from '../hooks/register.js'

// The test kit refuses any `backdrop` in $.theme.set, so putting the look on is checked live in the
// app; these cover the state machine and the drawing.
function engine(on: On) {
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('turn.start', () => ({ turnId: 't1' }))
  on('tool.call', () => ({ result: {} }))
}

const BACKDROP = {
  plugin: 'pixel-district',
  component: 'Backdrop',
  surface: 'desktop',
  props: { scene: 'pixel-district', plugin: 'pixel-district', glass: { blur: 0, opacity: 0.9 } },
} as const

// A main-loop turn, or a helper agent's turn when agentId is given.
const turn = ($: Engine, agentId?: string) => $.turn.start({ text: 'hi', turnId: agentId ?? 't1', agentId })

async function drawn($: Engine): Promise<string> {
  const ui = await $.ui.mount(BACKDROP)
  const source = String((await ui.find({ type: 'Svg' }))?.props.source)
  await ui.unmount()

  return /class="([^"]*)"/.exec(source)?.[1] ?? ''
}

test('tools map to monitor screens', async () => {
  expect(toolKind('Bash')).toBe('term')
  expect(toolKind('Grep')).toBe('search')
  expect(toolKind('Read')).toBe('read')
  expect(toolKind('Edit')).toBe('edit')
  expect(toolKind('WebFetch')).toBe('web')
  expect(toolKind('Agent')).toBe('agent')
  expect(toolKind('TodoWrite')).toBe('todo')
  expect(toolKind('SomethingElse')).toBe('')
})

test('time of day follows the clock', async () => {
  expect(timeOfDay(new Date(2026, 0, 1, 6))).toBe('dawn')
  expect(timeOfDay(new Date(2026, 0, 1, 12))).toBe('day')
  expect(timeOfDay(new Date(2026, 0, 1, 18))).toBe('dusk')
  expect(timeOfDay(new Date(2026, 0, 1, 23))).toBe('night')
})

test('root classes: work/idle first, search also reads, pips and helpers capped', async () => {
  const base = { mode: 'work', tool: 'search', flash: 'big', pips: 9, agents: 7, tired: true, tod: 'dusk' } as const
  expect(rootClass(base)).toBe('work m-work t-search t-read f-big f-done p5 agents a3 tired tod-dusk')
  expect(rootClass({ ...base, mode: 'sleep', flash: '', pips: 0, agents: 0, tired: false, tod: 'night' })).toBe('idle m-sleep')
})

test('idle, then working during a turn, with the tool’s screen and a pip per finished step', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect((await drawn($)).startsWith('idle m-idle')).toBe(true)

  await turn($)
  const working = await drawn($)
  expect(working.startsWith('work m-work t-think')).toBe(true)
  expect(working).toContain('f-heard')

  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.tool.call({ tool: 'Read', file_path: '/x' })
  expect(await drawn($)).toContain('p2')
})

test('helper agents bring a helper cat', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await turn($)
  await turn($, 'helper-1')
  await turn($, 'helper-2')
  expect(await drawn($)).toContain('agents a2')
})

test('a long answered turn ends with the big finish (and still says done)', async ($, on) => {
  engine(on)
  on('turn.complete', () => ({ text: 'ok' }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await turn($)

  for (let i = 0; i < 6; i += 1) {
    await $.tool.call({ tool: 'Read', file_path: `/f${i}` })
  }

  await $.turn.complete({ reason: 'answer', answer: 'ok', durationMs: 1, isAborted: false, turnId: 't1' })
  const end = await drawn($)
  expect(end.startsWith('idle m-idle')).toBe(true)
  expect(end).toContain('f-big')
  expect(end).toContain('f-done')
})

test('another plugin’s backdrop is left alone', async ($, on) => {
  engine(on)
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>engine</Text>
  })

  const ui = await $.ui.mount({ ...BACKDROP, props: { ...BACKDROP.props, plugin: 'someone-else' } })
  expect((await ui.find({ type: 'Svg' })) === undefined).toBe(true)
  await ui.unmount()
})
