import smartpy as sp


class RegistrarStorage(sp.Contract):
    def __init__(self, _mainContractAddress):
        self.init(
            contractOwner=sp.sender,
            mainContract=_mainContractAddress,
        )

    def onlyOwner(self):
        sp.verify(self.data.contractOwner == sp.sender)

    def onlyMainContract(self):
        sp.verify(self.data.mainContract == sp.sender)

    @sp.entry_point
    def upgradeMainContractAddress(self, _mainContractAddress):
        self.data.mainContract = _mainContractAddress

    @sp.entry_point
    def registerRegistrar(self, _registrar, _registrarName):
        regNameBytes = bytes(_registrarName)
        self.data.Registrars[_registrar].isRegisteredRegistrar = True
        self.data.Registrars[_registrar].registrarName = _registrarName
        self.data.Registrars[_registrar].registarAddress = _registrar

        self.data.registrarNameToAddress[regNameBytes] = _registrar
        self.data.isAddressTaken[_registrar] = True
        self.data.totalRegistrars += 1
        return True

    @sp.entry_point
    def updateRegistrar(self, _registrar, _newRegistrarName):
        newNameBytes = bytes(_newRegistrarName)

        sp.verify(self.data.isAddressTaken[_registrar] == True)
        sp.verify(
            self.data.totalRegistrarUpdates[_registrar]+1 <= 5) #MAX_NAME_UPDATES

        registrarObject = self.data.Registrars[_registrar]
        oldName = registrarObject.registrarName
        oldNameBytes = bytes(oldName)
        self.data.registrarNameToAddress[oldNameBytes] = 0 #address(0x0)

        self.data.resolveOldRegistrarAddress[_registrar].push(
            bytes(self.data.Registrars[_registrar].registrarName))

        self.data.Registrars[_registrar].registrarName = _newRegistrarName
        self.data.Registrars[_registrar].registarAddress = _registrar

        self.data.registrarNameToAddress[newNameBytes] = _registrar
        self.data.totalRegistrarUpdates[_registrar] += 1
        return True

    @sp.entry_point
    def resolveRegistrarName(self, _name):
        regNameBytes = bytes(_name)
        sp.verify(self.data.registrarNameToAddress[regNameBytes] != 0)
        return self.data.registrarNameToAddress[regNameBytes]
  
    @sp.entry_point
    def registerSafleId(self, _registrar, _userAddress, _safleId):
        sp.verify(self.data.isAddressTaken[_userAddress] ==
                  False)

        idBytes = bytes(_safleId)

        self.data.resolveAddressFromSafleId[idBytes] = _userAddress
        self.data.isAddressTaken[_userAddress] = True
        self.data.resolveUserAddress[_userAddress] = _safleId
        self.data.totalSafleIdRegistered += 1

        return True

    @sp.entry_point
    def updateSafleId(self, _registrar, _userAddress, _safleId):
        sp.verify(
            self.data.totalSafleIDCount[_userAddress]+1 <= 5) #MAX_NAME_UPDATES

        sp.verify(self.data.isAddressTaken[_userAddress] == True)
        sp.verify(self.data.auctionProcess[_userAddress] == False)

        idBytes = bytes(_safleId)

        oldName = self.data.resolveUserAddress[_userAddress]
        oldIdBytes = bytes(oldName)

        self.data.unavailableSafleIds[oldName] = True
        self.data.resolveAddressFromSafleId[oldIdBytes] = 0 #address(0x0)
        self.data.oldSafleIds(_userAddress, oldIdBytes)

        self.data.resolveAddressFromSafleId[idBytes] = _userAddress
        self.data.resolveUserAddress[_userAddress] = _safleId

        self.data.totalSafleIDCount[_userAddress] += 1
        self.data.totalSafleIdRegistered += 1

        return True
    @sp.entry_point
    def resolveSafleId(self, _safleId):
        idBytes = bytes(_safleId)
        sp.verify(len(bytes(_safleId)) != 0)
        sp.verify(
            self.data.resolveAddressFromSafleId[idBytes] != 0) #address(0x0),)
        return self.data.resolveAddressFromSafleId[idBytes]

    @sp.entry_point
    def transferSafleId(self, _safleId, _oldOwner, _newOwner):
        idBytes = bytes(_safleId)

        sp.verify(self.data.isAddressTaken[_oldOwner] == True)
        sp.verify(self.data.resolveAddressFromSafleId[idBytes] != 0) #address(0x0))

        self.data.oldSafleIds(_oldOwner, idBytes)
        self.data.isAddressTaken[_oldOwner] = False

        self.data.resolveAddressFromSafleId[idBytes] = _newOwner

        self.data.auctionProcess[_oldOwner] = False
        self.data.isAddressTaken[_newOwner] = True
        self.data.resolveUserAddress[_newOwner] = _safleId
        return True

    @sp.entry_point
    def oldSafleIds(self, _userAddress, _safleId):
        self.data.resolveOldSafleIdFromAddress[_userAddress].push(_safleId)
        self.data.resolveOldSafleID[_safleId] = _userAddress
    @sp.entry_point

    def setAuctionContract(self, _auctionAddress):
        self.data.auctionContractAddress = _auctionAddress
        return True

    @sp.entry_point
    def auctionInProcess(self, _safleIdOwner, _safleId):
        idBytes = bytes(_safleId)

        sp.verify(bytes(_safleId).length != 0)
        sp.verify(
            self.data.resolveAddressFromSafleId[idBytes] !=0) #address(0x0))
        self.data.auctionProcess[_safleIdOwner] = True
        return True

    @sp.entry_point
    def mapCoin(self, _indexnumber, _coinName, _aliasName, _registrar):
        sp.verify(self.data.OtherCoin[_indexnumber].isIndexMapped == False)
        sp.verify(self.data.isCoinMapped[_coinName] == False)
        sp.verify(
            self.data.Registrars[_registrar].registarAddress != 0) #address(0x0))

        self.data.OtherCoin[_indexnumber].isIndexMapped = True
        self.data.OtherCoin[_indexnumber].aliasName = _aliasName
        self.data.OtherCoin[_indexnumber].coinName = _coinName
        self.data.isCoinMapped[_coinName] = True
        return True

    @sp.entry_point
    def registerCoinAddress(self, _userAddress, _index, _address, _registrar):
        sp.verify(
            self.data.Registrars[_registrar].registarAddress != 0) #address(0x0))
        sp.verify(self.data.auctionProcess[_userAddress] == False)
        sp.verify(self.data.OtherCoin[_index].isIndexMapped == True)

        safleId = self.data.resolveUserAddress[_userAddress]
        self.data.safleIdToCoinAddress[safleId][_index] = _address
        self.data.coinAddressToSafleId[_address] = safleId
        return True

    @sp.entry_point
    def updateCoinAddress(self, _userAddress, _index, _newAddress, _registrar):
        sp.verify(self.data.Registrars[_registrar].registarAddress != address(
            0x0))
        sp.verify(self.data.auctionProcess[_userAddress] == False)
        sp.verify(self.data.OtherCoin[_index].isIndexMapped == True)

        safleId = self.data.resolveUserAddress[_userAddress]
        previousAddress = self.data.safleIdToCoinAddress[safleId][_index]
        sp.verify(len(previousAddress) > 0)

        self.data.safleIdToCoinAddress[safleId][_index] = _newAddress
        self.data.coinAddressToSafleId[_newAddress] = safleId
        return True

    @sp.entry_point
    def coinAddressToId(self, _address):
        return self.data.coinAddressToSafleId[_address]

    @sp.entry_point
    def idToCoinAddress(self, _safleId, _index):
        return self.data.safleIdToCoinAddress[_safleId][_index]

    @sp.add_test(name="SafleID Storage")
    def test():
        scenario = sp.test_scenario()
        scenario.table_of_contents()
        scenario.h1("Safle Storage")

        # Initialize test admin addresses
        contractOwner = sp.address("tz1-admin-1234")
        seller = sp.address("tz1-seller-1234")
        mainContract = sp.address("tz1-proxy-1234")

        c1 = RegistrarStorage(mainContract)
        scenario += c1

        scenario += c1.registerRegistrar(_registrar=1,
                                 _registrarName=seller).run(sender=mainContract)