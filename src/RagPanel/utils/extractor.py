import re
from tqdm import tqdm
from cardinal import ChatOpenAI, HumanMessage, AssistantMessage
from .graph_utils import parseEntity, parseRelation

class Extractor:
    def __init__(self, lang, max_gleaning):
        self.chat_model = ChatOpenAI()
        self.max_gleaning = max_gleaning
        from .prompt import prompts
        self.prompts = prompts[lang]
        
    def chat(self, messages):
        response = self.chat_model.chat(messages=messages)
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
        prompt = self.prompts["GRAPH_EXTRACTION"].format(**prompt_config)
        global_entities = []
        global_relations = []
        bar = tqdm(total=len(file_contents), desc="extract graph")
        for file_content in file_contents:
            entities, relations = self._extract_graph_one(file_content=file_content, prompt=prompt, prompt_config=prompt_config)
            global_entities.append(entities)
            global_relations.append(relations)
            bar.update(1)
        bar.close()
        return global_entities, global_relations
            
    def _extract_graph_one(self, file_content, prompt, prompt_config):
        entities = []
        relations = []
        messages = []
        messages.append(HumanMessage(content=prompt.format(input_text = file_content)))
        response = self.chat(messages)
        for i in range(self.max_gleaning - 1):
            messages.append(HumanMessage(content=self.prompts["GRAPH_LOOP"]))
            loop = self.chat(messages)
            if "no" in loop.lower():
                break
            messages.append(HumanMessage(content=self.prompts["GRAPH_CONTINUE"]))
            response += self.chat(messages)
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
    
    def extract_claim():
        claims = []
        return claims
