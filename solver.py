from functools import total_ordering
import json
import itertools
from collections import Counter
from timeit import default_timer as timer
import sys, getopt

allWords = [];
possibleResults = [''.join(x) for x in itertools.product('gby', repeat=5)]
HELP_STRING = "solver.py [-h --help] [-s --simulate] [-f --firstword]"

def main(argv):
    if len(argv) == 0:
        run()
    else:
        try:
            opts, args = getopt.getopt(argv, "hsf", [])
        except getopt.GetoptError:
            print(HELP_STRING)
        
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(HELP_STRING)
                sys.exit()
            elif opt in ("-s", "--simulate"):
                result_list = simulatePerformance()
                print(Counter(elem[1] for elem in result_list))
                sys.exit()
            elif opt in ("-f", "--firstword"):
                print("Calculating the best first word!")
                print("WARNING: This may take a short while")
                calcBestFirstWord()
                sys.exit()


def run():
    """
    Runs the solver.
    """
    answerWords = loadData()
    while(True):
        print("Enter your guess: (Recommended first guess is 'ISTLE'):")
        guess = str(input()).upper()
        if not isValidGuess(guess):
            print("Guess not valid")
            continue

        print("Please enter your result: (format xxxxx, g=green, y=yellow, b=black. e.g. gbybb):")
        result = str(input()).lower()
        while(not isValidResult(result)):
            print("Please enter your result: (format xxxxx, g=green, y=yellow, b=black. e.g. gbybb):")
            result = str(input()).lower()
        
        # Filter currWords by matching on guess, result
        answerWords = list(filter(lambda ansWord: match(ansWord, guess, result), answerWords))
        if len(answerWords) == 1:
            print("Solved! Answer: " + answerWords[0])
            return

        bestGuess, bestScore = getBestWord(answerWords)
        print("{} possible words remaining. Best guess is: {}".format(len(answerWords), bestGuess))

def isValidResult(result):
    """
    Determines if a given result string is valid.

    Valid means matches the required formatting "xxxxx" where x in {g, b , y}

    Parameters:
    result (string): A given result string

    Returns:
    bool: True if string is a valid result, False otherwise.
    """
    if len(result) != 5:
        return False
    
    for i in range(0,5):
        if result[i] != 'g' and result[i] != 'y' and result[i] != 'b':
            return False
    
    return True

def isValidGuess(guess):
    """
    Determines if a given guess is valid.

    Parameters:
    result (string): A given guess string

    Returns:
    bool: True if string is a valid guess, False otherwise.
    """
    if len(guess) != 5:
        return False
    
    if not guess.isalpha():
        return False

    if guess not in allWords:
        return False
   
    return True

def loadData():
    """
    Loads the word lists from the data file.
    """
    f = open('words.json')

    data = json.load(f)
    
    answerWords = data['possibleWords']
    impossibleWords = data['impossibleWords']

    '''
    ## Confirmed no overlap in both
    for i in answerWords:
        if i in impossibleWords:
            print(i);
    ## never prints
    '''

    global allWords
    allWords = answerWords + impossibleWords

    return answerWords

def calcBestFirstWord():
    """
    Entry point. Calculates scores for all possible guess words and returns the best word
    to guess, along with its score.
    """
    answer_words = loadData()
    bestWord, lowestScore = getBestWord(answer_words)
    print("Best is {} with avg words left {}".format(bestWord, lowestScore))

def getScoreAvg(testWord, answerWords, depth=0):
    """
    Recursively calculates the score for a given guess (testWord), given the remaining possible
    answer words.

    Guesses are scored by the average size of the remaining solution set, considering all possible
    results.

    Parameters:
    testWord (string): A guess word.
    answer_words (list): The remaining possible solution words.
    depth (int): The current depth (limit 0-4 inclusive).

    Returns:
    string, int: The best guess and its score.
    
    """
    if depth>4:
        return len(answerWords)
    
    if len(answerWords) == 0:
        return 0
    
    total = 0
    nonzero = 0

    gWords = list(filter(lambda t: testWord[depth] == t[depth], answerWords))
    if len(gWords) > 0:
        nonzero += 1
        total += getScoreAvg(testWord, gWords, depth+1)
    
    yWords = list(filter(lambda t: testWord[depth] in t and testWord[depth] != t[depth], answerWords))
    if len(yWords) > 0:
        nonzero += 1
        total += getScoreAvg(testWord, yWords, depth+1)
    
    bWords = list(filter(lambda t: testWord[depth] not in t, answerWords))
    if len(bWords) > 0:
        nonzero += 1
        total += getScoreAvg(testWord, bWords, depth+1)
    
    return total / nonzero

def getScoreWorstCase(testWord, answerWords, depth):
    """
    Recursively calculates the score for a given guess (testWord), given the remaining possible
    answer words.

    Guesses are scored by the size of the biggest possible remaining solution set, considering 
    all possible results. This is an alternative scoring mechanism (unused). Unsure on correctness
    as it is not kept up to date with getScoreAvg.

    Parameters:
    testWord (string): A guess word.
    answer_words (list): The remaining possible solution words.
    depth (int): The current depth (limit 0-4 inclusive).

    Returns:
    string, int: The best guess and its score.

    """
    if depth>4:
        return len(answerWords)
    
    worst = -1

    gWords = list(filter(lambda t: testWord[depth] == t[depth], answerWords))
    if len(gWords) > 0:
        score = getScoreAvg(testWord, gWords, depth+1)
        if score > worst:
            worst = score
    
    yWords = list(filter(lambda t: testWord[depth] in t and testWord[depth] != t[depth] ))
    if len(yWords) > 0:
        score = getScoreAvg(testWord, yWords, depth+1)
        if score > worst:
            worst = score
    
    bWords = list(filter(lambda t: testWord[depth] not in t))
    if len(bWords) > 0:
        score = getScoreAvg(testWord, bWords, depth+1)
        if score > worst:
            worst = score
    
    return worst

def getBestWord(answer_words):
    """
    Given the remaining possible solutions, returns the best valid guess along with its score.

    Guesses are scored by the average size of the remaining solution set, considering all possible
    answers

    Parameters:
    answer_words (list): The remaining possible solution words

    Returns:
    string, int: The best guess and its score.
    
    """
    lowestScore = 9999999
    bestWord = ""

    for i in range(len(allWords)):
        currWord = allWords[i]
        avg = getScoreAvg(currWord, answer_words, 0)
        if avg < lowestScore:
            lowestScore = avg
            bestWord = currWord
    
    return bestWord, lowestScore

def match(potentialAns, prevGuess, score):
    """
    Determines if a given answer word is valid given a combination of a guess and its result.

    I.e. if the answer is the given word, then could that combination of guess and result have happened.

    Parameters:
    potentialAns (string): A potential answer word
    prevGuess (string): A guessed word
    score (string): The result of guessing prevGuess, in the form "xxxxx" where x in {g, y, b}

    Returns:
    bool: True if answer word valid under given information, False otherwise.
    """

    # Optimisation: Instead of calculating the full result and comparing, we
    #   could exit early in the process of generating the result if it doesn't match
    #   at some point.
    return calcResult(potentialAns, prevGuess) == score

def calcResult(answer, guess):
    """
    Given the answer to a wordle and a guess, calculates the result string.

    Parameters:
    answer (string): The answer to a wordle
    guess (string): The guess word

    Returns:
    string: The colour-coded result of making the guess against the given answer. Format "xxxxx" for x in {g, b, y}
    """
    letter_counts = Counter(answer)

    result = ['b', 'b', 'b', 'b', 'b']

    for i in range(0, 5):
        if answer[i] == guess[i]:
            result[i] = 'g'
            letter_counts[guess[i]] -= 1
    
    for i in range(0, 5):
        if result[i] == 'g':
            continue
        if guess[i] in answer and letter_counts[guess[i]] > 0:
            result[i] = 'y'
    
    return ''.join(result)

# Make the solver play the game vs itself for all the possible answer words
def simulatePerformance():
    """
    For every possible answer word, makes the solver play a game of Wordle for that
    word. Prints results and metrics.

    Returns:
    list: A list of tuples (word, score) giving the solvers score for each word.    
    """
    print("WARNING: THIS WILL TAKE A VERY LONG TIME TO RUN!")
    print("On my machine this takes almost 4 hours to complete")
    answerWords = loadData()
    scoreArray = []

    guess = "ISTLE" # Computed from calcBestFirstWord() and cached here

    origAnswerWords = loadData()

    count = 0

    totalScore = 0.0
    totalElapsed = 0

    maxScore = 0
    maxScoreWord = ""

    maxTime = 0
    maxTimeWord = ""

    for w in origAnswerWords:
            start = timer()
            answerWords = origAnswerWords.copy()
            turn = 1
            while(True):
                result = calcResult(w, guess)
        
                answerWords = list(filter(lambda ansWord: match(ansWord, guess, result), answerWords))
                if len(answerWords) == 1:
                    # SOLVED
                    scoreArray.append((w, turn))
                    break

                guess, _ = getBestWord(answerWords)
                turn += 1
            end = timer()
            elapsed = end - start
            count += 1
            totalElapsed += elapsed
            totalScore += turn
            
            if turn > maxScore:
                maxScore = turn
                maxScoreWord = w

            if elapsed > maxTime:
                maxTime = elapsed
                maxTimeWord = w
            print("{} : Time Elapsed: {:.2f}s :: Score: {} :: Avg Time: {:.2f}s :: Total Time: {:.2f}s :: Avg Score: {:.4f}".format(count, elapsed, turn, totalElapsed/count, totalElapsed, totalScore/count)) # Time in second
    
    print("RESULTS")
    print("Turns to solve: Average {:.4f} turns :: Maximum {} turns to solve word {}".format(totalScore / count, maxScore, maxScoreWord))
    print("Time per game: Average {:.2f} seconds :: Maximum {:.2f} seconds to solve word {}".format(totalElapsed / count, maxTime, maxTimeWord))
    print("Total time elapsed to play all games: {:.2f} seconds.".format(totalElapsed))
    print("Score Array:")
    print(scoreArray)
    return scoreArray


if __name__ == "__main__":
    main(sys.argv[1:])