from transformers import pipeline
import re

ner_pipeline = pipeline("ner", grouped_entities=True, model="dslim/bert-base-NER")

def extract_entities(text: str):
    results = ner_pipeline(text)
    entities = [{"text": res['word'], "label": res['entity_group']} for res in results]

    dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
    addresses = [line for line in text.splitlines() if any(x in line.lower() for x in ['street', 'st', 'rd', 'road', 'avenue', 'lane'])]

    return {
        "entities": entities,
        "dates": dates,
        "addresses": addresses
    }
