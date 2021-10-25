import smartpy as sp

registrarStorage = sp.io.import_stored_contract("RegistrarStorage.py")
checker = sp.io.import_stored_contract("CheckingClass.py")


class RegistrarMain(sp.Contract):
    def __init__(self):
        self.init(
            contractOwner=sp.address("tz1"),
            walletAddress=sp.address("tz1"),
            safleIdRegStatus=False,
            registrarStorageContractAddress=sp.address("tz1"),
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
        sp.verify(checker.isSafleIdValid(_registrarName))

    def safleIdChecks(self, _safleId):
        sp.verify(sp.amount >= self.data.safleIdFees, "Registration fees not matched.")
        sp.verify(checker.isSafleIdValid(_safleId))

    @sp.entry_point
    def setOwner(self):
        sp.verify(self.data.contractOwner == sp.address("tz1"), "Owner can be set only once.")
        self.data.contractOwner = sp.sender

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

        lower = checker.toLower(params._registrarName)
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

        lower = checker.toLower(params._registrarName)
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

        lower = checker.toLower(params._safleId)
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

        lower = checker.toLower(params._newSafleId)
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

        sp.verify(~checker.isContract(params._walletAddress))
        self.data.walletAddress = params._walletAddress

    @sp.entry_point
    def mapCoins(self, params):
        lowerBlockchainName = checker.toLower(params._blockchainName)
        lowerAliasName = checker.toLower(params._aliasName)
        sp.verify(params._indexNumber != 0)
        sp.verify(checker.checkAlphaNumeric(lowerBlockchainName) & checker.checkAlphaNumeric(lowerAliasName), "Only alphanumeric allowed in blockchain name and alias name")
        
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
        lowerAddress = checker.toLower(params._address)
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
        lowerAddress = checker.toLower(params._address)
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


@sp.add_test(name="SafleID Main")
def test():
    scenario = sp.test_scenario()
    scenario.table_of_contents()
    scenario.h1("Safle Main")

    # Initialize test admin addresses
    owner = sp.test_account("owner")
    seller = sp.test_account("seller")

    mainContract = RegistrarMain()
    scenario += mainContract
    mainContract.setOwner().run(sender=owner)

    storageContract = registrarStorage.RegistrarStorage()
    scenario += storageContract

    scenario += storageContract.setOwner().run(sender=owner)
    scenario += storageContract.upgradeMainContractAddress(
        _mainContractAddress=mainContract.address
    ).run(sender=owner)

    scenario += mainContract.setStorageContract(
        _registrarStorageContract=storageContract.address
    ).run(sender=owner)
    scenario += mainContract.registerRegistrar(
        _registrarName="seller"
    ).run(sender=seller)