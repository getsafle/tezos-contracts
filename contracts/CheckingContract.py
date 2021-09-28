import smartpy as sp


class CheckingContract(sp.contract):
    def __init__(self, _mainContractAddress):
        self.init()

    def isContract(self, address):
        return (address < sp.address("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU")) & (address > sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"))
