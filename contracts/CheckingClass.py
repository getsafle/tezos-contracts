import smartpy as sp


def isContract(address):
    return (address < sp.address("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU")) & (address > sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"))

def toLower(string):
    return string
    lower = sp.string("")
    sp.for ch in string.items():
        sp.if 'A' <= ch & ch <= 'Z':
            lower += ch+32
        sp.else:
            lower += ch
    return lower

def isSafleIdValid(_registrarName):
    VNinLowerCase = toLower(string=_registrarName)
    length = sp.len(_registrarName)
    sp.verify(4 <= length, "SafleId length should be greater than 3 characters")
    sp.verify(length <= 16, "SafleId length should be less than 17 characters")
    return True
