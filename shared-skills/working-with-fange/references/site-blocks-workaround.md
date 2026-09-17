# JS-heavy site + blocked platforms workaround

**Symptom**: A site returns HTTP 200 but curl gets empty HTML (JS-rendered).
B站/YouTube are both blocked on company network. Hermes browser tool
can't connect to the target site. All three paths fail simultaneously.

**Root cause**: Single-page apps deliver no content without JS execution.
Company network blocks major video platforms at the transport level.

**Escalation path**:
1. Try curl first (fastest). If empty HTML → try browser_navigate
2. If browser_navigate times out → try 360/头条 search for tutorial links
3. If B站/YouTube timeout → tell the user: "All paths blocked."
4. **Final fallback**: Ask the user to screenshot the page they have open
   and send it to you for analysis. This is the only remaining path.

**Do NOT**: spend more than 3 attempts trying different URLs or curl flags.
After 3 failures across all paths, immediately escalate to screenshots.

**Example (ACE Studio 2026-07-03)**:
- acestudio.ai → curl 200 but empty HTML
- docs.acestudio.ai → timeout
- B站 search → empty results
- YouTube search → empty results
- 头条 search → only generic descriptions, no tutorials
→ Escalated: asked user for screenshots of the page they had open
