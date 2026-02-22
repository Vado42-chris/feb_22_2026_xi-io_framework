# Xibalba Universal Interaction Standard (XUIS)

**Concept:** "One Interface, Infinite Contexts."

## The Core Thesis
All AI interactions—whether directing a movie, writing code, or managing a team of agents—follow the same fundamental loop:
1.  **Input** (Text/Voice/Asset)
2.  **Process** (Single Agent / Swarm)
3.  **Artifact** (Text/Code/Media)
4.  **Refinement** (Chat/Edit)

Therefore, we do not need different UIs. We need **one** UI with deep configuration.

## Component Architecture: `<UniversalChat />`

### 1. Configuration Props (The Variables)
Instead of hardcoding "Editor" or "Coder", we pass a `context` object:

```typescript
interface ChatContext {
  level: 'ORCHESTRATOR' | 'EXECUTOR'; // The "2 Types"
  domain: 'TEXT' | 'CODE' | 'MEDIA' | 'AUDIO';
  topology: 'SINGLE' | 'SWARM';
  theme: ThemeConfig;
}
```

### 2. The Two Primary Modes

#### Mode A: Orchestration (The Conductor)
*   **Role:** Planning, Routing, High-level direction.
*   **UI variance:**
    *   Input: Broad directives ("Make a sci-fi movie").
    *   Output: Plans, Timelines, Agent assignments (Graph view?).
    *   *Example Config:* `{ level: 'ORCHESTRATOR', domain: 'MEDIA', topology: 'SWARM' }`

#### Mode B: Execution (The Performer)
*   **Role:** Development, Design, Doing.
*   **UI variance:**
    *   Input: Specific instructions ("Fix this function", "Rewrite paragraph 2").
    *   Output: Raw Artifacts (Code blocks, Text, Image URLs).
    *   *Example Config:* `{ level: 'EXECUTOR', domain: 'CODE', topology: 'SINGLE' }`

### 3. Implementation Strategy (White Label)

We can refactor `SidebarCoPilot` to become `UniversalChat`.

**Prop Injection:**
```tsx
// Scenario 1: The Code Editor
<UniversalChat 
  config={{ level: 'EXECUTOR', domain: 'CODE' }}
  actions={['Generate Snippet', 'Explain', 'Debug']}
/>

// Scenario 2: The Movie Director
<UniversalChat 
  config={{ level: 'ORCHESTRATOR', domain: 'MEDIA' }}
  actions={['Generate Script', 'Cast Actors', 'Scout Locations']}
  visualization="TIMELINE" // Optional prop for orchestration views
/>
```

## Standardization Value
*   **Efficiency:** Build the "Chat Bubble", "Input Box", and "History" ONCE.
*   **Consistency:** Users feel at home whether they are coding or writing music.
*   **Scalability:** Adding a "Songwriter" mode is just a config file, not a new UI.
