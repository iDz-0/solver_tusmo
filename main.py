import json

import requests as requests
import unidecode

def generate_data():
    with open('array_words.json', 'r') as f:
        data = json.load(f)
        cleaned_data = dict()
        for word in data:
            if not '-' in word:
                if not len(word) in cleaned_data:
                    cleaned_data[len(word)] = dict([(k, []) for k in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.lower()])
                cleaned_word = unidecode.unidecode(word).lower()
                cleaned_data[len(word)][cleaned_word[0]].append(cleaned_word)

    with open('cleaned_words.json', 'w') as f:
        json.dump(cleaned_data, f)

def load_data():
    with open('cleaned_words.json', 'r') as f:
        return json.load(f)

def start_game():
    url = 'https://www.tusmo.xyz/graphql?opname=StartMotus'
    data = {"operationName":"StartMotus","variables":{"type":"SOLO","lang":"fr"},"query":"mutation StartMotus($type: String!, $lang: String!) {\n  startMotus(type: $type, lang: $lang) {\n    shortId\n    __typename\n  }\n}"}
    res = requests.post(url, json=data)
    shortID = res.json()['data']['startMotus']['shortId']
    return shortID

def join_game(shortID):
    url = 'https://www.tusmo.xyz/graphql?opname=JoinMotus'
    data = {"operationName":"JoinMotus","variables":{"shortId":str(shortID),"playerId":"9a150c145dc613cdc9d3628a64","playerName":"null","accessToken":""},"query":"mutation JoinMotus($shortId: ID!, $playerId: ID!, $playerName: String, $accessToken: String) {\n  joinMotus(\n    shortId: $shortId\n    playerId: $playerId\n    playerName: $playerName\n    accessToken: $accessToken\n  ) {\n    shortId\n    type\n    state\n    lang\n    currentRound\n    isStarted\n    isEnded\n    playersNumber\n    rounds {\n      _id\n      firstLetter\n      length\n      __typename\n    }\n    me {\n      _id\n      name\n      hasWon\n      currentRound\n      state\n      rounds {\n        score\n        hasFoundWord\n        tries {\n          word\n          validation\n          wordExists\n          hasFoundWord\n          mask\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"}
    res = requests.post(url, json=data)
    return res.json()['data']['joinMotus']['rounds'][0]

def try_word(shortID, word):
    url = 'https://www.tusmo.xyz/graphql?opname=TryWord'
    data = {"operationName": "TryWord", "variables": {"word": word, "shortId": shortID, "playerId": "9a150c145dc613cdc9d3628a64", "accessToken": "", "lang": "fr"}, "query": "mutation TryWord($shortId: ID!, $word: String!, $playerId: ID!, $lang: String!, $accessToken: String) {\n  tryWord(\n    shortId: $shortId\n    word: $word\n    playerId: $playerId\n    lang: $lang\n    accessToken: $accessToken\n  ) {\n    word\n    validation\n    wordExists\n    hasFoundWord\n    mask\n    score\n    __typename\n  }\n}"}
    res = requests.post(url, json=data)
    return res.json()['data']['tryWord']

def test_match(word, constraints):

    for c in constraints:
        if c['type'] == 'is' and word[c['index']] != c['value']:
            return False
        if c['type'] == 'is_not' and word[c['index']] == c['value']:
            return False
        if c['type'] == 'contains' and c['value'] not in word:
            return False
        if c['type'] == 'not_contains' and c['value'] in word:
            return False
    return True

if __name__ == '__main__':
    #generate_data()
    data = load_data()
    #shortID = start_game()
    shortID = input('ShortID : ')
    round = join_game(shortID)
    valid_data = data[str(round['length'])][round['firstLetter'].lower()]

    print('Round : ', round)
    constraints = []

    play = True
    while play:
        for i in range(len(valid_data)):
            if test_match(valid_data[i], constraints):
                print('Try : ', valid_data[i])
                result = try_word(shortID, valid_data[i].upper())
                for j, l in enumerate(result['validation']):
                    if l == 'r':
                        for c in constraints:
                            if c['value'] == valid_data[i][j]:
                                constraints.remove(c)
                        constraints.append({'index': j, 'type': 'is', 'value': valid_data[i][j]})
                    if l == 'y':
                        constraints.append({'index': j, 'type': 'contains', 'value': valid_data[i][j]})
                        constraints.append({'index': j, 'type': 'is_not', 'value': valid_data[i][j]})
                    if l == '-':
                        valid = True
                        for c in constraints:
                            if c['value'] == valid_data[i][j] and c['type'] == 'is':
                                valid = False
                        if valid:
                            constraints.append({'index': j, 'type': 'not_contains', 'value': valid_data[i][j]})

                print(constraints)
                if result['hasFoundWord']:
                    play = False
                    print(result)
                break