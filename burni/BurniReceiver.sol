pragma solidity ^0.5.0;
import "./Burni.sol";

function onERC20Received(address _from, uint256 _value) public returns (bytes32 sig) {
	address REDIRECT_ADDRESS = 0x0
	address BURNI_ADDRESS = 0x076a7c93343579355626F1426dE63F8827C9b9B2;
	bytes32 METHOD_ID = 0x00000000000000000000000000000000000000000000000000000000bc04f0af;

	require(msg.sender == BURNI_ADDRESS);
	/* Process tx here. */

	uint256 spare = 1; // Amount to spare from destruction.
  uint256 leftover = _value - spare; // Amount to remove from circulation.
  bool didRedirect = burni.transfer(REDIRECT_ADDRESS, spare); // Forward Burni to wallet.
  require(didRedirect);
  burni.burn(leftover);  // And, it's gone.

	return METHOD_ID;
}