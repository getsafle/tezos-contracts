import smartpy as sp


class RegistrarStorage(sp.Contract):
    def __init__(self, _ownerAddress, _mainContractAddress):
        self.init(
            contractOwner=_ownerAddress,
            mainContract=_mainContractAddress,
            resolveAddressFromSafleId=sp.map(),
            auctionProcess=sp.map(),
            coinAddressToSafleId=sp.map(),
            OtherCoin=sp.map(),
            isCoinMapped=sp.map(),
            Registrars=sp.map(
                tkey=sp.TAddress,
                tvalue=sp.TRecord(
                    isRegisteredRegistrar=sp.TBool,
                    registrarName=sp.TString,
                    registarAddress=sp.TAddress
                )
            ),
            safleIdToCoinAddress=sp.map(
                tkey=sp.TString,
                tvalue=sp.TMap(sp.TNat, sp.TAddress)
            ),
            resolveUserAddress=sp.map(),
            registrarNameToAddress=sp.map(),
            isAddressTaken=sp.map(),
            totalRegistrars=0,
            totalSafleIdRegistered=0,
            auctionContractAddress=sp.address("tz1"),
            resolveOldSafleIdFromAddress=sp.map(
                tkey=sp.TAddress,
                tvalue=sp.TList(sp.TBytes)
            ),
            resolveOldSafleID=sp.map(),
            totalRegistrarUpdates=sp.map(),
            resolveOldRegistrarAddress=sp.map(
                tkey=sp.TAddress,
                tvalue=sp.TList(sp.TBytes)
            ),
            totalSafleIDCount=sp.map(),
            unavailableSafleIds=sp.map()
        )

    def onlyOwner(self):
        sp.verify(self.data.contractOwner == sp.sender)

    def onlyMainContract(self):
        sp.verify(self.data.mainContract == sp.sender)

    def registrarChecks(self, _registrarName):
        regNameBytes = sp.pack(_registrarName)
        sp.verify(~self.data.registrarNameToAddress.contains(regNameBytes), "Registrar name is already taken.")
        sp.verify(~self.data.resolveAddressFromSafleId.contains(regNameBytes), "This Registrar name is already registered as an SafleID.")

    def safleIdChecks(self, _safleId, _registrar):
        idBytes = sp.pack(_safleId)

        sp.verify(self.data.Registrars.contains(_registrar), "Invalid Registrar.")
        sp.verify(~self.data.registrarNameToAddress.contains(idBytes), "This SafleId is taken by a Registrar.")
        sp.verify(~self.data.resolveAddressFromSafleId.contains(idBytes), "This SafleId is already registered.")
        sp.verify(~self.data.unavailableSafleIds.contains(_safleId), "SafleId is already used once, not available now")

    def auctionContract(self):
        sp.verify(sp.sender == self.data.auctionContractAddress)

    def coinAddressCheck(self, _userAddress, _index, _registrar):
        sp.verify(self.data.Registrars.contains(_registrar), "Invalid Registrar")
        sp.verify(self.data.OtherCoin.contains(_index), "This index number is not mapped.");
        sp.if self.data.auctionProcess.contains(_userAddress):
            sp.verify(~self.data.auctionProcess[_userAddress])

    @sp.entry_point
    def upgradeMainContractAddress(self, params):
        self.data.mainContract = params._mainContractAddress

    @sp.entry_point
    def registerRegistrar(self, _registrar, _registrarName):
        regNameBytes = sp.pack(_registrarName)
        self.data.Registrars[_registrar] = sp.record(
            isRegisteredRegistrar=True,
            registrarName=_registrarName,
            registarAddress=_registrar
        )

        self.data.registrarNameToAddress[regNameBytes] = _registrar
        self.data.isAddressTaken[_registrar] = True
        self.data.totalRegistrars += 1

    @sp.entry_point
    def updateRegistrar(self, _registrar, _newRegistrarName):
        newNameBytes = sp.pack(_newRegistrarName)

        sp.verify(self.data.isAddressTaken[_registrar] == True)
        sp.verify(self.data.totalRegistrarUpdates[_registrar]+1 <= 5) #MAX_NAME_UPDATES

        registrarObject = self.data.Registrars[_registrar]
        oldName = registrarObject.registrarName
        oldNameBytes = sp.pack(oldName)
        del self.data.registrarNameToAddress[oldNameBytes]

        self.data.resolveOldRegistrarAddress[_registrar].push(
            sp.pack(self.data.Registrars[_registrar].registrarName))

        self.data.Registrars[_registrar].registrarName = _newRegistrarName
        self.data.Registrars[_registrar].registarAddress = _registrar

        self.data.registrarNameToAddress[newNameBytes] = _registrar
        self.data.totalRegistrarUpdates[_registrar] += 1

    @sp.utils.view(sp.TAddress)
    def resolveRegistrarName(self, _name):
        regNameBytes = sp.pack(_name)
        sp.verify(self.data.registrarNameToAddress.contains(regNameBytes))
        sp.result(self.data.registrarNameToAddress[regNameBytes])
  
    @sp.entry_point
    def registerSafleId(self, _registrar, _userAddress, _safleId):
        sp.verify(self.data.isAddressTaken[_userAddress] == False)

        idBytes = sp.pack(_safleId)

        self.data.resolveAddressFromSafleId[idBytes] = _userAddress
        self.data.isAddressTaken[_userAddress] = True
        self.data.resolveUserAddress[_userAddress] = _safleId
        self.data.totalSafleIdRegistered += 1

    @sp.entry_point
    def updateSafleId(self, _registrar, _userAddress, _safleId):
        sp.verify(self.data.totalSafleIDCount[_userAddress]+1 <= 5) #MAX_NAME_UPDATES
        sp.verify(self.data.isAddressTaken[_userAddress] == True)
        sp.verify(self.data.auctionProcess[_userAddress] == False)

        idBytes = sp.pack(_safleId)

        oldName = self.data.resolveUserAddress[_userAddress]
        oldIdBytes = sp.pack(oldName)

        self.data.unavailableSafleIds[oldName] = True
        del self.data.resolveAddressFromSafleId[oldIdBytes]
        self.oldSafleIds(_userAddress, oldIdBytes)

        self.data.resolveAddressFromSafleId[idBytes] = _userAddress
        self.data.resolveUserAddress[_userAddress] = _safleId

        self.data.totalSafleIDCount[_userAddress] += 1
        self.data.totalSafleIdRegistered += 1

    @sp.utils.view(sp.TAddress)
    def resolveSafleId(self, _safleId):
        idBytes = sp.pack(_safleId)
        sp.verify(sp.len(sp.pack(_safleId)) != 0)
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes))
        sp.result(self.data.resolveAddressFromSafleId[idBytes])

    @sp.entry_point
    def transferSafleId(self, _safleId, _oldOwner, _newOwner):
        idBytes = sp.pack(_safleId)

        sp.verify(self.data.isAddressTaken[_oldOwner] == True)
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes))

        self.oldSafleIds(_oldOwner, idBytes)
        self.data.isAddressTaken[_oldOwner] = False

        self.data.resolveAddressFromSafleId[idBytes] = _newOwner

        self.data.auctionProcess[_oldOwner] = False
        self.data.isAddressTaken[_newOwner] = True
        self.data.resolveUserAddress[_newOwner] = _safleId

    def oldSafleIds(self, _userAddress, _safleId):
        self.data.resolveOldSafleIdFromAddress[_userAddress].push(_safleId)
        self.data.resolveOldSafleID[_safleId] = _userAddress

    @sp.entry_point
    def setAuctionContract(self, _auctionAddress):
        self.data.auctionContractAddress = _auctionAddress

    @sp.entry_point
    def auctionInProcess(self, _safleIdOwner, _safleId):
        idBytes = sp.pack(_safleId)

        sp.verify(_safleId.length != 0)
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes))
        self.data.auctionProcess[_safleIdOwner] = True

    @sp.entry_point
    def mapCoin(self, _indexnumber, _coinName, _aliasName, _registrar):
        sp.verify(self.data.OtherCoin[_indexnumber].isIndexMapped == False)
        sp.verify(self.data.isCoinMapped[_coinName] == False)
        sp.verify(self.data.Registrars[_registrar].isRegisteredRegistrar)

        self.data.OtherCoin[_indexnumber].isIndexMapped = True
        self.data.OtherCoin[_indexnumber].aliasName = _aliasName
        self.data.OtherCoin[_indexnumber].coinName = _coinName
        self.data.isCoinMapped[_coinName] = True

    @sp.entry_point
    def registerCoinAddress(self, _userAddress, _index, _address, _registrar):
        sp.verify(
            self.data.Registrars[_registrar].isRegisteredRegistrar)
        sp.verify(self.data.auctionProcess[_userAddress] == False)
        sp.verify(self.data.OtherCoin[_index].isIndexMapped == True)

        safleId = self.data.resolveUserAddress[_userAddress]
        self.data.safleIdToCoinAddress[safleId][_index] = _address
        self.data.coinAddressToSafleId[_address] = safleId

    @sp.entry_point
    def updateCoinAddress(self, _userAddress, _index, _newAddress, _registrar):
        sp.verify(self.data.Registrars[_registrar].isRegisteredRegistrar)
        sp.verify(self.data.auctionProcess[_userAddress] == False)
        sp.verify(self.data.OtherCoin[_index].isIndexMapped == True)

        safleId = self.data.resolveUserAddress[_userAddress]
        sp.verify(self.data.safleIdToCoinAddress[safleId].contains(_index))

        self.data.safleIdToCoinAddress[safleId][_index] = _newAddress
        self.data.coinAddressToSafleId[_newAddress] = safleId

    @sp.utils.view(sp.TString)
    def coinAddressToId(self, _address):
        sp.result(self.data.coinAddressToSafleId[_address])

    @sp.utils.view(sp.TAddress)
    def idToCoinAddress(self, params):
        sp.result(self.data.safleIdToCoinAddress[params._safleId][params._index])
