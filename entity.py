import requests
import torch 
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


class EntityLinker:
    """Helper class to disambiguate entities
    using wikidata"""

    wikidata_url = "https://www.wikidata.org/w/api.php?action=wbsearchentities"\
            + "&search={0}"\
            + "&language={1}"\
            + "format=json"

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.cos_sim = nn.CosineSimilarity(dim=1, eps=1e-6)
    

    def disambiguate(self, ent_name, sentences):
        """
        :param ent_name: the name of the entity to disambiguate
        :param sentences: a list of sentence in which the `ent_name` appears
        """
        ent = {
            "wikidata_id": None,
            "name": None
        }
        try:
            response_data = requests.get(wikidata_url.format(ent_name, "en"))
            max_sim_score = 0 
            max_score_idx = None
            for idx, wiki_ent in enumerate(response_data["search"]):
                sim_score = sentence_simscore(wiki_ent['description'], 
                        sentences[0])
                if max_sim_score < sim_score:
                    max_score_idx = idx
                # TODO consider the list of sentences in which ent_name appear
            return response_data['search'][idx]
        except:#TODO precise the exception
            return None


    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


    def sentence_simscore(self, sentence1, sentence2):
        """
        Compute the a similarity score between two sentences
        """
        tokenizer = self.tokenizer
        model = self.model
        encoded_input1 = tokenizer(sentence1, padding=True, truncation=True, return_tensors='pt')
        encoded_input2 = tokenizer(sentence2, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output1 = model(**encoded_input1)
            model_output2 = model(**encoded_input2)
        sentence_embeddings1 = self.mean_pooling(model_output1, encoded_input1['attention_mask'])
        sentence_embeddings2 = self.mean_pooling(model_output2, encoded_input2['attention_mask'])
        sentence_embeddings1 = F.normalize(sentence_embeddings1, p=2, dim=1)
        sentence_embeddings2 = F.normalize(sentence_embeddings2, p=2, dim=1)
        return self.cos_sim(sentence_embeddings1, sentence_embeddings2)




if __name__ == "__main__":
    lnk = EntityLinker()
    score = lnk.sentence_simscore(
        "This is a soccer ball",
        "I like sakura flowers"
    )
    print(score)
    score = lnk.sentence_simscore(
        "This is a soccer ball",
        "This is a basket ball"
    )
    print(score)