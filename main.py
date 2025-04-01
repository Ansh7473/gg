import time
from web3 import Web3

# Load Private Key from File
with open("private_keys.txt", "r") as f:
    private_key = f.read().strip()

# Hardcoded Config (from your config.json)
config = {
    "rpc_url": "https://rpc.soneium.org/",
    "chain_id": 1868,
    "swap_amount_eth": 0.0001,
    "swap_amount_variation": 0.000002,
    "swap_back_percentage": 100,
    "number_of_swaps": 6,
    "delay_between_swaps": 1,
    "min_delay_sec": 1,
    "max_delay_sec": 2,
    "gas_settings": {
        "max_fee_gwei": 0.5,
        "priority_fee_gwei": 0.1
    }
}

# Connect to Soneium
w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
if not w3.is_connected():
    raise Exception("Failed to connect to Soneium RPC")
account = w3.eth.account.from_key(private_key)

# Contract Addresses
swap_router_address = "0xeba58c20629ddab41e21a3E4E2422E583ebD9719"
quoter_address = "0x22e5195BcC9b0C87f330FbCE2755B263662578E2"  # QuoterV2
weth_address = "0x4200000000000000000000000000000000000006"
usdt_address = "0x3A337a6adA9d885b6Ad95ec48F9b75f197b5AE35"
algebra_factory_address = "0x8Ff309F68F6Caf77a78E9C20d2Af7Ed4bE2D7093"

# Hardcoded ABIs
weth_abi = [
    {"constant": False, "inputs": [], "name": "deposit", "outputs": [], "payable": True, "stateMutability": "payable", "type": "function"},
    {"constant": False, "inputs": [{"name": "wad", "type": "uint256"}], "name": "withdraw", "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "guy", "type": "address"}, {"name": "wad", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": False, "inputs": [{"name": "src", "type": "address"}, {"name": "dst", "type": "address"}, {"name": "wad", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": False, "inputs": [{"name": "dst", "type": "address"}, {"name": "wad", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "src", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [{"name": "src", "type": "address"}, {"name": "guy", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}
]

usdt_abi = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}
]

factory_abi = [
    {"inputs": [{"internalType": "address", "name": "tokenA", "type": "address"}, {"internalType": "address", "name": "tokenB", "type": "address"}], "name": "poolByPair", "outputs": [{"internalType": "address", "name": "pool", "type": "address"}], "stateMutability": "view", "type": "function"}
]

pool_abi = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "int24", "name": "bottomTick", "type": "int24"}, {"indexed": True, "internalType": "int24", "name": "topTick", "type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "liquidityAmount", "type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"}], "name": "Burn", "type": "event"},
    {"inputs": [], "name": "activeIncentive", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "int24", "name": "bottomTick", "type": "int24"}, {"internalType": "int24", "name": "topTick", "type": "int24"}, {"internalType": "uint128", "name": "amount", "type": "uint128"}], "name": "burn", "outputs": [{"internalType": "uint256", "name": "amount0", "type": "uint256"}, {"internalType": "uint256", "name": "amount1", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "liquidity", "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "globalState", "outputs": [{"internalType": "uint160", "name": "price", "type": "uint160"}, {"internalType": "int24", "name": "tick", "type": "int24"}, {"internalType": "uint16", "name": "lastFee", "type": "uint16"}, {"internalType": "uint8", "name": "pluginConfig", "type": "uint8"}, {"internalType": "uint16", "name": "communityFee", "type": "uint16"}, {"internalType": "bool", "name": "unlocked", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "token0", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "token1", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getReserves", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}, {"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

quoter_abi = [
    {"inputs": [{"internalType": "address", "name": "_factory", "type": "address"}, {"internalType": "address", "name": "_WNativeToken", "type": "address"}, {"internalType": "address", "name": "_poolDeployer", "type": "address"}], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "WNativeToken", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "int256", "name": "amount0Delta", "type": "int256"}, {"internalType": "int256", "name": "amount1Delta", "type": "int256"}, {"internalType": "bytes", "name": "path", "type": "bytes"}], "name": "algebraSwapCallback", "outputs": [], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "factory", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "poolDeployer", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "tokenIn", "type": "address"}, {"internalType": "address", "name": "tokenOut", "type": "address"}, {"internalType": "address", "name": "deployer", "type": "address"}, {"internalType": "uint256", "name": "amountIn", "type": "uint256"}, {"internalType": "uint160", "name": "limitSqrtPrice", "type": "uint160"}], "name": "quoteExactInputSingle", "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}, {"internalType": "uint16", "name": "fee", "type": "uint16"}], "stateMutability": "nonpayable", "type": "function"}
]

swap_router_abi = [
    {"inputs": [{"internalType": "address", "name": "_factory", "type": "address"}, {"internalType": "address", "name": "_WNativeToken", "type": "address"}, {"internalType": "address", "name": "_poolDeployer", "type": "address"}], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "WNativeToken", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "int256", "name": "amount0Delta", "type": "int256"}, {"internalType": "int256", "name": "amount1Delta", "type": "int256"}, {"internalType": "bytes", "name": "data", "type": "bytes"}], "name": "algebraSwapCallback", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "address", "name": "tokenIn", "type": "address"}, {"internalType": "address", "name": "tokenOut", "type": "address"}, {"internalType": "address", "name": "deployer", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}, {"internalType": "uint256", "name": "amountIn", "type": "uint256"}, {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"}, {"internalType": "uint160", "name": "limitSqrtPrice", "type": "uint160"}], "internalType": "struct ISwapRouter.ExactInputSingleParams", "name": "params", "type": "tuple"}], "name": "exactInputSingle", "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}], "stateMutability": "payable", "type": "function"}
]

# Contract Instances
swap_router = w3.eth.contract(address=w3.to_checksum_address(swap_router_address), abi=swap_router_abi)
quoter = w3.eth.contract(address=w3.to_checksum_address(quoter_address), abi=quoter_abi)
factory = w3.eth.contract(address=w3.to_checksum_address(algebra_factory_address), abi=factory_abi)
weth = w3.eth.contract(address=w3.to_checksum_address(weth_address), abi=weth_abi)
usdt = w3.eth.contract(address=w3.to_checksum_address(usdt_address), abi=usdt_abi)

# Gas Settings
max_fee = w3.to_wei(config["gas_settings"]["max_fee_gwei"], "gwei")
max_priority_fee = w3.to_wei(config["gas_settings"]["priority_fee_gwei"], "gwei")

# Pool Info
def get_pool_info(token_in, token_out, slippage_tolerance=0.02):
    pool_address = factory.functions.poolByPair(token_in, token_out).call()
    if pool_address == "0x0000000000000000000000000000000000000000":
        raise Exception("Pool not found")
    pool = w3.eth.contract(address=w3.to_checksum_address(pool_address), abi=pool_abi)
    
    liquidity = pool.functions.liquidity().call()
    token0_addr = pool.functions.token0().call()
    token1_addr = pool.functions.token1().call()
    global_state = pool.functions.globalState().call()
    reserves = pool.functions.getReserves().call()
    
    price = global_state[0]  # sqrtPriceX96
    tick = global_state[1]
    print(f"Pool: {pool_address}, Token0: {token0_addr}, Token1: {token1_addr}, Liquidity: {liquidity}")
    print(f"Price (sqrtPriceX96): {price}, Tick: {tick}")
    print(f"Reserves: {reserves[0] / 10**6} USDT, {reserves[1] / 10**18} WETH")
    
    reserve_price = (reserves[0] / 10**6) / (reserves[1] / 10**18) if reserves[1] > 0 else 0
    usdt_per_weth = int(reserve_price * 10**6)
    eth_per_usdt = int((10**18 / reserve_price)) if reserve_price > 0 else 0
    
    print(f"Reserve Price: {reserve_price} USDT/WETH")
    print(f"Calculated Price: {usdt_per_weth / 10**6} USDT/WETH, {eth_per_usdt / 10**18} ETH/USDT")
    return pool_address, usdt_per_weth, eth_per_usdt, reserves, slippage_tolerance

# Quote Swap
def quote_swap(token_in, token_out, amount_in):
    amount_out, _ = quoter.functions.quoteExactInputSingle(
        token_in,
        token_out,
        algebra_factory_address,  # Deployer = factory for Algebra pools
        amount_in,
        0  # No sqrtPriceLimitX96
    ).call()
    print(f"Quoted output: {amount_out / 10**6} USDT")
    return amount_out

# Approve Token
def approve_token(token_contract, amount, token_name):
    allowance = token_contract.functions.allowance(account.address, swap_router_address).call()
    if allowance >= amount:
        print(f"{token_name} approved for {allowance / 10**(18 if token_name == 'WETH' else 6)}")
        return
    nonce = w3.eth.get_transaction_count(account.address)
    tx = token_contract.functions.approve(swap_router_address, amount * 2).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
        "gas": 100000,
        "chainId": config["chain_id"]
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    print(f"{token_name} Approval Tx: {tx_hash.hex()}")
    if receipt["status"] == 0:
        raise Exception(f"{token_name} approval failed")

# Wrap ETH to WETH
def wrap_eth(amount):
    nonce = w3.eth.get_transaction_count(account.address)
    tx = weth.functions.deposit().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "value": amount,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
        "gas": 100000,
        "chainId": config["chain_id"]
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    print(f"WETH Deposit Tx: {tx_hash.hex()}")
    if receipt["status"] == 0:
        raise Exception("WETH deposit failed")

# Swap Function
def perform_swap(amount_in, token_in, token_out):
    pool_address, usdt_per_weth, eth_per_usdt, reserves, slippage = get_pool_info(token_in, token_out)
    
    expected_out = (amount_in * usdt_per_weth) // 10**18
    amount_out_minimum = int(expected_out * (1 - slippage))
    print(f"Expected output: {expected_out / 10**6} USDT, Min: {amount_out_minimum / 10**6} USDT")
    
    # Quote the swap
    quoted_out = quote_swap(token_in, token_out, amount_in)
    if quoted_out < amount_out_minimum:
        raise Exception(f"Quoted output {quoted_out / 10**6} USDT below min {amount_out_minimum / 10**6} USDT")
    
    nonce = w3.eth.get_transaction_count(account.address)
    eth_balance = w3.eth.get_balance(account.address)
    if eth_balance < amount_in:
        raise Exception(f"Insufficient ETH balance: {eth_balance / 10**18} ETH")
    wrap_eth(amount_in)
    weth_balance = weth.functions.balanceOf(account.address).call()
    if weth_balance < amount_in:
        raise Exception(f"Insufficient WETH balance: {weth_balance / 10**18} WETH")
    approve_token(weth, amount_in, "WETH")
    
    swap_params = (
        weth_address,
        usdt_address,
        algebra_factory_address,  # Deployer = factory for Algebra pools
        account.address,
        int(time.time()) + 1200,
        amount_in,
        amount_out_minimum,
        0  # No sqrtPriceLimitX96
    )
    
    # Simulate
    try:
        simulated_out = swap_router.functions.exactInputSingle(swap_params).call({"from": account.address})
        print(f"Simulated output: {simulated_out / 10**6} USDT")
        if simulated_out < amount_out_minimum:
            raise Exception(f"Simulated output {simulated_out / 10**6} below min {amount_out_minimum / 10**6}")
    except Exception as e:
        print(f"Simulation failed: {str(e)}")
        raise
    
    # Execute
    tx = swap_router.functions.exactInputSingle(swap_params).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
        "gas": 500000,
        "chainId": config["chain_id"]
    })
    print(f"Tx details: {tx}")
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if receipt["status"] == 0:
        print(f"Swap failed: {tx_hash.hex()}")
        try:
            revert_reason = w3.eth.call(tx, block_identifier=receipt["blockNumber"] - 1)
            if revert_reason.hex().startswith("0x08c379a0"):
                error_msg = w3.to_text(revert_reason[68:]).split('\x00')[0]
                print(f"Decoded revert reason: {error_msg}")
            else:
                print(f"Raw revert data: {revert_reason.hex()}")
        except Exception as e:
            print(f"Revert decode failed: {str(e)}")
        raise Exception(f"Swap failed with tx: {tx_hash.hex()}")
    
    print(f"Swap Tx: {tx_hash.hex()}")
    print(f"Swapped {amount_in / 10**18} ETH → {simulated_out / 10**6} USDT")
    return simulated_out

# Execute
if __name__ == "__main__":
    try:
        print("\nSwapping 0.0001 ETH to USDT...")
        amount_in_eth = w3.to_wei(config["swap_amount_eth"], "ether")
        perform_swap(amount_in_eth, weth_address, usdt_address)
        print("Swap completed!")
    except Exception as e:
        print(f"Execution failed: {str(e)}")
