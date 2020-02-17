pragma solidity ^0.5.0;

import "openzeppelin-solidity/contracts/ownership/Ownable.sol";
import "openzeppelin-solidity/contracts/token/ERC721/ERC721Full.sol";
import "./Strings.sol";
import "./Burni.sol";

contract OwnableDelegateProxy {}

contract ProxyRegistry {
    mapping(address => OwnableDelegateProxy) public proxies;
}

contract Burnin is ERC721Full, Ownable {
    using Strings for string;
    address proxyRegistryAddress;
    uint256 private _currentTokenId = 0;
    address private payment_address;
    string private base_uri;
    mapping(uint256 => uint256) private valuation;
    mapping(uint256 => string) private multihash;

    address constant BURNI_ADDRESS = 0x076a7c93343579355626F1426dE63F8827C9b9B2;

    constructor(
        string memory _name,
        string memory _symbol,
        address _proxyRegistryAddress
    ) public ERC721Full(_name, _symbol) {
        proxyRegistryAddress = _proxyRegistryAddress;
        payment_address = 0x7bde389181EC80591ED40E011b0Ff576a2Beb74b;
        base_uri = "https://burni.co/nft/";
    }

    modifier onlyOwnerOf(uint256 _tokenId) {
        require(ownerOf(_tokenId) == msg.sender);
        _;
    }

    function baseTokenURI() public view returns (string memory) {
        return base_uri;
    }

    function setMultihash(uint256 _tokenId, string memory _mh)
        public
        onlyOwnerOf(_tokenId)
    {
        bytes memory mhBytes = bytes(multihash[_tokenId]);
        require(mhBytes.length == 0);
        multihash[_tokenId] = _mh;
    }

    function getMultihash(uint256 _tokenId)
        external
        view
        returns (string memory)
    {
        return multihash[_tokenId];
    }

    function tokenURI(uint256 _tokenId) external view returns (string memory) {
        bytes memory mhBytes = bytes(multihash[_tokenId]);
        if (mhBytes.length == 0) {
            return baseTokenURI();
        }
        return Strings.strConcat(baseTokenURI(), multihash[_tokenId]);
    }

    function onERC20Received(address _from, uint256 _value)
        public
        returns (bytes32 sig)
    {
        Burni burni = Burni(BURNI_ADDRESS);

        require(msg.sender == BURNI_ADDRESS);
        require(_value >= 40);

        uint256 fee = _value / 40;
        uint256 burniValue = _value - fee;
        bool didPayFee = burni.transfer(payment_address, fee);
        require(didPayFee);
        burni.burn(burniValue);

        uint256 newTokenId = _getNextTokenId();
        _mint(_from, newTokenId);
        valuation[newTokenId] = burniValue;
        _incrementTokenId();

        bytes32 METHOD_ID = 0x00000000000000000000000000000000000000000000000000000000bc04f0af;

        return METHOD_ID;
    }

    function getValuation(uint256 _tokenId)
        public
        view
        returns (uint256 _value)
    {
        return valuation[_tokenId];
    }

    function _getNextTokenId() private view returns (uint256) {
        return _currentTokenId.add(1);
    }

    function _incrementTokenId() private {
        _currentTokenId++;
    }

    function isApprovedForAll(address owner, address operator)
        public
        view
        returns (bool)
    {
        ProxyRegistry proxyRegistry = ProxyRegistry(proxyRegistryAddress);
        if (address(proxyRegistry.proxies(owner)) == operator) {
            return true;
        }

        return super.isApprovedForAll(owner, operator);
    }

    function updatePaymentAddress(address _payment_address) public {
        require(msg.sender == payment_address);
        payment_address = _payment_address;
    }

    function updateBaseTokenURI(string memory _base_uri) public {
        require(msg.sender == payment_address);
        base_uri = _base_uri;
    }
}
