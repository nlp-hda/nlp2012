from nltk.probability import FreqDist

inputfile = open('text-utf8.txt', 'r')
outputfile = open('output_file.txt', 'w')

read = inputfile.read()
words = read.split()

# Create Tupels (word|freq)
dictionary = FreqDist(words)


for word in dictionary:
    pair = word + ',' + str(dictionary[word])
    print pair
    #output.write(pair+'\n')
    
input.close()
output.close()