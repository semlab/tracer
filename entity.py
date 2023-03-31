import requests

class EntityLinker:
    """Helper class to disambiguate entities
    using wikidata"""

    wikidata_url = "https://www.wikidata.org/w/api.php?action=wbsearchentities"
            + "&search={0}"
            + "&language={1}"
            + "format=json"

    def __init__():
        pass 
    

    def disambiguate(ent_name, sentences):
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


    def sentence_simscore(sentence1, sentence2):
        """
        Compute the a similarity score between two sentences
        """
        pass