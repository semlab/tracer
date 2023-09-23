import pandas as pd
from tqdm import tqdm
from transformers import pipeline


if __name__ == "__main__":
    sentiment_analysis = pipeline("sentiment-analysis",model="siebert/sentiment-roberta-large-english")

    #print(sentiment_analysis(["I love this!", 
    #'I recommend you to subordinate your ego and follow the person in charge.',
    #'do not do bad things',
    #'this might be disgusting'
    #]))

    df = pd.read_csv("../triplex/output/triples.csv")
    sentences = list(df['SENTENCE'])
    #scores = [res['score'] if res['score'] > 0 else -1*res['score'] for res in sentiment_analysis(sentences) )]
    scores = []
    for sentence in tqdm(sentences):
        score = None
        try:
            results = sentiment_analysis(sentence)
            res = results[0]
            score = res['score'] if res['label'] == 'POSITIVE' else -1*res['score']
        except Exception as e:
            print('ERROR')
            print(e)
        scores.append(score)


    assert len(scores) == len(sentences)
    df['sentiments'] = scores
    df.to_csv("../triplex/output/triples-sentiment.csv")
