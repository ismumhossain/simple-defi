// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

error MustAboveZero();
error TokenNotAllowed();
error DidNotStakeThatMuch();
error YouDoNotHaveReward();
error YouAreNotTheStaker();

contract DeFi is Ownable {
    using SafeERC20 for IERC20;
    using Counters for Counters.Counter;

    struct Staker {
        address[] _token;
        uint256 _balance;
        uint256 _reward;
        uint256 _lastTimeUpdate;
    }

    struct Token {
        string _name;
        address _tokenAddress;
    }

    event Staked(address indexed _staker, uint256 _amount, uint256 indexed _idOfToken);
    event Unstaked(address indexed _unstaker, uint256 _amount, uint256 indexed _idOfToken);

    mapping(address => Staker) private s_stakers;
    mapping(address => address) private s_tokenToPrice;
    mapping(uint256 => Token) private s_tokens;
    IERC20 private s_ihToken;
    Counters.Counter private _tokenId;
    uint256 private constant HOUR_SECONDS = 3600;
    uint256 private constant PER_HOUR_REWARD = 100000;

    constructor(IERC20 ihToken) {
        s_ihToken = ihToken;
    }

    function setPrice(address _token, address _priceFeed) external onlyOwner {
        s_tokenToPrice[_token] = _priceFeed;
    }

    function setToken(string memory name, address tokenAddress) external onlyOwner {
        s_tokens[_tokenId.current()] = Token(name, tokenAddress);
        _tokenId.increment();
    }

    function stake(uint256 _amount, uint256 _idOfToken) external {
        Token memory token = s_tokens[_idOfToken];
        Staker storage staker = s_stakers[msg.sender];
        if (staker._token.length > 0) {
            updateReward(msg.sender);
        } else {
            staker._lastTimeUpdate = block.timestamp;
        }
        if(_amount <= 0) {
            revert MustAboveZero(); 
        }
        if(token._tokenAddress == address(0)) {
            revert TokenNotAllowed();
        }
        address _tokenAddress = token._tokenAddress;
        IERC20(_tokenAddress).transferFrom(msg.sender, address(this), _amount);
        if(staker._token.length == 0) {
          staker._token.push(address(0));
        }
        for(uint256 i = 0; i < staker._token.length; i++) {
            if (_tokenAddress == staker._token[i]) {
                break;
            } else {
              staker._token.push(_tokenAddress);
            }
        }
        staker._balance += _amount;
        emit Staked(msg.sender, _amount, _idOfToken);
    }

    function unstake(uint256 _amount, uint256 _idOfToken) external {
        Token memory token = s_tokens[_idOfToken];
        Staker storage staker = s_stakers[msg.sender];
        updateReward(msg.sender);
        if(staker._token.length == 0) {
            revert YouAreNotTheStaker();
        }
        updateReward(msg.sender);
        if(staker._balance < _amount) {
            revert DidNotStakeThatMuch();
        }
        address _tokenAddress = token._tokenAddress;
        IERC20(_tokenAddress).transfer(msg.sender, _amount);
        staker._balance -= _amount;
        emit Unstaked(msg.sender, _amount, _idOfToken);
    }

    function claimReward() external {
        Staker storage staker = s_stakers[msg.sender];
        if(staker._token[0] == address(0)) {
            revert YouAreNotTheStaker();
        }
        uint256 reward = calculateReward() + staker._reward;
        if(reward <= 0) {
            revert YouDoNotHaveReward();
        }
        staker._lastTimeUpdate = block.timestamp;
        staker._reward = 0;
        s_ihToken.transfer(msg.sender, reward);
    }

    function getTokenValue(address _token) public view returns (uint256, uint256) {
        address priceFeedAddress = s_tokenToPrice[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (,int256 price,,,)= priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);
    }

    function calculateReward() internal view returns (uint256) {
        Staker memory staker = s_stakers[msg.sender];
        return (((((block.timestamp - staker._lastTimeUpdate) * staker._token.length)) *
            PER_HOUR_REWARD) / HOUR_SECONDS);
    }

    function updateReward(address) internal {
        Staker storage staker = s_stakers[msg.sender];

        staker._reward += calculateReward();
        staker._lastTimeUpdate = block.timestamp;
    }

    function getStakers(address _staker) external view returns(Staker memory) {
        return s_stakers[_staker];
    }

    function getTokenPriceAddress(address _token) external view returns(address) {
        return s_tokenToPrice[_token];
    }

    function getTokens(uint256 _idToken) external view returns(Token memory) {
        return s_tokens[_idToken];
    }

    function getPerHourReward() external pure returns(uint256) {
        return PER_HOUR_REWARD;
    }
}