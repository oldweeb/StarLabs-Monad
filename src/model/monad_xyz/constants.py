AMBIENT_ABI = [{'inputs': [{'internalType': 'address', 'name': 'authority', 'type': 'address'}, {'internalType': 'address', 'name': 'coldPath', 'type': 'address'}], 'stateMutability': 'nonpayable', 'type': 'constructor'}, {'inputs': [{'internalType': 'bytes32', 'name': 'pool', 'type': 'bytes32'}, {'internalType': 'int24', 'name': 'tick', 'type': 'int24'}, {'internalType': 'bool', 'name': 'isBid', 'type': 'bool'}, {'internalType': 'uint32', 'name': 'pivotTime', 'type': 'uint32'}, {'internalType': 'uint64', 'name': 'feeMileage', 'type': 'uint64'}], 'name': 'CrocKnockoutCross', 'type': 'event'}, {'inputs': [{'internalType': 'uint16', 'name': 'callpath', 'type': 'uint16'}, {'internalType': 'bytes', 'name': 'cmd', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'sudo', 'type': 'bool'}], 'name': 'protocolCmd', 'outputs': [{'internalType': 'bytes', 'name': '', 'type': 'bytes'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': 'slot', 'type': 'uint256'}], 'name': 'readSlot', 'outputs': [{'internalType': 'uint256', 'name': 'data', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'base', 'type': 'address'}, {'internalType': 'address', 'name': 'quote', 'type': 'address'}, {'internalType': 'uint256', 'name': 'poolIdx', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'isBuy', 'type': 'bool'}, {'internalType': 'bool', 'name': 'inBaseQty', 'type': 'bool'}, {'internalType': 'uint128', 'name': 'qty', 'type': 'uint128'}, {'internalType': 'uint16', 'name': 'tip', 'type': 'uint16'}, {'internalType': 'uint128', 'name': 'limitPrice', 'type': 'uint128'}, {'internalType': 'uint128', 'name': 'minOut', 'type': 'uint128'}, {'internalType': 'uint8', 'name': 'reserveFlags', 'type': 'uint8'}], 'name': 'swap', 'outputs': [{'internalType': 'int128', 'name': '', 'type': 'int128'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'uint16', 'name': 'callpath', 'type': 'uint16'}, {'internalType': 'bytes', 'name': 'cmd', 'type': 'bytes'}], 'name': 'userCmd', 'outputs': [{'internalType': 'bytes', 'name': '', 'type': 'bytes'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'uint16', 'name': 'proxyIdx', 'type': 'uint16'}, {'internalType': 'bytes', 'name': 'cmd', 'type': 'bytes'}, {'internalType': 'bytes', 'name': 'conds', 'type': 'bytes'}, {'internalType': 'bytes', 'name': 'relayerTip', 'type': 'bytes'}, {'internalType': 'bytes', 'name': 'signature', 'type': 'bytes'}], 'name': 'userCmdRelayer', 'outputs': [{'internalType': 'bytes', 'name': 'output', 'type': 'bytes'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'uint16', 'name': 'proxyIdx', 'type': 'uint16'}, {'internalType': 'bytes', 'name': 'input', 'type': 'bytes'}, {'internalType': 'address', 'name': 'client', 'type': 'address'}, {'internalType': 'uint256', 'name': 'salt', 'type': 'uint256'}], 'name': 'userCmdRouter', 'outputs': [{'internalType': 'bytes', 'name': '', 'type': 'bytes'}], 'stateMutability': 'payable', 'type': 'function'}]

#AMBIENT CONSTANTS
AMBIENT_CONTRACT = "0x88B96aF200c8a9c35442C8AC6cd3D22695AaE4F0"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
POOL_IDX = 36000
RESERVE_FLAGS = 0
TIP = 0
MAX_SQRT_PRICE = 21267430153580247136652501917186561137
MIN_SQRT_PRICE = 65537
SLIPPAGE = 1  # 1%


AMBIENT_TOKENS = {
    "usdt": {
        "address": "0x88b8E2161DEDC77EF4ab7585569D2415a1C1055D",
        "decimals": 6
    },
    "usdc": {
        "address": "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea",
        "decimals": 6
    },
    "weth": {
        "address": "0xB5a30b0FDc5EA94A52fDc42e3E9760Cb8449Fb37",
        "decimals": 18
    },
    "wbtc": {
        "address": "0xcf5a6076cfa32686c0Df13aBaDa2b40dec133F1d",
        "decimals": 8
    }
}