# White Label AI Components

**Version:** 1.0.0
**Status:** Production Ready

## Overview
These components (`SidebarCoPilot`, `AICompletion`) are designed as "Drop-in" AI interfaces for any Xibalba project. They support full white-labeling via props or context.

## Customization Strategy
To use these in different projects (e.g. a Medical App vs a Coding Tool), you should wrap them with a context provider or pass the following props:

### 1. Visual Identity (Theming)
Currently hardcoded to `zinc/orange`. To white label:
- Refactor `bg-zinc-900` -> `bg-[var(--bg-primary)]`
- Refactor `text-orange-500` -> `text-[var(--accent-color)]`

### 2. Contextual Modes
The `mode` selector is flexible. You can inject a `modes` array prop:

```typescript
const medicalModes = [
  { id: 'DIAGNOSTICIAN', label: 'Doctor', desc: 'Symptom Analysis' },
  { id: 'SCRIBE', label: 'Scribe', desc: 'Patient Notes' }
];

<SidebarCoPilot modes={medicalModes} ... />
```

### 3. API Endpoint
Pass the endpoint as a prop to support different backends:
`<SidebarCoPilot apiEndpoint="/api/v1/business/ai" ... />`

## Component List

### SidebarCoPilot.tsx
*   **Role:** Always-on sidecar assistant.
*   **Best For:** Long-form editing, Coding IDEs, Complex Data Entry.

### AICompletion.tsx
*   **Role:** Modal overlay for specific tasks.
*   **Best For:** "One-off" transformations, specific instruction input.

## Integration
Copy this folder to your project's `components` directory and install dependencies (React, Tailwind).
