#coding:utf-8

import hashlib
import time
import json
from urllib.parse import urlparse
import requests

class BlockChain(object):
    def __init__(self):

        self.chain = []
        self.current_transaction = []
        self.nodes = set()

        self.new_block(previous_hash=1, proof=100)



    def register_node(self, address):
        """
        Add a new node to the list fo node
        """
        parse_url = urlparse(address)
        if parse_url.netloc:
            self.nodes.add(parse_url.netloc)
        elif parse_url.path:
            self.nodes.add(parse_url.path)
        else:
            raise ValueError("Invalid URL")






    def transactions_new(self, sender, recipient, amount):
        new_transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        }
        self.current_transaction.append(new_transaction)
        return self.last_block["index"] + 1




    def new_block(self, proof, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,  #��ʼ����ʱ��ʹ��chain�ĳ�������ʾȷ��index
            "timestamp": time.time(),
            "transaction": self.current_transaction,
            "proof": proof,
            "previous_hash": previous_hash if previous_hash else self.hash(self.last_block)

        }

        self.current_transaction = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()



    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof


    @property
    def last_block(self):
        return self.chain[-1]


    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block["previous_hash"] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False

            last_block = block
            current_index += 1
        return True



    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f"http://{node}/chain")
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False





