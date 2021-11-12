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
    def __init__(self, page, get_table, get_kv, get_text):
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

    def process_response(self):
        final_map, table_info, text = None, None, None

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

        return table_info, final_map, text
