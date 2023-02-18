from brownie import DeFi, MockWETH
from scripts.set_token_and_price import main
from scripts.helpful_scripts import get_account

def main():
    main()
    non_owner = get_account(1)
    defi = DeFi[-1]
    amount = 10
    id = 0
    weth = MockWETH[-1]
    weth.transfer(non_owner, 20)
    weth.approve(defi.address, 15)
    tokenTx = defi.stake(amount, id)
    tokenTx.wait(1)
    print(f'Staked {amount} token...')
    priceTx = defi.unstake(amount, id)
    priceTx.wait(1)
    print(f'Unstaked {amount} token...')