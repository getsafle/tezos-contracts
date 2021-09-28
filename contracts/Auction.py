import smartpy as sp


class Auction(sp.contract):
    def __init__(self, _storageContract):
        self.init(
            contractOwner=sp.sender,
            storageContract=_storageContract
        )

    @sp.entry_point
    def auctionSafleId(self, _safleId, _auctionSeconds):
        lower = _safleId.toLower()
        self.data.auction[sp.sender].isAuctionLive = True
        self.data.auction[sp.sender].auctionConductor = sp.sender
        self.data.auction[sp.sender].safleId = lower
        self.data.auction[sp.sender].auctionLastFor = now + _auctionSeconds
        self.data.safleIdToAddress[lower] = sp.sender
        self.data.alreadyActiveAuction[sp.sender] = True
        self.data.storageContract.auctionInProcess(sp.sender, lower)

    @sp.entry_point
    def bidForSafleId(self, _safleId):
        lower = _safleId.toLower()
        bidAmount = sp.value
        sp.verify(self.data.safleIdToAddress[lower] != address(0x0))
        sp.verify(self.data.isContract(sp.sender)==False)
        

        auctioner = self.data.safleIdToAddress[lower]

        sp.verify(self.data.auction[auctioner].isAuctionLive)
        sp.verify(self.data.auction[auctioner].auctionConductor != sp.sender)
        sp.verify(self.data.bidAmount + self.data.auction[auctioner].bidRate[sp.sender]> self.data.auction[auctioner].highestBid)
        sp.verify(self.data.now < self.data.auction[auctioner].auctionLastFor)

        if(self.data.auction[auctioner].bidRate[sp.sender]==0):
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
        sp.verify(self.data.auction[sp.sender].returnBidsOfOther ==  False)
        sp.verify(self.data.auction[sp.sender].auctionConductor == sp.sender)
        sp.verify(self.data.auction[sp.sender].biddersArray.length > 0)

        for i in range(self.data.auction[sp.sender].biddersArray.length):
            if(self.data.auction[sp.sender].biddersArray[i] != self.data.auction[sp.sender].higestBidderAddress):
                bidderAmount = self.data.auction[sp.sender].bidRate[self.data.auction[sp.sender].biddersArray[i]]
                self.data.auction[sp.sender].biddersArray[i].transfer(bidderAmount)
                self.data.alreadyActiveAuction[sp.sender] = False

        self.data.auction[sp.sender].returnBidsOfOther = True
        self.data.auction[sp.sender].auctionConductor.transfer(self.data.auction[sp.sender].highestBid)
        self.data.auction[sp.sender].safleIdTransferred = True
        #transfer in storage contract

    @sp.entry_point
    def directlyTransferSafleId(_safleId, _newOwner):
        return True

    @sp.entry_point
    def arrayOfbidders(self,_auctioner):
        sp.verify((self.data.auction[_auctioner].auctionConductor != address(0x0)))
        return self.data.auction[_auctioner].biddersArray

    @sp.entry_point
    def getBidRate(self,_auctioner, _bidder):
        sp.verify((self.data.auction[_auctioner].auctionConductor != address(0x0)))
        return self.data.auction[_auctioner].bidRate[_bidder]

    @sp.add_test(name="SafleID Auction")
    def test():
      pass
