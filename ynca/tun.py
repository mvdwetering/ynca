from __future__ import annotations

import logging
from typing import Optional

from .constants import Band, Subunit
from .function_mixins import FunctionMixinBase
from .helpers import number_to_string_with_stepsize
from .subunit import SubunitBase


class TunerFunctionMixin(FunctionMixinBase):

    FUNCTION_MIXIN_FUNCTIONS = ["BAND", "AMFREQ", "FMFREQ"]

    def function_mixin_on_initialize_attributes(self):
        self._attr_band: str | None = None
        self._attr_amfreq: str | None = None
        self._attr_fmfreq: str | None = None

    @property
    def band(self) -> Optional[Band]:
        """Get band of subunit"""
        return Band(self._attr_band) if self._attr_band is not None else None

    @band.setter
    def band(self, value: Band):
        """Set band of subunit"""
        self._put("BAND", value)  # type: ignore

    @property
    def amfreq(self) -> Optional[int]:
        """Get AM frequency of subunit"""
        return int(self._attr_amfreq) if self._attr_amfreq is not None else None

    @amfreq.setter
    def amfreq(self, value: int):
        """Set AM frequency of subunit"""
        self._put("AMFREQ", number_to_string_with_stepsize(value, 0, 10))  # type: ignore

    @property
    def fmfreq(self) -> Optional[float]:
        """Get FM frequency of subunit"""
        return float(self._attr_fmfreq) if self._attr_fmfreq is not None else None

    @fmfreq.setter
    def fmfreq(self, value: int):
        """Set FM frequency of subunit"""
        self._put("FMFREQ", number_to_string_with_stepsize(value, 2, 0.2))  # type: ignore


class Tun(
    TunerFunctionMixin,
    SubunitBase,
):
    id = Subunit.TUN
