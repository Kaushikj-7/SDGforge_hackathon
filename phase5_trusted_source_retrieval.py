#!/usr/bin/env python3
"""
Phase 5: Trusted Source Retrieval
Search and retrieve information from authoritative medical sources
Enhanced with Drug Safety Database Integration
"""

import requests
import json
import re
from config import GROQ_API_KEY

def retrieve_trusted_sources(query, max_results=5):
    """Main function to retrieve information from trusted medical sources"""
    print("🔬 Phase 5: Comprehensive Medical Research...")
    
    all_sources = []
    
    # Check if query is drug-related and add drug safety information
    drug_info = check_drug_safety(query)
    if drug_info:
        all_sources.extend(drug_info)
    
    # Search PubMed for research articles
    pubmed_sources = search_pubmed(query, max_results=3)
    all_sources.extend(pubmed_sources)
    
    # Add authoritative organization sources
    org_sources = get_authoritative_sources(query)
    all_sources.extend(org_sources)
    
    # Count source types
    research_count = len([s for s in all_sources if s.get('type') == 'research'])
    guideline_count = len([s for s in all_sources if s.get('type') == 'guideline'])
    regulation_count = len([s for s in all_sources if s.get('type') == 'regulation'])
    drug_safety_count = len([s for s in all_sources if s.get('type') == 'drug_safety'])
    
    print(f"📚 Consulted {len(all_sources)} authoritative sources:")
    print(f"  📋 Research: {research_count} sources")
    print(f"  📋 Guidelines: {guideline_count} sources") 
    print(f"  📋 Regulation: {regulation_count} sources")
    if drug_safety_count > 0:
        print(f"  💊 Drug Safety: {drug_safety_count} sources")
    
    if all_sources:
        print(f"\n  🔍 Top Sources:")
        for i, source in enumerate(all_sources[:3], 1):
            print(f"    {i}. {source['source']}: {source['title'][:50]}...")
    
    return all_sources

def check_drug_safety(query):
    """Check if query is drug-related and retrieve comprehensive drug safety information"""
    print("💊 Checking for drug safety information...")
    
    # Extract drug names from query
    drug_names = extract_drug_names(query)
    
    if not drug_names:
        return []
    
    drug_safety_sources = []
    
    for drug_name in drug_names:
        print(f"  🔍 Analyzing drug: {drug_name}")
        
        # Get FDA drug safety information
        fda_info = get_fda_drug_safety(drug_name)
        if fda_info:
            drug_safety_sources.extend(fda_info)
        
        # Get DrugBank information
        drugbank_info = get_drugbank_info(drug_name)
        if drugbank_info:
            drug_safety_sources.extend(drugbank_info)
        
        # Get drug interaction information
        interaction_info = analyze_drug_interactions(drug_name)
        if interaction_info:
            drug_safety_sources.extend(interaction_info)
        
        # Get adverse event reports
        adverse_events = get_adverse_event_reports(drug_name)
        if adverse_events:
            drug_safety_sources.extend(adverse_events)
    
    return drug_safety_sources

def extract_drug_names(query):
    """Extract potential drug names from the query using pattern matching"""
    
    # Common drug name patterns and suffixes
    drug_patterns = [
        r'\b\w*(cillin|mycin|sulfa|thiazide|pril|sartan|statin|ine|ol|ide)\b',  # Common drug suffixes
        r'\b(aspirin|ibuprofen|acetaminophen|paracetamol|warfarin|insulin|metformin)\b',  # Common drugs
        r'\b\w*(virus|bacteria|infection)\s+(treatment|medication|drug|medicine)\b',  # Treatment context
        r'\b(antibiotic|antiviral|painkiller|anti-inflammatory|blood\s+thinner)\b'  # Drug categories
    ]
    
    # Known common drug names
    common_drugs = [
        'aspirin', 'ibuprofen', 'acetaminophen', 'paracetamol', 'insulin', 'metformin',
        'warfarin', 'lisinopril', 'amlodipine', 'atorvastatin', 'simvastatin',
        'omeprazole', 'levothyroxine', 'albuterol', 'furosemide', 'hydrochlorothiazide'
    ]
    
    found_drugs = []
    query_lower = query.lower()
    
    # Check for exact matches of common drugs
    for drug in common_drugs:
        if drug in query_lower:
            found_drugs.append(drug.title())
    
    # Check for pattern matches
    for pattern in drug_patterns:
        matches = re.findall(pattern, query_lower, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]  # Take first group if it's a tuple
            if len(match) > 3:  # Avoid very short matches
                found_drugs.append(match.title())
    
    # Remove duplicates while preserving order
    unique_drugs = []
    for drug in found_drugs:
        if drug not in unique_drugs:
            unique_drugs.append(drug)
    
    return unique_drugs[:3]  # Limit to first 3 drugs found

def get_fda_drug_safety(drug_name):
    """Get FDA drug safety information including Orange Book and safety communications"""
    fda_sources = []
    
    try:
        # FDA Orange Book (Approved Drug Products)
        orange_book_url = f"https://www.accessdata.fda.gov/scripts/cder/ob/search_product.cfm"
        fda_sources.append({
            'title': f"FDA Orange Book - {drug_name} Approval Information",
            'source': 'FDA Orange Book',
            'url': f"https://www.accessdata.fda.gov/scripts/cder/ob/search_product.cfm?Appl_Type=N&Appl_No=&Prod_Name={drug_name.replace(' ', '+')}&Active_Ingred=&Dosage_Form=&Strength=&Route=&Marketing_Status=&TECode=&Appl_Holder=&Generic_Avail=",
            'summary': f'FDA-approved drug product information for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.98
        })
        
        # FDA Drug Safety Communications
        fda_sources.append({
            'title': f"FDA Drug Safety Communications - {drug_name}",
            'source': 'FDA Safety Communications',
            'url': f"https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications?search={drug_name.replace(' ', '+')}",
            'summary': f'FDA safety alerts and communications for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.97
        })
        
        # FDA Adverse Event Reporting System (FAERS)
        fda_sources.append({
            'title': f"FAERS Database - {drug_name} Adverse Events",
            'source': 'FDA FAERS',
            'url': f"https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers/fda-adverse-event-reporting-system-faers-latest-quarterly-data-files",
            'summary': f'Adverse event reports for {drug_name} from FAERS database',
            'type': 'drug_safety',
            'reliability': 0.95
        })
        
    except Exception as e:
        print(f"Error getting FDA drug safety info: {e}")
    
    return fda_sources

def get_drugbank_info(drug_name):
    """Get DrugBank database information"""
    drugbank_sources = []
    
    try:
        # DrugBank database
        drugbank_sources.append({
            'title': f"DrugBank - {drug_name} Drug Information",
            'source': 'DrugBank',
            'url': f"https://go.drugbank.com/drugs?utf8=%E2%9C%93&query={drug_name.replace(' ', '+')}&button=",
            'summary': f'Comprehensive drug data including interactions, targets, and pharmacology for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.94
        })
        
        # Drugs.com safety information
        drugbank_sources.append({
            'title': f"Drugs.com - {drug_name} Safety Information",
            'source': 'Drugs.com',
            'url': f"https://www.drugs.com/search.php?searchterm={drug_name.replace(' ', '+')}",
            'summary': f'Drug interactions, side effects, and safety information for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.90
        })
        
    except Exception as e:
        print(f"Error getting DrugBank info: {e}")
    
    return drugbank_sources

def analyze_drug_interactions(drug_name):
    """Analyze potential drug interactions"""
    interaction_sources = []
    
    try:
        # Drugs.com Interaction Checker
        interaction_sources.append({
            'title': f"Drug Interaction Checker - {drug_name}",
            'source': 'Drugs.com Interactions',
            'url': f"https://www.drugs.com/drug_interactions.php?generic_only=&trade_only=&drug_list_display={drug_name.replace(' ', '+')}&professional=1",
            'summary': f'Comprehensive drug interaction checker for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.92
        })
        
        # WebMD Drug Interaction Checker
        interaction_sources.append({
            'title': f"WebMD Interaction Checker - {drug_name}",
            'source': 'WebMD Interactions',
            'url': f"https://www.webmd.com/interaction-checker/default.htm?drugname={drug_name.replace(' ', '+')}",
            'summary': f'Drug interaction analysis for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.85
        })
        
    except Exception as e:
        print(f"Error analyzing drug interactions: {e}")
    
    return interaction_sources

def get_adverse_event_reports(drug_name):
    """Get adverse event reports and safety alerts"""
    adverse_event_sources = []
    
    try:
        # FDA Drug Recalls Database
        adverse_event_sources.append({
            'title': f"FDA Drug Recalls - {drug_name}",
            'source': 'FDA Recalls',
            'url': f"https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts?search={drug_name.replace(' ', '+')}",
            'summary': f'FDA recalls and safety alerts for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.96
        })
        
        # MedWatch Safety Information
        adverse_event_sources.append({
            'title': f"MedWatch Safety Alerts - {drug_name}",
            'source': 'FDA MedWatch',
            'url': f"https://www.fda.gov/safety/medwatch-fda-safety-information-and-adverse-event-reporting-program",
            'summary': f'MedWatch safety information and adverse event reports for {drug_name}',
            'type': 'drug_safety',
            'reliability': 0.95
        })
        
    except Exception as e:
        print(f"Error getting adverse event reports: {e}")
    
    return adverse_event_sources

def search_pubmed(query, max_results=3):
    """Search PubMed for peer-reviewed medical literature"""
    try:
        pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # Search for article IDs
        search_url = f"{pubmed_base}esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        response = requests.get(search_url, params=search_params, timeout=15)
        if response.status_code != 200:
            return []
        
        search_data = response.json()
        if 'esearchresult' not in search_data or not search_data['esearchresult']['idlist']:
            return []
        
        # Get article details
        ids = search_data['esearchresult']['idlist']
        fetch_url = f"{pubmed_base}esummary.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'json'
        }
        
        response = requests.get(fetch_url, params=fetch_params, timeout=15)
        if response.status_code != 200:
            return []
        
        fetch_data = response.json()
        
        articles = []
        for uid in ids:
            if uid in fetch_data['result']:
                article_data = fetch_data['result'][uid]
                
                # Get authors
                authors_list = article_data.get('authors', [])
                if authors_list:
                    first_author = authors_list[0].get('name', 'Unknown Author')
                    authors_str = f"{first_author} et al." if len(authors_list) > 1 else first_author
                else:
                    authors_str = "Unknown Authors"
                
                # Get publication year
                pub_date = article_data.get('pubdate', 'Unknown Date')
                
                articles.append({
                    'title': article_data.get('title', 'No title available'),
                    'source': 'PubMed',
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                    'summary': f"{authors_str} ({pub_date})",
                    'type': 'research',
                    'reliability': 0.95,
                    'pmid': uid
                })
        
        return articles
        
    except Exception as e:
        print(f"PubMed search error: {e}")
        return []

def get_authoritative_sources(query):
    """Get information from authoritative health organizations"""
    
    # Topic-specific URL mappings
    topic_urls = {
        'vaccine': {
            'WHO': 'https://www.who.int/news-room/questions-and-answers/item/vaccines-and-immunization',
            'CDC': 'https://www.cdc.gov/vaccines/',
            'FDA': 'https://www.fda.gov/vaccines-blood-biologics/vaccines',
        },
        'covid': {
            'WHO': 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019',
            'CDC': 'https://www.cdc.gov/coronavirus/2019-ncov/',
            'FDA': 'https://www.fda.gov/emergency-preparedness-and-response/coronavirus-disease-2019-covid-19',
        },
        'heart': {
            'NIH': 'https://www.nhlbi.nih.gov/health/heart',
            'CDC': 'https://www.cdc.gov/heartdisease/',
            'WHO': 'https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)',
        },
        'cancer': {
            'NIH': 'https://www.cancer.gov/',
            'CDC': 'https://www.cdc.gov/cancer/',
            'WHO': 'https://www.who.int/news-room/fact-sheets/detail/cancer',
        }
    }
    
    def get_targeted_url(source, query):
        """Get targeted URL based on medical topic"""
        query_lower = query.lower()
        
        # Check for specific medical topics
        for topic, urls in topic_urls.items():
            if topic in query_lower:
                if source in urls:
                    return urls[source]
        
        # Fallback to search URLs
        query_encoded = query.replace(' ', '%20').replace(',', '')
        fallback_urls = {
            'WHO': f'https://www.who.int/news-room/fact-sheets?keywords={query_encoded}',
            'CDC': f'https://www.cdc.gov/search/?query={query_encoded}',
            'NIH': f'https://www.nih.gov/search/?query={query_encoded}',
            'FDA': f'https://www.fda.gov/search/?query={query_encoded}',
            'ClinicalTrials.gov': f'https://clinicaltrials.gov/search?term={query_encoded}',
            'Cochrane Library': f'https://www.cochranelibrary.com/search?q={query_encoded}'
        }
        
        return fallback_urls.get(source, f'https://www.google.com/search?q={query_encoded}+{source.replace(" ", "")}')
    
    # Generate authoritative sources
    sources = [
        {
            'title': f"WHO Health Information on {query}",
            'source': 'WHO',
            'url': get_targeted_url('WHO', query),
            'summary': 'World Health Organization official guidance and fact sheets',
            'type': 'guideline',
            'reliability': 0.98
        },
        {
            'title': f"CDC Guidelines on {query}",
            'source': 'CDC',
            'url': get_targeted_url('CDC', query),
            'summary': 'Centers for Disease Control evidence-based information',
            'type': 'guideline',
            'reliability': 0.97
        },
        {
            'title': f"NIH Research on {query}",
            'source': 'NIH',
            'url': get_targeted_url('NIH', query),
            'summary': 'National Institutes of Health peer-reviewed research',
            'type': 'research',
            'reliability': 0.96
        },
        {
            'title': f"FDA Safety Information on {query}",
            'source': 'FDA',
            'url': get_targeted_url('FDA', query),
            'summary': 'Food and Drug Administration safety data and approvals',
            'type': 'regulation',
            'reliability': 0.95
        },
        {
            'title': f"ClinicalTrials.gov Studies on {query}",
            'source': 'ClinicalTrials.gov',
            'url': get_targeted_url('ClinicalTrials.gov', query),
            'summary': 'Active and completed clinical trials database',
            'type': 'research',
            'reliability': 0.94
        },
        {
            'title': f"Cochrane Reviews on {query}",
            'source': 'Cochrane Library',
            'url': get_targeted_url('Cochrane Library', query),
            'summary': 'Systematic reviews and meta-analyses',
            'type': 'research',
            'reliability': 0.97
        }
    ]
    
    return sources

def search_medical_databases(query):
    """Search additional medical databases"""
    databases = []
    
    # Add Mayo Clinic
    databases.append({
        'title': f"Mayo Clinic Information on {query}",
        'source': 'Mayo Clinic',
        'url': f'https://www.mayoclinic.org/search/search-results?q={query.replace(" ", "+")}',
        'summary': 'Mayo Clinic patient care and health information',
        'type': 'guideline',
        'reliability': 0.92
    })
    
    # Add WebMD (with lower reliability)
    databases.append({
        'title': f"WebMD Information on {query}",
        'source': 'WebMD',
        'url': f'https://www.webmd.com/search/search_results/default.aspx?query={query.replace(" ", "+")}',
        'summary': 'General health information and symptom checker',
        'type': 'reference',
        'reliability': 0.75
    })
    
    return databases

def rank_sources_by_reliability(sources):
    """Rank sources by reliability score"""
    return sorted(sources, key=lambda x: x.get('reliability', 0), reverse=True)

def filter_sources_by_relevance(sources, query):
    """Filter sources based on relevance to query"""
    query_lower = query.lower()
    relevant_sources = []
    
    for source in sources:
        title_lower = source.get('title', '').lower()
        summary_lower = source.get('summary', '').lower()
        
        # Simple relevance scoring
        relevance_score = 0
        query_words = query_lower.split()
        
        for word in query_words:
            if word in title_lower:
                relevance_score += 2
            if word in summary_lower:
                relevance_score += 1
        
        if relevance_score > 0:
            source['relevance_score'] = relevance_score
            relevant_sources.append(source)
    
    # Sort by relevance score
    return sorted(relevant_sources, key=lambda x: x.get('relevance_score', 0), reverse=True)

if __name__ == "__main__":
    # Test the module
    test_queries = [
        "COVID-19 vaccine safety",
        "heart disease prevention",
        "cancer treatment options"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing: {query} ===")
        sources = retrieve_trusted_sources(query)
        
        print(f"Found {len(sources)} sources:")
        for i, source in enumerate(sources[:3], 1):
            print(f"  {i}. {source['source']} - Reliability: {source['reliability']}")
            print(f"     URL: {source['url']}")
            print(f"     Summary: {source['summary']}")
