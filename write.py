import stanza
import re
import pickle
import random

DO_LEARN = False
DO_WRITE = True
LINES_TO_LEARN = 100
LINES_TO_WRITE = 10000

LEARN_FROM = "res/hunger_games.txt"
WRITE_FROM = "res/bla.txt"

DEBUG_PRINT_TYPES = False
DEBUG_PRINT_ORIG = False
DEBUG_PRINT_DETAILED = False
DEBUG_PRINT_LINE = False
DEBIG_PRINT_SPACE = False

found_data = dict()
found_data_feats = dict()

nlp = stanza.Pipeline(lang='en', processors='tokenize,pos', use_gpu=True, pos_batch_size=3000)
required_common = {"PRON":["Person", "Case"]}

class CleanWord:
    def __init__(self, word):
        self.text = word.text
        self.feats = parse_feats(word)
        self.xpos = word.xpos
        self.upos = word.upos
    def __repr__(self):
        return f'<{self.text},{self.feats}>'
        
    def __eq__(self, other):
        if(self.text != other.text):
            return False
        if(self.feats != other.feats):
            return False
        if(self.xpos != other.xpos):
            return False
        if(self.upos != other.upos):
            return False
        return True
        
    def __hash__(self):
        h = 0
        h += hash(self.text)
        h += hash(self.xpos) + hash(self.upos)
        for feat in self.feats:
            h += hash(self.feats[feat])
        return h

def check_a_vs_an(line):
    As = line.replace(" an ", " a ").split(" a ")
    vowels = "aeiouAEIOU"
    new_line = ""
    new_line += As[0]
    for i in range(1,len(As)):
        segment = As[i]
        if segment[0] in vowels:
            new_line += " an "
        else:
            new_line += " a "
        new_line += segment
    return new_line
            

def parse_feats(word):
    if word is None:
        return None
    feats = dict()
    if word.feats is not None:
        for feat in word.feats.split("|"):
            feat_parts = feat.split("=")
            param = feat_parts[0]
            val = feat_parts[1]
            feats[param] = val
    return feats
    
def find_word_of_type(word):
    up = word.upos
    xp = word.xpos
    feats = word.feats

    if up not in found_data:
        return None
    if xp not in found_data[up]:
        return None
    if len(found_data[up][xp]) == 0:
        return None
    canidates = found_data[up][xp]
    
    #if no special cases required, just pick from this list
    if (up not in required_common):
        return random.sample(canidates, 1)[0]
   
    #check if special rules apply
    for POS in required_common:
        if up == POS:
            better_canidates = set()
            for pot_word in canidates:
                required_common_elements = required_common[POS]
                for element in required_common:
                    if(feats is None):
                        continue
                    if(element not in feats):
                        continue
                    if(element not in pot_feats):
                        continue
                    if(pot_feats[element] != feats[element]):
                        continue
                better_canidates.add(pot_word)
            if(len(better_canidates) == 0):
                better_canidates = canidates
            return random.sample(better_canidates, 1)[0]

def add_to_found_data(word):
    up = word.upos
    xp = word.xpos
    feats = parse_feats(word)

    if up not in found_data:
        found_data[up] = dict()
    if xp not in found_data[up]:
        found_data[up][xp] = set()
    
    found_data[up][xp].add(CleanWord(word))

def serial_dump_found_data():
    pickle.dump(found_data, open( "word_bank.gar", "wb" ) )
    
def serial_load_found_data():
    words = pickle.load(open( "word_bank.gar", "rb" ) )
    return words

def learn_words():
    with open(LEARN_FROM, 'r') as file:
        data = file.read().lower().replace('\n', ' ')

    data = data.replace('!', '.').split('.')[0:LINES_TO_LEARN]
    
    i = 0
    for sentence_string in data:
        print(i, ":", sentence_string)
        doc = nlp(sentence_string)
        if(len(doc.sentences) == 0):
            continue
        sentence = doc.sentences[0]
        for word in sentence.words:
            add_to_found_data(word)
        i+=1
    
def write_song():
    with open(WRITE_FROM, 'r') as file:
        data = file.read().lower().split('\n')
    
    i = 0
    for sentence_string in data[0:min(LINES_TO_WRITE,len(data))]:
        doc = nlp(sentence_string)
        if(len(doc.sentences) == 0):
            continue
        sentence = doc.sentences[0]
        new_sentence = ""
        type_sentence = ""
        for word in sentence.words:
            new_word = find_word_of_type(word)
            if(new_word is None):
                continue
            
            sep = " "
            if(word.upos == "PUNCT"):
                sep = ""
                new_word = word
            
            if(word.upos == "DET" or word.upos == "PUNCT"):
                new_word = word
            
            new_sentence += sep + new_word.text
            type_sentence += " " + word.xpos
        
        new_sentence = check_a_vs_an(new_sentence)
        
        print_sentance(sentence, new_sentence, type_sentence)
        i+=1
    
def print_sentance(sentence, new_sentence, type_sentence):
    if(DEBIG_PRINT_SPACE):
        print()
    if(DEBUG_PRINT_ORIG):
        if(DEBUG_PRINT_LINE):
            print(i, ": ", end="")
        print(" " + " ".join([word.text for word in sentence.words]))
    if(DEBUG_PRINT_LINE):
        print(i, ": ", end="")
    print(new_sentence)
    if(DEBUG_PRINT_TYPES):
        if(DEBUG_PRINT_LINE):
            print(i, ": ", end="")
        print(type_sentence)
    if(DEBUG_PRINT_DETAILED):
        print(sentence.words)

if __name__ == '__main__':
    if(DO_LEARN):
        learn_words()
        serial_dump_found_data()
    if(DO_WRITE):
        found_data = serial_load_found_data()
        write_song()