import smartpy as sp

checkingContract = sp.io.import_stored_contract("CheckingContract.py")


class RegistrarMain(checkingContract.CheckingContract):
    def __init__(self, _ownerAddress, _walletAddress):
        self.init(
            contractOwner=_ownerAddress,
            walletAddress=_walletAddress,
            safleIdRegStatus=False,
            registrarStorageContractAddress=sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"),
            safleIdFees=sp.mutez(0),
            registrarFees=sp.mutez(0),
            storageContractAddress=False
        )

    def onlyOwner(self):
        sp.verify(self.data.contractOwner == sp.sender, "sender is not a contract owner")

    def checkStorageContractAddress(self):
        sp.verify(self.data.storageContractAddress, "storage address not set")

    def checkRegistrationStatus(self):
        sp.verify(self.data.safleIdRegStatus == False, "SafleId Registration is Paused")

    def registrarChecks(self, _registrarName):
        sp.verify(sp.amount >= self.data.registrarFees, "Registration fees not matched.")
        self.isSafleIdValid(_registrarName)

    def safleIdChecks(self, _safleId):
        sp.verify(sp.amount >= self.data.safleIdFees, "Registration fees not matched.")
        self.isSafleIdValid(_safleId)

    @sp.entry_point
    def setSafleIdFees(self, params):
        self.onlyOwner()

        sp.verify(params._amount >= 0, "Please set a fees for SafleID registration.")
        self.data.safleIdFees = sp.utils.nat_to_mutez(params._amount)

    @sp.entry_point
    def setRegistrarFees(self, params):
        self.onlyOwner()

        sp.verify(params._amount >= 0, "Please set a fees for Registrar registration.")
        self.data.registrarFees = sp.utils.nat_to_mutez(params._amount)

    @sp.entry_point
    def toggleRegistrationStatus(self):
        self.onlyOwner()

        self.data.safleIdRegStatus = ~(self.data.safleIdRegStatus)

    @sp.entry_point
    def registerRegistrar(self, params):
        self.registrarChecks(params._registrarName)
        self.checkRegistrationStatus()
        self.checkStorageContractAddress()

        lower = self.toLower(params._registrarName)
        sp.send(self.data.walletAddress, sp.balance)
        registrarStorageContract = sp.contract(
            sp.TRecord(
                _registrar=sp.TAddress,
                _registrarName=sp.TString
            ),
            self.data.registrarStorageContractAddress,
            entry_point="registerRegistrar"
        ).open_some()
        sp.transfer(
            sp.record(
                _registrar=sp.sender,
                _registrarName=lower
            ),
            sp.mutez(0),
            registrarStorageContract
        )

    @sp.entry_point
    def updateRegistrar(self, params):
        self.registrarChecks(params._registrarName)
        self.checkRegistrationStatus()
        self.checkStorageContractAddress()

        lower = self.toLower(params._registrarName)
        sp.send(self.data.walletAddress, sp.balance)
        registrarStorageContract = sp.contract(
            sp.TRecord(
                _registrar=sp.TAddress,
                _newRegistrarName=sp.TString
            ),
            self.data.registrarStorageContractAddress,
            entry_point="updateRegistrar"
        ).open_some()
        sp.transfer(
            sp.record(
                _registrar=sp.sender,
                _newRegistrarName=lower
            ),
            sp.mutez(0),
            registrarStorageContract
        )

    @sp.entry_point
    def registerSafleId(self, params):
        self.safleIdChecks(params._safleId)
        self.checkRegistrationStatus()
        self.checkStorageContractAddress()

        lower = self.toLower(params._safleId)
        sp.send(self.data.walletAddress, sp.balance)
        registrarStorageContract = sp.contract(
            sp.TRecord(
                _registrar=sp.TAddress,
                _userAddress=sp.TAddress,
                _safleId=sp.TString
            ),
            self.data.registrarStorageContractAddress,
            entry_point="registerSafleId"
        ).open_some()
        sp.transfer(
            sp.record(
                _registrar=sp.sender,
                _userAddress=params._userAddress,
                _safleId=lower
            ),
            sp.mutez(0),
            registrarStorageContract
        )

    @sp.entry_point
    def updateSafleId(self, params):
        self.safleIdChecks(params._newSafleId)
        self.checkRegistrationStatus()
        self.checkStorageContractAddress()

        lower = self.toLower(params._newSafleId)
        sp.send(self.data.walletAddress, sp.balance)
        registrarStorageContract = sp.contract(
            sp.TRecord(
                _registrar=sp.TAddress,
                _userAddress=sp.TAddress,
                _safleId=sp.TString
            ),
            self.data.registrarStorageContractAddress,
            entry_point="updateSafleId"
        ).open_some()
        sp.transfer(
            sp.record(
                _registrar=sp.sender,
                _userAddress=params._userAddress,
                _safleId=lower
            ),
            sp.mutez(0),
            registrarStorageContract
        )

    @sp.entry_point
    def setStorageContract(self, params):
        self.onlyOwner()

        self.data.registrarStorageContractAddress = params._registrarStorageContract
        self.data.storageContractAddress = True

    @sp.entry_point
    def updateWalletAddress(self, params):
        self.onlyOwner()

        sp.verify(~self.isContract(params._walletAddress))
        self.data.walletAddress = params._walletAddress

    @sp.entry_point
    def mapCoins(self, params):
        lowerBlockchainName = self.toLower(params._blockchainName)
        lowerAliasName = self.toLower(params._aliasName)
        sp.verify(params._indexNumber != 0)
        self.checkAlphaNumeric(lowerBlockchainName)
        self.checkAlphaNumeric(lowerAliasName)

        registrarStorageContract = sp.contract(
            sp.TRecord(
                _indexnumber=sp.TNat,
                _coinName=sp.TString,
                _aliasName=sp.TString,
                _registrar=sp.TAddress
            ),
            self.data.registrarStorageContractAddress,
            entry_point="mapCoin"
        ).open_some()
        sp.transfer(
            sp.record(
                _indexnumber=params._indexNumber,
                _coinName=lowerBlockchainName,
                _aliasName=lowerAliasName,
                _registrar=sp.sender
            ),
            sp.mutez(0),
            registrarStorageContract
        )

    @sp.entry_point
    def registerCoinAddress(self, params):
        lowerAddress = self.toLower(params._address)
        sp.verify(params._index != 0)
        
        registrarStorageContract = sp.contract(
            sp.TRecord(
                _userAddress=sp.TAddress,
                _index=sp.TNat,
                _address=sp.TString,
                _registrar=sp.TAddress
            ),
            self.data.registrarStorageContractAddress,
            entry_point="registerCoinAddress"
        ).open_some()
        sp.transfer(
            sp.record(
                _userAddress=params._userAddress,
                _index=params._index,
                _address=lowerAddress,
                _registrar=sp.sender
            ),
            sp.mutez(0),
            registrarStorageContract
        )

    @sp.entry_point
    def updateCoinAddress(self, params):
        lowerAddress = self.toLower(params._address)
        sp.verify(params._index != 0)
        
        registrarStorageContract = sp.contract(
            sp.TRecord(
                _userAddress=sp.TAddress,
                _index=sp.TNat,
                _newAddress=sp.TString,
                _registrar=sp.TAddress
            ),
            self.data.registrarStorageContractAddress,
            entry_point="updateCoinAddress"
        ).open_some()
        sp.transfer(
            sp.record(
                _userAddress=params._userAddress,
                _index=params._index,
                _newAddress=lowerAddress,
                _registrar=sp.sender
            ),
            sp.mutez(0),
            registrarStorageContract
        )
