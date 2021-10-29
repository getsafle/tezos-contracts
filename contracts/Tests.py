import smartpy as sp

registrarMain = sp.io.import_stored_contract("RegistrarMain.py")
registrarStorage = sp.io.import_stored_contract("RegistrarStorage.py")
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
