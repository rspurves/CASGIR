import math

class Postings:
    
    def __init__(self, firstMondayTerms, sample, nlp):
        #Load a language model to do NLP
        self.ndocs = len(sample)
                
        # firstMonday works like an inverse stop list, and we only use words in these lists for our posting file
        if firstMondayTerms:
            #We do this so that the serialisation of the Pickle works propery
            data_folder = Path('./data')
            fn1 = data_folder / 'elements.txt'
            fn2 = data_folder / 'qualities.txt'
            fn3 = data_folder / 'activities.txt'
            
            elements = set(pd.read_csv(fn1, header=None)[0])
            qualities = set(pd.read_csv(fn2, header=None)[0])
            activities = set(pd.read_csv(fn3, header=None)[0])

            terms = elements.union(qualities).union(activities)
            lemmas = ' '.join(str(e) for e in terms)

            doc = nlp(lemmas)
            terms = set()
            for token in doc:
                terms.add(token.lemma_)
                
            # Now we process our corpus and create a postings file
            docs = nlp.pipe(sample.text,n_process=2, batch_size=100)

            self.postings = dict()

            for (idxRow, s1), (_, s2) in zip(sample.iterrows(), enumerate(docs)):
                id = s1.id
                for token in s2:
                    lemma = token.lemma_
                    if lemma in terms:

                        if lemma in self.postings:
                            tf = self.postings[lemma]
                            if id in tf:
                                tf[id] = tf[id] + 1
                            else:
                                tf[id] = 1
                        else:
                            tf = {id: 1}
                        self.postings[lemma] = tf
        else:
            # Now we process our corpus and create a postings file
            docs = nlp.pipe(sample.text,n_process=2, batch_size=100)

            self.postings = dict()

            for (idxRow, s1), (_, s2) in zip(sample.iterrows(), enumerate(docs)):
                id = s1.id
                for token in s2:
                    lemma = token.lemma_
                    if lemma in self.postings:
                        tf = self.postings[lemma]
                        if id in tf:
                            tf[id] = tf[id] + 1
                        else:
                            tf[id] = 1
                    else:
                        tf = {id: 1}
                    self.postings[lemma] = tf

    def tfIdf(self, query,nlp):
        results = {}
        qdoc = nlp(query)
        for token in qdoc:
            qt = token.lemma_
            if qt in self.postings:
                dc = len(self.postings[qt])
                idf = math.log10(self.ndocs/(dc + 1))
                for doc in self.postings[qt]:
                    tf = self.postings[qt][doc]
                    tfidf = tf * idf
                    if doc in results:
                        score = results[doc]
                        results[doc] = tfidf + score
                    else:
                        results[doc] = tfidf
        results = dict(sorted(results.items(), key = lambda x: x[1], reverse=True))
        
        return results
    
