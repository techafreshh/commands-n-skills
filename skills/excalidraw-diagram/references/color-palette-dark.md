# Color Palette — Dark Mode Variant

**Companion to `color-palette.md`.** Use this palette when a diagram is requested in dark mode:
set `appState.viewBackgroundColor` to `#0f172a` and take every stroke/fill/text color from here.
The contrast rule inverts: pair a **darker muted fill with a lighter stroke**.

---

## Canvas

| Property | Value |
|----------|-------|
| Background | `#0f172a` |

## Shape Colors (Semantic)

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#1e3a5f` | `#60a5fa` |
| Secondary | `#334155` | `#94a3b8` |
| Start/Trigger | `#7c2d12` | `#fb923c` |
| End/Success | `#064e3b` | `#34d399` |
| Warning/Reset | `#7f1d1d` | `#f87171` |
| Decision | `#78350f` | `#fbbf24` |
| AI/LLM | `#4c1d95` | `#a78bfa` |
| Inactive/Disabled | `#1e293b` | `#64748b` (dashed stroke) |
| Error | `#7f1d1d` | `#ef4444` |

## Text Colors (Hierarchy)

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#93c5fd` | Section headings, major labels |
| Subtitle | `#60a5fa` | Subheadings, secondary labels |
| Body/Detail | `#94a3b8` | Descriptions, annotations, metadata |
| On dark fills | `#e2e8f0` | Text inside dark-filled shapes |
| Accent on dark | `#fbbf24` | Emphasis inside decision/amber shapes |

## Evidence Artifact Colors

| Artifact | Background | Stroke | Text Color |
|----------|-----------|--------|------------|
| Code snippet / data example | `#1e293b` | `#334155` | `#e2e8f0` (prose), `#4ade80` (data/values) |

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Source element's stroke color |
| Structural lines (lifelines, dividers, timelines) | `#475569` |
| Marker dots | `#60a5fa` |
| Section boundaries | `#475569` (dashed) |
