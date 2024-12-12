import re
import json
from collections import defaultdict
from tqdm import tqdm
from cardinal import ChatOpenAI, HumanMessage, AssistantMessage, AutoGraphStorage
from .graph_utils import parseEntity, parseRelation
from .protocol import Entity

class GraphProcessor:
    def __init__(self, lang, max_gleaning, collection):
        self._chat_model = ChatOpenAI()
        self._max_gleaning = max_gleaning
        self._graph_storage = AutoGraphStorage(collection)
        self._graph_storage.drop_community()
        from .prompt import prompts
        self._prompts = prompts[lang]
        
    def _chat(self, messages):
        response = self._chat_model.chat(messages=messages)
        messages.append(AssistantMessage(content=response))
        return response
        
    def extract_graph(self, file_contents):
        prompt_config = {
            "tuple_delimiter": "<|>",
            "record_delimiter": "##",
            "completion_delimiter": "<|COMPLETE|>",
            "entity_types": "person, organization, geo, event",
            "input_text": "{input_text}"
        }
        prompt = self._prompts["GRAPH_EXTRACTION"].format(**prompt_config)
        global_entities = []
        global_relations = []
        bar = tqdm(total=len(file_contents), desc="extract graph")
        for file_content in file_contents:
            entities, relations = self._extract_graph_one(file_content=file_content, prompt=prompt, prompt_config=prompt_config)
            global_entities.extend(entities)
            global_relations.extend(relations)
            bar.update(1)
        bar.close()
        return global_entities, global_relations
            
    def _extract_graph_one(self, file_content, prompt, prompt_config):
        entities = []
        relations = []
        messages = []
        messages.append(HumanMessage(content=prompt.format(input_text = file_content)))
        response = self._chat(messages)
        for i in range(self._max_gleaning - 1):
            messages.append(HumanMessage(content=self._prompts["GRAPH_LOOP"]))
            loop = self._chat(messages)
            if "no" in loop.lower():
                break
            messages.append(HumanMessage(content=self._prompts["GRAPH_CONTINUE"]))
            response += self._chat(messages)
        
        delimiters = re.escape(prompt_config["record_delimiter"]) + "|" + re.escape(prompt_config["completion_delimiter"])
        elements = re.split(delimiters, response)
        for element in elements:
            element = re.search(r"\((.*)\)", element)
            if element is None:
                continue
            element_attributes = element.group(1).split(prompt_config["tuple_delimiter"])
            element_type = element_attributes[0].lower()
            if "entity" in element_type:
                entities.extend(parseEntity(element_attributes))
            elif "relationship" in element_type:
                relations.extend(parseRelation(element_attributes))
        return entities, relations
    
    def insert_entities(self, entities):
        # record and return new entities' names
        new_entities = []
        entities_to_summarize = {}
        bar = tqdm(total=len(entities), desc="insert entities")
        for entity in entities:
            name = entity.name
            node = self._graph_storage.query_node(name)
            if node is None:
                self._graph_storage.insert_node([name], [entity])
                new_entities.append(name)
            else:
                # update node
                if name not in entities_to_summarize.keys():
                    entity.desc = node["desc"] + "\n##\n" + entity.desc
                    entities_to_summarize[name] = entity
                else:
                    entities_to_summarize[name].desc += "\n##\n" + entity.desc
            bar.update(1)
        bar.close()
        bar = tqdm(total=len(entities_to_summarize), desc="summarize same entities")
        # summarize and insert same name entity
        for name, entity in entities_to_summarize.items():
            prompt = self._prompts["SUMMARIZE"].format(entity_name=name, description_list=entity.desc)
            entities_to_summarize[name].desc = self._chat([HumanMessage(content=prompt)])
            self._graph_storage.insert_node([name], [entity])
            bar.update(1)
        bar.close()
        return new_entities

    def insert_relations(self, relations):
        new_relations = []
        relations_to_summarize = {}
        bar = tqdm(total=len(relations), desc="insert relations")
        for relation in relations:
            head = relation.head
            tail = relation.tail
            edge = self._graph_storage.query_edge(head, tail)
            if edge is None:
                # check node and create non-exist node
                for name in [head, tail]:
                    node = self._graph_storage.query_node(name)
                    if node is None:
                        entity = Entity(name=name, type="UNKNOWN", desc=relation.desc)
                        self._graph_storage.insert_node([name], [entity])
                self._graph_storage.insert_edge([head], [tail], [relation])
                new_relations.append((head, tail))
            else:
                if (head, tail) not in relations_to_summarize.keys():
                    relation.desc = edge["desc"] + "\n##\n" + relation.desc
                    relation.strength += edge["strength"]
                    relations_to_summarize[(head, tail)] = relation
                else:
                    relations_to_summarize[(head, tail)].desc += "\n##\n" + relation.desc
                    relations_to_summarize[(head, tail)].strength += relation.strength
            bar.update(1)
        bar.close()
        
        bar = tqdm(total=len(relations_to_summarize), desc="summarize same relations")
        for key, relation in relations_to_summarize.items():
            entity1, entity2 = key
            entities = entity1 + " ## " + entity2
            prompt = self._prompts["SUMMARIZE"].format(entity_name=entities, description_list=relation.desc)
            relations_to_summarize[key].desc = self._chat([HumanMessage(content=prompt)])
            self._graph_storage.insert_edge([entity1], [entity2], [relation])
            bar.update(1)
        bar.close()
        return new_relations

    def generater_community_report(self):
        self._graph_storage.clustering()
        communities_schema = self._graph_storage.community_schema()
        communities_by_level = defaultdict(list)
        for community in communities_schema.values():
            communities_by_level[community["level"]].append(community)
        reports = {}
        for level in sorted(list(communities_by_level.keys())):
            # generate level by level
            for community in communities_by_level[level]:
                community_elements_info = self._pack_community_elements(community)
                prompt = self._prompts["COMMUNITY_REPORT"].format(input_text = community_elements_info)
                response = self._chat([HumanMessage(content=prompt)])
                try:
                    report = json.loads(response) # TODO: json format error exception handler
                except json.decoder.JSONDecodeError:
                    report = ""
                reports.update({
                    community["title"]:{"report": report,
                                               "data": community}})
        self._graph_storage.drop_community()
        return reports

    def _pack_community_elements(self, community):
        # TODO: truncate & use sub communities
        entities = "\nEntities\n\nid,entity,description\n"
        relations = "\nRelations\n\nid,source,target,description\n"
        for i, entity_name in enumerate(community["nodes"]):
            entity = self._graph_storage.query_node(entity_name)
            entities += ",".join([str(i), entity["name"], entity["desc"]]) + '\n'
        for i, (head, tail) in enumerate(community["edges"]):
            relation = self._graph_storage.query_edge(head, tail)
            relations += ",".join([str(i), head, tail, relation["desc"]]) + '\n'
        return entities + relations
