import smartpy as sp

registrarMain = sp.io.import_stored_contract("RegistrarMain.py")
registrarStorage = sp.io.import_stored_contract("RegistrarStorage.py")
auctionContract = sp.io.import_stored_contract("Auction.py")
checkingContract = sp.io.import_stored_contract("CheckingContract.py")


@sp.add_test(name="SafleID Main")
def test():
    scenario = sp.test_scenario()
    scenario.h1("Safle Main")

    owner = sp.test_account("owner")
    registrar = sp.test_account("registrar")
    wallet = sp.test_account("wallet")
    newWallet = sp.test_account("newWallet")
    user = sp.test_account("user")

    scenario.h2("RegistrarMain Contract")
    mainContract = registrarMain.RegistrarMain(
        _ownerAddress=owner.address, _walletAddress=wallet.address
    )
    scenario += mainContract

    scenario.h2("RegistrarStorage Contract")
    storageContract = registrarStorage.RegistrarStorage(
        _ownerAddress=owner.address, _mainContractAddress=mainContract.address
    )
    scenario += storageContract

    scenario.h4("Setting Storage contract address in the Main contract")
    scenario += mainContract.setStorageContract(
        _registrarStorageContract=storageContract.address
    ).run(sender=owner)

    scenario.h2("Serial usage of Trasactions testing all entry_points")

    scenario.h4("Setting SafleID fees")
    scenario += mainContract.setSafleIdFees(_amount=1000).run(sender=owner)

    scenario.h4("Setting SafleID fee for the registrar")
    scenario += mainContract.setRegistrarFees(_amount=100000).run(sender=owner)

    scenario.h4("Toggling registration status on/off")
    scenario += mainContract.toggleRegistrationStatus().run(sender=owner)
    scenario += mainContract.toggleRegistrationStatus().run(sender=owner)

    scenario.h4("Registering a new Registrar")
    scenario += mainContract.registerRegistrar(_registrarName="registrarer").run(
        sender=registrar, amount=sp.mutez(100000)
    )

    scenario.h4("Updating the name of the registrar")
    scenario += mainContract.updateRegistrar(_registrarName="registrar").run(
        sender=registrar, amount=sp.mutez(100000)
    )

    scenario.h4("Registering a new SafleID")
    scenario += mainContract.registerSafleId(
        _safleId="userrrr", _userAddress=user.address
    ).run(sender=registrar, amount=sp.mutez(1000))

    scenario.h4("Updating the name of the SafleID")
    scenario += mainContract.updateSafleId(
        _newSafleId="user", _userAddress=user.address
    ).run(sender=registrar, amount=sp.mutez(1000))

    scenario.h4("Updating the wallet address for a new wallet")
    scenario += mainContract.updateWalletAddress(_walletAddress=newWallet.address).run(
        sender=owner
    )

    scenario.h4("Mapping a coin to a SafleID")
    scenario += mainContract.mapCoins(
        _blockchainName="Tezos", _aliasName="XTZ", _indexNumber=1
    ).run(sender=registrar)

    scenario.h4("Register a new coin address")
    scenario += mainContract.registerCoinAddress(
        _address="aDdReSsssss", _userAddress=user.address, _index=1
    ).run(sender=registrar)

    scenario.h4("Updating a coin address")
    scenario += mainContract.updateCoinAddress(
        _address="aDdReSs", _userAddress=user.address, _index=1
    ).run(sender=registrar)

    scenario.h4("Fetching SafleID from coin address")
    scenario.show(storageContract.coinAddressToId(sp.record(_address="address")))

    scenario.h4("Fetching coin address from SafleID")
    scenario.show(storageContract.idToCoinAddress(sp.record(_safleId="user", _index=1)))

    scenario.h4("Fetching Address of a registrar")
    scenario.show(storageContract.resolveRegistrarName(sp.record(_name="registrar")))

    scenario.h4("Fetching Address of a SafleID")
    scenario.show(storageContract.resolveSafleId(sp.record(_safleId="user")))

    scenario.h4("Updating to a new Main Contract")
    newMainContract = registrarMain.RegistrarMain(
        _ownerAddress=owner.address, _walletAddress=wallet.address
    )
    scenario += newMainContract
    scenario += storageContract.upgradeMainContractAddress(
        _mainContractAddress = newMainContract.address
    ).run(sender=owner)


@sp.add_test(name="SafleID Auction")
def test():
    scenario = sp.test_scenario()
    scenario.h1("Safle Auction")

    owner = sp.test_account("owner")
    registrar = sp.test_account("registrar")
    wallet = sp.test_account("wallet")
    oldSafleUser = sp.test_account("oldSafleUser")
    bidder1 = sp.test_account("bidder1")
    bidder2 = sp.test_account("bidder2")
    bidder3 = sp.test_account("bidder3")

    scenario.h2("RegistrarMain Contract")
    mainContract = registrarMain.RegistrarMain(
        _ownerAddress=owner.address, _walletAddress=wallet.address
    )
    scenario += mainContract

    scenario.h2("RegistrarStorage Contract")
    storageContract = registrarStorage.RegistrarStorage(
        _ownerAddress=owner.address, _mainContractAddress=mainContract.address
    )
    scenario += storageContract

    scenario.h2("Auction Contract")
    auction = auctionContract.Auction(
        _ownerAddress=owner.address, _storageContract=storageContract.address
    )
    scenario += auction

    scenario.h4("Setting Contracts to each other")
    mainContract.setStorageContract(
        _registrarStorageContract=storageContract.address
    ).run(sender=owner)
    storageContract.setAuctionContract(
        _auctionAddress=auction.address
    ).run(sender=owner)

    # Initial Setup
    mainContract.setSafleIdFees(_amount=1000).run(sender=owner)
    mainContract.setRegistrarFees(_amount=100000).run(sender=owner)
    mainContract.registerRegistrar(_registrarName="registrar").run(
        sender=registrar, amount=sp.mutez(100000)
    )
    mainContract.registerSafleId(
        _safleId="oldSafleUser", _userAddress=oldSafleUser.address
    ).run(sender=registrar, amount=sp.mutez(1000))

    scenario.h4("Starting an Auction")
    scenario += auction.auctionSafleId(
        _safleId="oldsafleuser", _auctionSeconds=600
    ).run(sender=oldSafleUser)

    scenario.h4("Bidding on the SafleID")
    scenario += auction.bidForSafleId(
        _safleId="oldsafleuser"
    ).run(sender=bidder1, amount=sp.mutez(100))
    scenario += auction.bidForSafleId(
        _safleId="oldsafleuser"
    ).run(sender=bidder2, amount=sp.mutez(200))
    scenario += auction.bidForSafleId(
        _safleId="oldsafleuser"
    ).run(sender=bidder3, amount=sp.mutez(300))
    scenario += auction.bidForSafleId(
        _safleId="oldsafleuser"
    ).run(sender=bidder1, amount=sp.mutez(1000))

    scenario.h4("Refunding the bidders except the winner")
    scenario += auction.refundOtherBidders().run(sender=oldSafleUser)

    scenario.h4("Directly sending the safleID to the old user")
    scenario += auction.directlyTransferSafleId(
        _safleId="oldsafleuser",
        _newOwner=oldSafleUser.address
    ).run(sender=bidder1)

    scenario.h4("Getting the array of all the bidders")
    scenario.show(auction.arrayOfbidders(sp.record(_auctioner=oldSafleUser.address)))

    scenario.h4("Getting the current bid rate of a bidder")
    scenario.show(auction.getBidRate(sp.record(_auctioner=oldSafleUser.address, _bidder=bidder1.address)))
