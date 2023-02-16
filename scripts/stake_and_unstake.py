from brownie import DeFi

def main():
    defi = DeFi[-1]
    amount = 10
    id = 1
    tokenTx = defi.stake(amount, id)
    tokenTx.wait(1)
    print(f'Staked {amount} token...')
    priceTx = defi.unstake(amount, id)
    priceTx.wait(1)
    print(f'Unstaked {amount} token...')