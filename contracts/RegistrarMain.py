import smartpy as sp

checker = sp.io.import_stored_contract("CheckingClass.py")


class RegistrarMain(sp.Contract):
    def __init__(self):
        self.init(
            contractOwner=sp.address("tz1"),
            walletAddress=sp.address("tz1"),
            safleIdRegStatus=False,
            registrarStorageContractAddress=sp.address("tz1"),
            registrarFees=sp.mutez(0),
            storageContractAddress=False
        )

    @sp.entry_point
    def setOwner(self):
        sp.verify(self.data.contractOwner == sp.address("tz1"), "Owner can be set only once.")
        self.data.contractOwner = sp.sender

    def onlyOwner(self):
        sp.verify(self.data.contractOwner == sp.sender)

    def setSafleIdFees(self, _amount):
        sp.verify(_amount > 0)
        self.data.safleIdFees = _amount

    def setRegistrarFees(self, _amount):
        sp.verify(_amount > 0)
        self.data.registrarFees = _amount

    def checkStorageContractAddress(self):
        sp.verify(self.data.storageContractAddress, "storage address not set")

    def checkRegistrationStatus(self):
        sp.verify(self.data.safleIdRegStatus == sp.bool(False))

    def registrarChecks(self, _registrarName):
        sp.verify(sp.amount >= self.data.registrarFees, "Registration fees not matched.")
        sp.verify(checker.isSafleIdValid(_registrarName=_registrarName))

    def toggleRegisterationStatus(self):
        self.data.safleIdRegStatus = not (self.data.safleIdRegStatus)
        return True

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

    def updateRegistrar(self, _registrarName):
        lower = _registrarName.toLower()
        c = sp.contract(sp.TRecord(num = sp.TInt),self.data.registrarStorageContractAddress,entry_point="updateRegistrar").open_some()
        mydata = sp.record(sp.sender,lower)
        sp.transfer(mydata,sp.mutez(0),c)

    def registerSafleId(self, _userAddress,_safleId):
        lower = _safleId.toLower()
        c = sp.contract(sp.TRecord(num = sp.TInt),self.data.registrarStorageContractAddress,entry_point="registerSafleId").open_some()
        mydata = sp.record(sp.sender,_userAddress,lower)
        sp.transfer(mydata,sp.mutez(0),c)

    def updateSafleId(self, _userAddress,_newSafleId):
        lower = _newSafleId.toLower()
        c = sp.contract(sp.TRecord(num = sp.TInt),self.data.registrarStorageContractAddress,entry_point="updateSafleId").open_some()
        mydata = sp.record(sp.sender,_userAddress,lower)
        sp.transfer(mydata,sp.mutez(0),c)

    @sp.entry_point
    def setStorageContract(self, params):
        self.data.registrarStorageContractAddress = params._registrarStorageContract
        self.data.storageContractAddress = True

    def updateWalletAddress(self, _walletAddress):
        self.data.walletAddress = _walletAddress

    def mapCoins(self, _indexNumber, _blockchainName, _aliasName):
        sp.verify(_indexNumber != 0)
        c = sp.contract(sp.TRecord(num = sp.TInt),self.data.registrarStorageContractAddress,entry_point="mapCoin").open_some()
        mydata = sp.record(_indexNumber,_blockchainName.toLower(),_aliasName.toLower(), sp.sender)
        sp.transfer(mydata,sp.mutez(0),c)
        return True

    def registerCoinAddress(self, _userAddress, _index, _address):
        length = len(_address)
        sp.verify(_index != 0)
        sp.verify(_userAddress != 0)
        sp.verify(length > 0)
        c = sp.contract(sp.TRecord(num = sp.TInt),self.data.registrarStorageContractAddress,entry_point="registerCoinAddress").open_some()
        mydata = sp.record(_userAddress,_index,_address.toLower(), sp.sender)
        sp.transfer(mydata,sp.mutez(0),c)

    def updateCoinAddress(self, _userAddress, _index, _address):
        length = len(_address)      
        sp.verify(_index != 0)
        sp.verify(_userAddress != 0)
        sp.verify(length > 0)                     #confirm why? should be a fixed length string
        c = sp.contract(sp.TRecord(num = sp.TInt),self.data.registrarStorageContractAddress,entry_point="updateCoinAddress").open_some()
        mydata = sp.record(_userAddress,_index,_address.toLower(), sp.sender)
        sp.transfer(mydata,sp.mutez(0),c)
