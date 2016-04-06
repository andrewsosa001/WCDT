import sys, os, praw, nltk, wikipedia

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import *

def extract_entities(sample):
    """
    Returns a set of proposed entities
    """
    sentences = nltk.sent_tokenize(sample)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    def extract_entity_names(t):
        entity_names = []

        if hasattr(t, 'label') and t.label:
            if t.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in t]))
            else:
                for child in t:
                    entity_names.extend(extract_entity_names(child))

        return entity_names

    entity_names = []
    for tree in chunked_sentences:
        # Print results per sentence
        # print extract_entity_names(tree)

        entity_names.extend(extract_entity_names(tree))

    # Print unique entity names
    return set(entity_names)

def detect(headline):

    # Check with NLTK
    entities = extract_entities(headline)

    # Generate Extra Options from Entities
    ents = [e.split() for e in list(entities)]
    ents = [[x[i:i+2] for i in range(len(x)-1)] for x in ents]
    ents = [[' '.join(x) for x in y] for y in ents]

    entities = set([item for sublist in ents for item in sublist])

    #print ents

    # Check with name list
    #for e in list(entities):
    #    for t in e.split():
    #        if (t.upper() not in firsts and t.upper() not in lasts) or len(e.split()) is not 2:
    #            entities.discard(e)

    # Check with Wikipedia
    for e in list(entities):
        try:
            page = wikipedia.page(str(e), auto_suggest=False)
            cats = page.categories

            flag = True
            for c in cats:
                if "deaths" in c.lower() or "births" in c.lower():
                    flag = False
                    break
            if flag:
                #print "REJECTED (MISSING CATEGORY)", e
                entities.discard(e)

        except:
            #print "REJECTED (PAGE NOT FOUND)", e
            entities.discard(e)
    return entities

def process(t):

    if not any(ext in t.lower() for ext in ["dead", "passed away", "died", "rip", "r.i.p."]):
        return

    print "Processing: " + t
    names = list(detect(t))
    for name in names:
        #print t, s
        try:
            hd = Headline(text=t, person=name)
            hd.save()
        except Exception as e:
            print "ERROR", e
        #if any(ext in t.lower() for ext in ["dead", "passed away", "died", "rip", "r.i.p."]):
        #    print  "dead"


def main():
    user_agent = "A headline crawler by /u/jezusosaku"
    r = praw.Reddit(user_agent=user_agent)
    #headlines = r.get_front_page()
    subreddits = ["news", "worldnews", "all"]
    headlines = r.get_subreddit("news").get_hot()

    for sub in subreddits:
        headlines = r.get_subreddit(sub).get_hot()
        for t in [x.title for x in headlines]:
            process(t)

if __name__ == "__main__":
    #main()
    x = "Erik Bauersfeld, voice of Admiral Ackbar, has died at 93"
    process(x)

    #x = "Jackie Chan, Pedro Almodovar among celebrities implicated by Panama Papers"
    #print detect(x)
