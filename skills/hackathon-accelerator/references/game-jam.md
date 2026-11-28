# Game Jams

Use this whenever the event is a game jam, or the user says "game jam", "jam", "Ludum Dare", "GMTK", "itch.io", or names an engine (Roblox, Godot, Unity, Unreal). The `game-designer` agent leads; the usual phases still apply, but the deliverable is a **playable game** and its itch.io (or Roblox) page, not a pitch.

## How jams are judged
- **Players rate after a few minutes of play.** Typical categories: Overall, Fun, Innovation, Theme, Graphics, Audio, Humor, Mood. Read the jam's own list into `HACKATHON_BRIEF.md`.
- **Web builds get played far more.** A download-only game gets a fraction of the ratings.
- **The first 30 seconds decide it.** Clear goal, instant control, juicy feedback, quick restart.
- **Rules to check in Phase 1:** solo vs team, theme announcement time, pre-made code or asset rules (Ludum Dare Compo vs Jam differ), required tags, submission window, AI-generated content rules.

## Step 0: connect Claude Code to the engine (do this first)
Ask which engine the team uses, then check whether it's connected: run `detect_environment.py` or `/mcp` in Claude Code. If it isn't connected, give the user **these exact steps** before any building. After connecting, restart Claude Code and run `/mcp` to confirm the server shows as connected.

### Roblox Studio (official, built into Studio)
1. Update Roblox Studio and Claude Code to the latest versions.
2. In Studio, open **Assistant**, click **…** → **Manage MCP Servers**, and turn on **Enable Studio as MCP server**.
3. Under **Quick connect**, turn on **Claude Code**. (If it isn't listed, restart Studio.)
4. Manual alternative, from a terminal in your project folder:
   - Windows: `claude mcp add --transport stdio Roblox_Studio -- cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat`
   - macOS: `claude mcp add --transport stdio Roblox_Studio -- /Applications/RobloxStudio.app/Contents/MacOS/StudioMCP`
5. Restart Studio and Claude Code. In Studio, the MCP panel shows a green dot with the number of connected clients.
6. Keep the place open in Studio while you work. Claude can read the game tree, edit scripts, run Luau and start playtests.
- Optional, if you prefer files and git: Rojo (`rojo serve`) syncs a `src/` folder into Studio, so Claude edits `.luau` files directly.

### Godot 4
1. Install Node.js 18+ (`winget install OpenJS.NodeJS.LTS` · `brew install node`).
2. From your Godot project folder: `claude mcp add godot -- npx @coding-solo/godot-mcp`
3. If Godot isn't on your PATH, add its location: `claude mcp add godot -e GODOT_PATH="C:\Godot\Godot_v4.x.exe" -- npx @coding-solo/godot-mcp` (macOS: `/Applications/Godot.app/Contents/MacOS/Godot`).
4. Restart Claude Code and run `/mcp`. Claude can launch the editor, run the project, read debug output, and create scenes and nodes.
- Godot projects are plain text (`.gd`, `.tscn`), so Claude can also edit them directly without MCP.

### Unity (official plugin)
1. Inside Claude Code: `/plugin marketplace add Unity-Technologies/unity-agent-plugin`, then `/plugin install unity@unity-agent-plugin`.
2. Install the **Unity CLI** (Unity's docs: docs.unity.com → Unity CLI), then in your project folder run `unity pipeline install`.
3. Open the project in the Unity Editor and check the CLI reaches it: `unity status`.
4. Optional live Editor control over MCP: `unity mcp configure`.
5. Type `/unity:` in Claude Code to see Unity's skills.

### Unreal Engine (official, Epic)
1. In Claude Code: `/plugin install unreal-engine-skills-for-claude-code@claude-plugins-official` (if that marketplace is missing: `/plugin marketplace add anthropics/claude-plugins-official` first).
2. In the editor, go to **Edit → Plugins**. Check **Unreal MCP** is enabled and enable **All Toolsets**, then restart the editor.
3. Go to **Edit → Editor Preferences → Agentic Workflows → Model Context Protocol**. Keep **Auto Start Server** on (default `http://127.0.0.1:8000/mcp`). Under **MCP Client**, choose **Claude Code** and click **Generate Client Config**. This writes `.mcp.json` into the project folder.
4. With the editor running, open a terminal in that folder and start `claude`. Ask "What actors do I have selected?" to confirm.
- Unreal MCP is marked Experimental in Epic's docs. Keep the editor open and save often.

### Other engines
- **Phaser, Three.js, Kaboom, plain HTML5 canvas:** no MCP needed. Claude edits the code, and the hackathon-ui and demo-video tools work directly. Best choice for web-first jams.
- **PICO-8, GameMaker, Love2D, Bevy:** code-only workflow, so Claude edits files and you run the game.

If a connection fails: restart both apps, confirm the path or command exists, then run `claude mcp list`. Remove a broken entry with `claude mcp remove <name>` and add it again.

## Jam plan (scale to the jam length)
| Share of time | Goal |
|---|---|
| 0–5% | Theme brainstorm (8 interpretations) → pick → one-line pitch |
| 5–40% | Core loop playable with placeholder art: one level, controls feel good |
| 40–75% | Content (3–5 levels or a difficulty curve), real art, game feel |
| 75–90% | Audio, menus, tutorial-by-design, fix bugs, playtest with someone new |
| 90–100% | Web build, itch.io page, submit early (uploads fail at the deadline) |

## Game feel (the cheapest big win)
Screen shake on impact · hit-stop of 50–100 ms · particles on every important event · squash and stretch · eased movement (no linear tweens) · sound on every action, with randomized pitch · camera smoothing · a satisfying death and a restart in under 1 second · readable UI with big numbers.

## The itch.io page (or the Roblox game page)
- A GIF of the best 5 seconds at the top, then 3–5 screenshots.
- The one-line pitch, how it fits the theme, the controls, and the team with roles.
- Credits and licenses for every asset, font, sound and tool. State AI use if the jam asks.
- The jam's required tags and the submission linked to the jam page.
- Embed size set (for example 960×540) with a fullscreen button. Test the web build in a private window.
- Roblox: a thumbnail and icon, a description with controls, and the place set to public before judging.

## Demo video for a game
Record gameplay with the engine's recorder, OBS or Win+G, then stitch with `make_video.py` (title card, 3–4 gameplay clips with captions, end card). For web games, `demo_video.py` can drive the browser build directly with `press` actions.
