// What the room shows. The scene reads it as classes on its root (work/idle always present).
export type SceneMode = 'idle' | 'work' | 'wait' | 'typing' | 'sleep'
// search also writes t-read
export type SceneTool = '' | 'term' | 'read' | 'search' | 'edit' | 'web' | 'agent' | 'todo'
// big = a long turn finished (also writes f-done)
export type SceneFlash = '' | 'heard' | 'done' | 'big' | 'error' | 'stopped' | 'compact'
export type TimeOfDay = 'night' | 'dawn' | 'day' | 'dusk'

export type SceneState = {
  mode: SceneMode
  tool: SceneTool
  flash: SceneFlash
  // finished steps this turn, shown as pips (capped at 5 when drawn)
  pips: number
  // helper agents running now
  agents: number
  // a rate-limit window is nearly used up
  tired: boolean
  tod: TimeOfDay
}

declare module 'claude-code' {
  interface PluginState {
    'pixel-district': {
      // what the backdrop shows right now
      scene: SceneState
    }
  }
}
