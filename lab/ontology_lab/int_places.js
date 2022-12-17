/* Validator document for creation of bow_int.Places collections.
  A Place is a location within a game world Location hierarchy. Each record relates to a
  specific Place, but is often located within or contains other Places.

  @reffrom:
    self
    bow_int.Markets

  @refto:
    self
    bow_sem.Glossary
    bow_sem.Images
    bow_sem.Sounds

*/
use admin
db.auth("bow_owner", "ananda23");
use bow_int
db.Places.drop();
db.createCollection("Places",
  /* Validator rules  */
  {
    validator: {
      $and: [
        /* *** REQUIRED KEYS *** */
        {
          "_id": { /* Unique surrogate key. */
            "$exists": "true",
            "$type": "objectId"
          }
        }, {
          placeName: { /* Short name of the place. Should be unique. */
            "$exists": "true",
            "$type": "string"
          }
        },

        /* *** REQUIRED FLAGS *** */
        {
          placeHasParentPlace: { /* Place is contained by another Place. */
            "$exists": "true",
            "$type": "bool"
          }
        }, {
          placeHasChildrenPlaces: { /* Place contains other Places. */
            "$exists": "true",
            "$type": "bool"
          }
        }, {
          placeHasNeighborPlaces: { /* Place is near or next to other Places. */
            "$exists": "true",
            "$type": "bool"
          }
        }, {
          placeContainsProps: { /* Game Props are located within the Place. */
            "$exists": "true",
            "$type": "bool"
          }
        },

        /* *** REQUIRED ATTRIBUTES *** */
        {
          placeDescription: {
            "$exists": "true",
            "$type": "string"
          }
        }, {
          placeType: {
            "$exists": "true",
            "$in": [
              "universe",
              "galaxy",
              "solarSystem",
              "planet",
              "satellite",
              "vessel",
              "region",
              "municipality",
              "enclosure",
              "structure",
              "room",
              "route",
              "wild"
            ]
          }
        }, {
          placeLocation: { /* Location of this place within specified coordinate system. */
            /* Dict providing location info indexed by system. */
            /* {coord_system: [values]}  */
            /* Distance between places should be computed, but could also be used in a
               descriptive manner here. "A village about 30 long hops from Borded."
            */
            /* The coordinate systems in use will obviously need to be defined, but that
               may be more the result of calling APIs that storing static data.
            */
            /* like:  { "text": "The southeast quadrant of the Town of Borded",
                        "geo": "(45.5 N, 28.9 E - 45.6.N, 28.10 E)"
                      }   .. etc.
            */
            "$exists": "true",
            "$type": "object" /* per style noted above */
          }
        },

        /* *** OPTIONAL ATTRIBUTES *** */
        /* *** OPTIONAL REFERENCES *** */
        {
          placeParentPlace: { /* Reference to parent / containing Place. */
            "$type": "object" /* DBRef --> bow_int.Places  */
          }
        }, {
          placeChildPlaces: { /* List of references to contained Places. */
            "$type": "array" /* of [ DBRef --> bow_int.Places  ] */
          }
        }, {
          placeNeighborPlaces: { /* links to Places nearby, but not contained by this Place. */
            "$type": "array" /* [ of DBRef --> bow_int.Places ]*/
          }
        }, {
          placePropsInventory: { /* List of Props that are within the Place. */
            "$type": "array" /* [ of DBRef --> bow_int.Props ]  */
          }
        }, {
          placeGloss: { /*Reference to Glossary entry for this Place. */
            /* DBRef --> bow_sem.Glossaries */
            "$type": "object"
          }
        }, {
          placeImages: { /* Dictionary of links to images representing the Place. */
            /* { <image_object_type>: DBRef --> bow_sem.Images }  */
            "$type": "object"
          }
        }, {
          placeSounds: { /* Dictionary of links to sounds representing the Place. */
            /* { <sound_object_type>: DBRef --> bow_sem.Sounds }  */
            "$type": "object"
          }
        }
      ]
    }
  }
)
