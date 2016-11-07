VERSION_STR = 'v1.0.0'


import db
import time
from error import Error
from flask import Blueprint, request, jsonify, json, g

blueprint = Blueprint(VERSION_STR, __name__)


#import nltk.data
#from nltk import tokenize
#from nltk.sentiment.vader import SentimentIntensityAnalyzer

#VADER_SENTIMENT_ANALYZER = SentimentIntensityAnalyzer()
#WORD_TOKENIZER = tokenize.TweetTokenizer()
#SENT_TOKENIZER = nltk.data.load('tokenizers/punkt/english.pickle')
#PARA_TOKENIZER = tokenize.BlanklineTokenizer()


#def score_word(word):
#    return VADER_SENTIMENT_ANALYZER.lexicon.get(word, 0.0)


#def compute_sentiment_record(text):
#    sentiment_record = {'text': text}
#    sentiment_record.update(VADER_SENTIMENT_ANALYZER.polarity_scores(text))
#    return sentiment_record


def r_remove_key(o, keys_to_remove):
    if hasattr(o, 'iteritems'):
        return {k: r_remove_key(v, keys_to_remove) \
                for k, v in o.iteritems() \
                    if k not in keys_to_remove}
    elif hasattr(o, '__iter__'):
        return [r_remove_key(i, keys_to_remove) for i in o]
    else:
        return o


def insert_into_db(request, response_dict, process_time_ms):
    parameters_dict = {'args': request.args,
                       'form': request.form,
                       'cookies': request.cookies,
                       'headers': request.headers,
                       'method': request.method,
                       'base_url': request.base_url,
                       'remote_addr': request.remote_addr}
    parameters_dict = r_remove_key(parameters_dict, set())
    response_dict = r_remove_key(response_dict, set())
    db.insert_query(json.dumps(parameters_dict),
                    json.dumps(response_dict),
                    process_time_ms)


@blueprint.route('/vader_sentiment', methods=['POST'])
def vader_sentiment():
    '''
	This API takes in a text string of interests/moods and returns 3 location names and lat/long of said places.
    ---
    tags:
      - v1.0.0

    responses:
      200:
        description: An text sentiment info object
        schema:
          $ref: '#/definitions/TextSentimentInfo'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: text
        in: formData
        description: The text document which shall be analyzed for places to visit.
        required: true
        type: string

    definitions:
      - schema:
          id: TextSentimentInfo
          type: object
          description: Info about the text sentiment at various levels of a document
          required:
            - process_time
          properties:
            document:
              $ref: '#/definitions/SentimentRecord'
              description: the sentiment of the entire document
            words:
              type: object
              description: an object having the sentiment of each word in the document, duplicates removed
            sentences:
              type: array
              items:
                $ref: '#/definitions/SentimentRecord'
              description: one object for each sentence in the document
            paragraphs:
              type: array
              items:
                $ref: '#/definitions/SentimentRecord'
              description: one object for each paragraph in the document
            process_time:
              type: number
              description: The processing time in milliseconds taken to build this object
      - schema:
          id: SentimentRecord
          type: object
          description: The sentiment of a text snippet
          required:
            - text
            - neg
            - neu
            - pos
            - compound
          properties:
            text:
              type: string
              description: echo the text of this snippet
            neg:
              type: number
              description: the negative component of the sentiment
            neu:
              type: number
              description: the neutral component of the sentiment
            pos:
              type: number
              description: the positive component of the sentiment
            compound:
              type: number
              description: the compound sentiment in the range [-1, 1]
    '''

    # Grab the 'text' parameter, and error if the user didn't give it!
    if 'text' not in request.form:
        raise Error(1412, "You must pass the 'text' parameter to the Destiny endpoint")
    text = request.form.get('text')

    # Grab the optional parameters.
#    word_level      = (request.form.get('word_level',      'true') == 'true')
#    sentence_level  = (request.form.get('sentence_level',  'true') == 'true')
#    paragraph_level = (request.form.get('paragraph_level', 'true') == 'true')
#    document_level  = (request.form.get('document_level',  'true') == 'true')

    # Build the response dictionary object.
    response_dict = {}
    response_dict['venue1'] = "barbarella"
    response_dict['lat1'] = "30.2671529"
    response_dict['long1'] = "-97.7366477"
    response_dict['venue2'] = "franklin-bbq"
    response_dict['lat2'] = "30.2701188"
    response_dict['long2'] = "-97.7312727"
    response_dict['venue3'] = "galvanize"
    response_dict['lat3'] = "30.2653263"
    response_dict['long3'] = "-97.7495499"


#    if word_level:
#        vocab = set(word.lower() for word in WORD_TOKENIZER.tokenize(text))
#        response_dict['words'] = {word: score_word(word) for word in vocab}
#    if sentence_level:
#        response_dict['sentences'] = [compute_sentiment_record(sentence)
#                for sentence in SENT_TOKENIZER.tokenize(text)]
#    if paragraph_level:
#        response_dict['paragraphs'] = [compute_sentiment_record(paragraph)
#                for paragraph in PARA_TOKENIZER.tokenize(text)]
#    if document_level:
#        response_dict['document'] = compute_sentiment_record(text)

    # Copute the processing time required to serve this reqeust.
    process_time_ms = (time.time() - g.start_time) * 1000.0
    response_dict['process_time'] = process_time_ms

    # Store this request/response pair to the database for our own records.
    insert_into_db(request, response_dict, process_time_ms)

    # Return the JSON encoded response Flask object.
    response = jsonify(response_dict)
    return response


@blueprint.after_request
def set_poper_headers(response):
    '''
    By default the browser will flip out if the API is on a remote domain
    and doesn't set the proper Access-Control-Allow-Origin header.
    This function fixes that so that the browsers are happy. This function
    will add the proper header to ALL responses returned from this
    blueprint.
    '''
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
