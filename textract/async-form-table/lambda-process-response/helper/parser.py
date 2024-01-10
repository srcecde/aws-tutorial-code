"""
-*- coding: utf-8 -*-
========================
AWS Lambda
========================
Contributor: Chirag Rathod (Srce Cde)
========================
"""


import uuid
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Parse:
    def __init__(self, page, get_table, get_kv, get_text, get_signatures, get_queries):
        self.response = page
        self.word_map = {}
        self.table_page_map = {}
        self.key_map = []
        self.value_map = {}
        self.final_map_list = []
        self.line_text = {}
        self.get_table = get_table
        self.get_kv = get_kv
        self.get_text = get_text
        self.get_signatures = get_signatures
        self.get_queries = get_queries

    def extract_text(self, extract_by="LINE"):
        for block in self.response:
            if block["BlockType"] == extract_by:
                page_key = f'page_{block["Page"]}'
                if page_key in self.line_text.keys():
                    self.line_text[page_key].append(block["Text"])
                else:
                    self.line_text[page_key] = [block["Text"]]
        return self.line_text

    def map_word_id(self):
        for block in self.response:
            if block["BlockType"] == "WORD":
                self.word_map[block["Id"]] = block["Text"]
            if block["BlockType"] == "SELECTION_ELEMENT":
                self.word_map[block["Id"]] = block["SelectionStatus"]
            if block["BlockType"] == "SIGNATURE":
                self.word_map[block["Id"]] = ""

    def extract_table_info(self):
        row = []
        table = {}
        ri = 0
        flag = False
        page = self.response[0]["Page"]
        response_block_len = len(self.response) - 1

        for n, block in enumerate(self.response):
            if block["BlockType"] == "TABLE":
                key = f"table_{uuid.uuid4().hex}_page_{block['Page']}"
                temp_table = []

            if block["BlockType"] == "CELL":
                if block["RowIndex"] != ri:
                    flag = True
                    row = []
                    ri = block["RowIndex"]

                if "Relationships" in block:
                    for relation in block["Relationships"]:
                        if relation["Type"] == "CHILD":
                            row.append(
                                " ".join([self.word_map[i] for i in relation["Ids"]])
                            )
                else:
                    row.append(" ")

                if flag:
                    temp_table.append(row)
                    table[key] = temp_table
                    flag = False

            if table:
                if block["Page"] != page:
                    self.table_page_map[page] = table
                    page = block["Page"]
                    table = {}
                if response_block_len == n:
                    self.table_page_map[page] = table

        return self.table_page_map

    def get_key_map(self):
        for block in self.response:
            if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block["EntityTypes"]:
                for relation in block["Relationships"]:
                    if relation["Type"] == "VALUE":
                        value_id = relation["Ids"]
                    if relation["Type"] == "CHILD":
                        v = " ".join([self.word_map[i] for i in relation["Ids"]])
                        self.key_map.append([v, value_id])

    def get_value_map(self):
        for block in self.response:
            if (
                block["BlockType"] == "KEY_VALUE_SET"
                and "VALUE" in block["EntityTypes"]
            ):
                if "Relationships" in block:
                    for relation in block["Relationships"]:
                        if relation["Type"] == "CHILD":
                            v = " ".join([self.word_map[i] for i in relation["Ids"]])
                            self.value_map[block["Id"]] = v
                else:
                    self.value_map[block["Id"]] = "VALUE_NOT_FOUND"

    def get_kv_map(self):
        for i in self.key_map:
            self.final_map_list.append(
                [i[0], "".join(["".join(self.value_map[k]) for k in i[1]])]
            )

        return self.final_map_list

    def get_signature_info(self):
        page, signature, confidence = [], [], []
        temp_counter = 0
        for e, block in enumerate(self.response):
            if block["BlockType"] == "SIGNATURE":
                page.append(block.get("Page"))
                signature.append(f"Signature {temp_counter+1}")
                confidence.append(block.get("Confidence"))
                temp_counter += 1
        return (page, signature, confidence)

    def get_queries_info(self):
        temp_id = []
        f_response = {}

        for e, block in enumerate(self.response):
            if block["BlockType"] == "QUERY":
                if "Relationships" not in block:
                    rp = {
                        "query": block.get("Query").get("Text"),
                        "alias": block.get("Query").get("Alias"),
                        "answer_ids": None,
                        "answer": None,
                        "confidence": None,
                        "page": None,
                    }
                else:
                    child_ids = [
                        ids
                        for rel in block.get("Relationships")
                        for ids in rel["Ids"]
                        if rel.get("Type") == "ANSWER"
                    ]
                    rp = {
                        "query": block.get("Query").get("Text"),
                        "alias": block.get("Query").get("Alias"),
                        "answer_ids": child_ids,
                        "answer": None,
                        "confidence": None,
                        "page": None,
                    }

                f_response[block.get("Id")] = rp
                temp_id.append({block.get("Id"): rp})

            if block["BlockType"] == "QUERY_RESULT":
                q_id = list(temp_id[-1].keys())[0]
                q_val = temp_id[-1].get(q_id)

                if q_val.get("answer_ids"):
                    if block.get("Id") in q_val.get("answer_ids"):
                        q_ans = block.get("Text")
                        confidence_s = block.get("Confidence")
                        q_val["confidence"] = confidence_s
                        if q_val.get("answer"):
                            q_val["answer"] = f"{q_val.get('answer')} {q_ans}"
                        else:
                            q_val["answer"] = q_ans
                        q_val["page"] = block.get("Page")
                f_response[q_id] = q_val
                temp_id = []
        return f_response

    def process_response(self):
        final_map, table_info, text, sign_info, queries_info = (
            None,
            None,
            None,
            None,
            None,
        )

        logging.info("Mapping Id with word")
        self.map_word_id()

        if self.get_text:
            logging.info("Extracting text")
            text = self.extract_text()

        if self.get_kv:
            logging.info("Extracting Key-Value pairs")
            self.get_key_map()
            self.get_value_map()
            final_map = self.get_kv_map()

        if self.get_table:
            logging.info("Extracting table information")
            table_info = self.extract_table_info()

        if self.get_signatures:
            logging.info("Extracting signature information")
            sign_info = self.get_signature_info()

        if self.get_queries:
            logging.info("Extracting queries information")
            queries_info = self.get_queries_info()

        return table_info, final_map, text, sign_info, queries_info
