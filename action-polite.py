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

liste_reponses_bonsoir = ["bonsoir, cordialement", "bonsoir", "bien le bonsoir", "oh bonsoir", "bonsoir très cher"]
liste_reponses_Au_revoir = ["Au revoir", "Bonne journée", "Bon courage pour le travail", "Ne rentrez pas trop tard", "Au revoir très cher", "La journée sera longue sans vous", "Faites attention sur la route et passez une bonne journée"]
liste_reponses_ca_va = ["En pleine forme aujourd'hui et vous?", "On fait aller", "Dur réveil je vais prendre un café", "prèt a concquerir le monde, ou du moins a le piloter au moins", "petite forme espéront que ca aille mieux plus tard", "je suis impatient de vous rendre service","plutot bien aujourd'hui, et vous?"]
liste_reponses_bonjour = ["Bonjour", "Salut", "Salut j'espère que ça va", "oh bonjour", "hey salut", "bien le bonjour", "Bonjour très cher", "Je vous souhaite le bonjour","salutations"]
liste_reponses_merci = ["de rien", "avec plaisir", "a votre service", "je ne fait que mon devoir", "il n'y a vraiment pas de quoi", "j'aime me rendre utile", "je reste a votre disposition","je suis la pour ça", "tout le plaisir est pour moi","enfin voyons vos desirs sont des ordres"]
liste_reponses_appetit = ["bon appétit", "Quoi de bon au menu?", "Soyez raisonable sur le menu bon appetit", "il faut macher lentement pour mieux digérer", "régalez vous"]
liste_reponses_bonne_nuit = ["A demain, faites de beaux rêves.", "Moi aussi je vais dormir, je suis crevée.", "Bonne nuit !", "Dormez bien, à demain !", "OK. Moi je vais regarder un bon film à la télé.", "ok bonne nuit.", "à demain !", "bonne nuit très cher.", "je crois que Morphée m'attend aussi, à demain"]
liste_reponses_apres_midi = ["bon après midi", "une petite sieste?", "bonne digestion", "bon après midi très cher","profitez de votre après midi"]
liste_reponses_Presentation = ["Je suis ravi de vous rencontrer", "Mes homages", "Quel plaisir de faire votre connaissance"]
state = {'cassos': False}

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
        
def choix_reponse(liste_phrases):
    index_reponse = random.randint(0,len(liste_phrases))
    result_sentence = liste_phrases[index_reponse]
    return result_sentence
    
def Bonsoir():
    return choix_reponse(liste_reponses_bonsoir)

def Au_revoir():
    return choix_reponse(liste_reponses_Au_revoir)

def Ca_va():
    return choix_reponse(liste_reponses_ca_va)

def Bonjour():
    return choix_reponse(liste_reponses_bonjour)

def Merci():
    return choix_reponse(liste_reponses_merci)

def Appetit():
    return choix_reponse(liste_reponses_appetit)

def Bonne_nuit():
    return choix_reponse(liste_reponses_bonne_nuit)

def Apres_midi():
    return choix_reponse(liste_reponses_apres_midi)

def Presentation():
    return choix_reponse(liste_reponses_Presentation)

def parseSlotsToObjects(message):
   slots = defaultdict(list)
   data = json.loads(message.payload)
   if 'slots' in data:
      for slotData in data['slots']:
         slot = slotModel.Slot(slotData)
         slots[slot.slotName].append(slot)
   return slots
    
def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("Loky31:", "")
    result = None
    if intent_name == "Bonsoir":
        result = Bonsoir()
    elif intent_name == "Ca_va":
        result = Ca_va()
    elif intent_name == "Bonjour":
        result = Bonjour()
    elif intent_name == "Merci":
        result =Merci()
    elif intent_name == "Appetit":
        result =  Appetit()
    elif intent_name == "Bonne_nuit":
        result = Bonne_nuit()
    elif intent_name == "Après_midi":
        result = Apres_midi()
    elif intent_name == "Au_revoir":
        state['cassos'] = True
        result = Au_revoir()
    elif intent_name == "Capacité": 
        result = "Je suis capable de tout un tas de choses allant de piloter les volets le home cinéma les lumières ou vous donner une définition de wikipédia faire une liste de courses et tant d'autres choses"
    elif intent_name == "Presentation":
        noms = parseSlotsToObjects(intent_message)
        if len(slots) == 1:
            result = ""+Presentation()+"{}".format(noms[0].value)
        elif len(slots) == 2: 
            result = ""+Presentation()+"{} et {}".format(noms[0].value,noms[1].value)
    if result is not None:
        if not state['cassos']:
            hermes.publish_continue_session(intent_message.session_id, result,["Loky31:"])
            #SiteMessage.publish_feedback_sound_toggleOn(siteId=default)
           # hermes.enable_sound_feedback(SiteMessage("default"))
        else:
            state['cassos'] = False
            hermes.publish_end_session(intent_message.session_id, result+"Merci pour cette discussion")
            #hermes.disable_sound_feedback(SiteMessage("default"))
            
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
