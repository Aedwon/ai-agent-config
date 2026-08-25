# Web Application Overlay

Baseline: `software-project.md`

Add these rules when browsers, servers, and network delivery form the product
boundary.

- Verify current framework behavior from authoritative documentation before
  relying on version-sensitive features.
- Place data access and secrets on the server side of explicit client/server
  boundaries.
- Verify critical flows in a real browser, including navigation, errors, and
  hydration or progressive-enhancement behavior.
- Check responsive behavior from narrow touch layouts through wide desktop
  layouts.
- Apply semantic markup, keyboard support, visible focus, accessible names, and
  sufficient contrast.
- Treat caching, routing, environment configuration, and deployment behavior as
  release concerns with separate evidence and authority.
