from brownie import DeFi

def main():
    defi = DeFi[-1]
    tokenName = "WETH"
    tokenAddress = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
    tokenTx = defi.setToken(tokenName, tokenAddress)
    tokenTx.wait(1)
    print("Token set....")
    priceAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    priceTx = defi.setPrice(tokenAddress, priceAddress)
    priceTx.wait(1)
    print("PriceFeed set....")