import os
import csv
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from googletrans import Translator
from nltk.corpus import wordnet
import json
#nltk.download('punkt_tab')
#nltk.download('wordnet')


script_dir = os.path.dirname(os.path.abspath(__file__))

csv_file_path = os.path.join(script_dir, 'disease_data.csv')

data = []
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append((row['symptom'], row['disease'], row['medicine'], row['specialization']))

symptoms_list = [item[0] for item in data]
diseases = [item[1] for item in data]
medicines = [item[2] for item in data]
specializations = [item[3] for item in data]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(symptoms_list)
clf = MultinomialNB()
clf.fit(X, diseases)

translator = Translator()

def translate_text(text, dest_language='en'):
    translation = translator.translate(text, dest=dest_language)
    return translation.text

def trans_tam(text, dest_language='ta'):
    translation = translator.translate(text, dest=dest_language)
    return translation.text

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

def extract_symptoms(text):
    words = nltk.word_tokenize(text.lower())
    symptoms = []
    for word in words:
        if word in vectorizer.get_feature_names_out():
            symptoms.append(word)
        else:
            for synonym in get_synonyms(word):
                if synonym in vectorizer.get_feature_names_out():
                    symptoms.append(synonym)
                    break
    return ' '.join(symptoms)

def process_symptoms(text):
    translated_text = translate_text(text, dest_language='en')
    symptoms = extract_symptoms(translated_text)
    if not symptoms:
        return {"response": "I'm sorry, I couldn't recognize any symptoms."}
    X_test = vectorizer.transform([symptoms])
    predicted_disease = clf.predict(X_test)[0]
    medicine = medicines[diseases.index(predicted_disease)]
    specialization = specializations[diseases.index(predicted_disease)]
    response = (f"Based on the symptoms you provided, it seems you might have {predicted_disease}. "
                f"I would recommend taking {medicine}. "
                f"For further assistance, you should consult a {specialization} specialist.")
    return {"response": response, "tam_res": trans_tam(response) , "disease": predicted_disease, "tam_disease": trans_tam(predicted_disease), "medicine": medicine, "tam_medicine": trans_tam(medicine), "specialization": specialization,"tam_specialization": trans_tam(specialization)}

if __name__ == "__main__":
    import sys
    text = sys.argv[1]
    #text="எனக்கு காய்ச்சலும் இருமலும் உள்ளது"
    result = process_symptoms(text)
    print(json.dumps(result))