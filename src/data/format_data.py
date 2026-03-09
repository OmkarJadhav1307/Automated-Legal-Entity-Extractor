import json
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import os
import random

def create_spacy_dataset(jsonl_path, train_out, dev_out, split_ratio=0.8):
    # Start with a blank English model for tokenization
    nlp = spacy.blank("en") 
    db_train = DocBin()
    db_dev = DocBin()

    # 1. Load the JSONL output from Doccano
    if not os.path.exists(jsonl_path):
        print(f"Error: Could not find {jsonl_path}")
        return

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    # 2. Shuffle data so the model doesn't overfit to alphabetical/chronological order
    random.seed(42)
    random.shuffle(data)
    
    # 3. Create the 80/20 Train-Dev Split
    split_index = int(len(data) * split_ratio)
    train_data = data[:split_index]
    dev_data = data[split_index:]

    # Helper function to align characters to SpaCy tokens
    def process_split(split_data, doc_bin):
        skipped_docs = 0
        total_ents = 0
        
        for entry in tqdm(split_data):
            text = entry.get('text', '')
            labels = entry.get('label', [])
            doc = nlp.make_doc(text)
            ents = []
            
            for start, end, label in labels:
                # We use strict alignment first. If the LLM highlighted half a space, 
                # we expand the bounds to grab the full words.
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    span = doc.char_span(start, end, label=label, alignment_mode="expand")
                
                if span is not None:
                    ents.append(span)
            
            try:
                # Remove any overlapping spans (e.g., if Gemini accidentally tagged
                # the same word as both PARTIES and GOVERNING_LAW)
                doc.ents = spacy.util.filter_spans(ents)
                doc_bin.add(doc)
                total_ents += len(doc.ents)
            except ValueError as e:
                skipped_docs += 1
                print(e)
                
        return doc_bin, skipped_docs, total_ents

    print(f"Processing {len(train_data)} train documents...")
    db_train, train_skipped, train_ents = process_split(train_data, db_train)
    db_train.to_disk(train_out)
    
    print(f"\nProcessing {len(dev_data)} dev documents...")
    db_dev, dev_skipped, dev_ents = process_split(dev_data, db_dev)
    db_dev.to_disk(dev_out)

    print("\n" + "="*50)
    print("STAGE 2: PREPROCESSING COMPLETE")
    print("="*50)
    print(f"Saved Train dataset to: {train_out} ({len(db_train)} docs, {train_ents} entities)")
    print(f"Saved Dev dataset to: {dev_out} ({len(db_dev)} docs, {dev_ents} entities)")
    if train_skipped or dev_skipped:
         print(f"Note: Skipped {train_skipped + dev_skipped} documents due to unresolvable layout issues.")
    print("="*50)
    print("These .spacy files are now ready to be uploaded to Google Colab!")

if __name__ == '__main__':
    # Ensure our output directory exists
    os.makedirs('data/processed', exist_ok=True)
    
    # Run the generation
    create_spacy_dataset(
        jsonl_path='data/annotations/doccano_export.jsonl',
        train_out='data/processed/train.spacy',
        dev_out='data/processed/dev.spacy'
    )
