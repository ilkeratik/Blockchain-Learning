from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD_INPUT
import pandas as pd

class Blockchain:
    """
    Blockchain: a public ledger(book) of transactions.
    Implemented as a list of blocks - data sets of transactions
    """
    def __init__(self):
        self.chain = [Block.genesis()] #chain is a list that has all blocks in it, the first element is generated manually because a block should have a manually setted up last_hash value
        
    def add_block(self, data):
        self.chain.append(Block.mine_block(self.chain[-1], data)) # adding a new node to the chain

    def __repr__(self): #a structured string representation of instances, instead of memory location
        return pd.DataFrame([t.__dict__ for t in self.chain]).to_string()
    
    def chain_df(self):
        return pd.DataFrame([t.__dict__ for t in self.chain])

    def to_json(self):
        """
        Serialize the blokchain into a list of blocks.
        """
        return list(map(lambda block: block.to_dict(), self.chain))

    def replace_chain(self, incoming_chain):

        """
        Replace the local chain with the incoming one if the followings applies:
            - the incoming chain is larger than the local one 
            - the incoming chain formatted correctly
        """

        if len(incoming_chain) <= len(self.chain):
            raise Exception('Cannot replace. The incoming chain must be longer')
        
        try:
            Blockchain.is_valid_chain(incoming_chain)
        except Exception as e:
            raise Exception(f'Cannot replace. The incoming chain is invalid: {e}')
        
        self.chain = incoming_chain

    @staticmethod
    def from_json(chain_json):
        """
        Deserialize a list of serialized blocks into a Blockchain instance.
        The result will contatin a chain list of block instances.
        """
        bc = Blockchain()
        bc.chain = list(
            map(lambda block_json: Block.from_dict(block_json), chain_json))
        print (bc)
        return bc

    @staticmethod
    def is_valid_chain(chain):
        """
        Validate the incoming chain.
        Enforce the following rules of the blockchain:
          - the chain must start with the genesis block
          - blocks must be formatted correctly
        """
        if chain[0] != Block.genesis():
            raise Exception('The genesis block must be valid')

        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i-1]
            Block.is_valid_block(last_block, block)

        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforce the rules of a chain composed of blocks of transactions.
            - Each transaction must only appear once in the chain.
            - There can only be one mining reward per block.
            - Each transaction must be valid.
        """
        transaction_ids = set()

        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False

            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(f'Transaction {transaction.id} is not unique')

                transaction_ids.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(
                            'There can only be one mining reward per block. '\
                            f'Check block with hash: {block.hash}'
                        )

                    has_mining_reward = True
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[0:i]
                    historic_balance = Wallet.calculate_balance(
                        historic_blockchain,
                        transaction.input['address']
                    )

                    if historic_balance != transaction.input['amount']:
                        raise Exception(
                            f'Transaction {transaction.id} has an invalid '\
                            'input amount'
                        )

                Transaction.is_valid_transaction(transaction)

def main(): #for testing purposes
    blockchain = Blockchain()
    blockchain.add_block('one')
    blockchain.add_block('two')

    print(blockchain)
    print(f'blockchain.py __name__: {__name__}')

if __name__ == '__main__':
    main()