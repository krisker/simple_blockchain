#coding:utf-8


from flask import Flask, request, jsonify
from flask_script import Manager
from blockchain import BlockChain
from uuid import uuid4



app = Flask(__name__)
manager = Manager(app)

blockChain = BlockChain()

node_identifier = str(uuid4()).replace("-", "")




@app.route("/")
def index_():
    return "hello"


@app.route("/mine", methods=["GET"])
def mine():
    last_block = blockChain.last_block
    last_proof = last_block["proof"]

    proof = blockChain.proof_of_work(last_proof)

    blockChain.transactions_new(
        sender=0,
        recipient=node_identifier,
        amount=1
    )
    block = blockChain.new_block(proof)

    response = {
        "message": "新区块被挖出",
        "index": block["index"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
        "transaction": block["transaction"]
    }

    return jsonify(response)


@app.route("/transactions/new", methods=["POST"])
def new_transactions():

    values = request.get_json()  #get_json获取的数据是字典格式的数据

    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return "Missing Values", 401
    index = blockChain.transactions_new(values["sender"], values["recipient"], values["amount"])

    response = {"message": f"新交易将会被加入到区块{index}中"}

    return jsonify(response)

@app.route("/chain")
def full_chain():
    response = {
        "chain": blockChain.chain,
        "length": len(blockChain.chain)
    }
    return jsonify(response)


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    nodes = request.form.get("nodes")

    if not nodes:
        return "Error, please supply a valid list of nodes", 400

    blockChain.register_node(nodes)

    response = {
        "message": "New nodes have been added",
        "total nodes": [node for node in blockChain.nodes]
    }

    return jsonify(response), 201



@app.route("/nodes/get", methods=["GET"])
def get_nodes():
    nodes = list(blockChain.nodes)
    response = {"nodes": nodes}
    return jsonify(response), 200


@app.route("/nodes/resolve", methods=["GEt"])
def resolve_conflicts():
    if blockChain.resolve_conflicts():
        response = {
            "message": "Our chain was replaced",
            "chain": blockChain.chain,
        }

    else:
        response = {
            "message": "Our chain is authoritative",
            "chain": blockChain.chain
        }

    return jsonify(response), 200





if __name__ == '__main__':
    manager.run()

