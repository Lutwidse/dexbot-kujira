import logging
import base64

from .contract import MainnetContract, TestnetContract
from .anchor_protocol.money_market import Overseer
from .anchor_protocol.liquidation import Liquidation
from ..terra_wrapper.wrapper import TerraWrapper

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.bank import MsgSend
from terra_sdk.core.wasm.msgs import MsgExecuteContract
from terra_sdk.core import Coins, Coin
from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)

COLUMBUS = ["https://lcd.terra.dev", "columbus-5"]
BOMBAY = ["https://bombay-lcd.terra.dev/", "bombay-12"]

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler("debug.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class OrcaDexbot:
    def __init__(self, network, mnemonic):
        if network == "mainnet":
            self._terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
            self._contract = MainnetContract()
        elif network == "testnet":
            self._terra = LCDClient(BOMBAY[0], BOMBAY[1])
            self._contract = TestnetContract()

        self._wallet = self._terra.wallet(MnemonicKey(mnemonic=mnemonic))
        self._sequence = self._wallet.sequence()
        self._ACC_ADDRESS = self._wallet.key.acc_address

        self._wrapper = TerraWrapper(self._wallet, logger)
        self._overseer = Overseer(self._terra, self._contract, logger)
        self._liquidation = Liquidation(self._terra, self._contract, logger, self._wrapper)

    def _usd_uusd_conversion(self, usd, is_usd=True) -> str:
        if is_usd:
            result = str(usd * 1000000)
        else:
            result = str(usd / 1000000)
        logger.info(result)
        return result

    def _get_native_token(self, wallet_address) -> dict:
        try:
            result = self._terra.bank.balance(wallet_address)
            logger.info(result)
            return result
        except:
            logger.debug(stack_info=True)

    def _get_cw_token(self, token_address) -> dict:
        try:
            query = {"balance": {"address": self._ACC_ADDRESS}}
            result = self._terra.wasm.contract_query(token_address, query)
            logger.info(result)
            return result
        except:
            logger.debug("[_get_cw_token]", stack_info=True)

    def _create_transaction(self, msgs) -> BlockTxBroadcastResult:
        try:
            logger.info(msgs)

            tx = self._wallet.create_and_sign_tx(
                CreateTxOptions(
                    msgs=msgs,
                    gas="auto",
                    fee_denoms="uusd",
                    gas_adjustment=2,
                    sequence=self._sequence,
                )
            )
            self._sequence = self._sequence + 1
            result = self._terra.tx.broadcast(tx)
            return result
        except:
            logger.debug("[_create_transaction]", stack_info=True)

    def test_transaction(self, amount):
        msgs = [
            MsgSend(
                from_address=self._ACC_ADDRESS,
                to_address=self._ACC_ADDRESS,
                amount=Coin("uusd", self._usd_uusd_conversion(amount)),
            )
        ]
        tx = self.create_transaction(msgs)
        logger.debug(tx)

    def transaction_anchor(self, amount):
        msgs = [
            MsgExecuteContract(
                sender=self._ACC_ADDRESS,
                contract=self._contract.ANCHOR_MARKET,
                execute_msg={"deposit_stable": {}},
                coins=Coins([Coin("uusd", self._usd_uusd_conversion(amount))]),
            )
        ]
        tx = self.create_transaction(msgs)
        logger.info(tx)

    def transaction_anchor_aust(self, amount, premium_slot, ltv, cumulative_value):
        self._liquidation.submit_bid(amount, premium_slot, ltv, cumulative_value)