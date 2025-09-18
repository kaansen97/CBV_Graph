"""
CBV Thesaurus Parser
Extracts keyword relationships from SKOS RDF thesaurus and creates JSON data
for interactive keyword graph visualization.
"""

import json
from rdflib import Graph, Namespace
from collections import defaultdict

# Define SKOS namespace
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

def get_labels_by_language(graph, concept_uri):
    """Extract preferred and alternative labels for a concept by language."""
    labels = {
        'en': {'pref': [], 'alt': []},
        'es': {'pref': [], 'alt': []}, 
        'fr': {'pref': [], 'alt': []}
    }
    
    # Get preferred labels
    for pref_label in graph.objects(concept_uri, SKOS.prefLabel):
        lang = pref_label.language or 'en'
        if lang in labels:
            labels[lang]['pref'].append(str(pref_label))
    
    # Get alternative labels
    for alt_label in graph.objects(concept_uri, SKOS.altLabel):
        lang = alt_label.language or 'en'
        if lang in labels:
            labels[lang]['alt'].append(str(alt_label))
    
    return labels

def parse_thesaurus_rdf(rdf_file):
    """Parse SKOS RDF file and extract keyword relationships."""
    print(f"Loading RDF file: {rdf_file}")
    
    # Load RDF graph
    g = Graph()
    g.parse(rdf_file, format="xml")
    
    print(f"Loaded {len(g)} triples from RDF file")
    
    # Storage for all concepts and relationships
    concepts = {}
    relationships = defaultdict(lambda: {
        'broader': set(),
        'narrower': set(), 
        'related': set(),
        'translation': defaultdict(set)
    })
    
    # Process all concepts
    for concept_uri in g.subjects(SKOS.prefLabel, None):
        concept_str = str(concept_uri)
        
        # Get labels by language
        labels = get_labels_by_language(g, concept_uri)
        concepts[concept_str] = labels
        
        # Process broader relationships
        for broader_uri in g.objects(concept_uri, SKOS.broader):
            broader_labels = get_labels_by_language(g, broader_uri)
            # Use English preferred label as primary identifier
            if broader_labels['en']['pref']:
                broader_name = broader_labels['en']['pref'][0]
                relationships[concept_str]['broader'].add(broader_name)
        
        # Process narrower relationships
        for narrower_uri in g.objects(concept_uri, SKOS.narrower):
            narrower_labels = get_labels_by_language(g, narrower_uri)
            if narrower_labels['en']['pref']:
                narrower_name = narrower_labels['en']['pref'][0]
                relationships[concept_str]['narrower'].add(narrower_name)
        
        # Process related relationships
        for related_uri in g.objects(concept_uri, SKOS.related):
            related_labels = get_labels_by_language(g, related_uri)
            if related_labels['en']['pref']:
                related_name = related_labels['en']['pref'][0]
                relationships[concept_str]['related'].add(related_name)
    
    print(f"Processed {len(concepts)} concepts")
    
    # Convert to keyword-based structure (using English preferred labels as keys)
    keyword_data = {}
    keyword_relationships = defaultdict(lambda: {
        'broader': set(),
        'narrower': set(),
        'related': set(),
        'translations': {}
    })
    
    # Create keyword entries
    for concept_uri, labels in concepts.items():
        if labels['en']['pref']:
            primary_keyword = labels['en']['pref'][0]
            
            # Store multilingual labels
            keyword_data[primary_keyword] = {
                'uri': concept_uri,
                'labels': labels
            }
            
            # Store translations
            for lang in ['es', 'fr']:
                if labels[lang]['pref']:
                    keyword_relationships[primary_keyword]['translations'][lang] = labels[lang]['pref']
                if labels[lang]['alt']:
                    if lang not in keyword_relationships[primary_keyword]['translations']:
                        keyword_relationships[primary_keyword]['translations'][lang] = []
                    keyword_relationships[primary_keyword]['translations'][lang].extend(labels[lang]['alt'])
    
    # Process relationships using English keywords
    for concept_uri, rels in relationships.items():
        if concept_uri in concepts and concepts[concept_uri]['en']['pref']:
            primary_keyword = concepts[concept_uri]['en']['pref'][0]
            
            keyword_relationships[primary_keyword]['broader'] = list(rels['broader'])
            keyword_relationships[primary_keyword]['narrower'] = list(rels['narrower'])
            keyword_relationships[primary_keyword]['related'] = list(rels['related'])
    
    # Convert sets to lists for JSON serialization
    final_relationships = {}
    for keyword, rels in keyword_relationships.items():
        final_relationships[keyword] = {
            'broader': list(rels['broader']),
            'narrower': list(rels['narrower']),
            'related': list(rels['related']),
            'translations': dict(rels['translations'])
        }
    
    return keyword_data, final_relationships

def create_keyword_list(keyword_data):
    """Create a simple list of all keywords for search functionality."""
    keywords = []
    for keyword, data in keyword_data.items():
        keywords.append({
            'name': keyword,
            'labels': data['labels']
        })
    return sorted(keywords, key=lambda x: x['name'].lower())

def create_unified_data(keyword_data, relationships):
    """Create a single unified JSON structure with all keyword information."""
    unified_data = {}
    
    for keyword, data in keyword_data.items():
        # Get relationship data for this keyword
        rels = relationships.get(keyword, {
            'broader': [],
            'narrower': [],
            'related': [],
            'translations': {}
        })
        
        # Create unified entry
        unified_data[keyword] = {
            'uri': data['uri'],
            'labels': data['labels'],
            'broader': rels['broader'],
            'narrower': rels['narrower'],
            'related': rels['related'],
            'translations': rels['translations']
        }
    
    return unified_data

def main():
    """Main function to parse thesaurus and generate unified JSON file."""
    rdf_file = "CBV_thesaurus_v4.rdf"
    
    try:
        # Parse the thesaurus
        keyword_data, relationships = parse_thesaurus_rdf(rdf_file)
        
        # Create unified data structure
        unified_data = create_unified_data(keyword_data, relationships)
        
        # Save unified data
        with open('cbv_data.json', 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nGenerated file:")
        print(f"- cbv_data.json: {len(unified_data)} keywords with complete data")
        
        # Print some statistics
        broader_count = sum(1 for k, v in unified_data.items() if v['broader'])
        narrower_count = sum(1 for k, v in unified_data.items() if v['narrower'])
        related_count = sum(1 for k, v in unified_data.items() if v['related'])
        translation_count = sum(1 for k, v in unified_data.items() if v['translations'])
        
        print(f"\nStatistics:")
        print(f"- Keywords with broader terms: {broader_count}")
        print(f"- Keywords with narrower terms: {narrower_count}")
        print(f"- Keywords with related terms: {related_count}")
        print(f"- Keywords with translations: {translation_count}")
        
        print(f"- All keyword data unified in single JSON file")
        
    except Exception as e:
        print(f"Error processing thesaurus: {e}")
        raise

if __name__ == "__main__":
    main()