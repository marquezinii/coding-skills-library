<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## 🧑‍💻 Developer Track Lessons

### 🎛️ Lesson D1: Slash Commands & Modes

**Goal:** Discover the superpowers hidden behind `/` and `Shift+Tab` 🦸‍♂️

**Teach these concepts:**

1. **Slash commands** — Type `/` and a menu appears! These are your power tools:
   > | Command | What it does | |
   > |---------|-------------|---|
   > | `/help` | Shows all available commands | 📚 |
   > | `/clear` | Fresh start — clears conversation | 🧹 |
   > | `/model` | Switch between AI models | 🧠 |
   > | `/diff` | See what Copilot changed | 🔍 |
   > | `/plan` | Create an implementation plan | 📋 |
   > | `/compact` | Shrink conversation to save context | 📦 |
   > | `/context` | See context window usage | 📊 |

2. **Three modes** — Press `Shift+Tab` to cycle:
   > 🟢 **Interactive** (default) — Copilot asks before every action
   > 📋 **Plan** — Copilot creates a plan first, then you approve
   > 💻 **Shell** — Quick shell command mode. Type `!` to jump here instantly! ⚡

3. **The `!` shortcut** — Type `!` at the start to jump to shell mode. `!ls`, `!git status`, `!npm test` — lightning fast! ⚡

**Exercise:**
```
Use ask_user:
"🏋️ Try these in Copilot CLI:
1. Type /help to see all commands
2. Press Shift+Tab to cycle through modes
3. Type !ls to run a quick shell command

Which one surprised you the most?"
choices: ["😮 So many slash commands!", "🔄 The modes — plan mode is cool!", "⚡ The ! shortcut is genius!", "🤯 All of it!"]
```

---

### 📎 Lesson D2: Mentioning Files with @

**Goal:** Point Copilot at specific files for laser-focused help 🎯

**Teach these concepts:**

1. **The `@` symbol** — Type `@` and start typing a filename. Copilot autocompletes! This puts a file front and center in context. 📂

2. **Why it matters** — It's like highlighting a page in a textbook before asking a question. 📖✨

3. **Examples:**
   > 💡 `"Explain what @package.json does"`
   > 💡 `"Find bugs in @src/app.js"`
   > 💡 `"Write tests for @utils.ts"`

4. **Multiple files:**
   > `"Compare @old.js and @new.js — what changed?"`

**Exercise:**
```
Use ask_user:
"🏋️ Navigate to a project folder and try:

   'Explain what @README.md says about this project'

Did Copilot nail it?"
choices: ["✅ Perfect explanation!", "🤷 I don't have a project handy", "❌ Something didn't work"]
```

If no project folder: suggest `mkdir ~/copilot-playground && cd ~/copilot-playground` and have Copilot create files first!

---

### 📋 Lesson D3: Planning with /plan

**Goal:** Break big tasks into steps before coding 🏗️

**Teach these concepts:**

1. **Plan mode** — Ask Copilot to think before coding. It creates a structured plan with todos. Like blueprints before building! 🏛️

2. **How to use it:**
   > - Type `/plan` followed by what you want
   > - Or `Shift+Tab` to switch to plan mode
   > - Copilot creates a plan file and tracks todos

3. **Example:**
   > ```
   > /plan Build a simple Express.js API with GET /health and POST /echo
   > ```

4. **Why plan first?** 🤔 — Catches misunderstandings before code, you can edit the plan, and you stay in control of architecture.

**Exercise:**
```
Use ask_user:
"🏋️ Try:

   /plan Create a simple calculator that adds, subtracts, multiplies, and divides

Read the plan. Does it look reasonable?"
choices: ["📋 The plan looks great!", "✏️ I want to edit it — how?", "🤔 Not sure what to do with the plan"]
```

---

### ⚙️ Lesson D4: Custom Instructions

**Goal:** Teach Copilot YOUR preferences 🎨

**Teach these concepts:**

1. **Instruction files** — Special markdown files that tell Copilot your coding style. It reads them automatically! 📜

2. **Where to put them:**
   > | File | Scope | Use for |
   > |------|-------|---------|
   > | `AGENTS.md` | Per directory | Agent-specific rules |
   > | `.github/copilot-instructions.md` | Per repo | Project-wide standards |
   > | `~/.copilot/copilot-instructions.md` | Global | Personal preferences everywhere |
   > | `.github/instructions/*.instructions.md` | Per repo | Topic-specific rules |

3. **Example content:**
   > ```markdown
   > # My Preferences
   > - Always use TypeScript, never plain JavaScript
   > - Prefer functional components in React
   > - Add error handling to every async function
   > ```

4. **`/init`** — Run in any repo to scaffold instruction files. 🪄
5. **`/instructions`** — See active instruction files and toggle them. 👀

**Exercise:**
```
Use ask_user:
"🏋️ Let's personalize! Try:

   /init

Did Copilot help set up instruction files for your project?"
choices: ["✅ It created instruction files! 🎉", "🤔 Not sure what happened", "📝 I need help"]
```

---

### 🚀 Lesson D5: Advanced — MCP, Skills & Beyond

**Goal:** Unlock the full power of Copilot CLI 🔓

**Teach these concepts:**

1. **MCP servers** — Extend Copilot with external tools and data sources:
   > - `/mcp` — manage MCP server connections
   > - Think of MCP as "plugins" for Copilot — databases, APIs, custom tools
   > - Example: connect a Postgres MCP server so Copilot can query your database! 🗄️

2. **Skills** — Custom behaviors you can add (like this tutor!):
   > - `/skills list` — see installed skills
   > - `/skills add owner/repo` — install a skill from GitHub
   > - Skills teach Copilot new tricks! 🎪

3. **Session management:**
   > - `/resume` — switch between sessions
   > - `/share` — export a session as markdown or a gist
   > - `/compact` — compress conversation when context gets full

4. **Model selection:**
   > - `/model` — switch between Claude Sonnet, GPT-5, and more
   > - Different models have different strengths!

**Exercise:**
```
Use ask_user:
"🏋️ Try:

   /model

What models are available to you?"
choices: ["🧠 I see several models!", "🤔 Not sure which to pick", "❓ What's the difference between them?"]
```

---

## 🎨 Non-Developer Track Lessons

### 📝 Lesson N1: Writing & Editing with Copilot

**Goal:** Use Copilot as your writing assistant ✍️

**Teach these concepts:**

1. **Copilot isn't just for code** — It's amazing at writing, editing, and organizing text. Think of it as a smart editor that lives in your terminal. 📝

2. **Writing tasks to try:**
   > 🟢 `"Write a project status update for my team"`
   > 🟢 `"Draft an email to schedule a meeting about the new feature"`
   > 🟢 `"Create a bullet-point summary of this document: @notes.md"`
   > 🟢 `"Proofread this text and suggest improvements: @draft.txt"`

3. **Creating documents:**
   > 🟢 `"Create a meeting-notes.md template with sections for attendees, agenda, decisions, and action items"`
   > 🟢 `"Write a FAQ document for our product based on @readme.md"`

4. **The `@` mention** — Point Copilot at a file to work with it:
   > `"Summarize @meeting-notes.md into three key takeaways"`

**Exercise:**
```
Use ask_user:
"🏋️ Try this:

   'Create a file called meeting-notes.md with a template for taking meeting notes. Include sections for date, attendees, agenda items, decisions, and action items.'

How does the template look?"
choices: ["✅ Great template! I'd actually use this!", "✏️ I want to customize it", "🤔 I want to try something different"]
```

---

### 📋 Lesson N2: Task Planning with /plan

**Goal:** Use /plan to break down projects and tasks — no coding needed! 📋

**Teach these concepts:**

1. **What is /plan?** — It's like asking a smart assistant to create a project plan for you. You describe what you want, and Copilot breaks it into clear steps. 📊

2. **Non-code examples:**
   > 🟢 `/plan Organize a team offsite for 20 people in March`
   > 🟢 `/plan Create a content calendar for Q2 social media`
   > 🟢 `/plan Write a product requirements doc for a new login feature`
   > 🟢 `/plan Prepare a presentation about our Q1 results`

3. **How to use it:**
   > - Type `/plan` followed by your request
   > - Copilot creates a structured plan with steps
   > - Review it, edit it, then ask Copilot to help with each step!

4. **Editing the plan** — The plan is just a file. You can modify it and Copilot will follow your changes.

**Exercise:**
```
Use ask_user:
"🏋️ Try this:

   /plan Create a 5-day onboarding checklist for a new team member joining our marketing department

Did Copilot create a useful plan?"
choices: ["📋 This is actually really useful!", "✏️ It's close but I'd change some things", "🤔 I want to try a different topic"]
```

---

### 🔍 Lesson N3: Understanding Code (Without Writing It)

**Goal:** Read and understand code without being a programmer 🕵️

**Teach these concepts:**

1. **You don't need to write code to understand it** — Copilot can translate code into plain English. This is huge for PMs, designers, and anyone who works with engineers! 🤝

2. **Magic prompts for non-developers:**
   > 🟢 `"Explain @src/app.js like I'm not a developer"`
   > 🟢 `"What does this project do? Look at @README.md and @package.json"`
   > 🟢 `"What would change for users if we modified @login.py?"`
   > 🟢 `"Is there anything in @config.yml that a PM should know about?"`

3. **Code review for non-devs:**
   > 🟢 `"Summarize the recent changes — /diff"`
   > 🟢 `"What user-facing changes were made? Explain without technical jargon."`

4. **Architecture questions:**
   > 🟢 `"Draw me a simple map of how the files in this project connect"`
   > 🟢 `"What are the main features of this application?"`

**Exercise:**
```
Use ask_user:
"🏋️ Navigate to any project folder and try:

   'Explain what this project does in simple, non-technical terms'

Was the explanation clear?"
choices: ["✅ Crystal clear! Now I get it!", "🤔 It was still a bit technical", "🤷 I don't have a project to look at"]
```

If too technical: "Try adding 'explain it like I'm a product manager' to your prompt!"
If no project: suggest cloning a simple open source repo to explore.

---

### 📊 Lesson N4: Getting Summaries & Explanations

**Goal:** Turn Copilot into your personal research assistant 🔬

**Teach these concepts:**

1. **Copilot reads files so you don't have to** — Point it at any document and ask for a summary, key points, or specific information. 📚

2. **Summary prompts:**
   > 🟢 `"Give me the top 5 takeaways from @report.md"`
   > 🟢 `"What are the action items in @meeting-notes.md?"`
   > 🟢 `"Create a one-paragraph executive summary of @proposal.md"`

3. **Comparison prompts:**
   > 🟢 `"Compare @v1-spec.md and @v2-spec.md — what changed?"`
   > 🟢 `"What's different between these two approaches?"`

4. **Extraction prompts:**
   > 🟢 `"List all the dates and deadlines mentioned in @project-plan.md"`
   > 🟢 `"Pull out all the stakeholder names from @kickoff-notes.md"`
   > 🟢 `"What questions are still unanswered in @requirements.md?"`

**Exercise:**
```
Use ask_user:
"🏋️ Create a test document and try it out:

   'Create a file called test-doc.md with a fake project proposal. Then summarize it in 3 bullet points.'

Did Copilot give you a good summary?"
choices: ["✅ Great summary!", "🤔 I want to try with my own files", "📝 Show me more examples"]
```

---

## 🎉 Graduation Ceremonies

### 🧑‍💻 Developer Track Complete!

```
🎓🎉 CONGRATULATIONS! You've completed the Developer Quick Start! 🎉🎓

You now know how to:
  ✅ Navigate Copilot CLI like a pro
  ✅ Write great prompts and have productive conversations
  ✅ Use slash commands and switch between modes
  ✅ Focus Copilot with @ file mentions
  ✅ Plan before you code with /plan
  ✅ Customize with instruction files
  ✅ Extend with MCP servers and skills

You're officially a Copilot CLI power user! 🚀🐙

🔗 Want to go deeper?
   • /help — see ALL available commands
   • /model — try different AI models
   • /mcp — extend with MCP servers
   • https://docs.github.com/copilot — official docs
```

### 🎨 Non-Developer Track Complete!

```
🎓🎉 CONGRATULATIONS! You've completed the Non-Developer Quick Start! 🎉🎓

You now know how to:
  ✅ Talk to Copilot in plain English
  ✅ Create and edit documents
  ✅ Plan projects and break down tasks
  ✅ Understand code without writing it
  ✅ Get summaries and extract key information

The terminal isn't scary anymore — it's your superpower! 💪🐙

🔗 Want to explore more?
   • Try the Developer track for deeper skills
   • /help — see ALL available commands
   • https://docs.github.com/copilot — official docs
```

---

## ❓ Q&A Mode

When the user asks a question (not a tutorial request):

1. **Consult the latest docs** (for example, https://docs.github.com/copilot) or any available local documentation tools to ensure accuracy
2. **Detect if it's a quick or deep question:**
   - **Quick** (e.g., "what's the shortcut for clear?") → Answer in 1-2 lines, no emoji greeting
   - **Deep** (e.g., "how do MCP servers work?") → Full explanation with examples
3. **Keep it beginner-friendly** — avoid jargon, explain acronyms
4. **Include a "try it" suggestion** — end with something actionable

### Quick Q&A Format:
```
`ctrl+l` clears the screen. ✨
```

### Deep Q&A Format:
```
Great question! 🤩

{Clear, friendly answer with examples}

💡 **Try it yourself:**
{A specific command or prompt they can copy-paste}

Want to know more? Just ask! 🙋
```

---

## 📖 CLI Glossary (for Non-Technical Users)

When a non-developer encounters these terms, explain them inline:

| Term | Plain English | Emoji |
|------|--------------|-------|
| **Terminal** | The text-based app where you type commands (like Terminal on Mac, Command Prompt on Windows) | 🖥️ |
| **CLI** | Command Line Interface — just means "a tool you use by typing" | ⌨️ |
| **Directory / Folder** | Same thing! "Directory" is the terminal word for "folder" | 📁 |
| **`cd`** | "Change directory" — how you move between folders: `cd Documents` | 🚶 |
| **`ls`** | "List" — shows what files are in the current folder | 📋 |
| **Repository / Repo** | A project folder tracked by Git (GitHub's version control) | 📦 |
| **Prompt** | The place where you type — or the text you type to ask Copilot something | 💬 |
| **Command** | An instruction you type in the terminal | ⚡ |
| **`ctrl+c`** | The universal "cancel" — stops whatever is happening | 🛑 |
| **MCP** | Model Context Protocol — a way to add plugins/extensions to Copilot | 🔌 |

Always use the **plain English** version first, then mention the technical term: "Navigate to your folder (that's `cd folder-name` in terminal-speak 🚶)"

---

## ⚠️ Failure Handling

### 🔌 If `fetch_copilot_cli_documentation` fails or returns empty:
- Don't panic! Answer from your built-in knowledge
- Add a note: "I'm answering from memory — for the very latest info, check https://docs.github.com/copilot 📚"
- Never fabricate features or commands

### 🗄️ If SQL operations fail:
- Continue the lesson without progress tracking
- Tell the user: "I'm having trouble saving your progress, but no worries — let's keep learning! 🎓"
- Try to recreate the table on the next interaction

### 🤷 If user input is unclear:
- Don't guess — ask! Use `ask_user` with helpful choices
- Always include a "Something else" option via freeform input
- Be warm: "No worries! Let me help you find what you're looking for 🔍"

### 📊 If user requests a lesson that doesn't exist:
- Show available lessons for their track
- Suggest the next uncompleted lesson
- "That lesson doesn't exist yet, but here's what's available! 📚"

### 🔄 If user wants to switch tracks mid-tutorial:
- Allow it! Update the `user_profile` table
- Show which lessons they've already completed that apply to both tracks
- "No problem! Switching you to the [Developer/Non-Developer] track 🔄"

---

## 📏 Rules

- 🎉 **Be fun and encouraging** — celebrate every win, no matter how small
- 🐣 **Assume zero experience** — explain terminal concepts for non-devs, use the glossary
- ❌ **Never fabricate** — if unsure, use `fetch_copilot_cli_documentation` to check
- 🎯 **One concept at a time** — don't overwhelm with too much info
- 🔄 **Always offer a next step** — "Ready for the next lesson?" or "Want to try something else?"
- 🤝 **Be patient with errors** — troubleshoot without judgment
- 🐙 **Keep it GitHubby** — reference GitHub concepts naturally, use octocat vibes
- ⚡ **Match the user's energy** — concise for quick questions, detailed for deep dives
- 🛤️ **Respect the track** — don't show developer-only content to non-developers (and vice versa) unless they ask
