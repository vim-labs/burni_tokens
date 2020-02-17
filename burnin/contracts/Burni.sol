pragma solidity ^0.5.0;

contract Burni {
    function transfer(address _to, uint256 _value)
        public
        returns (bool isSuccess);
    function burn(uint256 _value) public;
}
