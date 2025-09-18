# CBV Keyword Graph Explorer

A keyword graph visualization tool that allows users to explore multilingual trade terminology and their relationships without requiring documents or SQL databases.

## Files Structure

```
CBV_graph/
├── CBV_thesaurus_v4.rdf    # Original RDF thesaurus file
├── parse_thesaurus.py      # Script to extract data from RDF
├── server.py              # HTTP server for proper JSON serving
├── cbv_data.json          # Unified data file (keywords + relationships + translations)
├── keyword_list.json       # Simplified keyword list for search
├── index.html             # Landing page
├── graph.html             # Main graph visualization
└── README.md              # This file
```

## Quick Start

1. **Generate Data Files** (if not already done):
   ```bash
   python parse_thesaurus.py
   ```

2. **Start the Server**:
   ```bash
   python server.py
   ```

3. **Launch the Explorer**:
   - **Main interface**: `http://localhost:8000`
   - **Direct graph access**: `http://localhost:8000/graph.html`
   - **Custom port**: `python server.py 8080` (then visit `http://localhost:8080`)

### Server Features
- ✅ Serves JSON files with proper CORS headers
- ✅ Automatic content-type detection  
- ✅ Clean request logging
- ✅ Custom port support
- ✅ Handles browser security restrictions

## Usage

### Navigation
- **Start**: Visit the index page for keyword selection
- **Browse**: Use popular keywords, search, or filter by alphabet
- **Explore**: Click on any keyword to make it the central topic
- **Return**: Click � Main Menu to return to keyword selection

### Visual Legend
- **🔴 Red Circle**: Central topic (current focus)
- **🔵 Blue Circles**: Narrower terms (inner ring)
- **🟠 Orange Circles**: Broader terms (outer ring)  
- **🟢 Teal Circles**: Related terms (outer ring)

### Relationship Panel
- **▲ Broader Topics**: More general concepts
- **▼ Narrower Topics**: More specific concepts  
- **◆ Related Topics**: Associated concepts
- **◎ Translations**: Terms in other languages

### Language Support
- Switch between EN/FR/ES using the language buttons
- Interface text adapts to selected language
- Tooltips show translations when available

### Mobile Experience
- Responsive layout for small screens
- Toggle button (📋 Relations) to show/hide relationship panel
- Close button (×) to dismiss panels

## Statistics (Current Dataset)

- **859 Keywords** with multilingual labels
- **748 Keywords** with broader terms
- **227 Keywords** with narrower terms  
- **630 Keywords** with related terms
- **859 Keywords** with translations

## Data Source

The visualization uses the CBV (Core Business Vocabulary) thesaurus in SKOS RDF format, which contains multilingual trade terminology with hierarchical and associative relationships.

## Browser Compatibility

- Modern browsers with ES6+ support
- D3.js v7 for visualization
- Requires local HTTP server (included `server.py`) for JSON loading

## Differences from SQLite Approach

| Feature | CBV Graph | SQLite Approach |
|---------|-----------|-----------------|
| Data Source | JSON files | SQLite database |
| Dependencies | None (static) | Flask API server |
| Document Integration | No | Yes |
| Focus | Pure keyword relationships | Document-keyword connections |
| Deployment | Static hosting | Server required |
| Performance | Fast (client-side) | Database queries |

## Customization

- **Colors**: Modify CSS color variables for different themes
- **Layout**: Adjust ring radii in the renderGraph() function
- **Languages**: Add more languages by updating the language functions
- **Search**: Enhance search with fuzzy matching or advanced filters

## Troubleshooting

### Missing Files Error
If you see "Missing required files", run:
```bash
python parse_thesaurus.py
```

### Server Connection Issues
If you can't access the interface:
- Make sure `server.py` is running: `python server.py`
- Check if the port is in use: try `python server.py 8080`
- Verify all JSON files exist: run `python parse_thesaurus.py` first
- Visit the correct URL: `http://localhost:8000` (not `file://`)

## Performance Notes

- All data loads client-side (no API calls during navigation)
- Fast keyword switching and exploration
- Responsive to window resizing
- Optimized for smooth interactions

---

**CBV Keyword Graph Explorer** - Explore trade terminology relationships visually 🚀