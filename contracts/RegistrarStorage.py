import smartpy as sp


class RegistrarStorage(sp.Contract):
    def __init__(self, _ownerAddress, _mainContractAddress):
        self.init(
            contractOwner=_ownerAddress,
            mainContract=_mainContractAddress,
            resolveAddressFromSafleId=sp.map(),
            auctionProcess=sp.map(),
            coinAddressToSafleId=sp.map(),
            OtherCoin=sp.map(
                tkey=sp.TNat,
                tvalue=sp.TRecord(
                    isIndexMapped=sp.TBool,
                    aliasName=sp.TString,
                    coinName=sp.TString
                )
            ),
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
                tvalue=sp.TMap(sp.TNat, sp.TString)
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
        self.onlyOwner()

        self.data.mainContract = params._mainContractAddress

    @sp.entry_point
    def registerRegistrar(self, params):
        self.registrarChecks(params._registrarName)
        self.onlyMainContract()

        regNameBytes = sp.pack(params._registrarName)
        self.data.Registrars[params._registrar] = sp.record(
            isRegisteredRegistrar=True,
            registrarName=params._registrarName,
            registarAddress=params._registrar
        )

        self.data.registrarNameToAddress[regNameBytes] = params._registrar
        self.data.isAddressTaken[params._registrar] = True
        self.data.totalRegistrars += 1

    @sp.entry_point
    def updateRegistrar(self, params):
        self.registrarChecks(params._newRegistrarName)
        self.onlyMainContract()

        newNameBytes = sp.pack(params._newRegistrarName)

        sp.if ~self.data.totalRegistrarUpdates.contains(params._registrar):
            self.data.totalRegistrarUpdates[params._registrar] = 0
        sp.if ~self.data.resolveOldRegistrarAddress.contains(params._registrar):
            self.data.resolveOldRegistrarAddress[params._registrar] = sp.list([])

        sp.verify(self.data.isAddressTaken.get(params._registrar, False) == True, "Registrar should register first.")
        sp.verify(self.data.totalRegistrarUpdates[params._registrar]+1 <= 5, "Maximum update count reached.") #MAX_NAME_UPDATES

        registrarObject = self.data.Registrars[params._registrar]
        oldName = registrarObject.registrarName
        oldNameBytes = sp.pack(oldName)
        del self.data.registrarNameToAddress[oldNameBytes]

        self.data.resolveOldRegistrarAddress[params._registrar].push(
            sp.pack(self.data.Registrars[params._registrar].registrarName)
        )

        self.data.Registrars[params._registrar].registrarName = params._newRegistrarName
        self.data.Registrars[params._registrar].registarAddress = params._registrar

        self.data.registrarNameToAddress[newNameBytes] = params._registrar
        self.data.totalRegistrarUpdates[params._registrar] += 1

    @sp.onchain_view()
    def resolveRegistrarName(self, params):
        regNameBytes = sp.pack(params._name)
        sp.verify(self.data.registrarNameToAddress.contains(regNameBytes), "Resolver : Registrar is not yet registered for this SafleID.")
        sp.result(self.data.registrarNameToAddress[regNameBytes])

    @sp.entry_point
    def registerSafleId(self, params):
        self.safleIdChecks(params._safleId, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.isAddressTaken.get(params._userAddress, False) == False, "SafleID already registered")

        idBytes = sp.pack(params._safleId)

        self.data.resolveAddressFromSafleId[idBytes] = params._userAddress
        self.data.isAddressTaken[params._userAddress] = True
        self.data.resolveUserAddress[params._userAddress] = params._safleId
        self.data.totalSafleIdRegistered += 1

    @sp.entry_point
    def updateSafleId(self, params):
        self.safleIdChecks(params._safleId, params._registrar)
        self.onlyMainContract()

        sp.if ~self.data.totalSafleIDCount.contains(params._userAddress):
            self.data.totalSafleIDCount[params._userAddress] = 0

        sp.verify(self.data.totalSafleIDCount[params._userAddress]+1 <= 5, "Maximum update count reached.") #MAX_NAME_UPDATES
        sp.verify(self.data.isAddressTaken.get(params._userAddress, False) == True, "SafleID not registered.")
        sp.verify(self.data.auctionProcess.get(params._userAddress, False) == False, "SafleId cannot be updated inbetween Auction.")

        idBytes = sp.pack(params._safleId)

        oldName = self.data.resolveUserAddress[params._userAddress]
        oldIdBytes = sp.pack(oldName)

        self.data.unavailableSafleIds[oldName] = True
        del self.data.resolveAddressFromSafleId[oldIdBytes]
        self.oldSafleIds(params._userAddress, oldIdBytes)

        self.data.resolveAddressFromSafleId[idBytes] = params._userAddress
        self.data.resolveUserAddress[params._userAddress] = params._safleId

        self.data.totalSafleIDCount[params._userAddress] += 1
        self.data.totalSafleIdRegistered += 1

    @sp.onchain_view()
    def resolveSafleId(self, params):
        idBytes = sp.pack(params._safleId)
        sp.verify(sp.len(sp.pack(params._safleId)) != 0, "Resolver : user SafleID should not be empty.")
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes), "Resolver : User is not yet registered for this SafleID.")
        sp.result(self.data.resolveAddressFromSafleId[idBytes])

    @sp.entry_point
    def transferSafleId(self, params):
        self.auctionContract()

        idBytes = sp.pack(params._safleId)

        sp.verify(self.data.isAddressTaken.get(params._oldOwner, False) == True, "You are not an owner of this safleId.")
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes), "This SafleId does not have an owner.")

        self.oldSafleIds(params._oldOwner, idBytes)
        self.data.isAddressTaken[params._oldOwner] = False

        self.data.resolveAddressFromSafleId[idBytes] = params._newOwner

        self.data.auctionProcess[params._oldOwner] = False
        self.data.isAddressTaken[params._newOwner] = True
        self.data.resolveUserAddress[params._newOwner] = params._safleId

    def oldSafleIds(self, _userAddress, _safleId):
        sp.if ~self.data.resolveOldSafleIdFromAddress.contains(_userAddress):
            self.data.resolveOldSafleIdFromAddress[_userAddress] = sp.list([])

        self.data.resolveOldSafleIdFromAddress[_userAddress].push(_safleId)
        self.data.resolveOldSafleID[_safleId] = _userAddress

    @sp.entry_point
    def setAuctionContract(self, params):
        self.onlyOwner()

        self.data.auctionContractAddress = params._auctionAddress

    @sp.entry_point
    def auctionInProcess(self, params):
        self.auctionContract()

        idBytes = sp.pack(params._safleId)

        sp.verify(params._safleId.length != 0, "Resolver : User SafleID should not be empty.")
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes), "Resolver : User is not yet registered for this SafleID.")
        self.data.auctionProcess[params._safleIdOwner] = True

    @sp.entry_point
    def mapCoin(self, params):
        self.onlyMainContract()

        sp.verify(self.data.OtherCoin.get(params._indexnumber, sp.record(
                isIndexMapped = False,
                aliasName = "",
                coinName = ""
            )).isIndexMapped == False, "This index number has already been mapped.")
        sp.verify(self.data.isCoinMapped.get(params._coinName, False) == False, "This coin is already mapped.")
        sp.verify(self.data.Registrars[params._registrar].isRegisteredRegistrar, "Invalid Registrar.")

        self.data.OtherCoin[params._indexnumber] = sp.record(
            isIndexMapped = True,
            aliasName = params._aliasName,
            coinName = params._coinName
        )

        self.data.isCoinMapped[params._coinName] = True

    @sp.entry_point
    def registerCoinAddress(self, params):
        sp.set_type(params._index, sp.TNat)

        self.coinAddressCheck(params._userAddress, params._index, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.Registrars[params._registrar].isRegisteredRegistrar, "Invalid Registrar.")
        sp.verify(self.data.auctionProcess.get(params._userAddress, False) == False)
        sp.verify(self.data.OtherCoin[params._index].isIndexMapped == True)

        safleId = self.data.resolveUserAddress[params._userAddress]
        sp.if ~self.data.safleIdToCoinAddress.contains(safleId):
            self.data.safleIdToCoinAddress[safleId] = sp.map({})
        self.data.safleIdToCoinAddress[safleId][params._index] = params._address
        self.data.coinAddressToSafleId[params._address] = safleId

    @sp.entry_point
    def updateCoinAddress(self, params):
        sp.set_type(params._index, sp.TNat)

        self.coinAddressCheck(params._userAddress, params._index, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.Registrars[params._registrar].isRegisteredRegistrar, "Invalid Registrar")
        sp.verify(self.data.auctionProcess.get(params._userAddress, False) == False)
        sp.verify(self.data.OtherCoin[params._index].isIndexMapped == True, "This index number is not mapped.")

        safleId = self.data.resolveUserAddress[params._userAddress]
        sp.verify(self.data.safleIdToCoinAddress[safleId].contains(params._index))

        self.data.safleIdToCoinAddress[safleId][params._index] = params._newAddress
        self.data.coinAddressToSafleId[params._newAddress] = safleId

    @sp.onchain_view()
    def coinAddressToId(self, params):
        sp.result(self.data.coinAddressToSafleId[params._address])

    @sp.onchain_view()
    def idToCoinAddress(self, params):
        sp.result(self.data.safleIdToCoinAddress[params._safleId][params._index])
