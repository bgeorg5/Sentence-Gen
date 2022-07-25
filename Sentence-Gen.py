# import language_tests as test

### STAGE 1 ###

# returns: list 
# - list of words(unigrams)
#   ex.   input: "filename.txt"
#        output: [["hello", “world”], ["hello", "world", “again”]]
def load_book(filename):
    temp = []
    try:
        f = open(filename, "r")
        t = f.read().splitlines()

        for l in t:
            if l != '':
                tmp = l.split(" ")
                temp.append(tmp)
            
        f.close()
    except FileNotFoundError:
        print("File not found.")

    return temp

# returns: int 
# - total # of unigrams(single words and symbols) from a corpus(2D list)
#   ex.  input: [["hello", “world”], ["hello", "world", “again”]]
#       output: 5
def get_corpus_length(corpus):
    count = 0

    for e1 in corpus:
        for e2 in e1:
            count += 1 
    return count

# returns: list 
# - list of unique unigrams from a corpus(2D list)
#    ex.  input: [["hello", “world”], ["hello", "world", “again”]]
#        output: ["hello", "world", “again”]
def build_vocabulary(corpus):
    s = set()

    for e1 in corpus:
        for e2 in e1:
            s.add(e2)
    return s

# returns: dict, {string: int} 
# - dict of format {'word': total count of the word} from a corpus(2D list)
#    ex.  input: [["hello", “world”], ["hello", "world", “again”]]
#        output:  { "hello": 2, "world": 2, "again": 1 }
def count_unigrams(corpus):
    d = dict()

    for e1 in corpus:
        for e2 in e1:
            if e2 in d:
                temp = d.get(e2)
                temp += 1
                d[e2] = temp
            else:
                d[e2] = 1
    return d

# returns: corpus 
# - new corpus of the starting words of each sentence from the input corpus(2D list)
#    ex.  input: [["hello", “world”], ["hello", "world", “again”]]
#        output: [[“hello”], [“hello”]]
def make_start_corpus(corpus):
    l = []

    for e in corpus:
        l.append([e[0]])

    return l

# returns: dict, {string: {string: int}} 
# - 2D dict of format {"outerkey": {"innerkey": total # of occurences of innerkey following the outerkey} from the input corpus(2D list)
#   ex.   input: [["hello", “world”], ["hello", "world", “again”]]
#        output: { "hello": { "world": 2 }, "world": { "again": 1 }}
def count_bigrams(corpus):
    d = dict()

    for sent in corpus:
        for i in range(len(sent)-1):
            outkey = sent[i]
            inkey = sent[i+1]

            # step 4
            if outkey not in d:
                d[outkey] = dict()

            # step 5: inner key (sentence[i+1]) is NOT in 
            # the dictionary of the outer key (sentence[i+1]) 
            if inkey not in d.get(outkey):                   
                # take the current value of the inner dict and set temp as that value - {'the':1} 
                curr_value = d.get(outkey)
                # add another innerkey - {'have':1}
                curr_value[inkey] = 1
                # replace {'the':1} with {'the':1, 'have':1} 
                d[outkey] = curr_value

            # step 5: inner key (sentence[i+1]) IS already in 
            # the dictionary of the outer key (sentence[i+1]) 
            else: # if inkey in d.get(outkey):
                curr_value = d.get(outkey).get(inkey)+1
                temp = curr_value
                d[outkey] = {inkey:temp}
    return d

### STAGE 2 ###

# returns: list of format []
# - new list of the same length where 1/len(unigrams) is the value at each index. from the input UNIQUE list of unigrams
#   ex.   input: ["hello", "world", “again”]
#        output: [1/3, 1/3, 1/3]
def build_uniform_probs(unigrams):
    l = []
    n = len(unigrams)

    for i in range(0, n):
        l.append(1/n)

    return l

# returns: list
# - new list, same length as unigrams, where probability of each word being randomly chosen from the whole book from
# - input of format (unigrams(2D list), frequencies of occurences (dict), count of total unigrams (int))
#   ex.   input: [['hello', 'world'], ['hello', 'world', 'again']] ,  {'hello': 2, 'world': 2, 'again': 1} ,  5
#        output: [2/5, 2/5, 1/5]
def build_unigram_probs(unigrams, unigram_counts, total_count): # params are (list, dict, float)
    l = []*len(unigrams)
    n = total_count

    for i in unigram_counts:
        l.append((unigram_counts.get(i))/n)

    return l

# returns: 2D dict
# - new list, same length as unigrams, where probability of each word being randomly chosen from the whole book from
# - input of format (frequencies of occurences (dict), count of total bigrams (2D dict))
#   ex.   input: { "hello" : 2, "world" : 2, "again" : 1 }, { "hello" : { "world" : 2 }, "world" : { "again" : 1 } }
#        output: {"world" : { "words" : ["again"], "probs" : [0.5] } }
def build_bigram_probs(unigram_counts, bigram_counts):
    d = dict()

    for prev_word in bigram_counts:
        words = [] #word list
        probs = [] #prob list
        
        for k in bigram_counts.get(prev_word):
            n = unigram_counts.get(prev_word)
            k_value = bigram_counts.get(prev_word).get(k)

            # append word to word list
            words.append(k)

            # append prob to prob list
            probs.append(k_value/n) # (freq of k)/n

        td = dict()
        td["words"] = words # maps {"words": [...]}
        td["probs"] = probs # maps {"probs": [...]}

        d[prev_word] = td

    return d

# returns: 2D dict of format {string: float}
# - maps those highest probability words to their probabilities
#   input of format (number of top words, list of words, list of the corresponding probabilities, list of words to ignore)
#   ex.   input: 2, [ "hello", "world", "again"], [2/5, 2/5, 1/5], []
#        output: { "hello" : 2/5, "world" : 2/5 }
def get_top_words(count, words, probs, ignore_list): # params are (int, list, list, list)
    d = dict()
    max_p = 0
    max_w = ""

    for j in range(0, count):

        # repeatedly search for the highest probability word
        for i in range(0, len(probs)):

            # if the new highest prob is found -> replace
            # check that the highest probability word is not already a key in that dictionary and not in ignore_list
            if probs[i] > max_p and words[i] not in ignore_list and words[i] not in d: 
                max_p = probs[i]
                max_w = words[i]

        if max_w not in d:
            d[max_w] = max_p

        #reset for next iteration
        max_p = 0 

    return d


# returns: string
# - generated by concatenating probabilistically-chosen words together.
#   input of format (number of words to generate, word list, list of probabilities corresponding to word list)
from random import choices
def generate_text_from_unigrams(count, words, probs):
    s = ""
    c = 0

    # finish once you’ve added the number of words specified by count.
    while c < count: 
        # choices(words, weights=probs) -> returns ["chosen_word"] list containing the word picked 
        # index temp[0] = "chosen_word"
        temp = choices(words, probs) 

        # add to the string with a space between words
        prev_s = s
        s = prev_s+" "+temp[0]

        c += 1

    return s


# returns: string
# - string of count words generated probabilistically.
# - input of format (number of words to generate, start word list, start word probabilities list, bigram probabilities dictionary)
#   ex. input: 2, [ "hello", "world", "again"], [2/5, 2/5, 1/5], { "hello": { "world": 2 }, "world": { "again": 1 }
def generate_text_from_bigrams(count, start_words, start_word_probs, bigram_probs): #params are (int, list, list, dict) 
    from random import choices

    s = ""
    prev_word = ""

    for i in range(0, count):
        # possibly move inside of if, or inside of if and else
        chosen_word = choices(start_words, start_word_probs)[0]

        # Case 1: 
        # if nothing has been added to the string yet or the last word added was a period (indicating the end of a sentence)
        if s == "" or s[len(s)-1] == '.':
            prev_s = s
            s = prev_s+" "+chosen_word
            # stores previous word
            prev_word = chosen_word


        # Case 2:
        # look up the last word generated in the bigram_probs dictionary
        else:
            # Use the “words” and “probs” lists in the dictionary as parameters to choices,
            sub_dict = bigram_probs.get(prev_word)
            print(prev_word, sub_dict)
            innerkey_word = bigram_probs.get(prev_word).get('words')
            innerkey_prob = bigram_probs.get(prev_word).get('probs')

            choice_params_1 = innerkey_word
            choice_params_2 = innerkey_prob

            # generate new word
            new_chosen_word = choices(choice_params_1, choice_params_2)[0]

            # add the new word to the string you’ve generated thus far
            prev_s = s
            s = prev_s+" "+new_chosen_word

            # store the previous word
            prev_word = new_chosen_word

    return s


### RUN CODE ###

# This code runs the test cases to check your work
# if __name__ == "__main__":
    # test.test_all()
    # test.run()