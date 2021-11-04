import smartpy as sp

checkingContract = sp.io.import_stored_contract("CheckingContract.py")


class Auction(checkingContract.CheckingContract):
    def __init__(self, _ownerAddress, _storageContract):
        self.init(
            contractOwner=_ownerAddress,
            storageContract=_storageContract,
            auction=sp.map(
                tkey=sp.TAddress,
                tvalue=sp.TRecord(
                    isAuctionLive=sp.TBool,
                    auctionConductor=sp.TAddress,
                    safleId=sp.TString,
                    bidRate=sp.map(),
                    higestBidderAddress=sp.TAddress,
                    highestBid=sp.TNat,
                    totalBids=sp.TNat,
                    totalBidders=sp.TNat,
                    biddersArray=sp.TList,
                    returnBidsOfOther=sp.TBool,
                    auctionLastFor=sp.TNat,
                    safleIdTransferred=sp.TBool
                )
            ),
            alreadyActiveAuction=sp.TSet,
            safleIdToAddress=sp.map()
        )
    
    def validateAuctionData(self, _safleId, _auctionSeconds):
        sp.verify(sp.len(_safleId) <= 16, "Length of the safleId should be betweeb 4-16 characters.")
        sp.verify(_auctionSeconds > 300 & _auctionSeconds < 7776000, "Auction time should be in between 330 to 7776000 seconds.")
        sp.verify(~self.data.alreadyActiveAuction.contains(sp.sender), "Auction is already in process by this user.")
        
        safleAddress = sp.view(
            "resolveSafleId",
            self.data.storageContract,
            sp.record(_safleId=_safleId)
        ).open_some()
        sp.verify(safleAddress == sp.sender, "You are not an owner of this SafleId.")

    @sp.entry_point
    def auctionSafleId(self, params):
        self.validateAuctionData(params._safleId, params._auctionSeconds)

        lower = self.toLower(params._safleId)
        self.data.auction[sp.sender] = sp.record(
            isAuctionLive=True,
            auctionConductor=sp.sender,
            safleId=lower,
            bidRate=sp.map(),
            higestBidderAddress=sp.sender,
            highestBid=0,
            totalBids=0,
            totalBidders=0,
            biddersArray=[],
            returnBidsOfOther=False,
            auctionLastFor=sp.timestamp_from_utc_now().add_seconds(params._auctionSeconds),
        )
        self.data.safleIdToAddress[lower] = sp.sender
        self.data.alreadyActiveAuction[sp.sender] = True
        storageContract = sp.contract(
            sp.TRecord(
                _safleId=sp.TString,
                _safleIdOwner=sp.TAddress
            ),
            self.data.storageContract,
            entry_point="auctionInProcess"
        ).open_some()
        sp.transfer(
            sp.record(
                _safleId=lower,
                _safleIdOwner=sp.sender
            ),
            sp.mutez(0),
            storageContract
        )

    @sp.entry_point
    def bidForSafleId(self, params):
        lower = self.toLower(params._safleId)
        bidAmount = sp.amount

        sp.verify(self.data.safleIdToAddress.contains(lower))
        sp.verify(~self.isContract(sp.sender))

        auctioner = self.data.safleIdToAddress[lower]

        sp.verify(self.data.auction[auctioner].isAuctionLive, "Auction is not live")
        sp.verify(self.data.auction[auctioner].auctionConductor != sp.sender, "You cannot bid for your SafleId")
        sp.verify(bidAmount + self.data.auction[auctioner].bidRate.get(sp.sender, sp.mutez(0)) > self.data.auction[auctioner].highestBid, "Bid amount should be greater than the current bidrate.")
        sp.verify(sp.timestamp_from_utc_now() < self.data.auction[auctioner].auctionLastFor, "Auction time is completed")

        if(self.data.auction[auctioner].bidRate[sp.sender]==sp.mutez(0)):
            self.data.auction[auctioner].bidRate[sp.sender] = bidAmount
            self.data.auction[auctioner].highestBid = bidAmount
            self.data.auction[auctioner].biddersArray.push(sp.sender)
            self.data.auction[auctioner].totalBidders+=1
        else:
            self.data.auction[auctioner].bidRate[sp.sender] = self.data.auction[auctioner].bidRate[sp.sender]+bidAmount
            self.data.auction[auctioner].highestBid = self.data.auction[auctioner].bidRate[sp.sender]
        self.data.auction[auctioner].higestBidderAddress = sp.sender
        self.data.auction[auctioner].totalBids+=1

    @sp.entry_point
    def refundOtherBidders(self):
        thisAuction = self.data.auction[sp.sender]
        sp.verify(thisAuction.returnBidsOfOther ==  False)
        sp.verify(thisAuction.auctionConductor == sp.sender)
        sp.verify(sp.len(thisAuction.biddersArray) > 0)

        sp.for i in sp.range(0, sp.len(thisAuction.biddersArray)):
            sp.if thisAuction.biddersArray[i] != thisAuction.higestBidderAddress):
                bidderAmount = thisAuction.bidRate[thisAuction.biddersArray[i]]
                sp.send(thisAuction.biddersArray[i], bidderAmount)
                self.data.alreadyActiveAuction.remove(sp.sender)

        thisAuction.returnBidsOfOther = True
        self.transferSafleIdToWinner()

    @sp.sub_entry_point
    def transferSafleIdToWinner(self):
        thisAuction = self.data.auction[sp.sender]
        sp.send(thisAuction.auctionConductor, thisAuction.highestBid)
        thisAuction.safleIdTransferred = True
        storageContract = sp.contract(
            sp.TRecord(
                _safleId=sp.TString,
                _oldOwner=sp.TAddress,
                _newOwner=sp.TAddress
            ),
            self.data.storageContract,
            entry_point="transferSafleId"
        ).open_some()
        sp.transfer(
            sp.record(
                _safleId=thisAuction.safleId,
                _oldOwner=thisAuction.auctionConductor,
                _newOwner=thisAuction.higestBidderAddress
            ),
            sp.mutez(0),
            storageContract
        )

    @sp.entry_point
    def directlyTransferSafleId(self, params):
        safleAddress = sp.view(
            "resolveSafleId",
            self.data.storageContract,
            sp.record(_safleId=params._safleId)
        ).open_some()
        sp.verify(safleAddress == sp.sender, "You are not an owner of this SafleId.")

        storageContract = sp.contract(
            sp.TRecord(
                _safleId=sp.TString,
                _oldOwner=sp.TAddress,
                _newOwner=sp.TAddress
            ),
            self.data.storageContract,
            entry_point="transferSafleId"
        ).open_some()
        sp.transfer(
            sp.record(
                _safleId=params._safleId,
                _oldOwner=sp.sender,
                _newOwner=params._newOwner
            ),
            sp.mutez(0),
            storageContract
        )

    @sp.onchain_view()
    def arrayOfbidders(self, params):
        thisAuction = self.data.auction[params._auctioner]
        sp.result(thisAuction.biddersArray)

    @sp.entry_point
    def getBidRate(self,_auctioner, _bidder):
        sp.verify((self.data.auction[_auctioner].auctionConductor != address(0x0)))
        return self.data.auction[_auctioner].bidRate[_bidder]

    @sp.add_test(name="SafleID Auction")
    def test():
      pass
