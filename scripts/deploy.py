from scripts.helpful_scripts import get_account
from brownie import IHToken, DeFi, network, config

def deploy_defi_and_ih_token():
    account = get_account()
    ih_token = IHToken.deploy({"from": account})
    defi = DeFi.deploy(
        ih_token.address,
        {"from": account}
    )
    return ih_token, defi

def main():
    deploy_defi_and_ih_token()