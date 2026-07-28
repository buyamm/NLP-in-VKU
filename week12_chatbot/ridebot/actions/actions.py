# -*- coding: utf-8 -*-
"""
RideBot - Custom Actions
Xử lý logic đặt xe: tính khoảng cách, giá tiền và lưu lịch sử.
"""

import csv
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Text

from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.types import DomainDict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dữ liệu khoảng cách (km) giữa các địa điểm (hai chiều)
# ---------------------------------------------------------------------------
DISTANCES: Dict[tuple, int] = {
    ("vku", "sân bay"): 8,
    ("sân bay", "vku"): 8,
    ("cầu rồng", "bến xe"): 5,
    ("bến xe", "cầu rồng"): 5,
    ("vku", "bến xe"): 15,
    ("bến xe", "vku"): 15,
    ("cầu sông hàn", "sân bay"): 3,
    ("sân bay", "cầu sông hàn"): 3,
    ("cầu rồng", "sân bay"): 6,
    ("sân bay", "cầu rồng"): 6,
    ("vku", "cầu rồng"): 7,
    ("cầu rồng", "vku"): 7,
    ("vku", "cầu sông hàn"): 9,
    ("cầu sông hàn", "vku"): 9,
    ("bến xe", "sân bay"): 12,
    ("sân bay", "bến xe"): 12,
    ("bến xe", "cầu sông hàn"): 10,
    ("cầu sông hàn", "bến xe"): 10,
    ("cầu rồng", "cầu sông hàn"): 2,
    ("cầu sông hàn", "cầu rồng"): 2,
}

# Giá tiền theo loại xe (VNĐ/km)
PRICE_PER_KM: Dict[str, int] = {
    "xe máy": 8_000,
    "ô tô": 12_000,
    "4 chỗ": 14_000,
    "7 chỗ": 18_000,
}

# Danh sách loại xe hợp lệ
VALID_VEHICLE_TYPES = list(PRICE_PER_KM.keys())

# File lưu lịch sử đặt xe
HISTORY_FILE = "/app/data/ride_history.csv"


def _normalize(text: Optional[str]) -> str:
    """Chuẩn hóa chuỗi: lowercase, strip khoảng trắng."""
    if not text:
        return ""
    return text.strip().lower()


def _get_distance(from_loc: str, to_loc: str) -> int:
    """Lấy khoảng cách giữa 2 địa điểm. Mặc định 10 km nếu không tìm thấy."""
    key = (_normalize(from_loc), _normalize(to_loc))
    return DISTANCES.get(key, 10)


def _get_price_per_km(vehicle: str) -> int:
    """Lấy giá/km theo loại xe. Mặc định 10,000đ/km nếu không tìm thấy."""
    return PRICE_PER_KM.get(_normalize(vehicle), 10_000)


def _save_ride_history(
    from_location: str,
    to_location: str,
    vehicle_type: str,
    distance: int,
    total_price: int,
) -> None:
    """Lưu lịch sử đặt xe vào file CSV."""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        file_exists = os.path.isfile(HISTORY_FILE)
        with open(HISTORY_FILE, mode="a", newline="", encoding="utf-8") as f:
            fieldnames = [
                "timestamp",
                "from_location",
                "to_location",
                "vehicle_type",
                "distance_km",
                "total_price_vnd",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "from_location": from_location,
                    "to_location": to_location,
                    "vehicle_type": vehicle_type,
                    "distance_km": distance,
                    "total_price_vnd": total_price,
                }
            )
        logger.info("Đã lưu lịch sử đặt xe vào %s", HISTORY_FILE)
    except Exception as e:
        logger.error("Lỗi khi lưu lịch sử đặt xe: %s", e)


# ---------------------------------------------------------------------------
# Form Validation
# ---------------------------------------------------------------------------
class ValidateRideBookingForm(FormValidationAction):
    """Validate các slot trong ride_booking_form."""

    def name(self) -> Text:
        return "validate_ride_booking_form"

    def validate_vehicle_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Kiểm tra loại xe có hợp lệ không."""
        normalized = _normalize(slot_value)

        # Kiểm tra trực tiếp
        if normalized in [_normalize(v) for v in VALID_VEHICLE_TYPES]:
            # Chuẩn hóa về tên chính thức
            for v in VALID_VEHICLE_TYPES:
                if _normalize(v) == normalized:
                    return {"vehicle_type": v}

        dispatcher.utter_message(
            text=(
                f"Xin lỗi, loại xe '{slot_value}' không hợp lệ. "
                f"Vui lòng chọn một trong các loại sau: "
                f"{', '.join(VALID_VEHICLE_TYPES)}."
            )
        )
        return {"vehicle_type": None}

    def validate_from_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Kiểm tra điểm đi có hợp lệ không."""
        if slot_value and len(str(slot_value).strip()) > 0:
            return {"from_location": slot_value.strip()}
        dispatcher.utter_message(text="Vui lòng nhập điểm đi hợp lệ.")
        return {"from_location": None}

    def validate_to_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Kiểm tra điểm đến có hợp lệ không."""
        if slot_value and len(str(slot_value).strip()) > 0:
            return {"to_location": slot_value.strip()}
        dispatcher.utter_message(text="Vui lòng nhập điểm đến hợp lệ.")
        return {"to_location": None}


# ---------------------------------------------------------------------------
# Custom Action: Xác nhận đặt xe
# ---------------------------------------------------------------------------
class ActionConfirmRide(Action):
    """Tính giá và xác nhận đặt xe cho người dùng."""

    def name(self) -> Text:
        return "action_confirm_ride"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        from_location: str = tracker.get_slot("from_location") or "không xác định"
        to_location: str = tracker.get_slot("to_location") or "không xác định"
        vehicle_type: str = tracker.get_slot("vehicle_type") or "xe máy"

        # Tính khoảng cách và giá
        distance = _get_distance(from_location, to_location)
        unit_price = _get_price_per_km(vehicle_type)
        total_price = distance * unit_price

        _save_ride_history(from_location, to_location, vehicle_type, distance, total_price)

        message = (
            f"✅ Đã đặt {vehicle_type} từ *{from_location}* đến *{to_location}*.\n"
            f"📍 Khoảng cách dự kiến: {distance} km.\n"
            f"💰 Giá dự kiến: {total_price:,}đ.\n\n"
            f"Cảm ơn bạn đã sử dụng RideBot! 🚗"
        )
        dispatcher.utter_message(text=message)

        # Reset slots sau khi đặt xong
        return [
            SlotSet("from_location", None),
            SlotSet("to_location", None),
            SlotSet("vehicle_type", None),
        ]
