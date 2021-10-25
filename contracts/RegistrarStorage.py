import smartpy as sp


class RegistrarStorage(sp.Contract):
    def __init__(self):
        self.init(
            contractOwner=sp.address("tz1"),
            mainContract=sp.address("tz1"),
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

    @sp.entry_point
    def setOwner(self):
        sp.verify(self.data.contractOwner == sp.address("tz1"), "Owner can be set only once.")
        self.data.contractOwner = sp.sender

    def onlyOwner(self):
        sp.verify(self.data.contractOwner == sp.sender)

    def onlyMainContract(self):
        sp.verify(self.data.mainContract == sp.sender)

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

        sp.verify(self.data.isAddressTaken[params._registrar] == True, "Registrar should register first.")
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

    @sp.utils.view(sp.TAddress)
    def resolveRegistrarName(self, params):
        regNameBytes = sp.pack(params._name)
        sp.verify(self.data.registrarNameToAddress.contains(regNameBytes), "Resolver : Registrar is not yet registered for this SafleID.")
        sp.result(self.data.registrarNameToAddress[regNameBytes])

    @sp.entry_point
    def registerSafleId(self, params):
        self.safleIdChecks(params._safleId, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.isAddressTaken[params._userAddress] == False, "SafleID already registered")

        idBytes = sp.pack(params._safleId)

        self.data.resolveAddressFromSafleId[idBytes] = params._userAddress
        self.data.isAddressTaken[params._userAddress] = True
        self.data.resolveUserAddress[params._userAddress] = params._safleId
        self.data.totalSafleIdRegistered += 1

    @sp.entry_point
    def updateSafleId(self, params):
        self.safleIdChecks(params._safleId, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.totalSafleIDCount[params._userAddress]+1 <= 5, "Maximum update count reached.") #MAX_NAME_UPDATES
        sp.verify(self.data.isAddressTaken[params._userAddress] == True, "SafleID not registered.")
        sp.verify(self.data.auctionProcess[params._userAddress] == False, "SafleId cannot be updated inbetween Auction.")

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

    @sp.utils.view(sp.TAddress)
    def resolveSafleId(self, params):
        idBytes = sp.pack(params._safleId)
        sp.verify(sp.len(sp.pack(params._safleId)) != 0, "Resolver : user SafleID should not be empty.")
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes), "Resolver : User is not yet registered for this SafleID.")
        sp.result(self.data.resolveAddressFromSafleId[idBytes])

    @sp.entry_point
    def transferSafleId(self, params):
        self.auctionContract()

        idBytes = sp.pack(params._safleId)

        sp.verify(self.data.isAddressTaken[params._oldOwner] == True, "You are not an owner of this safleId.")
        sp.verify(self.data.resolveAddressFromSafleId.contains(idBytes), "This SafleId does not have an owner.")

        self.oldSafleIds(params._oldOwner, idBytes)
        self.data.isAddressTaken[params._oldOwner] = False

        self.data.resolveAddressFromSafleId[idBytes] = params._newOwner

        self.data.auctionProcess[params._oldOwner] = False
        self.data.isAddressTaken[params._newOwner] = True
        self.data.resolveUserAddress[params._newOwner] = params._safleId

    def oldSafleIds(self, _userAddress, _safleId):
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

        sp.verify(self.data.OtherCoin[params._indexnumber].isIndexMapped == False, "This index number has already been mapped.")
        sp.verify(self.data.isCoinMapped[params._coinName] == False, "This coin is already mapped.")
        sp.verify(self.data.Registrars[params._registrar].isRegisteredRegistrar, "Invalid Registrar.")

        self.data.OtherCoin[params._indexnumber].isIndexMapped = True
        self.data.OtherCoin[params._indexnumber].aliasName = params._aliasName
        self.data.OtherCoin[params._indexnumber].coinName = params._coinName
        self.data.isCoinMapped[params._coinName] = True

    @sp.entry_point
    def registerCoinAddress(self, params):
        self.coinAddressCheck(params._userAddress, params._index, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.Registrars[params._registrar].isRegisteredRegistrar, "Invalid Registrar.")
        sp.verify(self.data.auctionProcess[params._userAddress] == False)
        sp.verify(self.data.OtherCoin[params._index].isIndexMapped == True)

        safleId = self.data.resolveUserAddress[params._userAddress]
        self.data.safleIdToCoinAddress[safleId][params._index] = params._address
        self.data.coinAddressToSafleId[params._address] = safleId

    @sp.entry_point
    def updateCoinAddress(self, params):
        self.coinAddressCheck(params._userAddress, params._index, params._registrar)
        self.onlyMainContract()

        sp.verify(self.data.Registrars[params._registrar].isRegisteredRegistrar, "Invalid Registrar")
        sp.verify(self.data.auctionProcess[params._userAddress] == False)
        sp.verify(self.data.OtherCoin[params._index].isIndexMapped == True, "This index number is not mapped.")

        safleId = self.data.resolveUserAddress[params._userAddress]
        sp.verify(self.data.safleIdToCoinAddress[safleId].contains(params._index))

        self.data.safleIdToCoinAddress[safleId][params._index] = params._newAddress
        self.data.coinAddressToSafleId[params._newAddress] = safleId

    @sp.utils.view(sp.TString)
    def coinAddressToId(self, params):
        sp.result(self.data.coinAddressToSafleId[params._address])

    @sp.utils.view(sp.TAddress)
    def idToCoinAddress(self, params):
        sp.result(self.data.safleIdToCoinAddress[params._safleId][params._index])
