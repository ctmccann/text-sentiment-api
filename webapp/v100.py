VERSION_STR = 'v1.0.0'


import db
import time
from error import Error
from flask import Blueprint, request, jsonify, json, g

blueprint = Blueprint(VERSION_STR, __name__)


def r_remove_key(o, keys_to_remove):
    if hasattr(o, 'iteritems'):
        return {k: r_remove_key(v, keys_to_remove) \
                for k, v in o.iteritems() \
                    if k not in keys_to_remove}
    elif hasattr(o, '__iter__'):
        return [r_remove_key(i, keys_to_remove) for i in o]
    else:
        return o


def insert_into_db(request, response_dict):
    process_time_ms = (time.time() - g.start_time) * 1000.0
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
    Analyze text sentiment using Vader
    This endpoint accepts text input. It analyzes the sentiment of the
    text using the Vader Sentiment tool. For more detail on the Vader tool,
    see https://github.com/cjhutto/vaderSentiment

    The sentiment of the text is evaluated at several levels: the word level,
    the sentence level, the paragraph level, and the entire document level.
    The sentiment results are returned as JSON.
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
        description: The text document which shall be analyzed for sentiment at various levels
        required: true
        type: string
      - name: word_level
        in: query
        description: A boolean input flag (default=true) indicating whether or not to compute and return the sentiment at the word-level
        required: false
        type: boolean
      - name: sentence_level
        in: query
        description: A boolean input flag (default=true) indicating whether or not to compute and return the sentiment at the sentence-level
        required: false
        type: boolean
      - name: paragraph_level
        in: query
        description: A boolean input flag (default=true) indicating whether or not to compute and return the sentiment at the paragraph-level
        required: false
        type: boolean
      - name: document_level
        in: query
        description: A boolean input flag (default=true) indicating whether or not to compute and return the sentiment at the document-level
        required: false
        type: boolean

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
              type: array
              items:
                $ref: '#/definitions/SentimentRecord'
              description: an array of SentimentRecord objects, one item for each word in the document
            sentences:
              type: array
              items:
                $ref: '#/definitions/SentimentRecord'
              description: an array of SentimentRecord objects, one item for each sentence in the document
            paragraphs:
              type: array
              items:
                $ref: '#/definitions/SentimentRecord'
              description: an array of SentimentRecord objects, one item for each paragraph in the document
            process_time:
              type: number
              description: The processing time in milliseconds taken to build this object
      - schema:
          id: SentimentRecord
          type: object
          description: The sentiment of a text snippet
          required:
            - text
            - sentiment
          properties:
            text:
              type: string
              description: echo the text of this snippet
            sentiment:
              type: number
              description: the sentiment score of this snippet, ranging in [-1, 1]
    '''
    if 'text' not in request.form:
        raise Error(1412, "You must pass the 'text' parameter to the vader_sentiment endpoint")
    text = request.form.get('text')

    word_level      = (request.args.get('word_level',      'true') == 'true')
    sentence_level  = (request.args.get('sentence_level',  'true') == 'true')
    paragraph_level = (request.args.get('paragraph_level', 'true') == 'true')
    document_level  = (request.args.get('document_level',  'true') == 'true')

    response = {}

    # TODO nltk stuff
    response['text-echo'] = text
    response['word-level-echo'] = word_level
    response['sentence-level-echo'] = sentence_level
    response['paragraph-level-echo'] = paragraph_level
    response['document-level-echo'] = document_level

    # TODO add 'Access-Control-Allow-Origin' header to the response

    insert_into_db(request, response)
    return jsonify(response)


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
