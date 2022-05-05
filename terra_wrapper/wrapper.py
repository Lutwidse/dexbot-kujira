import logging
import base64

from terra_sdk.client.lcd import Wallet
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)


class TerraWrapper:
    def __init__(self, _wallet, _logger):
        self._wallet: Wallet = _wallet
        self._logger: logging = _logger
        pass

    def _create_transaction(self, msgs) -> BlockTxBroadcastResult:
        try:
            self._logger.info(msgs)

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
            self._logger.debug("[_create_transaction]", stack_info=True)
