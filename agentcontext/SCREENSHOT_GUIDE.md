# Screenshot Capture Guide

## When to Capture: 4:00 PM - 4:15 PM

**Purpose:** Create backup screenshots in case the live demo fails during the pitch.

---

## Required Screenshots

### 1. Graph Visualization (`backup_graph.png`)

**What to capture:**
- Full Streamlit app window with graph rendered
- All nodes visible with color coding
- Edges showing relationships
- Graph statistics (node/edge counts)
- Color legend visible

**Steps:**
1. Open app: `streamlit run app.py`
2. Wait for graph to stabilize (physics layout settles)
3. Ensure all 4 nodes are visible
4. Take full-window screenshot
5. Save as: `backup_graph.png` in project root

**Quality checklist:**
- [ ] All nodes clearly visible
- [ ] Node labels readable
- [ ] Edge labels visible
- [ ] Color legend present
- [ ] No error messages
- [ ] Browser chrome (URL bar, etc.) excluded

---

### 2. Agent Recommendation (`backup_rec.png`)

**What to capture:**
- Complete recommendation panel
- Target column highlighted
- Feature table recommendations expanded
- Confidence indicators visible
- SQL scaffold (optional but nice)

**Steps:**
1. Enter query: "What data should I use to predict target_outcome?"
2. Click "Find relevant data" button
3. Wait for full recommendation to load
4. Expand first feature table recommendation
5. Scroll to show complete recommendation section
6. Take screenshot from "Recommendation" header to footer
7. Save as: `backup_rec.png` in project root

**Quality checklist:**
- [ ] Target column visible with green success box
- [ ] At least one feature table expanded
- [ ] Confidence icons visible (🟢🟡🔴)
- [ ] Reasoning text readable
- [ ] No loading spinners
- [ ] No error messages
- [ ] Full width captured

---

### 3. Complete End-to-End (`backup_full.png`) - Optional

**What to capture:**
- Full page from title to footer
- Both graph and recommendation visible
- Shows complete workflow

**Steps:**
1. Zoom out browser to 75%
2. Scroll to top
3. Take full-page screenshot (use browser extension or tool)
4. Save as: `backup_full.png`

---

## Screenshot Tools

### macOS
```bash
# Full screen
Cmd + Shift + 3

# Selected area
Cmd + Shift + 4

# Specific window
Cmd + Shift + 4, then Space, then click window
```

### Windows
```bash
# Full screen
PrtScn key

# Active window
Alt + PrtScn

# Snip tool
Windows + Shift + S
```

### Linux
```bash
# Full screen
PrtScn key

# Selected area
Shift + PrtScn

# Specific window
Alt + PrtScn
```

### Browser Extensions (Recommended)
- **Awesome Screenshot** (Chrome/Firefox)
- **Nimbus Screenshot** (Chrome/Firefox)
- **Fireshot** (Chrome/Firefox)

**Why browser extensions:** Can capture full page scroll, not just visible area

---

## Image Requirements

### Resolution
- **Minimum:** 1920x1080 (Full HD)
- **Recommended:** 2560x1440 (2K) or higher
- **Format:** PNG (not JPG - better quality for screenshots)

### File Size
- Should be < 5MB each
- If larger, use PNG compression tool

### Content
- All text must be readable at 1080p display
- No personal information visible (emails, API keys, etc.)
- No system notifications or popups
- Clean browser (no distracting tabs or bookmarks)

---

## Verification

After capturing, verify each screenshot:

```bash
# Check if files exist
ls -lh backup_*.png

# Open and inspect
# macOS:
open backup_graph.png
open backup_rec.png

# Linux:
xdg-open backup_graph.png
xdg-open backup_rec.png

# Windows:
start backup_graph.png
start backup_rec.png
```

**Visual checks:**
- [ ] Text is sharp and readable
- [ ] Colors are accurate
- [ ] No pixelation or artifacts
- [ ] Full content captured (not cropped)
- [ ] File opens without errors

---

## Storage & Access

**Location:**
```
DatabricksOntology/
├── backup_graph.png        # Graph visualization
├── backup_rec.png          # Agent recommendation
└── backup_full.png         # Optional full page
```

**Backup copies:**
1. Save to cloud (Google Drive, Dropbox)
2. Send to team Slack channel
3. Keep on local device

**Access during demo:**
- Have image viewer open before demo starts
- Screenshots in separate window
- Easy to switch to if live demo fails

---

## Usage During Demo

### If live demo fails:

1. **Stay calm** - Don't apologize
2. **Switch to screenshots** - Alt+Tab or Cmd+Tab to image viewer
3. **Narrate** - Use same script as live demo
4. **Point** - Use cursor to highlight key elements
5. **Keep timing** - Still aim for 60 seconds

### Script adaptation:

**Live demo:**
> "I'll ask it: What data should I use to predict X?"

**Screenshot demo:**
> "When we ask: What data should I use to predict X, the system returns..."

**Transition smoothly:**
> "Let me show you what this looks like..." [switch to screenshot]

---

## Testing Screenshots

**Do a dry run with screenshots:**

1. Close Streamlit app (simulate failure)
2. Open screenshots
3. Practice narrating over static images
4. Time yourself - should still be ~60 seconds
5. Verify all key points are visible in screenshots

---

## Additional Tips

### Lighting & Display
- Use bright screen setting for screenshots
- Disable dark mode (better contrast)
- Close all unrelated apps/windows

### Browser Preparation
- Use incognito/private mode (clean slate)
- Zoom to 100% (standard size)
- Full screen mode (F11 on Windows/Linux, Cmd+Ctrl+F on macOS)

### Streamlit App Settings
- Ensure "wide" layout mode is active
- Check color legend is visible
- Verify all UI elements loaded fully

---

## Troubleshooting

**Screenshot is blurry:**
- Increase browser zoom to 125%
- Take screenshot
- Reduce back to 100% in image editor

**Can't capture full page:**
- Use browser extension (Awesome Screenshot)
- Or take multiple screenshots and stitch

**File size too large:**
- Use PNG compression: `pngquant backup_graph.png`
- Or reduce resolution slightly

**Colors look wrong:**
- Check monitor color calibration
- Ensure sRGB color profile
- Avoid screenshots with Night Shift/f.lux active

---

## Final Checklist

**Before 4:15 PM:**
- [ ] `backup_graph.png` captured and verified
- [ ] `backup_rec.png` captured and verified
- [ ] Screenshots saved in project root
- [ ] Backup copies in cloud storage
- [ ] Screenshots tested in image viewer
- [ ] Team has access to screenshots
- [ ] Demo narration over screenshots practiced

**Quality checks:**
- [ ] All text readable at normal viewing distance
- [ ] Colors match live app
- [ ] No errors or loading states visible
- [ ] Professional appearance (no clutter)

---

## Success Criteria

**Screenshots are ready when:**
- ✅ Files exist and open without errors
- ✅ All key information visible and readable
- ✅ Team can narrate over them confidently
- ✅ Backup plan tested and smooth
- ✅ Stored in multiple locations

**If screenshots aren't perfect:**
- That's okay! They're a fallback only
- Live demo is always preferred
- Screenshots just need to convey the concept

---

**Remember:** Screenshots are insurance. The goal is to never need them. But if the live demo fails, you'll be glad you have high-quality backups to fall back on.

---

**Capture deadline:** 4:15 PM
**Verification:** 4:20 PM
**Final check:** 4:45 PM (before demo)
