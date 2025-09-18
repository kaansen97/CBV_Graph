# CBV_Graph

🌐 **Live Demo**: https://kaansen97.github.io/CBV_Graph/

A keyword graph visualization tool that allows users to explore multilingual trade terminology and their relationships without requiring documents or SQL databases.

## Files Structure

```
CBV_Graph/
├── parse_thesaurus.py      # Script to extract data from RDF
├── cbv_data.json          # Unified data file (keywords + relationships + translations)
├── index.html             # Landing page with keyword browser
├── graph.html             # Interactive graph visualization
└── README.md              # This file
```

## Quick Start

**🌐 Live Version**: The CBV Keyword Explorer is hosted on GitHub Pages at:
**https://kaansen97.github.io/CBV_Graph/**


### Navigation
- **Start**: Visit the index page for keyword selection
- **Browse**: Use popular keywords, search, or filter by alphabet
- **Explore**: Click on any keyword to make it the central topic
- **Return**: Click � Main Menu to return to keyword selection

### Visual Legend
- **🔴 Red Circle**: Central topic (current focus)
- **▼ Purple Triangle**: Narrower terms (inner ring)
- **▲ Orange Triangle**: Broader terms (outer ring)  
- **◆ Blue Circles**: Related terms (outer ring)

### Relationship Panel
- **▲ Broader Topics**: More general concepts
- **▼ Narrower Topics**: More specific concepts  
- **◆ Related Topics**: Associated concepts
- **◎ Translations**: Terms in other languages

## Data Source

The visualization uses the CBV (Common Business Vocabulary) thesaurus in SKOS RDF format, which contains multilingual trade terminology with hierarchical and associative relationships.

## Customization

- **Colors**: Modify CSS color variables for different themes
- **Layout**: Adjust ring radii in the renderGraph() function
- **Languages**: Add more languages by updating the language functions
- **Search**: Enhance search with fuzzy matching or advanced filters

## Development

For local development or data updates:

1. **Update Data** (if needed):
   ```bash
   python parse_thesaurus.py
   ```

2. **Local Testing**:
   - Open `index.html` directly in a modern browser, or
   - Use any local HTTP server (Python, Node.js, VS Code Live Server, etc.)
