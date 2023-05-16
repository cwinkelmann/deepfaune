# Copyright CNRS 2023

# simon.chamaille@cefe.cnrs.fr; vincent.miele@univ-lyon1.fr

# This software is a computer program whose purpose is to identify
# animal species in camera trap images.

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import json

translations = {
    'txt_language': {'fr': "Langue", 'en': "Language", 'it': "Lingua"},
    'txt_other': {'fr': "autre", 'en': "other", 'it': "altro"},
    'txt_browse': {'fr': "Choisir", 'en': "Select", 'it': "Scegliere"},
    'txt_incorrect': {'fr': "Dossier incorrect - aucun media trouvé", 'en': "Incorrect folder - no media found",
                      'it': "File scorretto - media non trovato"},
    'txt_confidence': {'fr': "Seuil de confiance", 'en': "Confidence threshold",
                       'it': "Livello minimo di affidabilita"},
    'txt_sequencemaxlag': {'fr': "Intervalle max / séquence (secondes)", 'en': "Sequence max lag (seconds)",
                           'it': "Intervallo massimo / sequenza (secondi)"},
    'txt_configrun': {'fr': "Configurer et lancer", 'en': "Configure & Run", 'it': "Configurare e inviare"},
    'txt_run': {'fr': "Lancer", 'en': "Run", 'it': "Inviare"},
    'txt_nextpred': {'fr': "Suivant", 'en': "Next", 'it': "Prossimo"},
    'txt_prevpred': {'fr': "Précédent", 'en': "Previous", 'it': "Precedente"},
    'txt_paramframe': {'fr': "Paramètres", 'en': "Parameters", 'it': "Parametri"},
    'txt_selectclasses': {'fr': "Sélection des classes", 'en': "Classes selection", 'it': "Selezione delle classi"},
    'txt_close': {'fr': "Fermer", 'en': "Close", 'it': "Chiudere"},
    'txt_all': {'fr': "toutes", 'en': "all", 'it': "tutte"},
    'txt_classnotfound': {'fr': "Aucun média pour cette classe", 'en': "No media found for this class",
                          'it': "Nessun media per questa classe"},
    'txt_filename': {'fr': "Nom de fichier", 'en': "Filename", 'it': "Nome del file"},
    'txt_prediction': {'fr': "Prédiction", 'en': "Prediction", 'it': "Predizione"},
    'txt_count': {'fr': "Comptage", 'en': "Count", 'it': "Conto"},
    'txt_seqnum': {'fr': "Numéro de séquence", 'en': "Sequence ID", 'it': "Sequenza"},
    'txt_error': {'fr': "Erreur", 'en': "Error", 'it': "Errore"},
    'txt_savepredictions': {'fr': "Voulez-vous enregistrer les prédictions dans ",
                            'en': "Do you want to save predictions in ", 'it': "Volete registrare le predizioni nel"},
    'txt_destcopy': {'fr': "Copier dans des sous-dossiers de :", 'en': "Copy in subfolders of:",
                     'it': "Copiare nei sotto file di"},
    'txt_destmove': {'fr': "Déplacer vers des sous-dossiers de :", 'en': "Move to subfolders of:",
                     'it': "Spostare nei sotto file di"},
    'txt_loadingmetadata': {'fr': "Chargement des metadonnées... (cela peut prendre du temps)",
                            'en': "Loading metadata... (this may take a while)",
                            'it': "Carica dei metadata... (puo essere lungo)"},
    'txt_file': {'fr': "Fichier", 'en': "File", 'it': "File"},
    'txt_pref': {'fr': "Préférences", 'en': "Preferences", 'it': "Preferenze"},
    'txt_help': {'fr': "Aide", 'en': "Help", 'it': "Aiuto"},
    'txt_import': {'fr': "Importer", 'en': "Import", 'it': "Caricare"},
    'txt_importimage': {'fr': "Images", 'en': "Images", 'it': "Immagine"},
    'txt_importvideo': {'fr': "Vidéos", 'en': "Videos", 'it': "Video"},
    'txt_export': {'fr': "Exporter les résultats", 'en': "Export results", 'it': "Esportare i risultati"},
    'txt_ascsv': {'fr': "Format CSV", 'en': "As CSV", 'it': "Formato CSV"},
    'txt_asxlsx': {'fr': "Format XSLX", 'en': "As XSLX", 'it': "Formato XSLX"},
    'txt_createsubfolders': {'fr': "Créer des sous-dossiers", 'en': "Create subfolders", 'it': "Creare dei sotto file"},
    'txt_copy': {'fr': "Copier les fichiers", 'en': "Copy files", 'it': "Copiare i file"},
    'txt_move': {'fr': "Déplacer les fichiers", 'en': "Move files", 'it': "Spostare i file"},
    'txt_credits': {'fr': "A propos", 'en': "About DeepFaune", 'it': "A proposito"}
}

class TxtFactory:
    __translations = translations
    __lang = 'en'
    __all_lang = set(translations[list(translations.keys())[0]].keys())

    @staticmethod
    def __get_translation(key):
        try:
            txt_key = TxtFactory().__translations[key][TxtFactory().__lang]
        except KeyError:
            try:
                txt_key = TxtFactory().__translations[key]['en']
            except KeyError:
                raise ValueError("Invalid text key")
        return txt_key

    @staticmethod
    def setLanguage(lang):
        if lang not in list(TxtFactory().__all_lang):
            raise ValueError("Invalid language")
        TxtFactory.__lang = lang

    @staticmethod
    def getLanguage():
        return TxtFactory().__lang

    @staticmethod
    def __getattr__(name):
        return TxtFactory().__get_translation(name)
