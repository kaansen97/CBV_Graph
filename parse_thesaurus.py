"""
CBV Thesaurus Parser
Extracts keyword relationships and definitions from a SKOS RDF thesaurus 
and creates a unified JSON data file for interactive graph visualization.
"""

import json
from rdflib import Graph, Namespace, RDF
from collections import defaultdict

# Define SKOS namespace
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

def get_concept_details(graph, concept_uri):
    """Extract labels and definitions for a concept by language."""
    details = {
        'labels': {
            'en': {'pref': [], 'alt': []},
            'es': {'pref': [], 'alt': []},
            'fr': {'pref': [], 'alt': []}
        },
        'definitions': {
            'en': [], 'es': [], 'fr': []
        }
    }

    # Get preferred labels
    for pref_label in graph.objects(concept_uri, SKOS.prefLabel):
        lang = pref_label.language or 'en'
        if lang in details['labels']:
            details['labels'][lang]['pref'].append(str(pref_label))

    # Get alternative labels
    for alt_label in graph.objects(concept_uri, SKOS.altLabel):
        lang = alt_label.language or 'en'
        if lang in details['labels']:
            details['labels'][lang]['alt'].append(str(alt_label))

    # Get definitions
    for definition in graph.objects(concept_uri, SKOS.definition):
        lang = definition.language or 'en'
        if lang in details['definitions']:
            details['definitions'][lang].append(str(definition))

    return details

def parse_thesaurus_rdf(rdf_file):
    """Parse SKOS RDF file and extract keyword relationships, definitions, and collections."""
    print(f"Loading RDF file: {rdf_file}")
    
    # Load RDF graph
    g = Graph()
    g.parse(rdf_file, format="xml")
    
    print(f"Loaded {len(g)} triples from RDF file")
    
    # Storage for all concepts, collections, and relationships
    concepts = {}
    collections = {}
    relationships = defaultdict(lambda: {
        'broader': set(),
        'narrower': set(),
        'related': set(),
        'translation': defaultdict(set)
    })
    collection_relationships = defaultdict(lambda: {
        'members': set()
    })

    # Process all concepts
    for concept_uri in g.subjects(SKOS.prefLabel, None):
        concept_str = str(concept_uri)
        
        # Skip if this is a Collection (processed separately)
        if (concept_uri, RDF.type, SKOS.Collection) in g:
            continue
            
        # Get labels and definitions
        details = get_concept_details(g, concept_uri)
        concepts[concept_str] = details
        
        # Process broader relationships
        for broader_uri in g.objects(concept_uri, SKOS.broader):
            broader_details = get_concept_details(g, broader_uri)
            if broader_details['labels']['en']['pref']:
                broader_name = broader_details['labels']['en']['pref'][0]
                relationships[concept_str]['broader'].add(broader_name)
        
        # Process narrower relationships
        for narrower_uri in g.objects(concept_uri, SKOS.narrower):
            narrower_details = get_concept_details(g, narrower_uri)
            if narrower_details['labels']['en']['pref']:
                narrower_name = narrower_details['labels']['en']['pref'][0]
                relationships[concept_str]['narrower'].add(narrower_name)
        
        # Process related relationships
        for related_uri in g.objects(concept_uri, SKOS.related):
            related_details = get_concept_details(g, related_uri)
            if related_details['labels']['en']['pref']:
                related_name = related_details['labels']['en']['pref'][0]
                relationships[concept_str]['related'].add(related_name)
    
    print(f"Processed {len(concepts)} concepts")
    
    # Process all collections
    for collection_uri in g.subjects(RDF.type, SKOS.Collection):
        collection_str = str(collection_uri)
        
        # Get labels and definitions for collection
        details = get_concept_details(g, collection_uri)
        collections[collection_str] = details
        
        # Process member relationships
        for member_uri in g.objects(collection_uri, SKOS.member):
            member_details = get_concept_details(g, member_uri)
            if member_details['labels']['en']['pref']:
                member_name = member_details['labels']['en']['pref'][0]
                collection_relationships[collection_str]['members'].add(member_name)
    
    print(f"Processed {len(collections)} collections")
    
    # Convert to keyword-based structure (using English preferred labels as keys)
    keyword_data = {}
    keyword_relationships = defaultdict(lambda: {
        'broader': set(),
        'narrower': set(),
        'related': set(),
        'members': set(),
        'translations': {},
        'type': 'concept'  # Default type
    })
    
    # Create keyword entries for concepts
    for concept_uri, details in concepts.items():
        if details['labels']['en']['pref']:
            primary_keyword = details['labels']['en']['pref'][0]
            
            keyword_data[primary_keyword] = {
                'uri': concept_uri,
                'labels': details['labels'],
                'definitions': details['definitions'],
                'type': 'concept'
            }
            
            # Store translations
            for lang in ['es', 'fr']:
                if details['labels'][lang]['pref']:
                    keyword_relationships[primary_keyword]['translations'][lang] = details['labels'][lang]['pref']
                if details['labels'][lang]['alt']:
                    if lang not in keyword_relationships[primary_keyword]['translations']:
                        keyword_relationships[primary_keyword]['translations'][lang] = []
                    keyword_relationships[primary_keyword]['translations'][lang].extend(details['labels'][lang]['alt'])
    
    # Create keyword entries for collections
    for collection_uri, details in collections.items():
        if details['labels']['en']['pref']:
            primary_keyword = details['labels']['en']['pref'][0]
            
            keyword_data[primary_keyword] = {
                'uri': collection_uri,
                'labels': details['labels'],
                'definitions': details['definitions'],
                'type': 'collection'
            }
            
            keyword_relationships[primary_keyword]['type'] = 'collection'
            
            # Store translations
            for lang in ['es', 'fr']:
                if details['labels'][lang]['pref']:
                    keyword_relationships[primary_keyword]['translations'][lang] = details['labels'][lang]['pref']
                if details['labels'][lang]['alt']:
                    if lang not in keyword_relationships[primary_keyword]['translations']:
                        keyword_relationships[primary_keyword]['translations'][lang] = []
                    keyword_relationships[primary_keyword]['translations'][lang].extend(details['labels'][lang]['alt'])
    
    # Process concept relationships using English keywords
    for concept_uri, rels in relationships.items():
        if concept_uri in concepts and concepts[concept_uri]['labels']['en']['pref']:
            primary_keyword = concepts[concept_uri]['labels']['en']['pref'][0]
            
            keyword_relationships[primary_keyword]['broader'] = list(rels['broader'])
            keyword_relationships[primary_keyword]['narrower'] = list(rels['narrower'])
            keyword_relationships[primary_keyword]['related'] = list(rels['related'])
    
    # Process collection relationships using English keywords
    for collection_uri, rels in collection_relationships.items():
        if collection_uri in collections and collections[collection_uri]['labels']['en']['pref']:
            primary_keyword = collections[collection_uri]['labels']['en']['pref'][0]
            
            keyword_relationships[primary_keyword]['members'] = list(rels['members'])
    
    # Convert sets to lists for JSON serialization
    final_relationships = {}
    for keyword, rels in keyword_relationships.items():
        final_relationships[keyword] = {
            'broader': list(rels['broader']),
            'narrower': list(rels['narrower']),
            'related': list(rels['related']),
            'members': list(rels['members']),
            'translations': dict(rels['translations']),
            'type': rels['type']
        }
    
    return keyword_data, final_relationships

def create_unified_data(keyword_data, relationships):
    """Create a single unified JSON structure with all keyword information."""
    unified_data = {}
    
    for keyword, data in keyword_data.items():
        rels = relationships.get(keyword, {
            'broader': [],
            'narrower': [],
            'related': [],
            'members': [],
            'translations': {},
            'type': data.get('type', 'concept')
        })
        
        unified_data[keyword] = {
            'uri': data['uri'],
            'labels': data['labels'],
            'definitions': data['definitions'],
            'type': data.get('type', 'concept'),
            'broader': rels['broader'],
            'narrower': rels['narrower'],
            'related': rels['related'],
            'members': rels['members'],
            'translations': rels['translations']
        }
    
    return unified_data

def main():
    """Main function to parse thesaurus and generate unified JSON file."""
    rdf_file = "CBV_thesaurus_v4.rdf"
    
    try:
        keyword_data, relationships = parse_thesaurus_rdf(rdf_file)
        unified_data = create_unified_data(keyword_data, relationships)
        
        with open('cbv_data.json', 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nGenerated file:")
        print(f"- cbv_data.json: {len(unified_data)} keywords with complete data")
        
        # Print statistics
        concepts_count = sum(1 for v in unified_data.values() if v.get('type') == 'concept')
        collections_count = sum(1 for v in unified_data.values() if v.get('type') == 'collection')
        broader_count = sum(1 for v in unified_data.values() if v['broader'])
        narrower_count = sum(1 for v in unified_data.values() if v['narrower'])
        related_count = sum(1 for v in unified_data.values() if v['related'])
        members_count = sum(1 for v in unified_data.values() if v['members'])
        translation_count = sum(1 for v in unified_data.values() if v['translations'])
        definition_count = sum(1 for v in unified_data.values() if any(v['definitions'].values()))
        
        print(f"\nStatistics:")
        print(f"- Total entries: {len(unified_data)}")
        print(f"- Concepts: {concepts_count}")
        print(f"- Collections: {collections_count}")
        print(f"- Keywords with broader terms: {broader_count}")
        print(f"- Keywords with narrower terms: {narrower_count}")
        print(f"- Keywords with related terms: {related_count}")
        print(f"- Collections with members: {members_count}")
        print(f"- Keywords with translations: {translation_count}")
        print(f"- Keywords with definitions: {definition_count}")
        
        print(f"\n- All keyword data unified in single JSON file")
        
    except Exception as e:
        print(f"Error processing thesaurus: {e}")
        raise

if __name__ == "__main__":
    main()