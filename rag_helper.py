"""
RAG Helper Module for Second Brain App
Utilities for preparing and exporting data for LLM/RAG integration
"""

import json
from datetime import datetime
from typing import List, Dict, Any
import database as db


def format_experience_for_rag(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a single experience entry for RAG/LLM consumption.
    
    Args:
        experience: Experience record from database
    
    Returns:
        Formatted dictionary optimized for LLM processing
    """
    return {
        'id': experience['id'],
        'title': experience['title'],
        'content': experience['content'] or '',
        'tags': [tag.strip() for tag in (experience.get('tags', '') or '').split(',') if tag.strip()],
        'category': experience.get('category', ''),
        'context': experience.get('context', ''),
        'created_at': experience['created_at'],
        'updated_at': experience['updated_at'],
        'metadata': {
            'type': 'past_experience',
            'source': 'second_brain_app',
            'has_tags': bool(experience.get('tags')),
            'has_category': bool(experience.get('category')),
            'has_context': bool(experience.get('context'))
        }
    }


def get_all_experiences_for_rag() -> List[Dict[str, Any]]:
    """
    Retrieve all experiences formatted for RAG/LLM integration.
    
    Returns:
        List of formatted experience dictionaries
    """
    experiences = db.get_experiences()
    return [format_experience_for_rag(dict(exp)) for exp in experiences]


def export_experiences_to_json(filepath: str = 'experiences_export.json') -> str:
    """
    Export all experiences to a JSON file for LLM training/RAG.
    
    Args:
        filepath: Output file path (default: 'experiences_export.json')
    
    Returns:
        Path to the exported file
    """
    experiences = get_all_experiences_for_rag()
    
    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_records': len(experiences),
        'version': '1.0',
        'data': experiences
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def create_rag_prompt_context(query: str, relevant_experiences: List[Dict[str, Any]], max_experiences: int = 5) -> str:
    """
    Create a formatted context string for LLM prompts using relevant experiences.
    
    Args:
        query: User's query
        relevant_experiences: List of relevant experience records
        max_experiences: Maximum number of experiences to include
    
    Returns:
        Formatted context string for LLM prompt
    """
    context_parts = ["Based on the following past experiences:\n"]
    
    for i, exp in enumerate(relevant_experiences[:max_experiences], 1):
        exp_formatted = format_experience_for_rag(exp)
        
        context_parts.append(f"\n--- Experience {i} ---")
        context_parts.append(f"Title: {exp_formatted['title']}")
        
        if exp_formatted['category']:
            context_parts.append(f"Category: {exp_formatted['category']}")
        
        if exp_formatted['tags']:
            context_parts.append(f"Tags: {', '.join(exp_formatted['tags'])}")
        
        if exp_formatted['context']:
            context_parts.append(f"Context: {exp_formatted['context']}")
        
        context_parts.append(f"\nContent:\n{exp_formatted['content']}\n")
    
    context_parts.append(f"\nUser Query: {query}\n")
    context_parts.append("Please provide a helpful response based on the above experiences.")
    
    return '\n'.join(context_parts)


def search_experiences_by_tags(tags: List[str]) -> List[Dict[str, Any]]:
    """
    Search experiences by tags (simple keyword matching).
    
    Args:
        tags: List of tags to search for
    
    Returns:
        List of matching experiences formatted for RAG
    """
    all_experiences = db.get_experiences()
    matching_experiences = []
    
    for exp in all_experiences:
        exp_tags = [tag.strip().lower() for tag in (exp.get('tags', '') or '').split(',') if tag.strip()]
        query_tags = [tag.strip().lower() for tag in tags]
        
        # Check if any query tag matches any experience tag
        if any(qtag in exp_tags for qtag in query_tags):
            matching_experiences.append(format_experience_for_rag(dict(exp)))
    
    return matching_experiences


def search_experiences_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Search experiences by category.
    
    Args:
        category: Category to search for
    
    Returns:
        List of matching experiences formatted for RAG
    """
    all_experiences = db.get_experiences()
    matching_experiences = []
    
    for exp in all_experiences:
        if exp.get('category', '').lower() == category.lower():
            matching_experiences.append(format_experience_for_rag(dict(exp)))
    
    return matching_experiences


def get_experience_statistics() -> Dict[str, Any]:
    """
    Get statistics about stored experiences for RAG system monitoring.
    
    Returns:
        Dictionary with various statistics
    """
    all_experiences = get_all_experiences_for_rag()
    
    # Count by category
    category_counts = {}
    tag_counts = {}
    total_with_context = 0
    total_with_tags = 0
    
    for exp in all_experiences:
        # Category stats
        category = exp['category'] or 'Uncategorized'
        category_counts[category] = category_counts.get(category, 0) + 1
        
        # Tag stats
        for tag in exp['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Context stats
        if exp['context']:
            total_with_context += 1
        
        if exp['tags']:
            total_with_tags += 1
    
    return {
        'total_experiences': len(all_experiences),
        'experiences_with_context': total_with_context,
        'experiences_with_tags': total_with_tags,
        'category_distribution': category_counts,
        'top_tags': dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        'unique_categories': len(category_counts),
        'unique_tags': len(tag_counts)
    }


# Example usage for future RAG integration
if __name__ == '__main__':
    # Export all experiences to JSON
    export_path = export_experiences_to_json()
    print(f"Experiences exported to: {export_path}")
    
    # Get statistics
    stats = get_experience_statistics()
    print("\nExperience Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Example: Search by tags
    python_experiences = search_experiences_by_tags(['python', 'debugging'])
    print(f"\nFound {len(python_experiences)} experiences related to Python/Debugging")
    
    # Example: Create RAG context
    if python_experiences:
        context = create_rag_prompt_context(
            "How do I debug a Python application?",
            python_experiences
        )
        print("\nExample RAG Context:")
        print(context[:500] + "..." if len(context) > 500 else context)
