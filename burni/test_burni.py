import pytest
import logging
from eth_utils import denoms
from eth_tester.exceptions import TransactionFailed

log = logging.getLogger().info

@pytest.fixture
def burni(w3, get_contract):
	# Instantiate Burni smart contract.
	with open('./burni.vy') as f:
		contract_code = f.read()

	args = {
		'name': 'Burni',
		'symbol': 'BURN',
		'decimals': 18,
		'supply': int(1e6)
	}

	return get_contract(contract_code, *args.values())

@pytest.fixture
def burnin(w3, get_contract):
	# Instantiate Burnin smart contract.
	with open('./burnin.vy') as f:
		contract_code = f.read()

	return get_contract(contract_code)

def test_init_burni(w3, burni):
	# Test the initial Burni balance.
	k0 = w3.eth.accounts[0]
	log('DEV BURNI ADDRESS: {}'.format(burni.address))
	log('DEV PAYMENT ADDRESS: {}'.format(k0))
	assert burni.balanceOf(k0) == int(1e6) * denoms.ether

def test_burnin_interfaces(w3, burnin):
	interface_eip165 = bytes.fromhex('0000000000000000000000000000000000000000000000000000000001ffc9a7')
	interface_eip721 = bytes.fromhex('0000000000000000000000000000000000000000000000000000000080ac58cd')
	interface_eip721_metadata = bytes.fromhex('000000000000000000000000000000000000000000000000000000005b5e139f')
	interface_eip721_enumerable = bytes.fromhex('00000000000000000000000000000000000000000000000000000000780e9d63')

	assert burnin.supportsInterface(interface_eip165)
	assert burnin.supportsInterface(interface_eip721)
	assert burnin.supportsInterface(interface_eip721_metadata)
	assert burnin.supportsInterface(interface_eip721_enumerable)
	assert burnin.name() == 'Burnin'
	assert burnin.symbol() == 'BURNIN'
	assert burnin.decimals() == 0
	assert burnin.totalSupply() == 0

def test_transfer_burni(w3, burni):
	# Test a Burni transfer between two addresses (throws if insufficient funds).
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]

	burni.transfer(k1, burni.balanceOf(k0), transact={'from': k0})

	assert burni.balanceOf(k0) == 0
	assert burni.balanceOf(k1) == int(1e6) * denoms.ether

	with pytest.raises(TransactionFailed):
		burni.transfer(k1, 1 * denoms.ether, transact={'from': k0})

def test_burnin_mint(w3, burni, burnin):
	# Test a Burnin minting.

	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]

	burni.transfer(k1, burni.balanceOf(k0), transact={'from': k0})
	assert burni.balanceOf(k0) == 0
	pre_balance = burni.totalSupply()
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k1})

	assert burnin.exists(1) == True
	assert burnin.exists(2) == False

	fee = 1 * denoms.ether // 40
	valuation = 1 * denoms.ether - fee

	assert burni.totalSupply() == pre_balance - valuation
	assert burni.balanceOf(k0) == fee

def test_immutable_multihash(w3, burni, burnin):
	# Test setting a permanent multihash (throws if an attempt is made to change the value).
	k0 = w3.eth.accounts[0]

	hash_a = 'QmdD4wQEYVFU3dqHizmyVNdeEAYpxBsPd1mBZ6zjmtsVwM'
	hash_b = 'f1220dcee0db173c2d44d562631c925a4ccbfc94dbdd21350a5b9fa5dbd715e42f3c0'

	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})
	burnin.setImmutableMultihash(hash_a, 1, transact={'from': k0})

	with pytest.raises(TransactionFailed):
		burnin.setImmutableMultihash(hash_b, 1, transact={'from': k0})

def test_set_tokenURI(w3, burni, burnin):
	# Test setting an updatable multihash.
	k0 = w3.eth.accounts[0]

	baseURI = 'https://burni.co/nft/'

	assert burnin.baseTokenURI() == baseURI
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})
	assert burnin.tokenURI(1) == baseURI

	hash = 'QmdD4wQEYVFU3dqHizmyVNdeEAYpxBsPd1mBZ6zjmtsVwM'
	burnin.setImmutableMultihash(hash, 1, transact={'from': k0})
	assert burnin.tokenURI(1) == baseURI + hash

def test_ids(w3, burni, burnin):
	# Test expected token ids and indices.
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]

	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})

	assert burnin.totalSupply() == 3
	assert burnin.tokenByIndex(2) == 3

	burni.transfer(k1, 1 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k1})

	assert burnin.tokenOfOwnerByIndex(k1, 0) == 4

def test_transfer_nft(w3, burni, burnin):
	# Test a Burnin transfer.
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]
	k2 = w3.eth.accounts[2]
	k3 = w3.eth.accounts[3]

	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})

	burni.transfer(k1, 10 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k1})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k1})

	assert burnin.tokenOfOwnerByIndex(k1, 0) == 4
	assert burnin.tokenOfOwnerByIndex(k1, 1) == 5

	burnin.transferFrom(k1, k2, 4, transact={'from': k1})
	assert burnin.tokenOfOwnerByIndex(k1, 0) == 5
	assert burnin.tokenOfOwnerByIndex(k2, 0) == 4

	burnin.transferFrom(k1, k2, 5, transact={'from': k1})
	with pytest.raises(TransactionFailed):
		assert burnin.tokenOfOwnerByIndex(k1, 0) == 0

	assert burnin.balanceOf(k0) == 3
	assert burnin.balanceOf(k1) == 0
	assert burnin.balanceOf(k2) == 2

	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k1})
	assert burnin.balanceOf(k1) == 1

def test_transfer_nft_approve(w3, burni, burnin):
	# Test Burnin approvals.
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]
	k2 = w3.eth.accounts[2]

	burni.transfer(k1, 5 * denoms.ether, transact={'from': k0})
	burni.transfer(k2, 5 * denoms.ether, transact={'from': k0})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k0})

	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k1})
	burni.transfer(burnin.address, 1 * denoms.ether, transact={'from': k2})

	assert burnin.totalSupply() == 3
	assert burnin.balanceOf(k0) == 1
	assert burnin.balanceOf(k1) == 1
	assert burnin.balanceOf(k2) == 1

	burnin.approve(k1, 1, transact={'from': k0})
	burnin.transferFrom(k0, k2, 1, transact={'from': k1})
	assert burnin.balanceOf(k0) == 0
	assert burnin.balanceOf(k2) == 2

	with pytest.raises(TransactionFailed):
		assert burnin.tokenOfOwnerByIndex(k0, 0) == 0

	assert burnin.tokenOfOwnerByIndex(k2, 1) == 1

	with pytest.raises(TransactionFailed):
		assert burnin.clearApproval(k2, 1, transact={'from': k1})
	assert burnin.clearApproval(k2, 1, transact={'from': k2})

def test_upgrade(w3, burni, burnin):
	# Test an administrative upgrade (throws if unauthorized).
	k0 = w3.eth.accounts[0]
	k1 = w3.eth.accounts[1]

	with pytest.raises(TransactionFailed):
		burnin.updatePaymentAddress(k1, transact={'from': k1})
	with pytest.raises(TransactionFailed):
		burnin.updateBaseTokenURI('http://newdomain.com', transact={'from': k1})

	burnin.updatePaymentAddress(k1, transact={'from': k0})

	# Use new payment address to update baseURI
	burnin.updateBaseTokenURI('http://newdomain.com', transact={'from': k1})

	assert burnin.baseTokenURI() == 'http://newdomain.com'