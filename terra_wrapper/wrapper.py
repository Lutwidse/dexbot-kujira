import logging

from terra_sdk.client.lcd import LCDClient
from terra_sdk.client.lcd import Wallet
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)


class TerraWrapper:
    def __init__(self, _logger, _terra, _wallet, _sequence):
        self._logger: logging = _logger
        self._terra: LCDClient = _terra
        self._wallet: Wallet = _wallet
        self._sequence: int = _sequence
        pass

    def _create_transaction(self, msgs) -> BlockTxBroadcastResult:
        try:
            self._logger.debug(msgs)

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
            self._logger.debug("[_create_transaction]", exc_info=True, stack_info=True)
