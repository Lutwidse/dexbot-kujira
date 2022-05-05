import logging

from .contract import Contract

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.bank import MsgSend
from terra_sdk.core.wasm.msgs import MsgExecuteContract
from terra_sdk.core import Coins, Coin
from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)

COLUMBUS = ['https://lcd.terra.dev', 'columbus-5']
BOMBAY = ['https://bombay-lcd.terra.dev/', 'bombay-12']

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class OrcaDexbot():
    def __init__(self, network, mnemonic):
        if network == 'mainnet':
            self.terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
        elif network == 'testnet':
            self.terra = LCDClient(BOMBAY[0], BOMBAY[1])
        self.wallet = self.terra.wallet(MnemonicKey(mnemonic=mnemonic))

        self._ACC_ADDRESS = self.wallet.key.acc_address
        self._contract = Contract()

    def usd_to_uusd(self, usd) -> str:
        return str(usd*1000000)

    def create_transaction(self, msgs) -> BlockTxBroadcastResult:
        tx = self.wallet.create_and_sign_tx(CreateTxOptions(
            msgs=msgs,
        ))
        result = self.terra.tx.broadcast(tx)
        return result
    
    def test_transaction(self, amount):
        msgs=[MsgSend(
            from_address=self._ACC_ADDRESS,
            to_address=self._ACC_ADDRESS,
            amount=Coin('uusd', amount)
            )]
        tx = self.create_transaction(msgs)
        logger.debug(tx)
    
    def test_transaction_anchor(self, amount):
        msgs=[MsgExecuteContract(
            sender=self._ACC_ADDRESS,
            contract=self._contract.ANCHOR_MARKET,
            execute_msg={"deposit_stable": {}},
            coins=Coins([Coin('uusd', amount)])
            )]
        tx = self.create_transaction(msgs)
        logger.debug(tx)