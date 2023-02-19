from brownie import network, exceptions
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    INITIAL_PRICE_FEED_VALUE,
    DECIMALS,
    get_account,
    get_contract
)
import pytest
from scripts.deploy import deploy_defi_and_ih_token

def test_set_price():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    non_owner = get_account(index=1)
    ih_Token, defi = deploy_defi_and_ih_token()
    price_feed_address = get_contract("dai_usd_price_feed")
    defi.setPrice(ih_Token.address, price_feed_address)
    assert defi.getTokenPriceAddress(ih_Token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        defi.setPrice(
            ih_Token.address, price_feed_address, {"from": non_owner}
        )
        
def test_set_token():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    non_owner = get_account(index=1)
    defi = deploy_defi_and_ih_token()[1]
    weth_token = get_contract("weth_token")
    defi.setToken("WETH", weth_token)
    token = defi.getTokens(0)
    assert token[0] == "WETH"
    assert token[1] == weth_token
    with pytest.raises(exceptions.VirtualMachineError):
        defi.setToken(
            "WETH", weth_token, {"from": non_owner}
        )
        
def test_stake():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    defi = deploy_defi_and_ih_token()[1]
    weth_token = get_contract("weth_token")
    defi.setToken("WETH", weth_token)
    with pytest.raises(exceptions.VirtualMachineError, match="MustAboveZero"):
       defi.stake(0, 0,{"from": get_account()})
    with pytest.raises(exceptions.VirtualMachineError, match="TokenNotAllowed"):
       defi.stake(10, 2,{"from": get_account()})
    non_owner = get_account(index=1)
    weth_token.transfer(non_owner, 30)
    tx = weth_token.approve(defi.address, 22, {"from": non_owner})
    assert "Approval" in tx.events
    print(f"Staker token balance before staking: {weth_token.balanceOf(non_owner)}")
    tx1 = defi.stake(10, 0, {"from": non_owner})
    event = tx1.events["Staked"]
    assert event['_staker'] == non_owner
    assert event['_amount'] == 10
    assert event['_idOfToken'] == 0
    assert weth_token.balanceOf(defi.address) == 10
    staker = defi.getStakers(non_owner)
    assert staker[0][1] == weth_token
    assert staker[1] == 10
    assert staker[2] == 0
    
def test_unstake():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing....")
    ih_Token, defi = deploy_defi_and_ih_token()
    non_owner = get_account(index=1)
    weth_token = get_contract("weth_token")
    defi.setToken("WETH", weth_token)
    with pytest.raises(exceptions.VirtualMachineError, match="YouAreNotTheStaker"):
       defi.unstake(10, 0, {"from": non_owner})
    weth_token.transfer(non_owner, 30)
    tx = weth_token.approve(defi.address, 10, {"from": non_owner})
    assert "Approval" in tx.events
    defi.stake(10, 0, {"from": non_owner})
    with pytest.raises(exceptions.VirtualMachineError, match="DidNotStakeThatMuch"):
       defi.unstake(15, 0, {"from": non_owner})
    tx1 = defi.unstake(9, 0, {"from": non_owner})
    event = tx1.events["Unstaked"]
    assert event['_unstaker'] == non_owner
    assert event['_amount'] == 9
    assert event['_idOfToken'] == 0
    assert weth_token.balanceOf(defi.address) == 1
    staker = defi.getStakers(non_owner)
    assert staker[1] == 1
    event = tx1.events["Unstaked"]
    assert event['_unstaker'] == non_owner
    assert event['_amount'] == 9
    assert event['_idOfToken'] == 0