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
            + "&format=json"

    def __init__(self):
        #self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        #self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/msmarco-distilbert-base-tas-b')
        self.model = AutoModel.from_pretrained('sentence-transformers/msmarco-distilbert-base-tas-b')
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
            url = EntityLinker.wikidata_url.format(ent_name, "en")
            print(url)
            response = requests.get(url)
            data = response.json()
            max_sim_score = 0 
            max_score_idx = None
            if len(data['search']) == 1:# only one entity in the result
                return data['search'][0] 
            for idx, wiki_ent in enumerate(data["search"]):
                sim_score = self.sentence_simscore(wiki_ent['description'], 
                        sentences[0])
                print(f"{idx}: {wiki_ent['id']}, score={sim_score}")
                if max_sim_score < sim_score:
                    print(f"trading {sim_score} for {max_sim_score}")
                    max_sim_score = sim_score
                    max_score_idx = idx
                # TODO consider the list of sentences in which ent_name appear
            print("max idx", max_score_idx)
            return data['search'][max_score_idx]
        except Exception e:#TODO precise the exception
            print(data)
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
        cos_sim = self.cos_sim(sentence_embeddings1, sentence_embeddings2)
        return cos_sim.item()




if __name__ == "__main__":
    lnk = EntityLinker()
    sentences = ["Esselte said the Antonson unit, based in LaPorte, Indiana, manufactures scales and label printers."]
    ent = lnk.disambiguate("LaPorte", sentences)
    print(ent)