import smartpy as sp


class RegistrarMain(sp.Contract):
    def __init__(self, _walletAddress):
        self.init(
            contractOwner=sp.sender,
            walletAddress=_walletAddress,
            safleIdRegStatus=False,
            registrarStorageContractAddress=0
        )

    def onlyOwner(self):
        sp.verify(self.data.contractOwner == sp.sender)

    def setSafleIdFees(self, _amount):
        sp.verify(_amount > 0)
        self.data.safleIdFees = _amount

    def setRegistrarFees(self, _amount):
        sp.verify(_amount > 0)
        self.data.registrarFees = _amount

    def toggleRegisterationStatus(self):
        self.data.safleIdRegStatus = not (self.data.safleIdRegStatus)
        return True

    def registerRegistrar(self, _registrarName):
        lower = _registrarName.toLower()
        sp.transfer(self.data.walletAddress, sp.value)

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

    def setStorageContract(self, _registrarStorageContract):
        self.data.registrarStorageContractAddress = _registrarStorageContract
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
    
    @sp.add_test(name="SafleID Main")
    def test():
        scenario = sp.test_scenario()
        scenario.table_of_contents()
        scenario.h1("Safle Main")

        # Initialize test admin addresses
        contractOwner = sp.address("tz1-admin-1234")
        seller = sp.address("tz1-seller-1234")
        mainContract = sp.address("tz1-proxy-1234")

        c1 = RegistrarMain(mainContract)
        scenario += c1

        scenario += c1.registerRegistrar(_registrar=1,
                                 _registrarName=seller).run(sender=mainContract)