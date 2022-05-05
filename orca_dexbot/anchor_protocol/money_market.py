import logging
from terra_sdk.client.lcd import LCDClient
from orca_dexbot import contract


class Overseer:
    def __init__(self, _logger, _terra, _contract):
        self._logger: logging = _logger
        self._terra: LCDClient = _terra
        self._contract: contract = _contract

    def epoch_state(self):
        try:
            query = {"epoch_state": {}}
            result = self._terra.wasm.contract_query(
                self._contract.ANCHOR_MARKET, query
            )
            self._logger.info(result)
            return result
        except:
            self._logger.debug("[_get_cw_token]", exc_info=True, stack_info=True)
