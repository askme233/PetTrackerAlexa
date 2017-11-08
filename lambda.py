"""
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import time
import datetime


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Pet Tracker. " \
                    "Please tell me the type of pet you have by saying, " \
                    "I have a dog."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me the type of pet you have by saying, " \
                    "I have a dog."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you using Pet Tracker. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def set_pet_in_session(intent, session):

    intent_name = intent['name']
    session_attributes = {}
    if 'attributes' in session:
        session_attributes = session['attributes']
    else:
        session['attributes'] = {}


    should_end_session = False
    pet_type = ''
    speech_output = ''
    reprompt_text = None


    if 'PetType' in intent['slots'] and 'value' in intent['slots']['PetType']:
        pet_type = intent['slots']['PetType']['value']

        if intent_name not in session['attributes']:
            session['attributes'][intent_name] = {}
            session_attributes[intent_name] = {}

        if pet_type in session['attributes'][intent_name]:
            session_attributes[intent_name][pet_type] = session['attributes'][intent_name][pet_type]

        if intent_name == 'WalkPet':
            session_attributes[intent_name][pet_type] = time.time()
            speech_output = "I have saved that you walked your " + pet_type
        elif intent_name == 'FeedPet':
            session_attributes[intent_name][pet_type] = time.time()
            speech_output = "I have saved that you fed your " + pet_type
        elif intent_name == 'PetMeds':
            session_attributes[intent_name][pet_type] = time.time()
            speech_output = "I have saved that you gave your " + pet_type + " its meds"

    else:
        session_attributes = session['attributes'];
        speech_output = "I'm not sure what is going on. " \
                        "Please try again."
        reprompt_text = "I'm not sure what is happening. " \
                        "Please try again."


    return build_response(session_attributes, build_speechlet_response(
        'Action tracked', speech_output, reprompt_text, should_end_session))


def get_pet_from_session(intent, session):

    session_attributes = {}
    if 'attributes' in session:
        session_attributes = session['attributes']
    else:
        session['attributes'] = {}

    should_end_session = False
    reprompt_text = None
    intent_name = intent['name']
    pet_type = ''
    pet_action = ''
    speech_output = ''

    if 'PetType' in intent['slots'] and 'value' in intent['slots']['PetType']:
        pet_type = intent['slots']['PetType']['value']

    if 'PetAction' in intent['slots'] and 'value' in intent['slots']['PetAction']:
        pet_action = intent['slots']['PetAction']['value']

    if pet_type != '' and pet_action != '':

        if intent_name not in session['attributes']:
            session['attributes'][intent_name] = {}
            session_attributes[intent_name] = {}

        if pet_action == 'feed' or pet_action == 'fed':
            intentAction = 'FeedPet'
            actionWord = 'fed'
            speech_output = "Your " + pet_type + " was " + actionWord + " "
        elif pet_action == 'walk' or pet_action == 'walked':
            intentAction = 'WalkPet'
            actionWord = 'walked'
            speech_output = "Your " + pet_type + " was " + actionWord + " "
        elif pet_action == 'meds':
            intentAction = 'PetMeds'
            actionWord = 'walked'
            speech_output = "Your " + pet_type + " last got its " + actionWord + " "

        if intentAction in session['attributes'] and pet_type in session['attributes'][intentAction]:
            action_time = session['attributes'][intentAction][pet_type]

            seconds = (int(time.time()) - int(action_time))
            minutes = int(seconds)/60 % 60
            hours = int(seconds)/60/60 % 24
            days = int(seconds)/60/60/24

            time_frame = ''
            if days > 0:
                time_frame += str(days) + " day"
                if days > 1:
                    time_frame += "s"
                time_frame += " "

            if hours > 0:
                time_frame += str(hours) + " hour"
                if hours > 1:
                    time_frame += "s"
                time_frame += " "

            if time_frame != '':
                time_frame += "and "

            speech_output += time_frame + str(minutes) + " minute"
            if minutes > 1:
                speech_output += "s"
            speech_output += " ago"

            # datetime.datetime.fromtimestamp(int(action_time)).strftime('%A %Y-%m-%d at %H:%M %p')

            # speech_output += datetime.datetime.fromtimestamp(int(action_time)).strftime('%A %Y-%m-%d at %H:%M %p')
                # should_end_session = True
        else:
            speech_output = 'I do not know when you last ' + actionWord + ' your ' + pet_type
            session_attributes = session['attributes']

    if speech_output == '':
        speech_output = "I'm not sure what you want."
        session_attributes = session['attributes']
        # should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        'Action response', speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WalkPet" or intent_name == "FeedPet" or intent_name == "PetMeds":
        return set_pet_in_session(intent, session)
    elif intent_name == "AskPet":
        return get_pet_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
