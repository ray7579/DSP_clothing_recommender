import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')


def preprocess_text(text):
    #lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    #tokenize the text
    words = nltk.word_tokenize(text)
    #remove stopwords
    words = [word for word in words if word not in stopwords.words('english')]
    #lemmatization
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    #reconstructing
    text = ' '.join(words)
    return text



def preprocess_products(products):
    #combine the product name and description
    products['combined_features'] = products['name'] + ' ' + products['description']
    #preprocess the features
    products['combined_features'] = products['combined_features'].apply(preprocess_text)
    return products
