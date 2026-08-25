# Project-Type Overlays

Project types add reusable rules after the universal core and project-local
rules. Start with `software-project.md` for technical work, then add the one
overlay that best matches the product. Combine overlays only when each captures
a real, independent risk.

The software baseline owns common engineering rules. Every other file contains
deltas only and declares its baseline. Project rules win when a local decision
needs stricter behavior.

| Overlay | Use when |
| --- | --- |
| `software-project.md` | Code, automation, or configuration is a main output |
| `product-app.md` | People create durable state through an interactive product |
| `web-app.md` | Browser and server boundaries shape behavior and delivery |
| `bot-service.md` | Event-driven or background operation must recover safely |
| `content-heavy.md` | Sourced content and editorial review are primary risks |
| `utility-script.md` | A focused tool needs low ceremony and predictable input/output |
