CREATE TABLE IF NOT EXISTS langs (
    lang_name TEXT PRIMARY KEY,
    lang_desc TEXT NOT NULL,
	lang_object BLOB NOT NULL
);
/*
lang_object structure:
{"glossary": 
    {"phrase": "definition", ...},
 "lexicon": 
    {"word": "definition", ...},
 "grammar": 
    # the entire structure of a language, includes most of the following,
    # as well as things like rules for making plurals, etc. 
    {"rule": "explanation", ...},
 "phonology": 
   # distribtution of phonemes (sounds) in a language
    {"rule": "explanation", ...},
 "morphology":
   # how words are constructed from morphemes (smallest units of meaning) 
    {"rule": "explanation", ...},
 "syntax": 
    # how words are combined into phrases and sentences
    {"rule": "explanation", ...},
 "semantics": 
    {"rule": "explanation", ...},
 "pragmatics": 
   # how context affects meaning, for example, intention, social status, etc.
    {"rule": "explanation", ...},
 "orthography":
   # how a language is written, for example, alphabet, syllabary, etc.
    {"rule": "explanation", ...}, 
    {"letter": "pronunciation", ...},
 "phonotactics": 
    # how sounds are combined into syllables and words
     {"rule": "explanation", ...},
    {"rule": "explanation", ...},
*/