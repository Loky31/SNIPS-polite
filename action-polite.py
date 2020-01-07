#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import configparser
import io
import requests
import random
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology.feedback import SiteMessage
from collections import defaultdict

liste_reponses_bonsoir = ["bonsoir, cordialement", "bonsoir", "bien le bonsoir", "oh bonsoir", "bonsoir très cher"]
liste_reponses_au_revoir = ["bye bye","que la force soit avec vous","Au revoir", "Bonne journée", "Ne rentrez pas trop tard", "Au revoir très cher", "La journée sera longue sans vous", "Faites attention à vous et passez une bonne journée"]
liste_reponses_ca_va = ["En pleine forme aujourd'hui et vous?", "On fait aller", "Dur réveil je vais prendre un café", "prêt a conquérir le monde, ou du moins a le piloter", "petite forme espérons que ca aille mieux plus tard", "je suis impatient de vous rendre service", "plutôt bien aujourd'hui, et vous?"]
liste_reponses_bonjour = ["Bonjour", "Salut", "Coucou", "oh bonjour", "hey salut", "bien le bonjour", "Bonjour très cher", "Je vous souhaite le bonjour", "salutations"]
liste_reponses_merci = ["me remercier point vous n'avez besoin","de rien", "avec plaisir", "a votre service", "je ne fais que mon devoir", "il n'y a vraiment pas de quoi", "j'aime me rendre utile", "je reste à votre disposition", "je suis là pour ça", "tout le plaisir est pour moi", "enfin voyons vos désirs sont des ordres"]
liste_reponses_appetit = ["le gras c'est la vie","bon appétit", "Quoi de bon au menu?", "Soyez raisonnable sur le menu bon appétit", "il faut mâcher lentement pour mieux digérer", "régalez-vous"]
liste_reponses_bonne_nuit = ["A demain, faites de beaux rêves.", "Moi aussi je vais dormir, je suis crevée.", "Bonne nuit !", "Dormez bien, à demain !", "OK. Moi je vais regarder un bon film à la télé.", "ok bonne nuit.", "à demain !", "bonne nuit très cher.", "je crois que Morphée m'attend aussi, à demain"]
liste_reponses_apres_midi = ["bon après-midi", "une petite sieste?", "bonne digestion", "bon après-midi très cher", "profitez de votre après midi"]
liste_reponses_presentation = ["Je suis ravi de vous rencontrer", "Mes hommages", "Quel plaisir de faire votre connaissance"]
liste_reponses_capacite = ["Tout et un peu plus","Ma formation terminé j'ai, les pouvoirs du jédaï sont miens","Je suis très puissant grace au coté obscur de la force","mes pouvoir sont infini pauvre humain!","Nul besoin de me venter","Vous ne pouvez que l'imaginer"]
state = {'cassos': False}
status = {'thanks': False}

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {
            section: {
                option_name: option
                for option_name, option in self.items(section)
            }
            for section in self.sections()
        }

class Slot(object):
   def __init__(self, data):
      self.slotName = data['slotName']
      self.entity = data['entity']
      self.rawValue = data['rawValue']
      self.value = data['value']
      self.range = data['range']        
        
def answerChoice(answerList):
    return random.choice(answerList)
    
def Bonsoir():
    return answerChoice(liste_reponses_bonsoir)

def Au_revoir():
    return answerChoice(liste_reponses_au_revoir)

def Ca_va():
    return answerChoice(liste_reponses_ca_va)

def Bonjour():
    return answerChoice(liste_reponses_bonjour)

def Merci():
    return answerChoice(liste_reponses_merci)

def Appetit():
    return answerChoice(liste_reponses_appetit)

def Bonne_nuit():
    return choix_reponse(liste_reponses_bonne_nuit)

def Apres_midi():
    return answerChoice(liste_reponses_apres_midi)

def Presentation():
    return answerChoice(liste_reponses_presentation)

def Capacite():
    return answerChoice(liste_reponses_capacite)
    
def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("Loky31:", "")
    result = None
    print("{}".format(intent_name))
    if intent_name == "Bonsoir":
        result = Bonsoir()
    elif intent_name == "Ca_va":
        result = Ca_va()
    elif intent_name == "Bonjour":
        result = Bonjour()
    elif intent_name == "Merci":
        print("thanks activé")
        status['thanks'] = True
        result = Merci()
    elif intent_name == "Appetit":
        result = Appetit()
    elif intent_name == "Bonne_nuit":
        result = Bonne_nuit()
    elif intent_name == "Apres_midi":
        result = Apres_midi()
    elif intent_name == "Au_revoir":
        state['cassos'] = True
        result = Au_revoir()
    elif intent_name == "Capacite": 
        #result = "Je suis capable de tout un tas de choses allant de piloter les volets le home cinéma les lumières ou vous donner une définition de wikipédia faire une liste de courses et tant d'autres choses"
        result = Capacite()
    elif intent_name == "Presentation":
        slot_values = intent_message.slots.Prenoms.all().value
        if len(intent_message.slots["Prenoms"])== 1:
            print("1 slot de nom trouvé")
            result = ""+Presentation()+"{}".format(slot_values[0].value)
        elif len(intent_message.slots["Prenoms"])== 2: 
            print("2 slots de nom trouvé")
            result = ""+Presentation()+"{} et {}".format(slot_values[0].value,slot_values[1].value)
    if result is not None:
        if not status['thanks']:
            if not state['cassos']:
                print("{}".format(result))
                hermes.publish_continue_session(intent_message.session_id,result,["Loky31:Bonsoir","Loky31:Ca_va","Loky31:Bonjour","Loky31:Merci","Loky31:Appetit","Loky31:Bonne_nuit","Loky31:Apres_midi","Loky31:Au_revoir","Loky31:Capacite","Loky31:Presentation"])
                #SiteMessage.publish_feedback_sound_toggleOn(siteId=default)
           #     hermes.enable_sound_feedback(SiteMessage("default"))
            else:
                print("cassos activé")
                state['cassos'] = False
                hermes.publish_end_session(intent_message.session_id, result+"Merci pour cette discussion")
                #hermes.disable_sound_feedback(SiteMessage("default"))
        else:
            status['thanks'] = False
            hermes.publish_end_session(intent_message.session_id, result) 
    #if result is None:
        #hermes.publish_end_session(intent_message.session_id, "Merci pour cette discussion")
        #SiteMessage.publish_feedback_sound_toggleOn(siteId=default)
        #hermes.enable_sound_feedback(SiteMessage("default"))

if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
        #h.disable_sound_feedback(SiteMessage("default"))
        #h.subscribe_enable_sound_feedback(SiteMessage("default"))
