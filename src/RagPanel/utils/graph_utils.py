from .protocol import Entity, Relation


def parseEntity(entity_attributes):
    try:
        entity = Entity(name=entity_attributes[1], type=entity_attributes[2], desc=entity_attributes[3])
        return [entity]
    except:
        return []
    
def parseRelation(relation_attributes):
    try:
        relation = Relation(head=relation_attributes[1], tail=relation_attributes[2], desc=relation_attributes[3], strength=int(relation_attributes[4]))
        return [relation]
    except:
        return []
