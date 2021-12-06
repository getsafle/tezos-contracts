import smartpy as sp


class CheckingContract(sp.Contract):

    @sp.global_lambda
    def isContract(address):
        sp.result((address < sp.address("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU")) & (address >= sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT")))

    @sp.global_lambda
    def toLower(string):
        char_to_lower = sp.map({
            "A": "a", "B": "b", "C": "c", "D": "d", "E": "e", "F": "f", "G": "g", "H": "h", "I": "i", "J": "j", "K": "k", "L": "l", "M": "m", "N": "n", "O": "o", "P": "p", "Q": "q", "R": "r", "S": "s", "T": "t", "U": "u", "V": "v", "W": "w", "X": "x", "Y": "y", "Z": "z",
            "a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f", "g": "g", "h": "h", "i": "i", "j": "j", "k": "k", "l": "l", "m": "m", "n": "n", "o": "o", "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z"
        })
        lower_chars = sp.local("lower_chars", [])
        sp.for idx in sp.range(0, sp.len(string)):
            lower_chars.value.push(char_to_lower[sp.slice(string, idx, 1).open_some()])
        sp.result(sp.concat(lower_chars.value.rev()))

    @sp.global_lambda
    def checkAlphaNumeric(safleId):
        alphaNumericCharacters = sp.set(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        sp.for idx in sp.range(0, sp.len(safleId)):
            sp.verify(alphaNumericCharacters.contains(sp.slice(safleId, idx, 1).open_some()), "Only alphanumeric allowed in blockchain name and alias name")

    @sp.global_lambda
    def isSafleIdValid(_registrarName):
        length = sp.len(_registrarName)
        sp.verify(4 <= length, "SafleId length should be greater than 3 characters")
        sp.verify(length <= 16, "SafleId length should be less than 17 characters")
        alphaNumericCharacters = sp.set(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        sp.for idx in sp.range(0, sp.len(_registrarName)):
            sp.verify(alphaNumericCharacters.contains(sp.slice(_registrarName, idx, 1).open_some()), "Only alphanumeric allowed in blockchain name and alias name")
